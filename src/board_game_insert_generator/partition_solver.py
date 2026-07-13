"""P57 deterministic partition solver for the Fusion-only MVP.

The solver partitions the printable storage volume between requested container
bodies and explicitly sized complements.  It never turns a free region into an
automatic body.  Cavities remain local to their P55 minimum envelope.
"""

from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from typing import Any

from board_game_insert_generator.expandable_envelope import derive_expandable_envelope_contract
from board_game_insert_generator.project_v1 import normalize_project_draft
from board_game_insert_generator.top_inset_reservation import (
    apply_top_inset_reservations,
    compatibility_flat_stack_payload,
    derive_top_inset_reservations,
)
from board_game_insert_generator.volumetric_stage_solver import (
    SOLUTION_COMPLETE,
    SOLUTION_WITH_RESIDUALS,
    solve_stage_portfolio,
)


PARTITION_PLAN_SCHEMA_V1 = "bgig.partition_plan.v1"
_EPSILON = 0.0001


def solve_partition_plan(raw_project: object) -> dict[str, object]:
    """Return the bounded P64 volumetric-stage proposal for a project."""

    normalization = normalize_project_draft(raw_project)
    project = normalization.project
    top_inset_plan = derive_top_inset_reservations(project)
    flat = compatibility_flat_stack_payload(top_inset_plan)
    stack = {"flat_stack": flat, "top_inset_reservations": top_inset_plan}
    box = _dimension(_mapping(project["box"])["inner_dimensions_mm"])
    storage_height = float(top_inset_plan["design_top_z_mm"])
    xy_clearance = float(_mapping(project["layout"])["layout_clearance_mm"])
    box_xy_clearance = float(_mapping(project["layout"])["container_box_xy_clearance_mm"])
    z_clearance = float(_mapping(project["layout"])["container_z_clearance_mm"])
    diagnostics = [
        _diagnostic(
            str(item["code"]), str(item["message"]), str(item["action"]), str(item.get("reference_id", ""))
        )
        for item in _mappings(top_inset_plan["blockers"])
    ]

    envelope_report = derive_expandable_envelope_contract(
        project, max_container_height_mm=max(storage_height, 0.001)
    )
    diagnostics.extend(
        _diagnostic(
            "CONTAINER_MINIMUM_BLOCKED",
            str(item["message"]),
            "Corrige l element, le conteneur ou une dimension fixe.",
            str(item["container_group_id"]),
        )
        for item in _mappings(envelope_report["blockers"])
    )
    containers = [item for item in _mappings(envelope_report["containers"]) if item["status"] == "ready"]
    requested_group_count = len(_values(project["container_groups"]))
    if not requested_group_count:
        diagnostics.append(
            _diagnostic(
                "NO_CONTAINER_GROUP",
                "Aucun conteneur n est demande.",
                "Ajoute au moins un conteneur cible et une famille d elements.",
            )
        )
    if len(containers) != requested_group_count:
        diagnostics.append(
            _diagnostic(
                "CONTAINER_SET_INCOMPLETE",
                "Tous les conteneurs demandes ne possedent pas une enveloppe minimale constructible.",
                "Corrige les conteneurs bloques avant de recalculer.",
            )
        )

    participants = [_container_participant(item) for item in containers]
    for value in _values(project["fill_elements"]):
        complement = _mapping(value)
        if complement["mode"] != "exact":
            diagnostics.append(
                _diagnostic(
                    "EXPLICIT_COMPLEMENT_NEEDS_EXACT_SIZE",
                    f"Le corps explicite '{complement['name']}' utilise encore le mode auto.",
                    "Renseigne ses dimensions exactes ; BGIG ne cree aucun volume automatiquement.",
                    str(complement["id"]),
                )
            )
            continue
        participants.append(_complement_participant(complement))

    if diagnostics or not participants or storage_height <= 0.0:
        return _result(
            normalization, project, stack, envelope_report, diagnostics,
            status="incomplete" if not requested_group_count else "impossible",
            evaluated=0, stage_solver=None,
        )

    stage_solver = solve_stage_portfolio(
        participants,
        box,
        storage_height,
        xy_clearance,
        box_clearance_mm=box_xy_clearance,
        vertical_clearance_mm=z_clearance,
        preference=str(project["solver_preference"]),
    )
    evaluated = int(_mapping(stage_solver["search"])["groupings_evaluated"])
    if not _values(stage_solver["candidates"]):
        diagnostics.extend(
            _diagnostic(str(item["code"]), str(item["message"]), str(item["action"]))
            for item in _mappings(stage_solver["blockers"])
        )
        return _result(
            normalization, project, stack, envelope_report, diagnostics,
            status="impossible", evaluated=evaluated, stage_solver=stage_solver,
        )

    chosen: dict[str, object] | None = None
    chosen_envelopes: dict[str, object] | None = None
    chosen_top_insets: dict[str, object] | None = None
    chosen_validation: dict[str, object] | None = None
    rejection_diagnostics: list[dict[str, object]] = []
    content_names = {str(item["id"]): str(item["name"]) for item in _mappings(project["contents"])}
    for candidate in _mappings(stage_solver["candidates"]):
        proposals = {
            str(item["container_group_id"]): deepcopy(item["final_outer_dimensions_mm"])
            for item in _mappings(candidate["placements"])
            if item["role"] == "container"
        }
        available_by_group = {
            str(item["container_group_id"]): {
                "x": box["y"] if int(item.get("rotation_deg_z", 0)) == 90 else box["x"],
                "y": box["x"] if int(item.get("rotation_deg_z", 0)) == 90 else box["y"],
                "z": storage_height,
            }
            for item in _mappings(candidate["placements"])
            if item["role"] == "container"
        }
        validated_envelopes = derive_expandable_envelope_contract(
            project,
            final_outer_dimensions_by_group=proposals,
            available_outer_dimensions_by_group=available_by_group,
            max_container_height_mm=storage_height,
        )
        if _mapping(validated_envelopes["summary"])["status"] == "blocked":
            rejection_diagnostics.extend(
                _diagnostic(
                    "FINAL_ENVELOPE_REJECTED", str(item["message"]),
                    "Relache la dimension fixe ou cible indiquee.", str(item["container_group_id"]),
                )
                for item in _mappings(validated_envelopes["blockers"])
            )
            continue
        envelope_by_group = {
            str(item["container_group_id"]): item
            for item in _mappings(validated_envelopes["containers"])
        }
        placements: list[dict[str, object]] = []
        for placement in _mappings(candidate["placements"]):
            final = deepcopy(placement)
            if final["role"] == "container":
                contract = envelope_by_group[str(final["container_group_id"])]
                final["cavity_layout"] = deepcopy(contract["cavity_layout"])
                final["minimum_outer_envelope_mm"] = deepcopy(contract["minimum_outer_envelope_mm"])
                final["surplus_distribution_mm"] = deepcopy(contract["surplus_distribution_mm"])
                final["minimum_envelope_origin_in_final_mm"] = deepcopy(contract["minimum_envelope_origin_in_final_mm"])
                final["source_content_ids"] = [
                    str(cavity["content_id"]) for cavity in _mappings(contract["cavity_layout"])
                ]
                final["source_contents"] = [
                    {"id": content_id, "name": content_names[content_id]}
                    for content_id in final["source_content_ids"]
                ]
            placements.append(final)

        applied_top_insets = apply_top_inset_reservations(project, placements)
        if _values(applied_top_insets["blockers"]):
            rejection_diagnostics.extend(
                _diagnostic(
                    str(item["code"]), str(item["message"]), str(item["action"]),
                    str(item.get("reference_id", "")),
                )
                for item in _mappings(applied_top_insets["blockers"])
            )
            continue
        placements = _mappings(applied_top_insets["placements"])
        validation = _validate_placements(placements, box, storage_height, xy_clearance, box_xy_clearance, z_clearance)
        if not all(
            bool(validation[key])
            for key in ("inside_box", "box_xy_clearance_respected", "no_collisions", "clearances_respected")
        ):
            rejection_diagnostics.append(
                _diagnostic(
                    "INTERNAL_STAGE_PLAN_INVALID",
                    "Une proposition par etages viole une borne geometrique interne.",
                    "Conserve le projet et signale ce cas pour correction.",
                    str(candidate["candidate_id"]),
                )
            )
            continue
        conservation = _mapping(candidate["volume_conservation"])
        validation.update(deepcopy(conservation))
        validation["unassigned_printable_volume_mm3"] = conservation["residual_volume_mm3"]
        candidate["placements"] = placements
        chosen = candidate
        chosen_envelopes = validated_envelopes
        chosen_top_insets = applied_top_insets
        chosen_validation = validation
        break

    if chosen is None or chosen_envelopes is None or chosen_top_insets is None or chosen_validation is None:
        diagnostics.extend(rejection_diagnostics[:8])
        diagnostics.append(
            _diagnostic(
                "NO_VALIDATED_STAGE_PROPOSAL",
                "Les arrangements trouves echouent apres validation des cavites, appuis ou reservations superieures.",
                "Relache une dimension fixe, deplace un plateau ou reduis un contenu.",
            )
        )
        return _result(
            normalization, project, stack, envelope_report, diagnostics,
            status="impossible", evaluated=evaluated, stage_solver=stage_solver,
        )

    stack["top_inset_reservations"] = chosen_top_insets
    placements = _mappings(chosen["placements"])
    complete = chosen["solution_status"] == SOLUTION_COMPLETE
    result_status = "constructed" if complete else SOLUTION_WITH_RESIDUALS
    if not complete:
        diagnostics.append(
            _notice(
                "PROPOSAL_HAS_RESIDUALS",
                "Une proposition tient dans la boite mais laisse un volume residuel explicite.",
                "Ajuste les cibles ou confirme plus tard une cale suggeree ; la materialisation reste bloquee.",
            )
        )
    flat_removal = [
        {
            "order": int(item["order"]),
            "target_id": item["flat_item_id"],
            "target_type": "flat_item",
            "name": item["name"],
            "access_direction": "top",
        }
        for item in _mappings(chosen_top_insets.get("removal_sequence", []))
    ]
    body_offset = len(flat_removal)
    body_removal = [
        {
            **deepcopy(item),
            "order": body_offset + int(item["order"]),
            "target_id": item["placement_id"],
            "target_type": "requested_body",
        }
        for item in _mappings(chosen["removal_sequence"])
    ]
    metrics = _mapping(chosen["metrics"])
    search = _mapping(stage_solver["search"])
    summary = {
        "status": result_status,
        "solution_status": chosen["solution_status"],
        "materializable": complete,
        "requested_container_count": requested_group_count,
        "placed_container_count": sum(1 for item in placements if item["role"] == "container"),
        "explicit_complement_count": sum(1 for item in placements if item["role"] == "explicit_complement"),
        "final_body_count": len(placements),
        "automatic_body_count": 0,
        "stage_count": int(chosen["stage_count"]),
        "row_count": int(metrics["row_count"]),
        "rotation_count": int(metrics["rotation_count"]),
        "simplicity_score": chosen["quality_score"],
        "quality_score": chosen["quality_score"],
        "score_breakdown": deepcopy(chosen["score_breakdown"]),
        "complete_printable_partition": complete,
        "technical_voids_are_clearances_only": complete,
        "residual_volume_mm3": _mapping(chosen["volume_conservation"])["residual_volume_mm3"],
        "candidate_count_evaluated": evaluated,
        "candidate_count_feasible": int(search["candidate_count"]),
    }
    cavity_compensation_count = int(
        _mapping(chosen_top_insets["summary"]).get("cavity_depth_compensation_count", 0)
    )
    plan = {
        "schema_version": PARTITION_PLAN_SCHEMA_V1,
        "source": {"source_schema": normalization.source_schema, "migrated": normalization.migrated},
        "project_name": project["project_name"],
        "box": {"inner_dimensions_mm": _rounded(box), "storage_height_mm": _round(storage_height)},
        "clearance_policy": {
            "box_perimeter_mm": _round(box_xy_clearance),
            "between_bodies_mm": _round(xy_clearance),
            "box_perimeter_xy_mm": _round(box_xy_clearance),
            "between_bodies_xy_mm": _round(xy_clearance),
            "between_bodies_z_mm": _round(z_clearance),
            "box_top_z_clearance_mm": _round(float(_mapping(project["box"])["lid_clearance_mm"])),
            "box_bottom_z_clearance_mm": 0.0,
            "vertical_support_gap_mm": _round(z_clearance),
            "vertical_support_contact_mm": 0.0,
            "materialize_clearances": False,
        },
        "flat_stack": deepcopy(flat),
        "top_inset_reservations": _top_inset_payload(chosen_top_insets),
        "support": deepcopy(chosen_top_insets["support"]),
        "stage_support": deepcopy(chosen["support"]),
        "stages": deepcopy(chosen["stages"]),
        "removal_sequence": flat_removal + body_removal,
        "residuals": deepcopy(chosen["residuals"]),
        "suggestions": deepcopy(chosen["suggestions"]),
        "placements": placements,
        "diagnostics": diagnostics,
        "validation": chosen_validation,
        "summary": summary,
        "solver": {
            "kind": "bounded_volumetric_stage_solver",
            "schema_version": stage_solver["schema_version"],
            "candidate_id": chosen["candidate_id"],
            "preference": project["solver_preference"],
            "search_origin": deepcopy(chosen["search_origin"]),
            "budgets": deepcopy(stage_solver["budgets"]),
            "search": deepcopy(stage_solver["search"]),
            "deterministic": True,
            "globally_optimal": False,
        },
        "envelope_contract": deepcopy(chosen_envelopes),
        "invariants": {
            "fixed_cavity_layouts": cavity_compensation_count == 0,
            "base_cavity_layouts_fixed": True,
            "top_inset_cavity_depth_compensated": cavity_compensation_count > 0,
            "localized_top_insets": True,
            "volumetric_stages": True,
            "weighted_surplus": True,
            "dimension_modes": ["auto", "target", "fixed"],
            "requested_bodies_only": True,
            "automatic_body_count": 0,
            "suggestions_do_not_mutate": True,
            "free_space_materialized": False,
            "scene_is_not_source_of_truth": True,
        },
    }
    plan["plan_digest"] = _digest(plan)
    return plan


def _result(
    normalization: Any,
    project: dict[str, object],
    stack: dict[str, object],
    envelopes: dict[str, object],
    diagnostics: list[dict[str, object]],
    *,
    status: str,
    evaluated: int,
    stage_solver: dict[str, object] | None,
) -> dict[str, object]:
    search = _mapping(stage_solver["search"]) if stage_solver is not None else {}
    result = {
        "schema_version": PARTITION_PLAN_SCHEMA_V1,
        "source": {"source_schema": normalization.source_schema, "migrated": normalization.migrated},
        "project_name": project["project_name"],
        "box": {
            "inner_dimensions_mm": deepcopy(_mapping(project["box"])["inner_dimensions_mm"]),
            "storage_height_mm": _mapping(stack["flat_stack"])["storage_height_mm"],
        },
        "clearance_policy": {
            "box_perimeter_mm": _mapping(project["layout"])["container_box_xy_clearance_mm"],
            "between_bodies_mm": _mapping(project["layout"])["layout_clearance_mm"],
            "box_perimeter_xy_mm": _mapping(project["layout"])["container_box_xy_clearance_mm"],
            "between_bodies_xy_mm": _mapping(project["layout"])["layout_clearance_mm"],
            "between_bodies_z_mm": _mapping(project["layout"])["container_z_clearance_mm"],
            "box_top_z_clearance_mm": _mapping(project["box"])["lid_clearance_mm"],
            "box_bottom_z_clearance_mm": 0.0,
            "vertical_support_gap_mm": _mapping(project["layout"])["container_z_clearance_mm"],
            "vertical_support_contact_mm": 0.0,
            "materialize_clearances": False,
        },
        "flat_stack": deepcopy(stack["flat_stack"]),
        "top_inset_reservations": _top_inset_payload(_mapping(stack["top_inset_reservations"])),
        "support": {"status": "unresolved", "top_support_count": 0, "coverage_ratio": 0.0},
        "stage_support": {"status": "unresolved", "supports": []},
        "stages": [],
        "removal_sequence": [],
        "residuals": {"status": "unresolved", "zones": [], "residual_volume_mm3": 0.0},
        "suggestions": [],
        "placements": [],
        "diagnostics": diagnostics,
        "validation": {"inside_box": False, "box_xy_clearance_respected": False, "no_collisions": False, "clearances_respected": False},
        "summary": {
            "status": status,
            "solution_status": "impossible",
            "materializable": False,
            "requested_container_count": len(_values(project["container_groups"])),
            "placed_container_count": 0,
            "explicit_complement_count": 0,
            "final_body_count": 0,
            "automatic_body_count": 0,
            "stage_count": 0,
            "complete_printable_partition": False,
            "technical_voids_are_clearances_only": False,
            "candidate_count_evaluated": evaluated,
            "candidate_count_feasible": int(search.get("candidate_count", 0)),
        },
        "solver": {
            "kind": "bounded_volumetric_stage_solver",
            "schema_version": stage_solver.get("schema_version") if stage_solver else None,
            "budgets": deepcopy(stage_solver.get("budgets", {})) if stage_solver else {},
            "search": deepcopy(search),
            "deterministic": True,
            "globally_optimal": False,
        },
        "envelope_contract": deepcopy(envelopes),
        "invariants": {
            "fixed_cavity_layouts": True,
            "localized_top_insets": True,
            "volumetric_stages": True,
            "weighted_surplus": True,
            "requested_bodies_only": True,
            "automatic_body_count": 0,
            "suggestions_do_not_mutate": True,
            "free_space_materialized": False,
            "scene_is_not_source_of_truth": True,
        },
    }
    result["plan_digest"] = _digest(result)
    return result


def _container_participant(contract: dict[str, object]) -> dict[str, object]:
    minimum = _dimension(contract["minimum_outer_envelope_mm"])
    constraints = _mapping(contract["constraints"])
    return {
        "id": f"container:{contract['container_group_id']}",
        "role": "container",
        "container_group_id": contract["container_group_id"],
        "name": contract["container_name"],
        "minimum_local_mm": minimum,
        "dimension_modes": deepcopy(constraints["dimension_modes"]),
        "target_local_mm": deepcopy(constraints["target_outer_dimensions_mm"]),
        "surplus_preference": constraints["surplus_preference"],
    }


def _complement_participant(value: dict[str, object]) -> dict[str, object]:
    dimensions = _dimension(value["dimensions_mm"])
    return {
        "id": f"complement:{value['id']}",
        "role": "explicit_complement",
        "requested_complement_id": value["id"],
        "complement_kind": value["kind"],
        "name": value["name"],
        "minimum_local_mm": dimensions,
        "dimension_modes": {"x": "fixed", "y": "fixed", "z": "fixed"},
        "target_local_mm": deepcopy(dimensions),
        "surplus_preference": "fixed",
    }


def _validate_placements(
    placements: list[dict[str, object]],
    box: dict[str, float],
    storage_height: float,
    xy_clearance: float,
    box_xy_clearance: float,
    z_clearance: float,
) -> dict[str, object]:
    inside = all(
        all(float(_mapping(item["origin_mm"])[axis]) >= -_EPSILON for axis in ("x", "y", "z"))
        and float(_mapping(item["origin_mm"])["x"]) + float(_mapping(item["world_size_mm"])["x"]) <= box["x"] + _EPSILON
        and float(_mapping(item["origin_mm"])["y"]) + float(_mapping(item["world_size_mm"])["y"]) <= box["y"] + _EPSILON
        and float(_mapping(item["origin_mm"])["z"]) + float(_mapping(item["world_size_mm"])["z"]) <= storage_height + _EPSILON
        for item in placements
    )
    box_xy_clearance_respected = all(
        float(_mapping(item["origin_mm"])["x"]) >= box_xy_clearance - _EPSILON
        and float(_mapping(item["origin_mm"])["y"]) >= box_xy_clearance - _EPSILON
        and float(_mapping(item["origin_mm"])["x"]) + float(_mapping(item["world_size_mm"])["x"])
        <= box["x"] - box_xy_clearance + _EPSILON
        and float(_mapping(item["origin_mm"])["y"]) + float(_mapping(item["world_size_mm"])["y"])
        <= box["y"] - box_xy_clearance + _EPSILON
        for item in placements
    )
    no_collisions = all(
        not _intersects(left, right)
        for index, left in enumerate(placements)
        for right in placements[index + 1 :]
    )
    clearances = all(
        _separated_with_clearance(left, right, xy_clearance, z_clearance)
        for index, left in enumerate(placements)
        for right in placements[index + 1 :]
    )
    body_volume = sum(_volume(_mapping(item["world_size_mm"])) for item in placements)
    storage_volume = box["x"] * box["y"] * storage_height
    return {
        "inside_box": inside,
        "box_xy_clearance_respected": box_xy_clearance_respected,
        "no_collisions": no_collisions,
        "clearances_respected": clearances,
        "body_volume_mm3": _round(body_volume),
        "storage_volume_mm3": _round(storage_volume),
        "technical_void_volume_mm3": _round(max(0.0, storage_volume - body_volume)),
        "unassigned_printable_volume_mm3": 0.0,
    }


def _intersects(left: dict[str, object], right: dict[str, object]) -> bool:
    lo, ls = _mapping(left["origin_mm"]), _mapping(left["world_size_mm"])
    ro, rs = _mapping(right["origin_mm"]), _mapping(right["world_size_mm"])
    return all(float(lo[a]) < float(ro[a]) + float(rs[a]) - _EPSILON and float(ro[a]) < float(lo[a]) + float(ls[a]) - _EPSILON for a in ("x", "y", "z"))


def _separated_with_clearance(
    left: dict[str, object],
    right: dict[str, object],
    xy_clearance: float,
    z_clearance: float,
) -> bool:
    lo, ls = _mapping(left["origin_mm"]), _mapping(left["world_size_mm"])
    ro, rs = _mapping(right["origin_mm"]), _mapping(right["world_size_mm"])
    return any(
        float(lo[axis]) + float(ls[axis]) + clearance <= float(ro[axis]) + 0.001
        or float(ro[axis]) + float(rs[axis]) + clearance <= float(lo[axis]) + 0.001
        for axis, clearance in (("x", xy_clearance), ("y", xy_clearance), ("z", z_clearance))
    )


def _top_inset_payload(value: dict[str, object]) -> dict[str, object]:
    """Keep the resolved reservation contract without duplicating placements."""

    keys = (
        "schema_version", "status", "design_top_z_mm", "total_flat_height_mm",
        "clearance_mm", "reservations", "removal_sequence", "cuts", "supports",
        "cavity_depth_compensations", "support", "blockers", "warnings", "summary",
        "invariants",
    )
    return {key: deepcopy(value[key]) for key in keys if key in value}

def _diagnostic(code: str, message: str, action: str, reference_id: str = "") -> dict[str, object]:
    return {"code": code, "severity": "blocker", "message": message, "action": action, "reference_id": reference_id}


def _notice(code: str, message: str, action: str, reference_id: str = "") -> dict[str, object]:
    return {"code": code, "severity": "warning", "message": message, "action": action, "reference_id": reference_id}


def _digest(value: dict[str, object]) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _mapping(value: object) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise TypeError("Internal partition value must be a mapping.")
    return value


def _mappings(value: object) -> list[dict[str, Any]]:
    return [_mapping(item) for item in _values(value)]


def _values(value: object) -> list[Any]:
    if not isinstance(value, list):
        raise TypeError("Internal partition value must be a list.")
    return value


def _dimension(value: object) -> dict[str, float]:
    raw = _mapping(value)
    return {axis: float(raw[axis]) for axis in ("x", "y", "z")}


def _rounded(value: dict[str, object]) -> dict[str, float]:
    return {axis: _round(float(value[axis])) for axis in ("x", "y", "z")}


def _volume(value: dict[str, object]) -> float:
    return float(value["x"]) * float(value["y"]) * float(value["z"])


def _round(value: float) -> float:
    return round(float(value), 4)
