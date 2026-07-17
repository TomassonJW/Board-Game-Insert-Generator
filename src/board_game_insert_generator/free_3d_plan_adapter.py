"""Fail-closed reconstruction of complete free-3D product plans for P64-H07.

Free search families propose resolved outer envelopes.  This adapter restores
the existing product contracts (cavities, reservations, support, removal and
volume conservation) and returns a plan only after the common certificate has
accepted it.  It does not route the public solver; P64-H08 owns that product
surface.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import Mapping

from board_game_insert_generator.expandable_envelope import (
    derive_expandable_envelope_contract,
)
from board_game_insert_generator.free_3d_greedy_solver import Free3DPlacement
from board_game_insert_generator.partition_solver import (
    PARTITION_PLAN_SCHEMA_V1,
    _clearance_policy,
    _complement_participant,
    _container_participant,
    _digest,
    _dimension,
    _mapping,
    _mappings,
    _round,
    _solver_clearance_fallbacks,
    _top_inset_payload,
    _values,
)
from board_game_insert_generator.project_v1 import normalize_project_draft
from board_game_insert_generator.solver_contract import (
    PlacementSnapshot,
    SolverBudget,
    SolverCandidate,
    SolverStrategy,
    ValidationCertificate,
    certify_partition_candidate,
    validate_placement_geometry,
)
from board_game_insert_generator.solver_outcome import (
    SOLUTION_FOUND,
    SOLVER_RESULT_SCHEMA_V1,
    SOLVER_TELEMETRY_SCHEMA_V1,
    result_label,
)
from board_game_insert_generator.top_inset_reservation import (
    apply_top_inset_reservations,
    compatibility_flat_stack_payload,
    derive_top_inset_reservations,
)
from board_game_insert_generator.volumetric_stage_solver import (
    SOLUTION_COMPLETE,
    _dimension_contract,
    _interval_stages,
    _removal_sequence,
    _score_candidate,
    _support_contract,
    _volume_contract,
)


@dataclass(frozen=True)
class Free3DPreparedProblem:
    """Canonical product facts shared by greedy and beam adapters."""

    normalization_source_schema: str
    normalization_migrated: bool
    project: dict[str, object]
    top_inset_plan: dict[str, object]
    flat_stack: dict[str, object]
    envelope_report: dict[str, object]
    box: dict[str, float]
    storage_height_mm: float
    xy_clearance_mm: float
    box_xy_clearance_mm: float
    z_clearance_mm: float
    participants: tuple[dict[str, object], ...]
    requested_container_count: int


@dataclass(frozen=True)
class Free3DPreparation:
    """Preparation result that never converts invalid input into search failure."""

    status: str
    problem: Free3DPreparedProblem | None
    rejection_codes: tuple[str, ...]


@dataclass(frozen=True)
class CertifiedFree3DPlan:
    """A complete plan paired with the common immutable candidate/certificate."""

    plan: dict[str, object]
    candidate: SolverCandidate
    certificate: ValidationCertificate
    placement_digest: str


def prepare_free_3d_problem(raw_project: object) -> Free3DPreparation:
    """Derive the same canonical participants as the stage-stack baseline."""

    normalization = normalize_project_draft(raw_project)
    project = normalization.project
    top_inset_plan = derive_top_inset_reservations(project)
    box = _dimension(_mapping(project["box"])["inner_dimensions_mm"])
    storage_height = float(top_inset_plan["design_top_z_mm"])
    layout = _mapping(project["layout"])
    xy_clearance = float(layout["layout_clearance_mm"])
    box_xy_clearance = float(layout["container_box_xy_clearance_mm"])
    z_clearance = float(layout["container_z_clearance_mm"])
    envelope_report = derive_expandable_envelope_contract(
        project,
        max_container_height_mm=max(storage_height, 0.001),
    )
    rejection_codes: list[str] = []
    if _mappings(top_inset_plan["blockers"]):
        rejection_codes.append("TOP_INSET_INPUT_BLOCKED")
    if _mapping(envelope_report["summary"])["status"] == "blocked":
        rejection_codes.append("CONTAINER_MINIMUM_BLOCKED")
    containers = [
        item for item in _mappings(envelope_report["containers"]) if item["status"] == "ready"
    ]
    requested_count = len(_values(project["container_groups"]))
    if not requested_count:
        rejection_codes.append("NO_CONTAINER_GROUP")
    if len(containers) != requested_count:
        rejection_codes.append("CONTAINER_SET_INCOMPLETE")
    if storage_height <= 0.0:
        rejection_codes.append("NON_POSITIVE_STORAGE_HEIGHT")

    groups_by_id = {str(group["id"]): group for group in _mappings(project["container_groups"])}
    default_floor = float(layout["default_floor_thickness_mm"])
    participants = [
        _container_participant(
            item,
            groups_by_id[str(item["container_group_id"])],
            top_inset_plan=top_inset_plan,
            default_floor_mm=default_floor,
            storage_height_mm=storage_height,
        )
        for item in containers
    ]
    for participant in participants:
        minimum = _mapping(participant["minimum_local_mm"])
        modes = _mapping(participant["dimension_modes"])
        targets = _mapping(participant["target_local_mm"])
        for axis in ("x", "y", "z"):
            if str(modes[axis]) == "fixed" and targets[axis] is None:
                targets[axis] = float(minimum[axis])

    for value in _values(project["fill_elements"]):
        complement = _mapping(value)
        if complement["mode"] != "exact":
            rejection_codes.append("EXPLICIT_COMPLEMENT_NEEDS_EXACT_SIZE")
            continue
        participants.append(_complement_participant(complement))
    if not participants:
        rejection_codes.append("NO_PARTICIPANT")
    if rejection_codes:
        return Free3DPreparation(
            status="invalid_input",
            problem=None,
            rejection_codes=tuple(sorted(set(rejection_codes))),
        )

    solver_clearances = _solver_clearance_fallbacks(
        participants,
        xy_clearance,
        box_xy_clearance,
        z_clearance,
    )
    problem = Free3DPreparedProblem(
        normalization_source_schema=normalization.source_schema,
        normalization_migrated=normalization.migrated,
        project=project,
        top_inset_plan=top_inset_plan,
        flat_stack=compatibility_flat_stack_payload(top_inset_plan),
        envelope_report=envelope_report,
        box=box,
        storage_height_mm=storage_height,
        xy_clearance_mm=solver_clearances[0],
        box_xy_clearance_mm=solver_clearances[1],
        z_clearance_mm=solver_clearances[2],
        participants=tuple(participants),
        requested_container_count=requested_count,
    )
    return Free3DPreparation(status="ready", problem=problem, rejection_codes=())


def certify_free_3d_plan(
    problem: Free3DPreparedProblem,
    *,
    strategy: SolverStrategy,
    budget: SolverBudget,
    candidate_id: str,
    placements: tuple[Free3DPlacement, ...],
    search_telemetry: Mapping[str, object],
) -> tuple[CertifiedFree3DPlan | None, tuple[str, ...]]:
    """Reconstruct and certify one complete free-3D placement, or fail closed."""

    participants_by_id = {str(value["id"]): value for value in problem.participants}
    placement_ids = {value.participant_id for value in placements}
    if placement_ids != set(participants_by_id):
        return None, ("PARTICIPANT_SET_INCOMPLETE",)

    proposals = {
        str(participants_by_id[value.participant_id]["container_group_id"]): dict(
            zip(("x", "y", "z"), value.local_size_mm)
        )
        for value in placements
        if value.role == "container"
    }
    available_by_group = {
        str(participants_by_id[value.participant_id]["container_group_id"]): {
            "x": problem.box["y"] if value.rotation_deg_z == 90 else problem.box["x"],
            "y": problem.box["x"] if value.rotation_deg_z == 90 else problem.box["y"],
            "z": problem.storage_height_mm,
        }
        for value in placements
        if value.role == "container"
    }
    envelopes = derive_expandable_envelope_contract(
        problem.project,
        final_outer_dimensions_by_group=proposals,
        available_outer_dimensions_by_group=available_by_group,
        max_container_height_mm=problem.storage_height_mm,
    )
    if _mapping(envelopes["summary"])["status"] == "blocked":
        return None, ("FINAL_ENVELOPE_REJECTED",)
    envelope_by_group = {
        str(item["container_group_id"]): item for item in _mappings(envelopes["containers"])
    }
    content_names = {
        str(item["id"]): str(item["name"]) for item in _mappings(problem.project["contents"])
    }
    resolved: list[dict[str, object]] = []
    for value in sorted(placements, key=lambda item: item.participant_id):
        participant = participants_by_id[value.participant_id]
        final_local = dict(zip(("x", "y", "z"), value.local_size_mm))
        placement: dict[str, object] = {
            "id": value.participant_id,
            "role": value.role,
            "name": value.name,
            "origin_mm": dict(zip(("x", "y", "z"), value.origin_mm)),
            "world_size_mm": dict(zip(("x", "y", "z"), value.world_size_mm)),
            "rotation_deg_z": value.rotation_deg_z,
            "final_outer_dimensions_mm": final_local,
            "stage_id": "",
            "stage_index": -1,
            "stage_bottom_z_mm": _round(value.origin_mm[2]),
            "stage_top_z_mm": _round(value.origin_mm[2] + value.world_size_mm[2]),
            "reaches_stage_top": abs(
                value.origin_mm[2] + value.world_size_mm[2] - problem.storage_height_mm
            )
            <= 0.001,
            "dimension_contract": _dimension_contract(participant, final_local),
            "printable": True,
            "automatic": False,
        }
        if "external_clearance_effective_v1" in participant:
            placement["external_clearance_effective_v1"] = deepcopy(
                participant["external_clearance_effective_v1"]
            )
        for key in ("container_group_id", "requested_complement_id", "complement_kind"):
            if key in participant:
                placement[key] = participant[key]
        if value.role == "container":
            contract = envelope_by_group[str(participant["container_group_id"])]
            placement["cavity_layout"] = deepcopy(contract["cavity_layout"])
            placement["minimum_outer_envelope_mm"] = deepcopy(contract["minimum_outer_envelope_mm"])
            placement["surplus_distribution_mm"] = deepcopy(contract["surplus_distribution_mm"])
            placement["minimum_envelope_origin_in_final_mm"] = deepcopy(
                contract["minimum_envelope_origin_in_final_mm"]
            )
            placement["source_content_ids"] = [
                str(cavity["content_id"]) for cavity in _mappings(contract["cavity_layout"])
            ]
            placement["source_contents"] = [
                {"id": content_id, "name": content_names[content_id]}
                for content_id in placement["source_content_ids"]
            ]
        resolved.append(placement)

    applied_top_insets = apply_top_inset_reservations(problem.project, resolved)
    if _mappings(applied_top_insets["blockers"]):
        codes = tuple(
            sorted({str(item["code"]) for item in _mappings(applied_top_insets["blockers"])})
        )
        return None, codes or ("TOP_INSET_REJECTED",)
    resolved = _mappings(applied_top_insets["placements"])
    geometry = validate_placement_geometry(
        resolved,
        problem.box,
        problem.storage_height_mm,
        problem.xy_clearance_mm,
        problem.box_xy_clearance_mm,
        problem.z_clearance_mm,
    )
    if not all(
        bool(geometry[key])
        for key in (
            "inside_box",
            "box_xy_clearance_respected",
            "no_collisions",
            "clearances_respected",
        )
    ):
        return None, ("COMMON_GEOMETRY_REJECTED",)

    stages = _interval_stages(resolved, problem.storage_height_mm, 0)
    support = _support_contract(resolved, stages, problem.z_clearance_mm)
    if support["status"] != "supported":
        return None, ("SUPPORT_COVERAGE",)
    removal = _removal_sequence(resolved)
    volume = _volume_contract(
        resolved,
        problem.box,
        problem.storage_height_mm,
        problem.box_xy_clearance_mm,
        True,
    )
    geometry.update(deepcopy(volume))
    geometry["unassigned_printable_volume_mm3"] = 0.0
    scores = _score_candidate(
        resolved,
        stages,
        support,
        volume,
        str(problem.project["solver_preference"]),
        complete=True,
    )
    flat_removal = [
        {
            "order": int(item["order"]),
            "target_id": item["flat_item_id"],
            "target_type": "flat_item",
            "name": item["name"],
            "access_direction": "top",
        }
        for item in _mappings(applied_top_insets.get("removal_sequence", []))
    ]
    body_offset = len(flat_removal)
    body_removal = [
        {
            **deepcopy(item),
            "order": body_offset + int(item["order"]),
            "target_id": item["placement_id"],
            "target_type": "requested_body",
        }
        for item in removal
    ]
    cavity_compensation_count = int(
        _mapping(applied_top_insets["summary"]).get("cavity_depth_compensation_count", 0)
    )
    summary = {
        "status": "constructed",
        "solution_status": SOLUTION_COMPLETE,
        "materializable": True,
        "requested_container_count": problem.requested_container_count,
        "placed_container_count": sum(1 for item in resolved if item["role"] == "container"),
        "explicit_complement_count": sum(
            1 for item in resolved if item["role"] == "explicit_complement"
        ),
        "final_body_count": len(resolved),
        "automatic_body_count": 0,
        "stage_count": len({float(_mapping(item["origin_mm"])["z"]) for item in resolved}),
        "row_count": 0,
        "rotation_count": sum(int(item["rotation_deg_z"] != 0) for item in resolved),
        "simplicity_score": scores["total"],
        "quality_score": scores["total"],
        "score_breakdown": deepcopy(scores),
        "complete_printable_partition": True,
        "technical_voids_are_clearances_only": True,
        "residual_volume_mm3": 0.0,
        "candidate_count_evaluated": int(search_telemetry.get("search_states", 0)),
        "candidate_count_feasible": int(search_telemetry.get("admitted_complete_solutions", 1)),
    }
    solver_result = {
        "schema_version": SOLVER_RESULT_SCHEMA_V1,
        "status": SOLUTION_FOUND,
        "label": result_label(SOLUTION_FOUND),
        "legacy_summary_status": "constructed",
        "proof": None,
        "materializable": True,
    }
    telemetry = {
        "schema_version": SOLVER_TELEMETRY_SCHEMA_V1,
        "family": {"id": strategy.family_id, "version": strategy.version},
        "request": {"id": "not_applicable", "revision": "not_applicable"},
        "elapsed_ms": "not_applicable",
        "budgets": dict(budget.limits),
        "counters": deepcopy(dict(search_telemetry)),
        "prunes": {},
        "diagnostic_code_counts": {},
        "stop_reason": "validated_complete_proposal",
    }
    plan: dict[str, object] = {
        "schema_version": PARTITION_PLAN_SCHEMA_V1,
        "source": {
            "source_schema": problem.normalization_source_schema,
            "migrated": problem.normalization_migrated,
        },
        "project_name": problem.project["project_name"],
        "box": {
            "inner_dimensions_mm": deepcopy(problem.box),
            "storage_height_mm": _round(problem.storage_height_mm),
        },
        "clearance_policy": _clearance_policy(problem.project),
        "flat_stack": deepcopy(problem.flat_stack),
        "top_inset_reservations": _top_inset_payload(applied_top_insets),
        "support": deepcopy(applied_top_insets["support"]),
        "stage_support": support,
        "stages": stages,
        "removal_sequence": flat_removal + body_removal,
        "residuals": {
            "status": "none",
            "zones": [],
            "residual_volume_mm3": 0.0,
            "residual_ratio": 0.0,
        },
        "suggestions": [],
        "placements": resolved,
        "diagnostics": [],
        "validation": geometry,
        "summary": summary,
        "solver": {
            "kind": "bounded_free_3d_solver",
            "family_id": strategy.family_id,
            "schema_version": strategy.version,
            "candidate_id": candidate_id,
            "preference": problem.project["solver_preference"],
            "search_origin": {"family": strategy.family_id, "final_envelopes_in_search": True},
            "budgets": dict(budget.limits),
            "search": deepcopy(dict(search_telemetry)),
            "deterministic": True,
            "globally_optimal": False,
            "result": solver_result,
            "telemetry": telemetry,
        },
        "envelope_contract": deepcopy(envelopes),
        "invariants": {
            "fixed_cavity_layouts": cavity_compensation_count == 0,
            "base_cavity_layouts_fixed": True,
            "top_inset_cavity_depth_compensated": cavity_compensation_count > 0,
            "localized_top_insets": True,
            "volumetric_stages": False,
            "free_3d_final_envelopes": True,
            "weighted_surplus": False,
            "dimension_modes": ["auto", "target", "fixed"],
            "requested_bodies_only": True,
            "automatic_body_count": 0,
            "suggestions_do_not_mutate": True,
            "free_space_materialized": False,
            "scene_is_not_source_of_truth": True,
        },
    }
    plan["plan_digest"] = _digest(plan)
    product_candidate = SolverCandidate(
        strategy=strategy,
        candidate_id=candidate_id,
        plan_digest=str(plan["plan_digest"]),
        placements=tuple(
            PlacementSnapshot(
                placement_id=str(item["id"]),
                role=str(item["role"]),
                origin_mm=tuple(
                    float(_mapping(item["origin_mm"])[axis]) for axis in ("x", "y", "z")
                ),
                size_mm=tuple(
                    float(_mapping(item["world_size_mm"])[axis]) for axis in ("x", "y", "z")
                ),
                rotation_deg_z=int(item["rotation_deg_z"]),
            )
            for item in resolved
        ),
        score_breakdown=tuple(sorted((str(key), float(value)) for key, value in scores.items())),
        automatic_body_count=0,
    )
    certificate = certify_partition_candidate(plan, product_candidate)
    if not certificate.certified:
        return None, certificate.rejection_codes
    placement_digest = _digest(
        {
            "placements": [
                {
                    "id": item.placement_id,
                    "origin": item.origin_mm,
                    "size": item.size_mm,
                    "rotation": item.rotation_deg_z,
                }
                for item in sorted(
                    product_candidate.placements, key=lambda value: value.placement_id
                )
            ]
        }
    )
    return (
        CertifiedFree3DPlan(plan, product_candidate, certificate, placement_digest),
        (),
    )
