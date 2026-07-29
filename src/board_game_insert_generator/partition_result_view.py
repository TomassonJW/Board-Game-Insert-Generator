"""Read-only projections derived from a complete or partial P64 partition plan."""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping

from board_game_insert_generator.partition_solver import PARTITION_PLAN_SCHEMA_V1
from board_game_insert_generator.preview_explanations import build_preview_explanations


PARTITION_RESULT_VIEW_SCHEMA_V1 = "bgig.partition_result_view.v1"


class PartitionResultViewError(ValueError):
    """Raised when a partition cannot be projected honestly."""


def build_partition_result_view(partition: object) -> dict[str, object]:
    """Build honest top and X/Z primitives without changing the P64 plan."""

    plan = _mapping(partition, "partition")
    if plan.get("schema_version") != PARTITION_PLAN_SCHEMA_V1:
        raise PartitionResultViewError("Le resultat visuel exige un plan bgig.partition_plan.v1.")
    summary = _mapping(plan.get("summary"), "partition.summary")
    plan_status = str(summary.get("status", ""))
    if plan_status not in {"constructed", "proposal_with_residuals"}:
        raise PartitionResultViewError("Une partition impossible ne peut pas etre dessinee comme une solution.")
    materializable = bool(summary.get("materializable", plan_status == "constructed"))
    box = _dimension(_mapping(plan.get("box"), "partition.box").get("inner_dimensions_mm"), "partition.box.inner_dimensions_mm")
    storage_height = float(_mapping(plan["box"], "partition.box")["storage_height_mm"])
    placements = _mappings(plan.get("placements"), "partition.placements")
    section_y = box["y"] / 2.0

    top_bodies: list[dict[str, object]] = []
    top_cavities: list[dict[str, object]] = []
    cut_bodies: list[dict[str, object]] = []
    cut_cavities: list[dict[str, object]] = []
    cut_cavity_accesses: list[dict[str, object]] = []
    details: list[dict[str, object]] = []
    for index, placement in enumerate(placements):
        origin = _dimension(placement.get("origin_mm"), f"placement[{index}].origin_mm")
        size = _dimension(placement.get("world_size_mm"), f"placement[{index}].world_size_mm")
        composite_prisms = _composite_prisms(placement, index)
        body = {
            "id": str(placement["id"]),
            "kind": "body",
            "role": str(placement["role"]),
            "label": str(placement["name"]),
            "x_mm": _round(origin["x"]),
            "y_mm": _round(origin["y"]),
            "width_mm": _round(size["x"]),
            "height_mm": _round(size["y"]),
            "z_mm": _round(origin["z"]),
            "depth_mm": _round(size["z"]),
            "rotation_deg_z": int(placement.get("rotation_deg_z", 0)),
            "stage_id": str(placement.get("stage_id", "stage-1")),
            "stage_index": int(placement.get("stage_index", 0)),
            "color_slot": index % 8,
        }
        if composite_prisms:
            body["geometry_kind"] = "composite_rectangular_union"
            body["rectangles"] = _top_prism_rectangles(
                composite_prisms
            )
            body["composite_prism_count"] = len(composite_prisms)
        top_bodies.append(body)
        if composite_prisms:
            section_rectangles = _section_prism_rectangles(
                composite_prisms,
                section_y,
                box["z"],
            )
            if section_rectangles:
                cut_bodies.append(
                    {
                        "id": body["id"], "kind": "body",
                        "role": body["role"], "label": body["label"],
                        "stage_id": body["stage_id"],
                        "stage_index": body["stage_index"],
                        "x_mm": body["x_mm"],
                        "z_from_top_mm": _round(
                            box["z"] - origin["z"] - size["z"]
                        ),
                        "width_mm": body["width_mm"],
                        "height_mm": body["depth_mm"],
                        "color_slot": body["color_slot"],
                        "geometry_kind": "composite_rectangular_union",
                        "rectangles": section_rectangles,
                        "composite_prism_count": len(composite_prisms),
                    }
                )
        elif _crosses(section_y, origin["y"], size["y"]):
            cut_bodies.append(
                {
                    "id": body["id"], "kind": "body", "role": body["role"], "label": body["label"],
                    "stage_id": body["stage_id"], "stage_index": body["stage_index"],
                    "x_mm": body["x_mm"], "z_from_top_mm": _round(box["z"] - origin["z"] - size["z"]),
                    "width_mm": body["width_mm"], "height_mm": body["depth_mm"], "color_slot": body["color_slot"],
                }
            )
        content_names = {str(item["id"]): str(item["name"]) for item in _mappings(placement.get("source_contents", []), f"placement[{index}].source_contents")}
        cavities = _mappings(placement.get("cavity_layout", []), f"placement[{index}].cavity_layout")
        frozen_cavities = _optional_mappings(
            placement.get("frozen_cavities_v1"),
            f"placement[{index}].frozen_cavities_v1",
        )
        if frozen_cavities and len(frozen_cavities) != len(cavities):
            raise PartitionResultViewError(
                "Le nombre de cavites figees diverge du plan affiche."
            )
        for cavity_index, cavity in enumerate(cavities):
            bounds = (
                _frozen_cavity_world_bounds(
                    frozen_cavities[cavity_index]
                )
                if frozen_cavities
                else _cavity_world_bounds(placement, cavity)
            )
            cavity_view = {
                "id": str(cavity["cavity_id"]),
                "parent_id": body["id"],
                "kind": "cavity",
                "shape_kind": str(cavity["shape_kind"]),
                "content_id": str(cavity["content_id"]),
                "content_name": content_names.get(str(cavity["content_id"]), str(cavity["content_id"])),
                "x_mm": _round(bounds["x"]), "y_mm": _round(bounds["y"]),
                "width_mm": _round(bounds["width"]), "height_mm": _round(bounds["height"]),
                "z_mm": _round(bounds["z"]), "depth_mm": _round(bounds["depth"]),
                "stage_id": body["stage_id"], "stage_index": body["stage_index"],
            }
            if frozen_cavities:
                frozen = frozen_cavities[cavity_index]
                cavity_view.update(
                    {
                        "anchor_kind": frozen.get(
                            "anchor_kind",
                            "open_top",
                        ),
                        "minimum_z_mm": (
                            _round(
                                float(
                                    frozen["minimum_world_origin_mm"]["z"]
                                )
                            )
                            if isinstance(
                                frozen.get("minimum_world_origin_mm"),
                                dict,
                            )
                            else _round(bounds["z"])
                        ),
                        "final_z_mm": _round(bounds["z"]),
                        "calibrated_depth_source_mm": frozen.get(
                            "calibrated_depth_source_mm",
                            _round(bounds["depth"]),
                        ),
                        "calibrated_depth_final_mm": frozen.get(
                            "calibrated_depth_final_mm",
                            _round(bounds["depth"]),
                        ),
                        "responsible_reservation_id": frozen.get(
                            "responsible_reservation_id",
                            "",
                        ),
                        "responsible_local_region_id": frozen.get(
                            "responsible_local_region_id",
                            "",
                        ),
                        "retained_floor_mm": frozen.get(
                            "retained_floor_mm"
                        ),
                        "top_separation_mm": frozen.get(
                            "top_separation_mm"
                        ),
                        "intermediate_material_thickness_mm": frozen.get(
                            "intermediate_material_thickness_mm"
                        ),
                        "top_interface_kind": frozen.get(
                            "top_interface_kind"
                        ),
                        "top_void_continuity_certified": frozen.get(
                            "top_void_continuity_certified"
                        ),
                        "functional_top_z_mm": frozen.get(
                            "functional_top_z_mm"
                        ),
                        "functional_top_access_certified": frozen.get(
                            "functional_top_access_certified"
                        ),
                    }
                )
            top_cavities.append(cavity_view)
            if _crosses(section_y, bounds["y"], bounds["height"]):
                cut_cavities.append(
                    {
                        "id": cavity_view["id"], "parent_id": body["id"], "kind": "cavity",
                        "shape_kind": cavity_view["shape_kind"], "content_id": cavity_view["content_id"],
                        "content_name": cavity_view["content_name"], "stage_id": body["stage_id"],
                        "x_mm": cavity_view["x_mm"],
                        "z_from_top_mm": _round(box["z"] - bounds["z"] - bounds["depth"]),
                        "width_mm": cavity_view["width_mm"], "height_mm": cavity_view["depth_mm"],
                    }
                )
        for access in _composite_access_cuts(placement, index):
            access_origin = _dimension(
                access.get("world_origin_mm"),
                f"placement[{index}].composite_access.world_origin_mm",
            )
            access_size = _dimension(
                access.get("size_mm"),
                f"placement[{index}].composite_access.size_mm",
            )
            if _crosses(
                section_y,
                access_origin["y"],
                access_size["y"],
            ):
                cut_cavity_accesses.append(
                    {
                        "id": str(access["id"]),
                        "parent_id": body["id"],
                        "kind": "cavity_vertical_access",
                        "cavity_id": str(access["reservation_id"]),
                        "x_mm": _round(access_origin["x"]),
                        "z_from_top_mm": _round(
                            box["z"]
                            - access_origin["z"]
                            - access_size["z"]
                        ),
                        "width_mm": _round(access_size["x"]),
                        "height_mm": _round(access_size["z"]),
                    }
                )
        details.append(
            {
                "id": body["id"], "role": body["role"], "name": body["label"],
                "origin_mm": deepcopy(placement["origin_mm"]),
                "world_size_mm": deepcopy(placement["world_size_mm"]),
                "rotation_deg_z": body["rotation_deg_z"],
                "stage_id": body["stage_id"], "stage_index": body["stage_index"],
                "minimum_outer_envelope_mm": deepcopy(placement.get("minimum_outer_envelope_mm")),
                "final_outer_dimensions_mm": deepcopy(placement.get("final_outer_dimensions_mm")),
                "dimension_contract": deepcopy(placement.get("dimension_contract")),
                "surplus_distribution_mm": deepcopy(placement.get("surplus_distribution_mm")),
                "source_content_ids": deepcopy(placement.get("source_content_ids", [])),
                "source_contents": deepcopy(placement.get("source_contents", [])),
                "cavity_count": len(cavities),
                "cavity_anchors": deepcopy(frozen_cavities),
                "composite_prism_count": len(composite_prisms),
                "top_inset_cut_count": len(_mappings(placement.get("top_inset_cuts", []), f"placement[{index}].top_inset_cuts")),
                "requested_complement_id": placement.get("requested_complement_id"),
                "complement_kind": placement.get("complement_kind"),
            }
        )

    top_insets = _mapping(plan.get("top_inset_reservations", {}), "partition.top_inset_reservations")
    reservation_tops: list[dict[str, object]] = []
    reservation_cuts: list[dict[str, object]] = []
    for index, reservation in enumerate(_mappings(top_insets.get("reservations", []), "partition.top_inset_reservations.reservations")):
        origin = _xy(reservation.get("cut_origin_mm"), f"top_inset[{index}].cut_origin_mm")
        size = _xy(reservation.get("cut_size_mm"), f"top_inset[{index}].cut_size_mm")
        depth = float(reservation["inset_depth_from_top_mm"])
        top_item = {
            "id": str(reservation["id"]), "kind": "top_inset_reservation",
            "label": str(reservation["name"]), "flat_item_id": str(reservation["flat_item_id"]),
            "x_mm": _round(origin["x"]), "y_mm": _round(origin["y"]),
            "width_mm": _round(size["x"]), "height_mm": _round(size["y"]),
            "depth_mm": _round(depth), "removal_order": int(reservation["removal_order"]),
            "grip_zone": deepcopy(reservation.get("grip_zone")),
            "local_depth_regions": deepcopy(
                reservation.get("local_depth_regions", [])
            ),
        }
        reservation_tops.append(top_item)
        raw_regions = reservation.get("local_depth_regions", [])
        regions = (
            _mappings(
                raw_regions,
                f"top_inset[{index}].local_depth_regions",
            )
            if isinstance(raw_regions, list) and raw_regions
            else [
                {
                    "id": f"{top_item['id']}:legacy-region",
                    "cut_origin_mm": reservation["cut_origin_mm"],
                    "cut_size_mm": reservation["cut_size_mm"],
                    "inset_depth_from_top_mm": depth,
                    "layer_bottom_z_mm": (
                        float(top_insets.get("design_top_z_mm", storage_height))
                        - depth
                    ),
                    "overlapping_reservation_ids": [top_item["id"]],
                }
            ]
        )
        for region in regions:
            region_origin = _xy(
                region["cut_origin_mm"],
                f"top_inset[{index}].region.cut_origin_mm",
            )
            region_size = _xy(
                region["cut_size_mm"],
                f"top_inset[{index}].region.cut_size_mm",
            )
            if not _crosses(
                section_y,
                region_origin["y"],
                region_size["y"],
            ):
                continue
            reservation_cuts.append({
                "id": str(region["id"]),
                "reservation_id": top_item["id"],
                "kind": "top_inset_reservation",
                "label": top_item["label"],
                "flat_item_id": top_item["flat_item_id"],
                "x_mm": _round(region_origin["x"]),
                "z_from_top_mm": _round(
                    box["z"]
                    - float(
                        top_insets.get(
                            "design_top_z_mm",
                            storage_height,
                        )
                    )
                ),
                "width_mm": _round(region_size["x"]),
                "height_mm": _round(
                    float(region["inset_depth_from_top_mm"])
                ),
                "removal_order": top_item["removal_order"],
                "overlapping_reservation_ids": deepcopy(
                    region.get("overlapping_reservation_ids", [])
                ),
            })

    residual_contract = _mapping(plan.get("residuals", {}), "partition.residuals")
    residual_tops: list[dict[str, object]] = []
    residual_cuts: list[dict[str, object]] = []
    for index, zone in enumerate(_mappings(residual_contract.get("zones", []), "partition.residuals.zones")):
        origin = _dimension(zone.get("origin_mm"), f"residual[{index}].origin_mm")
        size = _dimension(zone.get("size_mm"), f"residual[{index}].size_mm")
        top_item = {
            "id": str(zone["id"]), "kind": "residual", "residual_kind": str(zone["kind"]),
            "stage_id": str(zone.get("stage_id", "")),
            "x_mm": _round(origin["x"]), "y_mm": _round(origin["y"]),
            "width_mm": _round(size["x"]), "height_mm": _round(size["y"]),
            "z_mm": _round(origin["z"]), "depth_mm": _round(size["z"]),
        }
        residual_tops.append(top_item)
        if _crosses(section_y, origin["y"], size["y"]):
            residual_cuts.append({
                "id": top_item["id"], "kind": "residual", "residual_kind": top_item["residual_kind"],
                "stage_id": top_item["stage_id"], "x_mm": top_item["x_mm"],
                "z_from_top_mm": _round(box["z"] - origin["z"] - size["z"]),
                "width_mm": top_item["width_mm"], "height_mm": top_item["depth_mm"],
            })

    # Historical singular keys remain as bounded compatibility aliases.
    reservation_top = reservation_tops[0] if reservation_tops else None
    reservation_cut = reservation_cuts[0] if reservation_cuts else None

    return {
        "schema_version": PARTITION_RESULT_VIEW_SCHEMA_V1,
        "source_plan_digest": str(plan.get("plan_digest", "")),
        "project_name": str(plan.get("project_name", "")),
        "status": plan_status,
        "materializable": materializable,
        "top_view": {
            "view_box_mm": {"x": 0.0, "y": 0.0, "width": _round(box["x"]), "height": _round(box["y"])},
            "bodies": top_bodies,
            "cavities": top_cavities,
            "flat_stack_reservation": reservation_top,
            "top_inset_reservations": reservation_tops,
            "residuals": residual_tops,
        },
        "section_xz": {
            "section_y_mm": _round(section_y),
            "view_box_mm": {"x": 0.0, "y": 0.0, "width": _round(box["x"]), "height": _round(box["z"])},
            "bodies": cut_bodies,
            "cavities": cut_cavities,
            "cavity_vertical_accesses": cut_cavity_accesses,
            "flat_stack_reservation": reservation_cut,
            "top_inset_reservations": reservation_cuts,
            "residuals": residual_cuts,
        },
        "details": details,
        "support": deepcopy(plan.get("support")),
        "stages": deepcopy(plan.get("stages", [])),
        "stage_support": deepcopy(plan.get("stage_support", {})),
        "removal_sequence": deepcopy(plan.get("removal_sequence", [])),
        "residuals": deepcopy(residual_contract),
        "suggestions": deepcopy(plan.get("suggestions", [])),
        "score_breakdown": deepcopy(summary.get("score_breakdown", {})),
        "presentation": build_preview_explanations(plan),
        "summary": deepcopy(summary),
        "diagnostics": deepcopy(plan.get("diagnostics", [])),
        "invariants": {
            "derived_from_real_placements": True,
            "indicative_geometry": False,
            "automatic_body_count": int(summary.get("automatic_body_count", -1)),
            "source_plan_unchanged": True,
            "localized_top_insets": True,
            "stage_aware": True,
            "frozen_cavity_world_poses_projected": True,
            "final_cavity_anchors_projected": all(
                not _optional_mappings(
                    placement.get("frozen_cavities_v1"),
                    f"placement[{index}].frozen_cavities_v1",
                )
                or all(
                    value.get("anchor_certified") is True
                    for value in _optional_mappings(
                        placement.get("frozen_cavities_v1"),
                        f"placement[{index}].frozen_cavities_v1",
                    )
                )
                for index, placement in enumerate(placements)
            ),
            "composite_prisms_projected": all(
                not isinstance(placement.get("composite_body"), dict)
                or bool(_composite_prisms(placement, index))
                for index, placement in enumerate(placements)
            ),
            "residuals_are_non_printable": all(
                not bool(item.get("printable", False))
                for item in _mappings(residual_contract.get("zones", []), "partition.residuals.zones")
            ),
            "partial_never_materializable": plan_status != "proposal_with_residuals" or not materializable,
        },
        "limitations": [
            "La vue dessus projette les vrais prismes composites, les cavites figees, les etages, les residus et les encastrements superieurs resolus.",
            "La coupe X/Z traverse le plan a Y = box.y / 2 et peut ne pas couper tous les corps.",
            "Le degagement vertical au-dessus d une cavite est distingue de la profondeur calibree de l asset.",
            "Les residus sont des volumes non imprimes ; une suggestion exige toujours confirmation.",
            "Cette vue ne constitue ni une CAD IR, ni une validation Fusion ou impression.",
        ],
    }


def _composite_prisms(
    placement: dict[str, object],
    index: int,
) -> list[dict[str, Any]]:
    composite = placement.get("composite_body")
    if not isinstance(composite, dict):
        return []
    if composite.get("schema_version") not in {
        "bgig.xy_composite_cad_body.v2",
        "bgig.xy_composite_container_body.v3",
    }:
        return []
    return _mappings(
        composite.get("prisms"),
        f"placement[{index}].composite_body.prisms",
    )


def _composite_access_cuts(
    placement: dict[str, object],
    index: int,
) -> list[dict[str, Any]]:
    composite = placement.get("composite_body")
    if not isinstance(composite, dict):
        return []
    return _optional_mappings(
        composite.get("frozen_cavity_access_cuts"),
        f"placement[{index}].composite_body.frozen_cavity_access_cuts",
    )


def _top_prism_rectangles(
    prisms: list[dict[str, Any]],
) -> list[dict[str, float]]:
    rectangles: dict[
        tuple[float, float, float, float],
        dict[str, float],
    ] = {}
    for index, prism in enumerate(prisms):
        origin_field, size_field = _composite_prism_geometry_fields(
            prism
        )
        origin = _dimension(
            prism.get(origin_field),
            f"composite.prisms[{index}].{origin_field}",
        )
        size = _dimension(
            prism.get(size_field),
            f"composite.prisms[{index}].{size_field}",
        )
        key = (
            _round(origin["x"]),
            _round(origin["y"]),
            _round(size["x"]),
            _round(size["y"]),
        )
        rectangles[key] = {
            "x_mm": key[0],
            "y_mm": key[1],
            "width_mm": key[2],
            "height_mm": key[3],
        }
    return [rectangles[key] for key in sorted(rectangles)]


def _section_prism_rectangles(
    prisms: list[dict[str, Any]],
    section_y: float,
    box_height: float,
) -> list[dict[str, float]]:
    rectangles: dict[
        tuple[float, float, float, float],
        dict[str, float],
    ] = {}
    for index, prism in enumerate(prisms):
        origin_field, size_field = _composite_prism_geometry_fields(
            prism
        )
        origin = _dimension(
            prism.get(origin_field),
            f"composite.prisms[{index}].{origin_field}",
        )
        size = _dimension(
            prism.get(size_field),
            f"composite.prisms[{index}].{size_field}",
        )
        if not _crosses(section_y, origin["y"], size["y"]):
            continue
        key = (
            _round(origin["x"]),
            _round(box_height - origin["z"] - size["z"]),
            _round(size["x"]),
            _round(size["z"]),
        )
        rectangles[key] = {
            "x_mm": key[0],
            "z_from_top_mm": key[1],
            "width_mm": key[2],
            "height_mm": key[3],
        }
    return [rectangles[key] for key in sorted(rectangles)]


def _composite_prism_geometry_fields(
    prism: Mapping[str, object],
) -> tuple[str, str]:
    if (
        "final_origin_mm" in prism
        and "closure_origin_mm" in prism
    ):
        return "final_origin_mm", "final_size_mm"
    return "cad_origin_mm", "cad_size_mm"


def _frozen_cavity_world_bounds(
    frozen: dict[str, Any],
) -> dict[str, float]:
    origin = _dimension(
        frozen.get("world_origin_mm"),
        "frozen_cavity.world_origin_mm",
    )
    size = _dimension(
        frozen.get("world_size_mm"),
        "frozen_cavity.world_size_mm",
    )
    return {
        "x": origin["x"],
        "y": origin["y"],
        "z": origin["z"],
        "width": size["x"],
        "height": size["y"],
        "depth": size["z"],
    }


def _cavity_world_bounds(placement: dict[str, Any], cavity: dict[str, Any]) -> dict[str, float]:
    origin = _dimension(placement["origin_mm"], "placement.origin_mm")
    final_local = _dimension(placement["final_outer_dimensions_mm"], "placement.final_outer_dimensions_mm")
    minimum_origin = _dimension(placement["minimum_envelope_origin_in_final_mm"], "placement.minimum_envelope_origin_in_final_mm")
    cavity_origin = _dimension(cavity["local_origin_mm"], "cavity.local_origin_mm")
    cavity_size = _dimension(cavity["inner_dimensions_mm"], "cavity.inner_dimensions_mm")
    local_x = minimum_origin["x"] + cavity_origin["x"]
    local_y = minimum_origin["y"] + cavity_origin["y"]
    # Storage cavities stay open on the resolved body top after envelope expansion.
    local_z = final_local["z"] - cavity_size["z"]
    rotation = int(placement.get("rotation_deg_z", 0))
    if rotation == 0:
        world_x, world_y = origin["x"] + local_x, origin["y"] + local_y
        width, height = cavity_size["x"], cavity_size["y"]
    elif rotation == 90:
        world_x = origin["x"] + final_local["y"] - local_y - cavity_size["y"]
        world_y = origin["y"] + local_x
        width, height = cavity_size["y"], cavity_size["x"]
    else:
        raise PartitionResultViewError(f"Rotation Z non prise en charge dans la vue P58 : {rotation}.")
    return {
        "x": world_x, "y": world_y, "z": origin["z"] + local_z,
        "width": width, "height": height, "depth": cavity_size["z"],
    }


def _crosses(section: float, origin: float, size: float) -> bool:
    return origin <= section <= origin + size


def _mapping(value: object, field: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise PartitionResultViewError(f"{field} doit etre un objet.")
    return value


def _mappings(value: object, field: str) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        raise PartitionResultViewError(f"{field} doit etre une liste.")
    return [_mapping(item, f"{field}[{index}]") for index, item in enumerate(value)]


def _optional_mappings(
    value: object,
    field: str,
) -> list[dict[str, Any]]:
    if value is None:
        return []
    return _mappings(value, field)


def _dimension(value: object, field: str) -> dict[str, float]:
    raw = _mapping(value, field)
    try:
        return {axis: float(raw[axis]) for axis in ("x", "y", "z")}
    except (KeyError, TypeError, ValueError) as exc:
        raise PartitionResultViewError(f"{field} doit contenir x, y et z numeriques.") from exc



def _xy(value: object, field: str) -> dict[str, float]:
    raw = _mapping(value, field)
    try:
        return {axis: float(raw[axis]) for axis in ("x", "y")}
    except (KeyError, TypeError, ValueError) as exc:
        raise PartitionResultViewError(f"{field} doit contenir x et y numeriques.") from exc

def _round(value: float) -> float:
    return round(float(value), 4)
