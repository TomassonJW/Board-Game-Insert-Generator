"""Read-only projections derived from a complete or partial P64 partition plan."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from board_game_insert_generator.partition_solver import PARTITION_PLAN_SCHEMA_V1


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
    details: list[dict[str, object]] = []
    for index, placement in enumerate(placements):
        origin = _dimension(placement.get("origin_mm"), f"placement[{index}].origin_mm")
        size = _dimension(placement.get("world_size_mm"), f"placement[{index}].world_size_mm")
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
        top_bodies.append(body)
        if _crosses(section_y, origin["y"], size["y"]):
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
        for cavity in cavities:
            bounds = _cavity_world_bounds(placement, cavity)
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
        }
        reservation_tops.append(top_item)
        if _crosses(section_y, origin["y"], size["y"]):
            reservation_cuts.append({
                "id": top_item["id"], "kind": "top_inset_reservation", "label": top_item["label"],
                "flat_item_id": top_item["flat_item_id"], "x_mm": top_item["x_mm"],
                "z_from_top_mm": _round(box["z"] - float(top_insets.get("design_top_z_mm", storage_height))),
                "width_mm": top_item["width_mm"], "height_mm": _round(depth),
                "removal_order": top_item["removal_order"],
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
        "score_breakdown": deepcopy(plan.get("score_breakdown", {})),
        "summary": deepcopy(summary),
        "diagnostics": deepcopy(plan.get("diagnostics", [])),
        "invariants": {
            "derived_from_real_placements": True,
            "indicative_geometry": False,
            "automatic_body_count": int(summary.get("automatic_body_count", -1)),
            "source_plan_unchanged": True,
            "localized_top_insets": True,
            "stage_aware": True,
            "residuals_are_non_printable": all(
                not bool(item.get("printable", False))
                for item in _mappings(residual_contract.get("zones", []), "partition.residuals.zones")
            ),
            "partial_never_materializable": plan_status != "proposal_with_residuals" or not materializable,
        },
        "limitations": [
            "La vue dessus projette les placements, etages, residus et encastrements superieurs resolus.",
            "La coupe X/Z traverse le plan a Y = box.y / 2 et peut ne pas couper tous les corps.",
            "Les residus sont des volumes non imprimes ; une suggestion exige toujours confirmation.",
            "Cette vue ne constitue ni une CAD IR, ni une validation Fusion ou impression.",
        ],
    }

def _cavity_world_bounds(placement: dict[str, Any], cavity: dict[str, Any]) -> dict[str, float]:
    origin = _dimension(placement["origin_mm"], "placement.origin_mm")
    final_local = _dimension(placement["final_outer_dimensions_mm"], "placement.final_outer_dimensions_mm")
    minimum_origin = _dimension(placement["minimum_envelope_origin_in_final_mm"], "placement.minimum_envelope_origin_in_final_mm")
    cavity_origin = _dimension(cavity["local_origin_mm"], "cavity.local_origin_mm")
    cavity_size = _dimension(cavity["inner_dimensions_mm"], "cavity.inner_dimensions_mm")
    local_x = minimum_origin["x"] + cavity_origin["x"]
    local_y = minimum_origin["y"] + cavity_origin["y"]
    local_z = minimum_origin["z"] + cavity_origin["z"]
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
