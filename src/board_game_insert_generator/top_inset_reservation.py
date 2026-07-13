"""P63 top-inset reservations for boards, rulebooks and other flat items.

The module stays CAD-agnostic.  It resolves flat-item placement and removal
order, then intersects the resulting top-down cuts with already placed
requested bodies.  A reservation is never turned into a printable body or a
content cavity.
"""

from __future__ import annotations

from copy import deepcopy
from math import isclose
from typing import Any

from board_game_insert_generator.project_v1 import ProjectNormalization, normalize_project_draft


TOP_INSET_RESERVATION_SCHEMA_V1 = "bgig.top_inset_reservations.v1"
TOP_INSET_CUT_KIND = "top_inset"
TOP_INSET_GRIP_CUT_KIND = "top_inset_grip"
TOP_INSET_OPERATION_KIND = "subtract_top_inset_reservation"
TOP_INSET_GRIP_OPERATION_KIND = "subtract_top_inset_grip"
_EPSILON = 0.0001
_PREFERRED_GRIP_DEPTH_MM = 8.0
_MIN_GRIP_DEPTH_MM = 2.0
_MIN_GRIP_WIDTH_MM = 16.0
_MAX_GRIP_WIDTH_MM = 32.0


def derive_top_inset_reservations(raw_project: object) -> dict[str, object]:
    """Resolve flat items into deterministic top-inset reservations.

    Items without an explicit XY origin are centred.  Items without an
    explicit rotation keep their declared orientation when it fits, otherwise
    a 90-degree rotation is attempted.  The returned order is bottom-to-top;
    ``removal_order`` is one-based and top-first.
    """

    normalization = normalize_project_draft(raw_project)
    project = normalization.project
    box_payload = _mapping(project["box"])
    box = _dimension(box_payload["inner_dimensions_mm"])
    design_top_z = min(float(box_payload["usable_height_mm"]), box["z"])
    clearance = float(_mapping(project["layout"])["layout_clearance_mm"])
    ordered = _ordered_flat_items(_mappings(project["flat_items"]))
    blockers: list[dict[str, object]] = []

    resolved: list[dict[str, object]] = []
    for item in ordered:
        reservation, item_blockers = _resolve_item(item, box, clearance)
        resolved.append(reservation)
        blockers.extend(item_blockers)

    reservations = _resolve_vertical_layers(resolved, design_top_z)
    total_stack_height = max(
        (float(item["inset_depth_from_top_mm"]) for item in reservations),
        default=0.0,
    )
    if total_stack_height > design_top_z + _EPSILON:
        blockers.append(
            _blocker(
                "TOP_INSET_STACK_EXCEEDS_HEIGHT",
                f"Les plateaux et livrets demandent { _round(total_stack_height) } mm, "
                f"mais la hauteur utilisable est { _round(design_top_z) } mm.",
                "Reduis leur epaisseur/quantite ou augmente la hauteur utilisable.",
            )
        )

    removal_sequence = [
        {
            "order": int(item["removal_order"]),
            "reservation_id": item["id"],
            "flat_item_id": item["flat_item_id"],
            "name": item["name"],
        }
        for item in sorted(reservations, key=lambda value: int(value["removal_order"]))
    ]
    status = "blocked" if blockers else ("not_required" if not reservations else "ready_for_intersection")
    return {
        "schema_version": TOP_INSET_RESERVATION_SCHEMA_V1,
        "source": _source_payload(normalization),
        "project_name": project["project_name"],
        "status": status,
        "design_top_z_mm": _round(design_top_z),
        "total_flat_height_mm": _round(total_stack_height),
        "clearance_mm": _round(clearance),
        "reservations": reservations,
        "removal_sequence": removal_sequence,
        "blockers": blockers,
        "summary": {
            "status": status,
            "reservation_count": len(reservations),
            "flat_copy_count": sum(int(item["quantity"]) for item in reservations),
            "reserved_height_mm": _round(total_stack_height),
            "storage_height_mm": _round(design_top_z),
        },
        "invariants": {
            "localized_top_down_cuts": True,
            "containers_keep_design_top_outside_footprints": True,
            "reservation_is_not_printable_body": True,
            "automatic_body_count": 0,
        },
    }


def apply_top_inset_reservations(
    raw_project: object,
    placements: list[dict[str, object]],
) -> dict[str, object]:
    """Intersect resolved reservations with placed bodies and validate cuts."""

    normalization = normalize_project_draft(raw_project)
    project = normalization.project
    plan = derive_top_inset_reservations(project)
    result_placements = deepcopy(placements)
    for placement in result_placements:
        placement["top_inset_cuts"] = []

    blockers = [deepcopy(item) for item in _mappings(plan["blockers"])]
    warnings: list[dict[str, object]] = []
    design_top = float(plan["design_top_z_mm"])
    layout = _mapping(project["layout"])
    group_floor = {
        str(group["id"]): float(group["floor_thickness_mm"] or layout["default_floor_thickness_mm"])
        for group in _mappings(project["container_groups"])
    }
    cuts: list[dict[str, object]] = []
    supports: list[dict[str, object]] = []
    cavity_compensation_by_placement: dict[str, dict[str, float]] = {}

    for reservation in _mappings(plan["reservations"]):
        reservation_cuts: list[dict[str, object]] = []
        reservation_support_area = 0.0
        footprint = _xy_rect(reservation["cut_origin_mm"], reservation["cut_size_mm"])
        grip = _mapping(reservation["grip_zone"])
        grip_rect = _xy_rect(grip["origin_mm"], grip["size_mm"])
        for placement in result_placements:
            body_origin = _dimension(placement["origin_mm"])
            body_size = _dimension(placement["world_size_mm"])
            body_top = body_origin["z"] + body_size["z"]
            body_rect = {
                "x": body_origin["x"],
                "y": body_origin["y"],
                "width": body_size["x"],
                "height": body_size["y"],
            }
            for cut_kind, requested_rect in (
                (TOP_INSET_CUT_KIND, footprint),
                (TOP_INSET_GRIP_CUT_KIND, grip_rect),
            ):
                intersection = _intersection(body_rect, requested_rect)
                if intersection is None:
                    continue
                if not isclose(body_top, design_top, abs_tol=0.001):
                    # P64 may place another requested body above this XY footprint.
                    # Only bodies opening on the design top receive the local cut;
                    # missing top coverage is diagnosed after all stages are scanned.
                    continue
                depth = float(reservation["inset_depth_from_top_mm"])
                minimum_floor = group_floor.get(
                    str(placement.get("container_group_id", "")),
                    float(layout["default_floor_thickness_mm"]),
                )
                retained = body_size["z"] - depth
                if retained + _EPSILON < minimum_floor:
                    blockers.append(
                        _blocker(
                            "TOP_INSET_PIERCES_BODY_FLOOR",
                            f"L encastrement '{reservation['name']}' laisserait { _round(retained) } mm "
                            f"sous le corps '{placement['name']}', minimum { _round(minimum_floor) } mm.",
                            "Reduis l epaisseur des elements plats ou augmente la hauteur de ce corps.",
                            str(placement["id"]),
                        )
                    )
                    continue
                cavity_overlap_area, overlapping_cavity_ids = _cavity_interactions(
                    placement,
                    intersection,
                )
                if cut_kind == TOP_INSET_CUT_KIND:
                    placement_compensation = cavity_compensation_by_placement.setdefault(
                        str(placement["id"]), {}
                    )
                    for cavity_id in overlapping_cavity_ids:
                        placement_compensation[cavity_id] = max(
                            placement_compensation.get(cavity_id, 0.0),
                            depth,
                        )
                cut = {
                    "id": f"{reservation['id']}:{placement['id']}:{cut_kind}:{len(reservation_cuts)}",
                    "kind": cut_kind,
                    "reservation_id": reservation["id"],
                    "flat_item_id": reservation["flat_item_id"],
                    "placement_id": placement["id"],
                    "removal_order": reservation["removal_order"],
                    "world_origin_mm": {
                        "x": _round(intersection["x"]),
                        "y": _round(intersection["y"]),
                        "z": _round(design_top - depth),
                    },
                    "local_origin_mm": {
                        "x": _round(intersection["x"] - body_origin["x"]),
                        "y": _round(intersection["y"] - body_origin["y"]),
                        "z": _round(body_size["z"] - depth),
                    },
                    "size_mm": {
                        "x": _round(intersection["width"]),
                        "y": _round(intersection["height"]),
                        "z": _round(depth),
                    },
                    "retained_body_below_mm": _round(retained),
                    "minimum_floor_mm": _round(minimum_floor),
                    "cavity_overlap_area_mm2": _round(cavity_overlap_area),
                    "non_perforating": True,
                }
                _values(placement["top_inset_cuts"]).append(cut)
                cuts.append(cut)
                reservation_cuts.append(cut)
                if cut_kind == TOP_INSET_CUT_KIND:
                    cut_area = intersection["width"] * intersection["height"]
                    reservation_support_area += max(0.0, cut_area - cavity_overlap_area)

        requested_area = footprint["width"] * footprint["height"]
        coverage = min(1.0, reservation_support_area / requested_area) if requested_area else 1.0
        if not reservation_cuts:
            blockers.append(
                _blocker(
                    "TOP_INSET_WITHOUT_SUPPORTING_BODY",
                    f"Aucun corps au sommet ne porte l element plat '{reservation['name']}'.",
                    "Ajuste son origine ou le placement des conteneurs.",
                    str(reservation["flat_item_id"]),
                )
            )
        elif coverage < 0.25:
            warnings.append(
                {
                    "code": "TOP_INSET_LOW_SUPPORT_COVERAGE",
                    "severity": "warning",
                    "message": f"L appui materiel estime pour '{reservation['name']}' est faible ({_round(coverage)}).",
                    "action": "Verifie la repartition des cavites et les zones d appui avant impression.",
                    "reference_id": reservation["flat_item_id"],
                }
            )
        supports.append(
            {
                "reservation_id": reservation["id"],
                "flat_item_id": reservation["flat_item_id"],
                "cut_count": len(reservation_cuts),
                "footprint_cut_count": sum(
                    1 for item in reservation_cuts if item["kind"] == TOP_INSET_CUT_KIND
                ),
                "required_area_mm2": _round(requested_area),
                "material_support_area_mm2": _round(reservation_support_area),
                "coverage_ratio": _round(coverage),
                "support_plane_z_mm": reservation["support_plane_z_mm"],
            }
        )

    compensations, compensation_blockers = _apply_cavity_depth_compensations(
        result_placements,
        cavity_compensation_by_placement,
        group_floor,
        float(layout["default_floor_thickness_mm"]),
    )
    blockers.extend(compensation_blockers)
    status = "blocked" if blockers else ("not_required" if not plan["reservations"] else "applied")
    ratios = [float(item["coverage_ratio"]) for item in supports]
    return {
        **deepcopy(plan),
        "status": status,
        "placements": result_placements,
        "cuts": cuts,
        "supports": supports,
        "cavity_depth_compensations": compensations,
        "support": {
            "status": "blocked" if blockers else ("not_required" if not supports else "supported_by_requested_bodies"),
            "top_support_count": sum(int(item["footprint_cut_count"]) for item in supports),
            "coverage_ratio": _round(min(ratios, default=1.0)),
            "reservations": supports,
            "note": (
                "Chaque element plat repose sur les surfaces restantes au fond de ses encastrements ; "
                "les cavites traversantes a ce niveau sont retranchees de la couverture."
            ),
        },
        "blockers": blockers,
        "warnings": warnings,
        "summary": {
            **deepcopy(_mapping(plan["summary"])),
            "status": status,
            "cut_count": len(cuts),
            "support_count": len(supports),
            "cavity_depth_compensation_count": len(compensations),
            "maximum_cavity_depth_compensation_mm": _round(
                max((float(item["compensation_mm"]) for item in compensations), default=0.0)
            ),
        },
    }


def compatibility_flat_stack_payload(top_inset_plan: dict[str, object]) -> dict[str, object]:
    """Return a bounded compatibility payload for historical consumers.

    ``storage_height_mm`` deliberately remains the design-top height: P63 no
    longer shrinks every body under one global stack.
    """

    reservations = _mappings(top_inset_plan.get("reservations", []))
    if not reservations:
        return {
            "status": "not_required",
            "reservation_clearance_mm": top_inset_plan.get("clearance_mm", 0.0),
            "physical_footprint_mm": None,
            "reservation_size_mm": None,
            "preferred_reservation_origin_mm": None,
            "reserved_height_mm": 0.0,
            "storage_height_mm": top_inset_plan.get("design_top_z_mm", 0.0),
            "items": [],
            "semantics": "localized_top_insets",
        }
    min_x = min(float(_mapping(item["cut_origin_mm"])["x"]) for item in reservations)
    min_y = min(float(_mapping(item["cut_origin_mm"])["y"]) for item in reservations)
    max_x = max(
        float(_mapping(item["cut_origin_mm"])["x"]) + float(_mapping(item["cut_size_mm"])["x"])
        for item in reservations
    )
    max_y = max(
        float(_mapping(item["cut_origin_mm"])["y"]) + float(_mapping(item["cut_size_mm"])["y"])
        for item in reservations
    )
    return {
        "status": "top_insets_reserved" if top_inset_plan.get("status") != "blocked" else "blocked",
        "reservation_clearance_mm": top_inset_plan.get("clearance_mm", 0.0),
        "physical_footprint_mm": {"x": _round(max_x - min_x), "y": _round(max_y - min_y), "z": top_inset_plan.get("total_flat_height_mm", 0.0)},
        "reservation_size_mm": {"x": _round(max_x - min_x), "y": _round(max_y - min_y), "z": top_inset_plan.get("total_flat_height_mm", 0.0)},
        "preferred_reservation_origin_mm": {"x": _round(min_x), "y": _round(min_y), "z": _round(float(top_inset_plan["design_top_z_mm"]) - float(top_inset_plan["total_flat_height_mm"]))},
        "reserved_height_mm": top_inset_plan.get("total_flat_height_mm", 0.0),
        "storage_height_mm": top_inset_plan.get("design_top_z_mm", 0.0),
        "items": deepcopy(reservations),
        "semantics": "localized_top_insets",
    }



def _resolve_vertical_layers(
    resolved: list[dict[str, object]], design_top_z: float
) -> list[dict[str, object]]:
    """Compose only overlapping flat footprints in Z.

    The input order is bottom-to-top.  Side-by-side footprints therefore share
    the same top plane instead of consuming one global stack height.
    """

    depths = [0.0 for _ in resolved]
    rectangles = [
        _xy_rect(item["cut_origin_mm"], item["cut_size_mm"])
        for item in resolved
    ]
    for index in range(len(resolved) - 1, -1, -1):
        above_depth = max(
            (
                depths[other]
                for other in range(index + 1, len(resolved))
                if _intersection(rectangles[index], rectangles[other]) is not None
            ),
            default=0.0,
        )
        depths[index] = above_depth + float(resolved[index]["total_thickness_mm"])

    count = len(resolved)
    reservations: list[dict[str, object]] = []
    for index, reservation in enumerate(resolved):
        thickness = float(reservation["total_thickness_mm"])
        depth = depths[index]
        layer_bottom = design_top_z - depth
        layer_top = layer_bottom + thickness
        final = deepcopy(reservation)
        final.update(
            {
                "level": index,
                "layer_bottom_z_mm": _round(layer_bottom),
                "layer_top_z_mm": _round(layer_top),
                "inset_depth_from_top_mm": _round(depth),
                "removal_order": count - index,
                "support_plane_z_mm": _round(layer_bottom),
            }
        )
        reservations.append(final)
    return reservations

def _resolve_item(
    item: dict[str, object],
    box: dict[str, float],
    clearance: float,
) -> tuple[dict[str, object], list[dict[str, object]]]:
    dimensions = _dimension(item["dimensions_mm"])
    requested_rotation = item.get("rotation_deg_z")
    rotations = [int(requested_rotation)] if requested_rotation is not None else [0, 90]
    blockers: list[dict[str, object]] = []
    chosen: tuple[int, float, float] | None = None
    for rotation in rotations:
        physical_x, physical_y = (
            (dimensions["x"], dimensions["y"])
            if rotation == 0
            else (dimensions["y"], dimensions["x"])
        )
        if physical_x + 2.0 * clearance <= box["x"] + _EPSILON and physical_y + 2.0 * clearance <= box["y"] + _EPSILON:
            chosen = (rotation, physical_x, physical_y)
            break
    if chosen is None:
        rotation = rotations[0]
        physical_x, physical_y = (
            (dimensions["x"], dimensions["y"])
            if rotation == 0
            else (dimensions["y"], dimensions["x"])
        )
        chosen = (rotation, physical_x, physical_y)
        blockers.append(
            _blocker(
                "TOP_INSET_FOOTPRINT_EXCEEDS_BOX",
                f"'{item['name']}' demande { _round(physical_x + 2 * clearance) } x "
                f"{ _round(physical_y + 2 * clearance) } mm avec jeu, au-dela de la boite.",
                "Reduis l empreinte, le jeu ou choisis une rotation compatible.",
                str(item["id"]),
            )
        )
    rotation, physical_x, physical_y = chosen
    cut_x = physical_x + 2.0 * clearance
    cut_y = physical_y + 2.0 * clearance
    origin_value = item.get("origin_mm")
    if origin_value is None:
        cut_origin_x = (box["x"] - cut_x) / 2.0
        cut_origin_y = (box["y"] - cut_y) / 2.0
        placement_source = "auto_center"
    else:
        physical_origin = _xy(origin_value)
        cut_origin_x = physical_origin["x"] - clearance
        cut_origin_y = physical_origin["y"] - clearance
        placement_source = "explicit_origin"
    if (
        cut_origin_x < -_EPSILON
        or cut_origin_y < -_EPSILON
        or cut_origin_x + cut_x > box["x"] + _EPSILON
        or cut_origin_y + cut_y > box["y"] + _EPSILON
    ):
        blockers.append(
            _blocker(
                "TOP_INSET_ORIGIN_OUTSIDE_BOX",
                f"L origine de '{item['name']}' place son encastrement hors de la boite.",
                "Recentre l element ou corrige son origine XY.",
                str(item["id"]),
            )
        )
    grip, grip_blocker = _grip_zone(
        cut_origin_x, cut_origin_y, cut_x, cut_y, box,
    )
    if grip_blocker is not None:
        blockers.append(
            _blocker(
                "TOP_INSET_GRIP_UNAVAILABLE",
                f"Aucune zone de prise rectangulaire ne tient autour de '{item['name']}'.",
                "Laisse au moins 2 mm libres sur un cote ou ajuste l origine.",
                str(item["id"]),
            )
        )
    return (
        {
            "id": f"top-inset:{item['id']}",
            "flat_item_id": item["id"],
            "name": item["name"],
            "kind": item["kind"],
            "quantity": item["quantity"],
            "stack_order": item["stack_order"],
            "rotation_deg_z": rotation,
            "placement_source": placement_source,
            "physical_size_mm": {
                "x": _round(physical_x),
                "y": _round(physical_y),
                "z": _round(dimensions["z"]),
            },
            "physical_origin_mm": {
                "x": _round(cut_origin_x + clearance),
                "y": _round(cut_origin_y + clearance),
            },
            "total_thickness_mm": _round(dimensions["z"] * int(item["quantity"])),
            "cut_origin_mm": {"x": _round(cut_origin_x), "y": _round(cut_origin_y)},
            "cut_size_mm": {"x": _round(cut_x), "y": _round(cut_y)},
            "grip_zone": grip,
        },
        blockers,
    )


def _grip_zone(
    x: float,
    y: float,
    width: float,
    height: float,
    box: dict[str, float],
) -> tuple[dict[str, object], str | None]:
    margins = {
        "front": y,
        "back": box["y"] - (y + height),
        "left": x,
        "right": box["x"] - (x + width),
    }
    available = [(side, value) for side, value in margins.items() if value >= _MIN_GRIP_DEPTH_MM - _EPSILON]
    if not available:
        return {
            "status": "blocked",
            "side": "none",
            "origin_mm": {"x": _round(x), "y": _round(y)},
            "size_mm": {"x": 0.0, "y": 0.0},
        }, "no_margin"
    side, margin = max(available, key=lambda entry: (entry[1], -list(margins).index(entry[0])))
    depth = min(_PREFERRED_GRIP_DEPTH_MM, margin)
    if side in {"front", "back"}:
        grip_width = min(_MAX_GRIP_WIDTH_MM, max(_MIN_GRIP_WIDTH_MM, width * 0.2), width)
        grip_x = x + (width - grip_width) / 2.0
        grip_y = y - depth if side == "front" else y + height
        size_x, size_y = grip_width, depth
    else:
        grip_width = min(_MAX_GRIP_WIDTH_MM, max(_MIN_GRIP_WIDTH_MM, height * 0.2), height)
        grip_x = x - depth if side == "left" else x + width
        grip_y = y + (height - grip_width) / 2.0
        size_x, size_y = depth, grip_width
    return {
        "status": "planned",
        "side": side,
        "origin_mm": {"x": _round(grip_x), "y": _round(grip_y)},
        "size_mm": {"x": _round(size_x), "y": _round(size_y)},
        "shape": "rectangle",
    }, None


def _cavity_interactions(
    placement: dict[str, object],
    cut_rect: dict[str, float],
) -> tuple[float, list[str]]:
    overlap_area = 0.0
    cavity_ids: list[str] = []
    for cavity in _mappings(placement.get("cavity_layout", [])):
        bounds = _cavity_world_bounds(placement, cavity)
        overlap = _intersection(cut_rect, bounds)
        if overlap is None:
            continue
        overlap_area += overlap["width"] * overlap["height"]
        cavity_ids.append(str(cavity["cavity_id"]))
    return min(cut_rect["width"] * cut_rect["height"], overlap_area), cavity_ids


def _apply_cavity_depth_compensations(
    placements: list[dict[str, object]],
    compensation_by_placement: dict[str, dict[str, float]],
    group_floor: dict[str, float],
    default_floor: float,
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    """Preserve useful asset depth below localized top insets."""

    compensations: list[dict[str, object]] = []
    blockers: list[dict[str, object]] = []
    for placement in placements:
        requested = compensation_by_placement.get(str(placement["id"]), {})
        if not requested:
            continue
        body_height = float(_mapping(placement["world_size_mm"])["z"])
        minimum_floor = group_floor.get(
            str(placement.get("container_group_id", "")),
            default_floor,
        )
        for cavity in _mappings(placement.get("cavity_layout", [])):
            cavity_id = str(cavity["cavity_id"])
            compensation = float(requested.get(cavity_id, 0.0))
            if compensation <= _EPSILON:
                continue
            base_dimensions = _dimension(
                cavity.get("base_inner_dimensions_mm", cavity["inner_dimensions_mm"])
            )
            compensated_depth = base_dimensions["z"] + compensation
            retained_floor = body_height - compensated_depth
            if retained_floor + _EPSILON < minimum_floor:
                blockers.append(
                    _blocker(
                        "TOP_INSET_PIERCES_CAVITY_FLOOR",
                        f"La cavite '{cavity_id}' dans '{placement['name']}' doit gagner "
                        f"{_round(compensation)} mm sous le plateau, mais ne laisserait que "
                        f"{_round(retained_floor)} mm de fond.",
                        "Augmente la hauteur du corps, reduis l epaisseur des elements plats "
                        "ou deplace leur empreinte.",
                        str(placement["id"]),
                    )
                )
                continue
            cavity["base_inner_dimensions_mm"] = {
                axis: _round(base_dimensions[axis]) for axis in ("x", "y", "z")
            }
            _mapping(cavity["inner_dimensions_mm"])["z"] = _round(compensated_depth)
            cavity["top_inset_compensation_mm"] = _round(compensation)
            cavity["depth_semantics"] = "asset_depth_below_localized_top_inset"
            compensations.append(
                {
                    "placement_id": placement["id"],
                    "cavity_id": cavity_id,
                    "base_depth_mm": _round(base_dimensions["z"]),
                    "compensation_mm": _round(compensation),
                    "final_depth_mm": _round(compensated_depth),
                    "retained_floor_mm": _round(retained_floor),
                }
            )
    return compensations, blockers

def _cavity_world_bounds(
    placement: dict[str, object], cavity: dict[str, object]
) -> dict[str, float]:
    body_origin = _dimension(placement["origin_mm"])
    final_local = _dimension(placement["final_outer_dimensions_mm"])
    minimum_origin = _dimension(placement["minimum_envelope_origin_in_final_mm"])
    cavity_origin = _dimension(cavity["local_origin_mm"])
    cavity_size = _dimension(cavity["inner_dimensions_mm"])
    local_x = minimum_origin["x"] + cavity_origin["x"]
    local_y = minimum_origin["y"] + cavity_origin["y"]
    rotation = int(placement.get("rotation_deg_z", 0))
    if rotation == 0:
        x, y = body_origin["x"] + local_x, body_origin["y"] + local_y
        width, height = cavity_size["x"], cavity_size["y"]
    elif rotation == 90:
        x = body_origin["x"] + final_local["y"] - local_y - cavity_size["y"]
        y = body_origin["y"] + local_x
        width, height = cavity_size["y"], cavity_size["x"]
    else:
        raise ValueError(f"Unsupported Z rotation for top-inset validation: {rotation}.")
    return {"x": x, "y": y, "width": width, "height": height, "depth": cavity_size["z"]}


def _ordered_flat_items(items: list[dict[str, object]]) -> list[dict[str, object]]:
    return sorted(
        items,
        key=lambda item: (
            item["stack_order"] is None,
            int(item["stack_order"]) if item["stack_order"] is not None else 0,
            -_area(_dimension(item["dimensions_mm"])),
            str(item["id"]),
        ),
    )


def _intersection(
    left: dict[str, float], right: dict[str, float]
) -> dict[str, float] | None:
    x0 = max(left["x"], right["x"])
    y0 = max(left["y"], right["y"])
    x1 = min(left["x"] + left["width"], right["x"] + right["width"])
    y1 = min(left["y"] + left["height"], right["y"] + right["height"])
    if x1 - x0 <= _EPSILON or y1 - y0 <= _EPSILON:
        return None
    return {"x": x0, "y": y0, "width": x1 - x0, "height": y1 - y0}


def _xy_rect(origin: object, size: object) -> dict[str, float]:
    origin_xy = _xy(origin)
    size_xy = _xy(size)
    return {"x": origin_xy["x"], "y": origin_xy["y"], "width": size_xy["x"], "height": size_xy["y"]}


def _blocker(code: str, message: str, action: str, reference_id: str = "") -> dict[str, object]:
    return {
        "code": code,
        "severity": "blocker",
        "message": message,
        "action": action,
        "reference_id": reference_id,
    }


def _source_payload(normalization: ProjectNormalization) -> dict[str, object]:
    return {
        "source_schema": normalization.source_schema,
        "migrated": normalization.migrated,
        "project_schema": normalization.project["schema_version"],
    }


def _mapping(value: object) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise TypeError("Internal top-inset value must be a mapping.")
    return value


def _mappings(value: object) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        raise TypeError("Internal top-inset value must be a list.")
    return [_mapping(item) for item in value]


def _values(value: object) -> list[Any]:
    if not isinstance(value, list):
        raise TypeError("Internal top-inset value must be a list.")
    return value


def _dimension(value: object) -> dict[str, float]:
    raw = _mapping(value)
    return {axis: float(raw[axis]) for axis in ("x", "y", "z")}


def _xy(value: object) -> dict[str, float]:
    raw = _mapping(value)
    return {axis: float(raw[axis]) for axis in ("x", "y")}


def _area(value: dict[str, float]) -> float:
    return value["x"] * value["y"]


def _round(value: float) -> float:
    return round(float(value), 4)
