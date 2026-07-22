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
import json
from typing import Mapping

from board_game_insert_generator.container_internal_variants import (
    ContainerInternalVariant,
    ContainerVariantFrontier,
)
from board_game_insert_generator.expandable_envelope import (
    _surplus_distribution,
    derive_expandable_envelope_contract,
)
from board_game_insert_generator.free_3d_greedy_solver import (
    EmptySpace,
    Free3DPlacement,
    TopInsetZone,
)
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
    ValidationCheck,
    certify_minimal_layout_candidate,
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

MINIMAL_LAYOUT_ARTIFACT_SCHEMA_V1 = "bgig.minimal_layout.v1"


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
    top_inset_zones: tuple[TopInsetZone, ...]
    requested_container_count: int
    container_variant_frontiers: tuple[ContainerVariantFrontier, ...] = ()


@dataclass(frozen=True)
class Free3DPreparation:
    """Preparation result that never converts invalid input into search failure."""

    status: str
    problem: Free3DPreparedProblem | None
    rejection_codes: tuple[str, ...]


@dataclass(frozen=True)
class SelectedContainerVariant:
    """One locally certified variant referenced by a complete placement."""

    container_group_id: str
    variant_id: str
    geometry_digest: str
    canonical: bool
    local_certificate_schema: str


@dataclass(frozen=True)
class ContainerVariantGlobalCertificate:
    """Explicit H03C selection certificate layered over the common validator."""

    schema_version: str
    selection_digest: str
    certified: bool
    checks: tuple[ValidationCheck, ...]

    @property
    def rejection_codes(self) -> tuple[str, ...]:
        return tuple(
            check.rejection_code
            for check in self.checks
            if not check.passed and check.rejection_code is not None
        )


@dataclass(frozen=True)
class CertifiedFree3DPlan:
    """A complete plan paired with the common immutable candidate/certificate."""

    plan: dict[str, object]
    candidate: SolverCandidate
    certificate: ValidationCertificate
    placement_digest: str
    selected_container_variants: tuple[SelectedContainerVariant, ...] = ()
    container_variant_global_certificate: ContainerVariantGlobalCertificate | None = None


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
    top_inset_zones = tuple(
        TopInsetZone(
            origin_xy_mm=(
                float(_mapping(item["cut_origin_mm"])["x"]),
                float(_mapping(item["cut_origin_mm"])["y"]),
            ),
            size_xy_mm=(
                float(_mapping(item["cut_size_mm"])["x"]),
                float(_mapping(item["cut_size_mm"])["y"]),
            ),
            support_plane_z_mm=float(item["support_plane_z_mm"]),
            inset_depth_mm=float(item["inset_depth_from_top_mm"]),
        )
        for item in _mappings(top_inset_plan["reservations"])
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
        top_inset_zones=top_inset_zones,
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

    selected_by_group, selected_references, variant_rejections = (
        _resolve_selected_container_variants(problem, participants_by_id, placements)
    )
    if variant_rejections:
        return None, variant_rejections

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
    if selected_by_group:
        envelopes, envelope_rejections = _selected_variant_envelope_contract(
            problem,
            proposals,
            selected_by_group,
        )
        if envelope_rejections:
            return None, envelope_rejections
    else:
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
            selected_variant = selected_by_group.get(
                str(participant["container_group_id"])
            )
            if selected_variant is not None:
                placement["container_internal_variant_v1"] = {
                    "variant_id": selected_variant.variant_id,
                    "geometry_digest": selected_variant.geometry_digest,
                    "canonical": selected_variant.canonical,
                    "local_certificate_schema": (
                        selected_variant.local_certificate.schema_version
                    ),
                }
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
    if selected_references:
        selection_digest = _digest(
            {
                "selected": [
                    {
                        "container_group_id": value.container_group_id,
                        "variant_id": value.variant_id,
                        "geometry_digest": value.geometry_digest,
                        "canonical": value.canonical,
                    }
                    for value in selected_references
                ]
            }
        )
        _mapping(plan["solver"])["container_variant_selection_v1"] = {
            "schema_version": "bgig.container_variant_selection.v1",
            "selection_digest": selection_digest,
            "selected": [
                {
                    "container_group_id": value.container_group_id,
                    "variant_id": value.variant_id,
                    "geometry_digest": value.geometry_digest,
                    "canonical": value.canonical,
                    "local_certificate_schema": value.local_certificate_schema,
                }
                for value in selected_references
            ],
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
    variant_global_certificate = _container_variant_global_certificate(
        selected_references,
        problem.requested_container_count,
        certificate,
    )
    if (
        variant_global_certificate is not None
        and not variant_global_certificate.certified
    ):
        return None, variant_global_certificate.rejection_codes
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
    if selected_references:
        placement_digest = _digest(
            {
                "base_placement_digest": placement_digest,
                "variant_selection": [
                    (value.container_group_id, value.geometry_digest)
                    for value in selected_references
                ],
            }
        )
    return (
        CertifiedFree3DPlan(
            plan,
            product_candidate,
            certificate,
            placement_digest,
            selected_references,
            variant_global_certificate,
        ),
        (),
    )



def certify_minimal_free_3d_plan(
    problem: Free3DPreparedProblem,
    *,
    strategy: SolverStrategy,
    budget: SolverBudget,
    candidate_id: str,
    placements: tuple[Free3DPlacement, ...],
    empty_spaces: tuple[EmptySpace, ...],
    search_telemetry: Mapping[str, object],
    search_provenance: Mapping[str, object],
) -> tuple[CertifiedFree3DPlan | None, tuple[str, ...]]:
    """Certify a complete minimum-envelope placement without closing residuals."""

    scaffold, rejection_codes = certify_free_3d_plan(
        problem,
        strategy=strategy,
        budget=budget,
        candidate_id=candidate_id,
        placements=placements,
        search_telemetry=search_telemetry,
    )
    if scaffold is None:
        return None, rejection_codes

    plan = deepcopy(scaffold.plan)
    resolved = _mappings(plan["placements"])
    volume = _volume_contract(
        resolved,
        problem.box,
        problem.storage_height_mm,
        problem.box_xy_clearance_mm,
        False,
    )
    validation = _mapping(plan["validation"])
    validation.update(deepcopy(volume))
    validation["unassigned_printable_volume_mm3"] = volume["residual_volume_mm3"]
    plan["validation"] = validation

    metrics = _minimal_layout_metrics(problem, resolved, empty_spaces)
    summary = _mapping(plan["summary"])
    summary.update(
        {
            "status": "constructed",
            "solution_status": "minimal_layout_certified",
            "materializable": False,
            "placement_certified": True,
            "minimal_layout_core_ready": True,
            "complete_printable_partition": False,
            "technical_voids_are_clearances_only": False,
            "residual_volume_mm3": volume["residual_volume_mm3"],
            "quality_score": None,
            "simplicity_score": None,
            "score_breakdown": deepcopy(metrics),
        }
    )
    plan["summary"] = summary
    displayed_spaces = tuple(
        sorted(
            empty_spaces,
            key=lambda value: (
                value.origin_mm[2],
                value.origin_mm[1],
                value.origin_mm[0],
                -value.volume_mm3,
                value.size_mm,
            ),
        )[:64]
    )
    plan["residuals"] = {
        "status": "unassigned",
        "classification": "maximal_empty_spaces_plus_conserved_volume",
        "zones": [
            {
                "id": f"minimal-residual-{index:03d}",
                "kind": "unassigned_residual",
                "stage_id": "",
                "origin_mm": dict(zip(("x", "y", "z"), value.origin_mm)),
                "size_mm": dict(zip(("x", "y", "z"), value.size_mm)),
                "volume_mm3": _round(value.volume_mm3),
                "printable": False,
            }
            for index, value in enumerate(displayed_spaces)
        ],
        "zone_count": len(empty_spaces),
        "displayed_zone_count": len(displayed_spaces),
        "zones_truncated": len(displayed_spaces) < len(empty_spaces),
        "zones_may_overlap": True,
        "residual_volume_mm3": volume["residual_volume_mm3"],
        "residual_ratio": volume["residual_ratio"],
        "residual_is_distributed": False,
    }
    plan["suggestions"] = []
    invariants = _mapping(plan["invariants"])
    invariants.update(
        {
            "minimal_layout": True,
            "minimum_outer_dimensions_only": True,
            "residual_distributed": False,
            "continuous_closure_applied": False,
            "weighted_surplus": False,
            "free_3d_final_envelopes": False,
            "automatic_body_count": 0,
            "free_space_materialized": False,
        }
    )
    plan["invariants"] = invariants
    solver = _mapping(plan["solver"])
    solver.update(
        {
            "kind": "bounded_minimal_layout_solver",
            "candidate_id": candidate_id,
            "search_origin": deepcopy(dict(search_provenance)),
            "deterministic": not bool(
                search_provenance.get("wall_clock_limited")
            ),
            "globally_optimal": False,
        }
    )
    result = _mapping(solver["result"])
    result["materializable"] = False
    solver["result"] = result
    telemetry = _mapping(solver["telemetry"])
    telemetry["stop_reason"] = "minimal_placement_certified"
    if isinstance(search_provenance.get("elapsed_ms"), int):
        telemetry["elapsed_ms"] = int(search_provenance["elapsed_ms"])
    if search_provenance.get("stop_reason") is not None:
        telemetry["search_stop_reason"] = str(
            search_provenance["stop_reason"]
        )
    telemetry["counters"] = deepcopy(dict(search_telemetry))
    solver["telemetry"] = telemetry
    plan["solver"] = solver
    plan["minimal_layout"] = {
        "schema_version": MINIMAL_LAYOUT_ARTIFACT_SCHEMA_V1,
        "artifact_kind": "minimal_layout",
        "geometry_statement": "minimum_envelopes_only_residual_unassigned",
        "best_candidate_statement": (
            "best_certified_proposal_found_within_budget"
        ),
        "search_provenance": deepcopy(dict(search_provenance)),
        "metrics": deepcopy(metrics),
        "residual": {
            "volume_mm3": volume["residual_volume_mm3"],
            "ratio": volume["residual_ratio"],
            "fragment_count": len(empty_spaces),
            "distributed": False,
        },
        "finalization_applied": False,
        "automatic_body_count": 0,
    }
    plan.pop("plan_digest", None)
    certifiable_payload_digest = _digest(plan)
    plan["minimal_layout"]["certifiable_payload_digest"] = certifiable_payload_digest

    product_candidate = SolverCandidate(
        strategy=strategy,
        candidate_id=candidate_id,
        plan_digest=certifiable_payload_digest,
        placements=tuple(
            PlacementSnapshot(
                placement_id=str(item["id"]),
                role=str(item["role"]),
                origin_mm=tuple(
                    float(_mapping(item["origin_mm"])[axis])
                    for axis in ("x", "y", "z")
                ),
                size_mm=tuple(
                    float(_mapping(item["world_size_mm"])[axis])
                    for axis in ("x", "y", "z")
                ),
                rotation_deg_z=int(item["rotation_deg_z"]),
            )
            for item in resolved
        ),
        score_breakdown=tuple(
            sorted(
                (str(key), float(value))
                for key, value in metrics.items()
                if isinstance(value, (int, float)) and not isinstance(value, bool)
            )
        ),
        automatic_body_count=0,
    )
    certificate = certify_minimal_layout_candidate(plan, product_candidate)
    if not certificate.certified:
        return None, certificate.rejection_codes
    variant_global_certificate = _container_variant_global_certificate(
        scaffold.selected_container_variants,
        problem.requested_container_count,
        certificate,
    )
    if (
        variant_global_certificate is not None
        and not variant_global_certificate.certified
    ):
        return None, variant_global_certificate.rejection_codes

    plan["minimal_layout"]["global_certificate"] = _certificate_payload(certificate)
    if variant_global_certificate is not None:
        plan["minimal_layout"]["container_variant_certificate"] = {
            "schema_version": variant_global_certificate.schema_version,
            "selection_digest": variant_global_certificate.selection_digest,
            "certified": variant_global_certificate.certified,
            "checks": [
                {
                    "name": check.name,
                    "passed": check.passed,
                    "rejection_code": check.rejection_code,
                }
                for check in variant_global_certificate.checks
            ],
        }
    plan["plan_digest"] = _digest(plan)
    return (
        CertifiedFree3DPlan(
            plan=plan,
            candidate=product_candidate,
            certificate=certificate,
            placement_digest=scaffold.placement_digest,
            selected_container_variants=scaffold.selected_container_variants,
            container_variant_global_certificate=variant_global_certificate,
        ),
        (),
    )


def _dimension_tuple(
    value: Mapping[str, object],
) -> tuple[float, float, float]:
    dimensions = _dimension(value)
    return (
        dimensions["x"],
        dimensions["y"],
        dimensions["z"],
    )


def _minimal_layout_metrics(
    problem: Free3DPreparedProblem,
    placements: list[dict[str, object]],
    empty_spaces: tuple[EmptySpace, ...],
) -> dict[str, float]:
    origins = [_dimension_tuple(_mapping(item["origin_mm"])) for item in placements]
    sizes = [_dimension_tuple(_mapping(item["world_size_mm"])) for item in placements]
    lower = [
        min(origin[index] for origin in origins)
        for index in range(3)
    ]
    upper = [
        max(origin[index] + size[index] for origin, size in zip(origins, sizes))
        for index in range(3)
    ]
    spans = [upper[index] - lower[index] for index in range(3)]
    body_volume = sum(size[0] * size[1] * size[2] for size in sizes)
    cluster_volume = spans[0] * spans[1] * spans[2]
    support_ratios = [
        float(item.get("support_coverage_ratio", 1.0))
        for item in placements
    ]
    return {
        "lowest_z_mm": _round(min(origin[2] for origin in origins)),
        "cluster_height_mm": _round(upper[2]),
        "cluster_footprint_mm2": _round(spans[0] * spans[1]),
        "cluster_volume_mm3": _round(cluster_volume),
        "internal_gap_mm3": _round(max(0.0, cluster_volume - body_volume)),
        "residual_fragmentation": float(len(empty_spaces)),
        "contact_count": float(
            _contact_count(
                placements,
                problem.xy_clearance_mm,
                problem.z_clearance_mm,
            )
        ),
        "minimum_support_ratio": _round(min(support_ratios, default=1.0)),
        "top_compatibility_certified": 1.0,
        "removal_sequence_certified": 1.0,
    }


def _contact_count(
    placements: list[dict[str, object]],
    xy_clearance: float,
    z_clearance: float,
) -> int:
    contacts = 0
    for index, left in enumerate(placements):
        left_origin = _dimension_tuple(_mapping(left["origin_mm"]))
        left_size = _dimension_tuple(_mapping(left["world_size_mm"]))
        for right in placements[index + 1 :]:
            right_origin = _dimension_tuple(_mapping(right["origin_mm"]))
            right_size = _dimension_tuple(_mapping(right["world_size_mm"]))
            overlaps = [
                min(
                    left_origin[axis] + left_size[axis],
                    right_origin[axis] + right_size[axis],
                )
                - max(left_origin[axis], right_origin[axis])
                for axis in range(3)
            ]
            gaps = [
                max(
                    0.0,
                    right_origin[axis] - (left_origin[axis] + left_size[axis]),
                    left_origin[axis] - (right_origin[axis] + right_size[axis]),
                )
                for axis in range(3)
            ]
            if (
                gaps[0] <= xy_clearance + 0.0001
                and overlaps[1] > 0.0001
                and overlaps[2] > 0.0001
            ) or (
                gaps[1] <= xy_clearance + 0.0001
                and overlaps[0] > 0.0001
                and overlaps[2] > 0.0001
            ) or (
                gaps[2] <= z_clearance + 0.0001
                and overlaps[0] > 0.0001
                and overlaps[1] > 0.0001
            ):
                contacts += 1
    return contacts


def _certificate_payload(
    certificate: ValidationCertificate,
) -> dict[str, object]:
    return {
        "schema_version": certificate.schema_version,
        "candidate_digest": certificate.candidate_digest,
        "certified": certificate.certified,
        "checks": [
            {
                "name": check.name,
                "passed": check.passed,
                "rejection_code": check.rejection_code,
            }
            for check in certificate.checks
        ],
    }


def _resolve_selected_container_variants(
    problem: Free3DPreparedProblem,
    participants_by_id: dict[str, dict[str, object]],
    placements: tuple[Free3DPlacement, ...],
) -> tuple[
    dict[str, ContainerInternalVariant],
    tuple[SelectedContainerVariant, ...],
    tuple[str, ...],
]:
    if not problem.container_variant_frontiers:
        return {}, (), ()
    frontiers = {
        value.container_group_id: value
        for value in problem.container_variant_frontiers
    }
    selected: dict[str, ContainerInternalVariant] = {}
    references: list[SelectedContainerVariant] = []
    rejections: set[str] = set()
    for placement in placements:
        if placement.role != "container":
            continue
        participant = participants_by_id[placement.participant_id]
        group_id = str(participant["container_group_id"])
        variant_id = str(getattr(placement, "container_variant_id", ""))
        geometry_digest = str(
            getattr(placement, "container_variant_digest", "")
        )
        frontier = frontiers.get(group_id)
        if frontier is None or not variant_id or not geometry_digest:
            rejections.add("GLOBAL_VARIANT_REFERENCE_MISSING")
            continue
        matches = [
            value
            for value in frontier.variants
            if value.variant_id == variant_id
            and value.geometry_digest == geometry_digest
        ]
        if len(matches) != 1:
            rejections.add("GLOBAL_VARIANT_REFERENCE_UNKNOWN")
            continue
        variant = matches[0]
        if not variant.local_certificate.certified:
            rejections.add("GLOBAL_VARIANT_LOCAL_CERTIFICATE_REJECTED")
            continue
        if any(
            placement.local_size_mm[index] + 0.0001
            < variant.draft.minimum_outer_envelope_mm[index]
            for index in range(3)
        ):
            rejections.add("GLOBAL_VARIANT_ENVELOPE_UNDERSIZED")
            continue
        if group_id in selected:
            rejections.add("GLOBAL_VARIANT_SELECTION_NOT_UNIQUE")
            continue
        selected[group_id] = variant
        references.append(
            SelectedContainerVariant(
                container_group_id=group_id,
                variant_id=variant.variant_id,
                geometry_digest=variant.geometry_digest,
                canonical=variant.canonical,
                local_certificate_schema=variant.local_certificate.schema_version,
            )
        )
    expected_groups = {
        str(value["container_group_id"])
        for value in problem.participants
        if value["role"] == "container"
    }
    if set(selected) != expected_groups:
        rejections.add("GLOBAL_VARIANT_SELECTION_INCOMPLETE")
    return (
        selected,
        tuple(sorted(references, key=lambda value: value.container_group_id)),
        tuple(sorted(rejections)),
    )


def _selected_variant_envelope_contract(
    problem: Free3DPreparedProblem,
    proposals: dict[str, dict[str, float]],
    selected_by_group: dict[str, ContainerInternalVariant],
) -> tuple[dict[str, object], tuple[str, ...]]:
    result = deepcopy(problem.envelope_report)
    source_contracts = {
        str(value["container_group_id"]): value
        for value in _mappings(problem.envelope_report["containers"])
    }
    contracts: list[dict[str, object]] = []
    rejections: set[str] = set()
    for group_id in sorted(selected_by_group):
        variant = selected_by_group[group_id]
        source = source_contracts.get(group_id)
        final = proposals.get(group_id)
        if source is None or final is None:
            rejections.add("GLOBAL_VARIANT_ENVELOPE_SOURCE_MISSING")
            continue
        minimum = dict(
            zip(("x", "y", "z"), variant.draft.minimum_outer_envelope_mm)
        )
        if any(final[axis] + 0.0001 < minimum[axis] for axis in ("x", "y", "z")):
            rejections.add("GLOBAL_VARIANT_ENVELOPE_UNDERSIZED")
            continue
        contract = deepcopy(source)
        constraints = _mapping(contract["constraints"])
        target = _mapping(constraints["target_outer_dimensions_mm"])
        surplus = {
            axis: _round(max(0.0, final[axis] - minimum[axis]))
            for axis in ("x", "y", "z")
        }
        distribution = _surplus_distribution(surplus)
        contract.update(
            {
                "status": "ready",
                "cavity_layout": _variant_cavity_layout(variant, source),
                "cavity_layout_frame": "minimum_outer_envelope.local",
                "minimum_outer_envelope_mm": deepcopy(minimum),
                "final_outer_envelope_mm": deepcopy(final),
                "minimum_envelope_origin_in_final_mm": {
                    "x": distribution["left"],
                    "y": distribution["front"],
                    "z": distribution["below"],
                },
                "surplus_distribution_mm": distribution,
                "dimension_resolution": {
                    axis: {
                        "mode": _mapping(constraints["dimension_modes"])[axis],
                        "minimum_mm": minimum[axis],
                        "target_mm": target[axis],
                        "calculated_mm": final[axis],
                        "target_deviation_mm": (
                            _round(final[axis] - float(target[axis]))
                            if target[axis] is not None
                            else None
                        ),
                    }
                    for axis in ("x", "y", "z")
                },
                "blockers": [],
                "invariants": {
                    "cavity_dimensions_fixed": True,
                    "cavity_local_origins_fixed": True,
                    "external_envelope_expansion_only": True,
                    "automatic_body_created": False,
                    "container_internal_variant_certified": True,
                },
            }
        )
        contracts.append(contract)
    if rejections:
        return result, tuple(sorted(rejections))
    result["containers"] = contracts
    _mapping(result["summary"]).update(
        {
            "status": "ready_for_p56",
            "ready_container_count": len(contracts),
            "blocked_container_count": 0,
            "fixed_cavity_count": sum(
                len(_mappings(value["cavity_layout"])) for value in contracts
            ),
            "invariant": (
                "certified_internal_variant__expandable_outer_envelope"
            ),
        }
    )
    result["blockers"] = []
    return result, ()


def _variant_cavity_layout(
    variant: ContainerInternalVariant,
    source_contract: dict[str, object],
) -> list[dict[str, object]]:
    source_by_id = {
        str(value["cavity_id"]): value
        for value in _mappings(source_contract["cavity_layout"])
    }
    result: list[dict[str, object]] = []
    for cavity in variant.draft.cavities:
        source = source_by_id[cavity.cavity_id]
        result.append(
            {
                "cavity_id": cavity.cavity_id,
                "content_id": cavity.content_id,
                "shape_kind": cavity.shape_kind,
                "local_origin_mm": dict(
                    zip(("x", "y", "z"), cavity.local_origin_mm)
                ),
                "inner_dimensions_mm": dict(
                    zip(("x", "y", "z"), cavity.inner_dimensions_mm)
                ),
                "base_inner_dimensions_mm": dict(
                    zip(("x", "y", "z"), cavity.base_dimensions_mm)
                ),
                "resolved_dimensions_mm": dict(
                    zip(("x", "y", "z"), cavity.resolved_dimensions_mm)
                ),
                "content_clearance_mm": source["content_clearance_mm"],
                "clearance_effective_v1": {
                    "values_mm": dict(
                        zip(("x", "y", "z"), cavity.clearance_values_mm)
                    ),
                    "source_by_axis": dict(
                        zip(("x", "y", "z"), cavity.clearance_sources)
                    ),
                },
                "quantity": json.loads(cavity.quantity_payload),
            }
        )
    return result


def _container_variant_global_certificate(
    selected: tuple[SelectedContainerVariant, ...],
    requested_container_count: int,
    common_certificate: ValidationCertificate,
) -> ContainerVariantGlobalCertificate | None:
    if not selected:
        return None
    selection_digest = _digest(
        {
            "selected": [
                {
                    "container_group_id": value.container_group_id,
                    "variant_id": value.variant_id,
                    "geometry_digest": value.geometry_digest,
                }
                for value in selected
            ]
        }
    )
    checks = (
        ValidationCheck(
            "exactly_one_variant_per_container",
            len(selected) == requested_container_count
            and len({value.container_group_id for value in selected})
            == requested_container_count,
            "GLOBAL_VARIANT_SELECTION_INCOMPLETE",
        ),
        ValidationCheck(
            "unique_variant_references",
            len(
                {
                    (value.container_group_id, value.variant_id)
                    for value in selected
                }
            )
            == len(selected),
            "GLOBAL_VARIANT_SELECTION_NOT_UNIQUE",
        ),
        ValidationCheck(
            "common_product_certificate",
            common_certificate.certified,
            "GLOBAL_PRODUCT_CERTIFICATE_REJECTED",
        ),
    )
    return ContainerVariantGlobalCertificate(
        schema_version="bgig.container_variant_global_certificate.v1",
        selection_digest=selection_digest,
        certified=all(value.passed for value in checks),
        checks=checks,
    )
