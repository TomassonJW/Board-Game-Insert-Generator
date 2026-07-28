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

from board_game_insert_generator.product_grid import (
    PRODUCT_GRID_SCHEMA_V1,
    PRODUCT_GRID_STEP_MM,
    ceil_mm,
    floor_mm,
    floor_ticks,
    is_on_product_grid,
    nearest_mm,
    nearest_ticks,
    outward_size_mm,
    ticks_to_mm,
)
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
_MAX_AUTOMATIC_LAYOUT_STATES = 64
_MAX_AUTOMATIC_AXIS_POSITIONS = 10
_MAX_AUTOMATIC_POSES_PER_STATE = 24


def derive_top_inset_reservations(raw_project: object) -> dict[str, object]:
    """Resolve flat items into deterministic top-inset reservations.

    XY placement is always automatic.  The bounded search first minimizes the
    required Z stack, then uses stable geometry keys.  This preview does not
    yet know the calculated bodies; the common certificate resolves the same
    search again against their frozen cavities.
    """

    normalization = normalize_project_draft(raw_project)
    return _derive_top_inset_reservations(normalization, placements=[])


def resolve_top_inset_reservations(
    raw_project: object,
    placements: list[dict[str, object]],
    *,
    require_reserved_prisms: bool = True,
) -> dict[str, object]:
    """Resolve automatic XY poses against frozen bodies and cavities."""

    normalization = normalize_project_draft(raw_project)
    return _derive_top_inset_reservations(
        normalization,
        placements=placements,
        require_reserved_prisms=require_reserved_prisms,
    )


def _derive_top_inset_reservations(
    normalization: ProjectNormalization,
    *,
    placements: list[dict[str, object]],
    require_reserved_prisms: bool = False,
) -> dict[str, object]:
    project = normalization.project
    box_payload = _mapping(project["box"])
    box = _dimension(box_payload["inner_dimensions_mm"])
    design_top_z = min(float(box_payload["usable_height_mm"]), box["z"])
    layout = _mapping(project["layout"])
    clearance = float(layout["layout_clearance_mm"])
    default_clearance = {
        "x": clearance,
        "y": clearance,
        "z": 0.0,
    }
    ordered = _ordered_flat_items(_mappings(project["flat_items"]))
    reservations, blockers, search = _resolve_automatic_xy_layout(
        ordered,
        box=box,
        design_top_z=design_top_z,
        default_clearance=default_clearance,
        project=project,
        placements=placements,
        require_reserved_prisms=require_reserved_prisms,
    )
    total_stack_height = max(
        (
            float(region["inset_depth_from_top_mm"])
            for item in reservations
            for region in _mappings(item.get("local_depth_regions", []))
        ),
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
        "clearance_defaults_v1": deepcopy(layout["clearance_defaults_v1"]),
        "reservations": reservations,
        "removal_sequence": removal_sequence,
        "blockers": blockers,
        "automatic_xy_search": search,
        "product_grid_v1": {
            "schema_version": PRODUCT_GRID_SCHEMA_V1,
            "step_mm": PRODUCT_GRID_STEP_MM,
            "candidate_origins_quantized": True,
            "required_xy_envelopes_quantized_outward": True,
            "numeric_epsilon_mm": _EPSILON,
            "epsilon_is_not_search_resolution": True,
        },
        "summary": {
            "status": status,
            "reservation_count": len(reservations),
            "flat_copy_count": sum(int(item["quantity"]) for item in reservations),
            "reserved_height_mm": _round(total_stack_height),
            "storage_height_mm": _round(design_top_z),
        },
        "invariants": {
            "localized_top_down_cuts": True,
            "local_depth_regions_certified": True,
            "disjoint_reservations_do_not_accumulate": True,
            "overlap_accumulates_only_inside_intersection": True,
            "containers_keep_design_top_outside_footprints": True,
            "reservation_is_not_printable_body": True,
            "automatic_body_count": 0,
            "automatic_xy_placement": True,
            "manual_xy_origin_ignored": True,
            "minimum_cavity_wall_envelope_certified": not blockers,
            "automatic_xy_candidates_on_product_grid": True,
            "required_xy_envelopes_not_rounded_inward": True,
        },
    }


def certify_top_inset_reservation_prisms(
    raw_project: object,
    placements: list[dict[str, object]],
    *,
    top_inset_plan: dict[str, object] | None = None,
) -> dict[str, object]:
    """Post-certify reserved top prisms without manufacturing support.

    Minimal calculation keeps every requested body at its certified minimum
    envelope. Flat items occupy explicit upper prisms; a body may touch the
    lower plane of a prism but may not enter it. Cuts and cavity compensation
    are deliberately deferred to finalization.
    """

    plan = (
        deepcopy(top_inset_plan)
        if top_inset_plan is not None
        else resolve_top_inset_reservations(raw_project, placements)
    )
    plan = _refresh_wall_envelope_certificates(raw_project, plan, placements)
    result_placements = deepcopy(placements)
    for placement in result_placements:
        placement["top_inset_cuts"] = []

    blockers = [deepcopy(item) for item in _mappings(plan["blockers"])]
    design_top = float(plan["design_top_z_mm"])
    reserved_prisms: list[dict[str, object]] = []
    certificates: list[dict[str, object]] = []

    for reservation in _mappings(plan["reservations"]):
        for region in _local_depth_regions(reservation):
            origin_xy = _xy(region["cut_origin_mm"])
            size_xy = _xy(region["cut_size_mm"])
            support_plane = float(region["layer_bottom_z_mm"])
            prism_height = design_top - support_plane
            colliding_ids: list[str] = []
            footprint = _xy_rect(
                region["cut_origin_mm"],
                region["cut_size_mm"],
            )

            for placement in result_placements:
                body_origin = _dimension(placement["origin_mm"])
                body_size = _dimension(placement["world_size_mm"])
                body_rect = {
                    "x": body_origin["x"],
                    "y": body_origin["y"],
                    "width": body_size["x"],
                    "height": body_size["y"],
                }
                if (
                    _intersection(body_rect, footprint) is not None
                    and body_origin["z"] < design_top - _EPSILON
                    and support_plane
                    < body_origin["z"] + body_size["z"] - _EPSILON
                ):
                    colliding_ids.append(str(placement["id"]))

            prism = {
                "id": f"reserved-prism:{region['id']}",
                "reservation_id": reservation["id"],
                "flat_item_id": reservation["flat_item_id"],
                "local_region_id": region["id"],
                "origin_mm": {
                    "x": _round(origin_xy["x"]),
                    "y": _round(origin_xy["y"]),
                    "z": _round(support_plane),
                },
                "size_mm": {
                    "x": _round(size_xy["x"]),
                    "y": _round(size_xy["y"]),
                    "z": _round(prism_height),
                },
                "printable": False,
                "semantics": "flat_item_local_reserved_volume",
            }
            reserved_prisms.append(prism)
            certificates.append(
                {
                    "reservation_id": reservation["id"],
                    "flat_item_id": reservation["flat_item_id"],
                    "local_region_id": region["id"],
                    "reserved_prism_id": prism["id"],
                    "collision_count": len(colliding_ids),
                    "colliding_placement_ids": colliding_ids,
                    "certified": not colliding_ids,
                    "support_required": False,
                }
            )
            if colliding_ids:
                blockers.append(
                    _blocker(
                        "TOP_INSET_RESERVED_PRISM_COLLISION",
                        f"Le prisme local reserve pour '{reservation['name']}' "
                        f"est traverse par {', '.join(colliding_ids)}.",
                        "Place le corps hors du prisme local ou sous son plan "
                        "inferieur sans l allonger.",
                        str(reservation["flat_item_id"]),
                    )
                )

    status = (
        "blocked"
        if blockers
        else ("not_required" if not reserved_prisms else "reserved_prisms_certified")
    )
    return {
        **deepcopy(plan),
        "status": status,
        "placements": result_placements,
        "cuts": [],
        "supports": [],
        "reserved_prisms": reserved_prisms,
        "reservation_certificates": certificates,
        "cavity_depth_compensations": [],
        "support": {
            "status": (
                "blocked"
                if blockers
                else (
                    "not_required"
                    if not reserved_prisms
                    else "not_required_for_minimal_layout"
                )
            ),
            "top_support_count": 0,
            "coverage_ratio": 0.0 if reserved_prisms else 1.0,
            "reservations": [],
            "note": (
                "Le calcul minimal reserve les prismes des elements plats sans "
                "fabriquer de corps porteur. Les encoches appartiennent a la finition."
            ),
        },
        "blockers": blockers,
        "warnings": [],
        "summary": {
            **deepcopy(_mapping(plan["summary"])),
            "status": status,
            "cut_count": 0,
            "support_count": 0,
            "reserved_prism_count": len(reserved_prisms),
            "certified_reserved_prism_count": sum(
                int(bool(item["certified"])) for item in certificates
            ),
            "cavity_depth_compensation_count": 0,
            "maximum_cavity_depth_compensation_mm": 0.0,
        },
        "invariants": {
            **deepcopy(_mapping(plan["invariants"])),
            "reservation_prisms_post_certified": not blockers,
            "reservation_requires_supporting_body": False,
            "top_inset_cuts_deferred_to_finalization": True,
            "container_envelopes_unchanged": True,
            "reserved_prisms_follow_local_depth_regions": True,
        },
    }


def apply_top_inset_reservations(
    raw_project: object,
    placements: list[dict[str, object]],
    *,
    top_inset_plan: dict[str, object] | None = None,
) -> dict[str, object]:
    """Intersect resolved reservations with placed bodies and validate cuts."""

    normalization = normalize_project_draft(raw_project)
    project = normalization.project
    plan = (
        deepcopy(top_inset_plan)
        if top_inset_plan is not None
        else resolve_top_inset_reservations(
            project,
            placements,
            require_reserved_prisms=False,
        )
    )
    plan = _refresh_wall_envelope_certificates(project, plan, placements)
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
    cavity_anchor_requests: list[dict[str, object]] = []

    for reservation in _mappings(plan["reservations"]):
        reservation_cuts: list[dict[str, object]] = []
        reservation_support_area = 0.0
        footprint = _xy_rect(reservation["cut_origin_mm"], reservation["cut_size_mm"])
        grip = _mapping(reservation["grip_zone"])
        grip_rect = _xy_rect(grip["origin_mm"], grip["size_mm"])
        requested_regions = [
            (
                TOP_INSET_CUT_KIND,
                _xy_rect(region["cut_origin_mm"], region["cut_size_mm"]),
                float(region["layer_top_z_mm"])
                - float(region["layer_bottom_z_mm"]),
                str(region["id"]),
                float(region["layer_bottom_z_mm"]),
                tuple(str(value) for value in region["overlapping_reservation_ids"]),
            )
            for region in _local_depth_regions(reservation)
        ]
        requested_regions.append(
            (
                TOP_INSET_GRIP_CUT_KIND,
                grip_rect,
                float(reservation["total_thickness_mm"]),
                f"{reservation['id']}:grip-region",
                design_top - float(reservation["total_thickness_mm"]),
                (str(reservation["id"]),),
            )
        )
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
            for (
                cut_kind,
                requested_rect,
                depth,
                local_region_id,
                local_layer_bottom,
                overlapping_reservation_ids,
            ) in requested_regions:
                intersection = _intersection(body_rect, requested_rect)
                if intersection is None:
                    continue
                if not isclose(body_top, design_top, abs_tol=0.001):
                    # P64 may place another requested body above this XY footprint.
                    # Only bodies opening on the design top receive the local cut;
                    # missing top coverage is diagnosed after all stages are scanned.
                    continue
                minimum_floor = group_floor.get(
                    str(placement.get("container_group_id", "")),
                    float(layout["default_floor_thickness_mm"]),
                )
                retained = local_layer_bottom - body_origin["z"]
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
                    for cavity_id in overlapping_cavity_ids:
                        cavity_anchor_requests.append(
                            {
                                "placement_id": placement["id"],
                                "cavity_id": cavity_id,
                                "reservation_id": reservation["id"],
                                "local_region_id": local_region_id,
                                "cut_bottom_z_mm": _round(
                                    local_layer_bottom
                                ),
                                "required_anchor": "below_top_inset",
                            }
                        )
                cut = {
                    "id": f"{reservation['id']}:{placement['id']}:{cut_kind}:{len(reservation_cuts)}",
                    "kind": cut_kind,
                    "reservation_id": reservation["id"],
                    "flat_item_id": reservation["flat_item_id"],
                    "placement_id": placement["id"],
                    "local_region_id": local_region_id,
                    "overlapping_reservation_ids": list(
                        overlapping_reservation_ids
                    ),
                    "removal_order": reservation["removal_order"],
                    "world_origin_mm": {
                        "x": _round(intersection["x"]),
                        "y": _round(intersection["y"]),
                        "z": _round(local_layer_bottom),
                    },
                    "local_origin_mm": {
                        "x": _round(intersection["x"] - body_origin["x"]),
                        "y": _round(intersection["y"] - body_origin["y"]),
                        "z": _round(
                            local_layer_bottom - body_origin["z"]
                        ),
                    },
                    "size_mm": {
                        "x": _round(intersection["width"]),
                        "y": _round(intersection["height"]),
                        "z": _round(depth),
                    },
                    "retained_body_below_mm": _round(retained),
                    "minimum_floor_mm": _round(minimum_floor),
                    "cavity_overlap_area_mm2": _round(cavity_overlap_area),
                    "local_interval_z_mm": {
                        "bottom": _round(local_layer_bottom),
                        "top": _round(local_layer_bottom + depth),
                    },
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

    status = "blocked" if blockers else ("not_required" if not plan["reservations"] else "applied")
    ratios = [float(item["coverage_ratio"]) for item in supports]
    return {
        **deepcopy(plan),
        "status": status,
        "placements": result_placements,
        "cuts": cuts,
        "supports": supports,
        "cavity_depth_compensations": [],
        "cavity_anchor_requests": cavity_anchor_requests,
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
            "cavity_depth_compensation_count": 0,
            "maximum_cavity_depth_compensation_mm": 0.0,
            "cavity_anchor_request_count": len(cavity_anchor_requests),
        },
        "invariants": {
            **deepcopy(_mapping(plan["invariants"])),
            "cavity_calibrated_depths_unchanged": True,
            "cavity_z_anchor_deferred_to_finalization": True,
            "local_depth_regions_applied": True,
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


def _resolve_automatic_xy_layout(
    items: list[dict[str, object]],
    *,
    box: dict[str, float],
    design_top_z: float,
    default_clearance: dict[str, float],
    project: dict[str, object],
    placements: list[dict[str, object]],
    require_reserved_prisms: bool,
) -> tuple[list[dict[str, object]], list[dict[str, object]], dict[str, object]]:
    """Keep a bounded deterministic beam of joint XY arrangements."""

    cavity_constraints = _cavity_wall_constraints(project, placements)
    states: list[list[dict[str, object]]] = [[]]
    evaluated = 0
    wall_rejections = 0
    geometry_rejections: list[dict[str, object]] = []
    grid_metrics = {
        "axis_anchor_occurrence_count_before_quantization": 0,
        "axis_anchor_occurrence_count_after_quantization": 0,
    }

    for item in items:
        expanded: list[list[dict[str, object]]] = []
        rotations = (
            [int(item["rotation_deg_z"])]
            if item.get("rotation_deg_z") is not None
            else [0, 90]
        )
        for state in states:
            state_expanded: list[list[dict[str, object]]] = []
            for rotation in rotations:
                variant = deepcopy(item)
                variant["rotation_deg_z"] = rotation
                variant["origin_mm"] = None
                template, template_blockers = _resolve_item(
                    variant,
                    box,
                    default_clearance,
                )
                footprint_blockers = [
                    blocker
                    for blocker in template_blockers
                    if blocker["code"] == "TOP_INSET_FOOTPRINT_EXCEEDS_BOX"
                ]
                if footprint_blockers:
                    geometry_rejections.extend(footprint_blockers)
                    continue
                size = _xy(template["cut_size_mm"])
                x_values = _automatic_axis_positions(
                    axis="x",
                    limit=box["x"],
                    size=size["x"],
                    reservations=state,
                    cavity_constraints=cavity_constraints,
                    grid_metrics=grid_metrics,
                )
                y_values = _automatic_axis_positions(
                    axis="y",
                    limit=box["y"],
                    size=size["y"],
                    reservations=state,
                    cavity_constraints=cavity_constraints,
                    grid_metrics=grid_metrics,
                )
                for x in x_values:
                    for y in y_values:
                        evaluated += 1
                        candidate, relocation_blockers = _relocate_reservation(
                            template,
                            x=x,
                            y=y,
                            box=box,
                        )
                        if relocation_blockers:
                            continue
                        wall_certificate = _reservation_wall_certificate(
                            candidate,
                            cavity_constraints,
                        )
                        candidate["wall_envelope_certificate"] = wall_certificate
                        if not bool(wall_certificate["certified"]):
                            wall_rejections += 1
                            continue
                        state_expanded.append(state + [candidate])
            expanded.extend(
                sorted(
                    state_expanded,
                    key=lambda value: _automatic_layout_rank(
                        value,
                        design_top_z,
                        box,
                        project=project,
                        placements=placements,
                        require_reserved_prisms=require_reserved_prisms,
                    ),
                )[:_MAX_AUTOMATIC_POSES_PER_STATE]
            )
        if not expanded:
            blockers = _unique_blockers(geometry_rejections)
            if wall_rejections:
                blockers.append(
                    _blocker(
                        "TOP_INSET_MINIMUM_WALL_NOT_CERTIFIED",
                        f"Aucune position automatique de '{item['name']}' ne conserve "
                        "l epaisseur de paroi deja definie autour des cavites.",
                        "Reduis son empreinte ou son jeu ; les cavites restent inchangees.",
                        str(item["id"]),
                    )
                )
            if not blockers:
                blockers.append(
                    _blocker(
                        "TOP_INSET_AUTOMATIC_PLACEMENT_NOT_FOUND",
                        f"Aucune position XY automatique admissible n a ete trouvee pour '{item['name']}'.",
                        "Reduis son empreinte, son jeu ou le nombre d elements plats.",
                        str(item["id"]),
                    )
                )
            return [], blockers, {
                "status": "blocked",
                "bounded": True,
                "evaluated_pose_count": evaluated,
                "retained_state_count": 0,
                "wall_rejection_count": wall_rejections,
                "placement_context": "frozen_bodies" if placements else "box_preview",
                **_grid_search_metrics(grid_metrics),
            }
        deduplicated: dict[tuple[object, ...], list[dict[str, object]]] = {}
        for candidate_state in expanded:
            signature = _automatic_layout_signature(candidate_state)
            deduplicated.setdefault(signature, candidate_state)
        states = sorted(
            deduplicated.values(),
            key=lambda value: _automatic_layout_rank(
                value,
                design_top_z,
                box,
                project=project,
                placements=placements,
                require_reserved_prisms=require_reserved_prisms,
            ),
        )[:_MAX_AUTOMATIC_LAYOUT_STATES]

    collision_rejections = 0
    application_rejections: list[dict[str, object]] = []
    selected: list[dict[str, object]] | None = None
    for state in sorted(
        states,
        key=lambda value: _automatic_layout_rank(
            value,
            design_top_z,
            box,
            project=project,
            placements=placements,
            require_reserved_prisms=require_reserved_prisms,
        ),
    ):
        layered = _resolve_vertical_layers(state, design_top_z)
        if (
            require_reserved_prisms
            and _reserved_prism_collision_ids(layered, placements, design_top_z)
        ):
            collision_rejections += 1
            continue
        if not require_reserved_prisms:
            pose_blockers = _top_inset_application_pose_blockers(
                layered,
                placements,
                project,
                design_top_z,
            )
            if pose_blockers:
                application_rejections.extend(pose_blockers)
                continue
        selected = layered
        break
    if selected is None and items:
        blockers = _unique_blockers(application_rejections)
        if not blockers:
            blockers = [
                _blocker(
                    "TOP_INSET_AUTOMATIC_PLACEMENT_NOT_FOUND",
                    "Les positions XY candidates entrent toutes dans un prisme superieur reserve.",
                    "Laisse un autre emplacement superieur disponible ; aucun corps ni aucune cavite "
                    "n a ete deplace.",
                )
            ]
        return [], blockers, {
            "status": "blocked",
            "bounded": True,
            "evaluated_pose_count": evaluated,
            "retained_state_count": len(states),
            "wall_rejection_count": wall_rejections,
            "reserved_prism_rejection_count": collision_rejections,
            "application_rejection_count": len(application_rejections),
            "placement_context": "frozen_bodies" if placements else "box_preview",
            **_grid_search_metrics(grid_metrics),
        }
    return selected or [], [], {
        "status": "resolved" if items else "not_required",
        "bounded": True,
        "evaluated_pose_count": evaluated,
        "retained_state_count": len(states),
        "wall_rejection_count": wall_rejections,
        "reserved_prism_rejection_count": collision_rejections,
        "application_rejection_count": len(application_rejections),
        "placement_context": "frozen_bodies" if placements else "box_preview",
        "selected_signature": list(_automatic_layout_signature(selected or [])),
        "selected_pose_on_product_grid": _automatic_layout_on_product_grid(
            selected or []
        ),
        **_grid_search_metrics(grid_metrics),
    }


def _automatic_axis_positions(
    *,
    axis: str,
    limit: float,
    size: float,
    reservations: list[dict[str, object]],
    cavity_constraints: list[dict[str, object]],
    grid_metrics: dict[str, int] | None = None,
) -> list[float]:
    axis_size = "width" if axis == "x" else "height"
    values = {0.0, (limit - size) / 2.0, limit - size}
    for reservation in reservations:
        rect = _xy_rect(reservation["cut_origin_mm"], reservation["cut_size_mm"])
        start = rect[axis]
        extent = rect[axis_size]
        values.update({start - size, start, start + extent - size, start + extent})
    for constraint in cavity_constraints:
        rect = _mapping(constraint["bounds"])
        wall = float(constraint["minimum_wall_mm"])
        start = float(rect[axis])
        extent = float(rect[axis_size])
        values.update(
            {
                start - size - wall,
                start - wall,
                start + extent + wall - size,
                start + extent + wall,
            }
        )
    maximum_origin_tick = floor_ticks(limit - size)
    admissible_before_quantization = {
        value
        for value in values
        if value >= -_EPSILON and value + size <= limit + _EPSILON
    }
    admissible_ticks = {
        min(max(nearest_ticks(value), 0), maximum_origin_tick)
        for value in admissible_before_quantization
    }
    admissible = {ticks_to_mm(value) for value in admissible_ticks}
    if grid_metrics is not None:
        grid_metrics[
            "axis_anchor_occurrence_count_before_quantization"
        ] += len(values)
        grid_metrics[
            "admissible_axis_anchor_occurrence_count_before_quantization"
        ] = grid_metrics.get(
            "admissible_axis_anchor_occurrence_count_before_quantization",
            0,
        ) + len(admissible_before_quantization)
        grid_metrics[
            "axis_anchor_occurrence_count_after_quantization"
        ] += len(admissible)
    center = (limit - size) / 2.0
    anchors = [0.0, nearest_mm(center), ticks_to_mm(maximum_origin_tick)]
    ordered = [value for value in anchors if value in admissible]
    spread = sorted(admissible)
    remaining_slots = _MAX_AUTOMATIC_AXIS_POSITIONS - len(ordered)
    if remaining_slots > 0 and spread:
        for index in range(remaining_slots):
            spread_index = round(
                index * (len(spread) - 1) / max(remaining_slots - 1, 1)
            )
            value = spread[spread_index]
            if value not in ordered:
                ordered.append(value)
    ordered.extend(
        value
        for value in sorted(admissible, key=lambda value: (abs(value - center), value))
        if value not in ordered
    )
    return ordered[:_MAX_AUTOMATIC_AXIS_POSITIONS]


def _relocate_reservation(
    template: dict[str, object],
    *,
    x: float,
    y: float,
    box: dict[str, float],
) -> tuple[dict[str, object], list[dict[str, object]]]:
    result = deepcopy(template)
    old_cut_origin = _xy(result["cut_origin_mm"])
    physical_origin = _xy(result["physical_origin_mm"])
    clearance_x = physical_origin["x"] - old_cut_origin["x"]
    clearance_y = physical_origin["y"] - old_cut_origin["y"]
    size = _xy(result["cut_size_mm"])
    result["placement_source"] = "automatic_xy"
    result["cut_origin_mm"] = {"x": nearest_mm(x), "y": nearest_mm(y)}
    result["physical_origin_mm"] = {
        "x": nearest_mm(x + clearance_x),
        "y": nearest_mm(y + clearance_y),
    }
    result["product_grid_ticks_v1"] = {
        "origin": {
            "x": nearest_ticks(x),
            "y": nearest_ticks(y),
        },
        "size": {
            "x": nearest_ticks(size["x"]),
            "y": nearest_ticks(size["y"]),
        },
    }
    grip, grip_blocker = _grip_zone(x, y, size["x"], size["y"], box)
    result["grip_zone"] = grip
    blockers: list[dict[str, object]] = []
    if grip_blocker is not None:
        blockers.append(
            _blocker(
                "TOP_INSET_GRIP_UNAVAILABLE",
                f"Aucune zone de prise rectangulaire ne tient autour de '{result['name']}'.",
                "Laisse au moins 2 mm libres sur un cote.",
                str(result["flat_item_id"]),
            )
        )
    return result, blockers


def _automatic_layout_rank(
    reservations: list[dict[str, object]],
    design_top_z: float,
    box: dict[str, float],
    *,
    project: dict[str, object],
    placements: list[dict[str, object]],
    require_reserved_prisms: bool,
) -> tuple[object, ...]:
    layered = _resolve_vertical_layers(reservations, design_top_z)
    reserved_prism_violation_count = (
        len(_reserved_prism_collision_ids(layered, placements, design_top_z))
        if require_reserved_prisms
        else 0
    )
    application_violation_count = (
        0
        if require_reserved_prisms
        else len(
            _top_inset_application_pose_blockers(
                layered,
                placements,
                project,
                design_top_z,
            )
        )
    )
    depth = max(
        (float(value["inset_depth_from_top_mm"]) for value in layered),
        default=0.0,
    )
    rectangles = [
        _xy_rect(value["cut_origin_mm"], value["cut_size_mm"])
        for value in reservations
    ]
    overlaps = sum(
        1
        for index, left in enumerate(rectangles)
        for right in rectangles[index + 1 :]
        if _intersection(left, right) is not None
    )
    center_distance = sum(
        abs(rect["x"] + rect["width"] / 2.0 - box["x"] / 2.0)
        + abs(rect["y"] + rect["height"] / 2.0 - box["y"] / 2.0)
        for rect in rectangles
    )
    return (
        reserved_prism_violation_count,
        application_violation_count,
        _round(depth),
        overlaps,
        _round(center_distance),
        _automatic_layout_signature(reservations),
    )


def _top_inset_application_pose_blockers(
    reservations: list[dict[str, object]],
    placements: list[dict[str, object]],
    project: dict[str, object],
    design_top_z: float,
) -> list[dict[str, object]]:
    if not placements:
        return []
    layout = _mapping(project["layout"])
    default_floor = float(layout["default_floor_thickness_mm"])
    group_floor = {
        str(group["id"]): float(group["floor_thickness_mm"] or default_floor)
        for group in _mappings(project["container_groups"])
    }
    blockers: list[dict[str, object]] = []
    for reservation in reservations:
        footprint = _xy_rect(reservation["cut_origin_mm"], reservation["cut_size_mm"])
        grip = _mapping(reservation["grip_zone"])
        grip_rect = _xy_rect(grip["origin_mm"], grip["size_mm"])
        depth = float(reservation["inset_depth_from_top_mm"])
        footprint_supported = False
        for placement in placements:
            if "origin_mm" not in placement or "world_size_mm" not in placement:
                continue
            body_origin = _dimension(placement["origin_mm"])
            body_size = _dimension(placement["world_size_mm"])
            body_top = body_origin["z"] + body_size["z"]
            if not isclose(body_top, design_top_z, abs_tol=0.001):
                continue
            body_rect = {
                "x": body_origin["x"],
                "y": body_origin["y"],
                "width": body_size["x"],
                "height": body_size["y"],
            }
            minimum_floor = group_floor.get(
                str(placement.get("container_group_id", "")),
                default_floor,
            )
            for cut_kind, requested_rect in (
                (TOP_INSET_CUT_KIND, footprint),
                (TOP_INSET_GRIP_CUT_KIND, grip_rect),
            ):
                intersection = _intersection(body_rect, requested_rect)
                if intersection is None:
                    continue
                if cut_kind == TOP_INSET_CUT_KIND:
                    footprint_supported = True
                retained_body = body_size["z"] - depth
                if retained_body + _EPSILON < minimum_floor:
                    blockers.append(
                        _blocker(
                            "TOP_INSET_PIERCES_BODY_FLOOR",
                            f"L encastrement '{reservation['name']}' laisserait "
                            f"{_round(retained_body)} mm sous le corps '{placement.get('name', placement['id'])}', "
                            f"minimum {_round(minimum_floor)} mm.",
                            "Choisis une autre pose XY ou reduis l epaisseur des elements plats.",
                            str(placement["id"]),
                        )
                    )
                    continue
                if cut_kind != TOP_INSET_CUT_KIND:
                    continue
                _, cavity_ids = _cavity_interactions(placement, intersection)
                cavities = {
                    str(cavity["cavity_id"]): cavity
                    for cavity in _mappings(placement.get("cavity_layout", []))
                }
                for cavity_id in cavity_ids:
                    cavity = cavities[cavity_id]
                    cavity_depth = float(_mapping(cavity["inner_dimensions_mm"])["z"])
                    retained_cavity_floor = body_size["z"] - cavity_depth - depth
                    if retained_cavity_floor + _EPSILON < minimum_floor:
                        blockers.append(
                            _blocker(
                                "TOP_INSET_PIERCES_CAVITY_FLOOR",
                                f"La pose de '{reservation['name']}' au-dessus de la cavite "
                                f"'{cavity_id}' ne laisserait que "
                                f"{_round(retained_cavity_floor)} mm de fond.",
                                "Choisis une autre pose XY ; la cavite reste inchangee.",
                                str(placement["id"]),
                            )
                        )
        if not footprint_supported:
            blockers.append(
                _blocker(
                    "TOP_INSET_WITHOUT_SUPPORTING_BODY",
                    f"Aucun corps au sommet ne porte l element plat '{reservation['name']}'.",
                    "Choisis une autre pose XY automatique.",
                    str(reservation["flat_item_id"]),
                )
            )
    return _unique_blockers(blockers)


def _automatic_layout_signature(
    reservations: list[dict[str, object]],
) -> tuple[object, ...]:
    return tuple(
        (
            str(value["flat_item_id"]),
            int(value["rotation_deg_z"]),
            float(_mapping(value["cut_origin_mm"])["x"]),
            float(_mapping(value["cut_origin_mm"])["y"]),
        )
        for value in reservations
    )


def _cavity_wall_constraints(
    project: dict[str, object],
    placements: list[dict[str, object]],
) -> list[dict[str, object]]:
    layout = _mapping(project["layout"])
    default_wall = float(layout["default_wall_thickness_mm"])
    walls = {
        str(group["id"]): float(group["wall_thickness_mm"] or default_wall)
        for group in _mappings(project["container_groups"])
    }
    result: list[dict[str, object]] = []
    for placement in placements:
        if not all(
            key in placement
            for key in (
                "origin_mm",
                "final_outer_dimensions_mm",
                "minimum_envelope_origin_in_final_mm",
            )
        ):
            continue
        wall = walls.get(str(placement.get("container_group_id", "")), default_wall)
        for cavity in _mappings(placement.get("cavity_layout", [])):
            result.append(
                {
                    "placement_id": placement["id"],
                    "cavity_id": cavity["cavity_id"],
                    "minimum_wall_mm": _round(wall),
                    "bounds": _cavity_world_bounds(placement, cavity),
                }
            )
    return result


def _reservation_wall_certificate(
    reservation: dict[str, object],
    constraints: list[dict[str, object]],
) -> dict[str, object]:
    footprint = _xy_rect(reservation["cut_origin_mm"], reservation["cut_size_mm"])
    grip = _mapping(reservation["grip_zone"])
    grip_rect = _xy_rect(grip["origin_mm"], grip["size_mm"])
    failures: list[dict[str, object]] = []
    shared_void_count = 0
    for constraint in constraints:
        cavity = _mapping(constraint["bounds"])
        wall = float(constraint["minimum_wall_mm"])
        footprint_overlap = _intersection(footprint, cavity)
        if footprint_overlap is not None:
            shared_void_count += 1
        elif _rect_distance(footprint, cavity) + _EPSILON < wall:
            failures.append(
                {
                    "placement_id": constraint["placement_id"],
                    "cavity_id": constraint["cavity_id"],
                    "cut_kind": TOP_INSET_CUT_KIND,
                    "minimum_wall_mm": _round(wall),
                    "reason": "separation_below_required_wall",
                }
            )
        grip_overlap = _intersection(grip_rect, cavity)
        if grip_overlap is not None:
            shared_void_count += 1
        elif _rect_distance(grip_rect, cavity) + _EPSILON < wall:
            failures.append(
                {
                    "placement_id": constraint["placement_id"],
                    "cavity_id": constraint["cavity_id"],
                    "cut_kind": TOP_INSET_GRIP_CUT_KIND,
                    "minimum_wall_mm": _round(wall),
                    "reason": "grip_cut_penetrates_cavity_wall_envelope",
                }
            )
    return {
        "certified": not failures,
        "constraint_count": len(constraints),
        "minimum_wall_source": "container_group_or_project_default",
        "cavities_unchanged": True,
        "shared_void_count": shared_void_count,
        "shared_void_semantics": "merged_cut_not_claimed_as_separating_wall",
        "failures": failures,
    }


def _refresh_wall_envelope_certificates(
    raw_project: object,
    plan: dict[str, object],
    placements: list[dict[str, object]],
) -> dict[str, object]:
    result = deepcopy(plan)
    project = normalize_project_draft(raw_project).project
    constraints = _cavity_wall_constraints(project, placements)
    blockers = [deepcopy(value) for value in _mappings(result.get("blockers", []))]
    failed_ids: list[str] = []
    for reservation in _mappings(result.get("reservations", [])):
        certificate = _reservation_wall_certificate(reservation, constraints)
        reservation["wall_envelope_certificate"] = certificate
        if not bool(certificate["certified"]):
            failed_ids.append(str(reservation["flat_item_id"]))
    if failed_ids:
        blockers.append(
            _blocker(
                "TOP_INSET_MINIMUM_WALL_NOT_CERTIFIED",
                "La pose superieure figee ne conserve plus l epaisseur de paroi "
                f"des cavites pour : {', '.join(sorted(set(failed_ids)))}.",
                "Conserve les corps et cavites du plan minimal ou relance un calcul complet.",
            )
        )
    result["blockers"] = _unique_blockers(blockers)
    result["status"] = (
        "blocked"
        if result["blockers"]
        else ("not_required" if not result.get("reservations") else result.get("status", "ready_for_intersection"))
    )
    invariants = _mapping(result.setdefault("invariants", {}))
    invariants["minimum_cavity_wall_envelope_certified"] = not failed_ids
    return result


def _reserved_prism_collision_ids(
    reservations: list[dict[str, object]],
    placements: list[dict[str, object]],
    design_top_z: float,
) -> list[str]:
    result: list[str] = []
    for reservation in reservations:
        for region in _local_depth_regions(reservation):
            footprint = _xy_rect(
                region["cut_origin_mm"],
                region["cut_size_mm"],
            )
            support_plane = float(region["layer_bottom_z_mm"])
            for placement in placements:
                if (
                    "origin_mm" not in placement
                    or "world_size_mm" not in placement
                ):
                    continue
                body_origin = _dimension(placement["origin_mm"])
                body_size = _dimension(placement["world_size_mm"])
                body_rect = {
                    "x": body_origin["x"],
                    "y": body_origin["y"],
                    "width": body_size["x"],
                    "height": body_size["y"],
                }
                if (
                    _intersection(body_rect, footprint) is not None
                    and body_origin["z"] < design_top_z - _EPSILON
                    and support_plane
                    < body_origin["z"] + body_size["z"] - _EPSILON
                ):
                    result.append(str(placement["id"]))
    return sorted(set(result))


def _rect_distance(
    left: dict[str, Any],
    right: dict[str, Any],
) -> float:
    dx = max(
        float(left["x"]) - (float(right["x"]) + float(right["width"])),
        float(right["x"]) - (float(left["x"]) + float(left["width"])),
        0.0,
    )
    dy = max(
        float(left["y"]) - (float(right["y"]) + float(right["height"])),
        float(right["y"]) - (float(left["y"]) + float(left["height"])),
        0.0,
    )
    return (dx * dx + dy * dy) ** 0.5


def _unique_blockers(
    blockers: list[dict[str, object]],
) -> list[dict[str, object]]:
    result: list[dict[str, object]] = []
    seen: set[tuple[str, str]] = set()
    for blocker in blockers:
        key = (str(blocker["code"]), str(blocker.get("reference_id", "")))
        if key in seen:
            continue
        seen.add(key)
        result.append(deepcopy(blocker))
    return result


def _grid_search_metrics(metrics: dict[str, int]) -> dict[str, object]:
    admissible_before = metrics.get(
        "admissible_axis_anchor_occurrence_count_before_quantization",
        0,
    )
    after = metrics[
        "axis_anchor_occurrence_count_after_quantization"
    ]
    return {
        "product_grid_schema": PRODUCT_GRID_SCHEMA_V1,
        "product_grid_step_mm": PRODUCT_GRID_STEP_MM,
        **metrics,
        "axis_anchor_quantized_duplicate_count": max(
            0,
            admissible_before - after,
        ),
    }


def _automatic_layout_on_product_grid(
    reservations: list[dict[str, object]],
) -> bool:
    for reservation in reservations:
        for payload_name in ("cut_origin_mm", "cut_size_mm"):
            payload = _xy(reservation[payload_name])
            if not all(is_on_product_grid(payload[axis]) for axis in ("x", "y")):
                return False
        grip = _mapping(reservation["grip_zone"])
        for payload_name in ("origin_mm", "size_mm"):
            payload = _xy(grip[payload_name])
            if not all(is_on_product_grid(payload[axis]) for axis in ("x", "y")):
                return False
    return True



def _resolve_vertical_layers(
    resolved: list[dict[str, object]], design_top_z: float
) -> list[dict[str, object]]:
    """Compose the Z depth on exact XY cells, never on a global envelope.

    The input order is bottom-to-top.  Every atomic XY cell records only the
    reservations that really cover it.  A lower reservation therefore gains
    the thickness of an upper one only inside their actual intersection.
    """

    regions_by_index: list[list[dict[str, object]]] = [
        [] for _ in resolved
    ]
    if resolved:
        rectangles = [
            _xy_rect(item["cut_origin_mm"], item["cut_size_mm"])
            for item in resolved
        ]
        xs = sorted(
            {
                value
                for rectangle in rectangles
                for value in (
                    rectangle["x"],
                    rectangle["x"] + rectangle["width"],
                )
            }
        )
        ys = sorted(
            {
                value
                for rectangle in rectangles
                for value in (
                    rectangle["y"],
                    rectangle["y"] + rectangle["height"],
                )
            }
        )
        region_sequence = 0
        for x_index in range(len(xs) - 1):
            for y_index in range(len(ys) - 1):
                x0, x1 = xs[x_index], xs[x_index + 1]
                y0, y1 = ys[y_index], ys[y_index + 1]
                if x1 - x0 <= _EPSILON or y1 - y0 <= _EPSILON:
                    continue
                center = {"x": (x0 + x1) / 2.0, "y": (y0 + y1) / 2.0}
                active = [
                    index
                    for index, rectangle in enumerate(rectangles)
                    if (
                        rectangle["x"] - _EPSILON
                        <= center["x"]
                        <= rectangle["x"] + rectangle["width"] + _EPSILON
                        and rectangle["y"] - _EPSILON
                        <= center["y"]
                        <= rectangle["y"] + rectangle["height"] + _EPSILON
                    )
                ]
                if not active:
                    continue
                depth = 0.0
                active_ids = [str(resolved[index]["id"]) for index in active]
                for index in reversed(active):
                    thickness = float(resolved[index]["total_thickness_mm"])
                    depth += thickness
                    layer_bottom = design_top_z - depth
                    regions_by_index[index].append(
                        {
                            "id": (
                                f"{resolved[index]['id']}:local-region:"
                                f"{region_sequence:04d}"
                            ),
                            "cut_origin_mm": {
                                "x": _round(x0),
                                "y": _round(y0),
                            },
                            "cut_size_mm": {
                                "x": _round(x1 - x0),
                                "y": _round(y1 - y0),
                            },
                            "layer_bottom_z_mm": _round(layer_bottom),
                            "layer_top_z_mm": _round(
                                layer_bottom + thickness
                            ),
                            "inset_depth_from_top_mm": _round(depth),
                            "overlapping_reservation_ids": active_ids,
                            "overlap_count": len(active),
                        }
                    )
                region_sequence += 1

    count = len(resolved)
    reservations: list[dict[str, object]] = []
    for index, reservation in enumerate(resolved):
        thickness = float(reservation["total_thickness_mm"])
        local_regions = regions_by_index[index]
        depth = max(
            (
                float(value["inset_depth_from_top_mm"])
                for value in local_regions
            ),
            default=thickness,
        )
        layer_bottom = min(
            (
                float(value["layer_bottom_z_mm"])
                for value in local_regions
            ),
            default=design_top_z - thickness,
        )
        layer_top = max(
            (
                float(value["layer_top_z_mm"])
                for value in local_regions
            ),
            default=design_top_z,
        )
        final = deepcopy(reservation)
        final.update(
            {
                "level": index,
                "layer_bottom_z_mm": _round(layer_bottom),
                "layer_top_z_mm": _round(layer_top),
                "inset_depth_from_top_mm": _round(depth),
                "removal_order": count - index,
                "support_plane_z_mm": _round(layer_bottom),
                "local_depth_regions": local_regions,
            }
        )
        reservations.append(final)
    return reservations

def _resolve_item(
    item: dict[str, object],
    box: dict[str, float],
    default_clearance: dict[str, float],
) -> tuple[dict[str, object], list[dict[str, object]]]:
    dimensions = _dimension(item["dimensions_mm"])
    effective = item.get("clearance_effective_v1")
    clearance_values = (
        _dimension(_mapping(effective["values_mm"]))
        if isinstance(effective, dict)
        else dict(default_clearance)
    )
    clearance_sources = (
        dict(_mapping(effective["source_by_axis"]))
        if isinstance(effective, dict)
        else {"x": "legacy_scalar", "y": "legacy_scalar", "z": "legacy_scalar"}
    )
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
        clearance_x = clearance_values['x'] if rotation == 0 else clearance_values['y']
        clearance_y = clearance_values['y'] if rotation == 0 else clearance_values['x']
        if (
            outward_size_mm(physical_x + 2.0 * clearance_x)
            <= box["x"] + _EPSILON
            and outward_size_mm(physical_y + 2.0 * clearance_y)
            <= box["y"] + _EPSILON
        ):
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
                f"'{item['name']}' demande { _round(physical_x + 2 * (clearance_values['x'] if rotation == 0 else clearance_values['y'])) } x "
                f"{ _round(physical_y + 2 * (clearance_values['y'] if rotation == 0 else clearance_values['x'])) } mm avec jeu, au-dela de la boite.",
                "Reduis l empreinte, le jeu ou choisis une rotation compatible.",
                str(item["id"]),
            )
        )
    rotation, physical_x, physical_y = chosen
    clearance_x = clearance_values['x'] if rotation == 0 else clearance_values['y']
    clearance_y = clearance_values['y'] if rotation == 0 else clearance_values['x']
    cut_x = outward_size_mm(physical_x + 2.0 * clearance_x)
    cut_y = outward_size_mm(physical_y + 2.0 * clearance_y)
    origin_value = item.get("origin_mm")
    if origin_value is None:
        cut_origin_x = nearest_mm((box["x"] - cut_x) / 2.0)
        cut_origin_y = nearest_mm((box["y"] - cut_y) / 2.0)
        placement_source = "auto_center"
    else:
        physical_origin = _xy(origin_value)
        cut_origin_x = nearest_mm(physical_origin["x"] - clearance_x)
        cut_origin_y = nearest_mm(physical_origin["y"] - clearance_y)
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
                "x": nearest_mm(cut_origin_x + clearance_x),
                "y": nearest_mm(cut_origin_y + clearance_y),
            },
            "total_thickness_mm": _round(dimensions["z"] * int(item["quantity"]) + clearance_values["z"]),
            "clearance_effective_v1": {
                "role": "flat_inset",
                "values_mm": _rounded_dimension(clearance_values),
                "source_by_axis": clearance_sources,
            },
            "cut_origin_mm": {
                "x": nearest_mm(cut_origin_x),
                "y": nearest_mm(cut_origin_y),
            },
            "cut_size_mm": {"x": cut_x, "y": cut_y},
            "product_grid_ticks_v1": {
                "origin": {
                    "x": nearest_ticks(cut_origin_x),
                    "y": nearest_ticks(cut_origin_y),
                },
                "size": {
                    "x": nearest_ticks(cut_x),
                    "y": nearest_ticks(cut_y),
                },
            },
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
    x0 = max(0.0, floor_mm(grip_x))
    y0 = max(0.0, floor_mm(grip_y))
    x1 = min(floor_mm(box["x"]), ceil_mm(grip_x + size_x))
    y1 = min(floor_mm(box["y"]), ceil_mm(grip_y + size_y))
    return {
        "status": "planned",
        "side": side,
        "origin_mm": {"x": x0, "y": y0},
        "size_mm": {
            "x": nearest_mm(max(0.0, x1 - x0)),
            "y": nearest_mm(max(0.0, y1 - y0)),
        },
        "shape": "rectangle",
        "product_grid_ticks_v1": {
            "origin": {"x": nearest_ticks(x0), "y": nearest_ticks(y0)},
            "size": {
                "x": nearest_ticks(max(0.0, x1 - x0)),
                "y": nearest_ticks(max(0.0, y1 - y0)),
            },
        },
    }, None


def _local_depth_regions(
    reservation: dict[str, object],
) -> list[dict[str, object]]:
    """Return exact local cut regions with a compatibility fallback."""

    raw_regions = reservation.get("local_depth_regions")
    if isinstance(raw_regions, list) and raw_regions:
        return _mappings(raw_regions)
    depth = float(reservation["inset_depth_from_top_mm"])
    layer_bottom = float(reservation["support_plane_z_mm"])
    thickness = float(reservation.get("total_thickness_mm", depth))
    return [
        {
            "id": f"{reservation['id']}:local-region:legacy",
            "cut_origin_mm": deepcopy(reservation["cut_origin_mm"]),
            "cut_size_mm": deepcopy(reservation["cut_size_mm"]),
            "layer_bottom_z_mm": _round(layer_bottom),
            "layer_top_z_mm": _round(layer_bottom + thickness),
            "inset_depth_from_top_mm": _round(depth),
            "overlapping_reservation_ids": [str(reservation["id"])],
            "overlap_count": 1,
        }
    ]


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


def _rounded_dimension(value: dict[str, float]) -> dict[str, float]:
    return {axis: _round(value[axis]) for axis in ("x", "y", "z")}


def _xy(value: object) -> dict[str, float]:
    raw = _mapping(value)
    return {axis: float(raw[axis]) for axis in ("x", "y")}


def _area(value: dict[str, float]) -> float:
    return value["x"] * value["y"]


def _round(value: float) -> float:
    return round(float(value), 4)
