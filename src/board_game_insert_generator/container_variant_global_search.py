"""Lazy globally certified consumption of local container variants for H03C.

The canonical portfolio remains authoritative and runs before this module.  This
fallback injects certified local variants directly into beam placement options,
so search states carry one chosen variant per placed container without building
a Cartesian product of assignments.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
import hashlib
import json
from typing import Callable, Mapping

from board_game_insert_generator.container_internal_variants import (
    ContainerInternalVariant,
    ContainerVariantBudget,
    ContainerVariantFrontier,
    derive_container_internal_variant_frontiers,
    variant_budget_for_effort,
)
from board_game_insert_generator.free_3d_beam_solver import (
    BEAM_SEARCH_INTERNAL_VARIANTS,
    Free3DBeamExecution,
    VariantFree3DPlacement,
    solve_free_3d_beam,
)
from board_game_insert_generator.free_3d_continuous_closure import (
    close_free_3d_residual,
)
from board_game_insert_generator.free_3d_plan_adapter import (
    CertifiedFree3DPlan,
    Free3DPreparedProblem,
    prepare_free_3d_problem,
    certify_free_3d_plan,
)
from board_game_insert_generator.solver_contract import SolverBudget
from board_game_insert_generator.solver_outcome import (
    INVALID_INPUT,
    NO_SOLUTION_WITHIN_BUDGET,
    SOLUTION_FOUND,
    STALE_OR_CANCELLED,
)


CONTAINER_VARIANT_GLOBAL_SEARCH_SCHEMA_V1 = (
    "bgig.container_variant_global_search.v1"
)
EFFORT_QUICK = "quick"
EFFORT_NORMAL = "normal"
EFFORT_DEEP = "deep"
_EFFORT_ORDER = (EFFORT_QUICK, EFFORT_NORMAL, EFFORT_DEEP)
_AXES = ("x", "y", "z")


@dataclass(frozen=True)
class ContainerVariantFrontierReport:
    container_group_id: str
    generated_count: int
    certified_count: int
    rejected_count: int
    duplicate_count: int
    dominated_count: int
    retained_count: int
    retained_digests: tuple[str, ...]
    local_rejection_codes: tuple[str, ...]
    generation_limit_reached: bool
    certification_limit_reached: bool
    retention_limit_reached: bool


@dataclass(frozen=True)
class ContainerVariantLaneReport:
    effort_profile: str
    variant_budget: ContainerVariantBudget
    beam_budget: SolverBudget
    status: str
    stop_reason: str
    frontier_reports: tuple[ContainerVariantFrontierReport, ...]
    search_states: int
    placement_trials: int
    feasible_options: int
    certified_plan_count: int
    candidate_digests: tuple[str, ...]
    selected_variant_digests: tuple[str, ...]
    rejection_codes: tuple[str, ...]
    state_limit_reached: bool
    placement_trial_limit_reached: bool
    cancelled: bool
    timed_out: bool
    deterministic_digest: str


@dataclass(frozen=True)
class ContainerVariantGlobalExecution:
    schema_version: str
    requested_effort_profile: str
    status: str
    stop_reason: str
    candidates: tuple[CertifiedFree3DPlan, ...]
    lane_reports: tuple[ContainerVariantLaneReport, ...]
    preparation_rejection_codes: tuple[str, ...]
    deterministic_digest: str


def run_container_variant_global_search(
    raw_project: object,
    *,
    requested_effort_profile: str,
    beam_budgets_by_effort: Mapping[str, SolverBudget],
    cancel_check: Callable[[], bool] | None = None,
) -> ContainerVariantGlobalExecution:
    """Run prefix-preserving variant lanes after canonical failure."""

    efforts = effort_prefix(requested_effort_profile)
    missing = [value for value in efforts if value not in beam_budgets_by_effort]
    if missing:
        raise ValueError(
            "Missing canonical beam budgets for variant lanes: "
            + ", ".join(missing)
            + "."
        )
    if cancel_check is not None and cancel_check():
        return _global_execution(
            requested_effort_profile,
            STALE_OR_CANCELLED,
            "cancelled_before_variant_preparation",
            (),
            (),
            (),
        )

    preparation = prepare_free_3d_problem(raw_project)
    if preparation.problem is None:
        return _global_execution(
            requested_effort_profile,
            INVALID_INPUT,
            "variant_input_validation_failed",
            (),
            (),
            preparation.rejection_codes,
        )
    canonical_problem = preparation.problem
    candidates: list[CertifiedFree3DPlan] = []
    lane_reports: list[ContainerVariantLaneReport] = []
    for effort in efforts:
        if cancel_check is not None and cancel_check():
            return _global_execution(
                requested_effort_profile,
                STALE_OR_CANCELLED,
                "cancelled_before_variant_lane",
                (),
                tuple(lane_reports),
                (),
            )
        run = derive_container_internal_variant_frontiers(
            raw_project,
            effort_profile=effort,
            max_container_height_mm=canonical_problem.storage_height_mm,
        )
        participants = _participants_with_variant_options(
            canonical_problem.participants,
            run.frontiers,
        )
        problem = replace(
            canonical_problem,
            participants=participants,
            container_variant_frontiers=run.frontiers,
        )
        variant_budget = variant_budget_for_effort(effort)
        beam_budget = _variant_beam_budget(
            beam_budgets_by_effort[effort],
            variant_budget,
        )
        beam = solve_free_3d_beam(
            problem.participants,
            problem.box,
            problem.storage_height_mm,
            problem.xy_clearance_mm,
            box_perimeter_xy_mm=problem.box_xy_clearance_mm,
            between_bodies_z_mm=problem.z_clearance_mm,
            budget=beam_budget,
            cancel_check=cancel_check,
            top_inset_zones=problem.top_inset_zones,
            search_variant=BEAM_SEARCH_INTERNAL_VARIANTS,
        )
        certified, rejections = _certify_variant_beam(problem, beam)
        candidates.extend(certified)
        lane_reports.append(
            _lane_report(
                effort,
                variant_budget,
                beam_budget,
                run.frontiers,
                beam,
                certified,
                rejections,
            )
        )
        if beam.status == STALE_OR_CANCELLED:
            return _global_execution(
                requested_effort_profile,
                STALE_OR_CANCELLED,
                beam.stop_reason,
                (),
                tuple(lane_reports),
                (),
            )

    unique = {
        value.candidate.digest: value
        for value in sorted(candidates, key=lambda item: item.candidate.digest)
    }
    ordered = tuple(unique[key] for key in sorted(unique))
    return _global_execution(
        requested_effort_profile,
        SOLUTION_FOUND if ordered else NO_SOLUTION_WITHIN_BUDGET,
        (
            "variant_common_certified_candidate_found"
            if ordered
            else "variant_lanes_exhausted_within_budget"
        ),
        ordered,
        tuple(lane_reports),
        (),
    )


def effort_prefix(requested_effort_profile: str) -> tuple[str, ...]:
    if requested_effort_profile not in _EFFORT_ORDER:
        raise ValueError(
            f"Unsupported variant effort profile: {requested_effort_profile}."
        )
    return _EFFORT_ORDER[: _EFFORT_ORDER.index(requested_effort_profile) + 1]


def container_variant_global_execution_to_dict(
    execution: ContainerVariantGlobalExecution,
) -> dict[str, object]:
    selected = execution.candidates[0] if execution.candidates else None
    global_certificate = (
        selected.container_variant_global_certificate
        if selected is not None
        else None
    )
    return {
        "schema_version": execution.schema_version,
        "requested_effort_profile": execution.requested_effort_profile,
        "status": execution.status,
        "stop_reason": execution.stop_reason,
        "canonical_portfolio_completed_first": True,
        "cartesian_product_materialized": False,
        "preparation_rejection_codes": list(
            execution.preparation_rejection_codes
        ),
        "candidate_count": len(execution.candidates),
        "candidate_digests": [
            value.candidate.digest for value in execution.candidates
        ],
        "selected_variants": (
            [
                {
                    "container_group_id": value.container_group_id,
                    "variant_id": value.variant_id,
                    "geometry_digest": value.geometry_digest,
                    "canonical": value.canonical,
                    "local_certificate_schema": value.local_certificate_schema,
                }
                for value in selected.selected_container_variants
            ]
            if selected is not None
            else []
        ),
        "global_certificate": (
            {
                "schema_version": global_certificate.schema_version,
                "selection_digest": global_certificate.selection_digest,
                "certified": global_certificate.certified,
                "rejection_codes": list(global_certificate.rejection_codes),
                "checks": [
                    {
                        "name": value.name,
                        "passed": value.passed,
                        "rejection_code": value.rejection_code,
                    }
                    for value in global_certificate.checks
                ],
            }
            if global_certificate is not None
            else None
        ),
        "lanes": [_lane_report_to_dict(value) for value in execution.lane_reports],
        "deterministic_digest": execution.deterministic_digest,
    }


def _participants_with_variant_options(
    participants: tuple[dict[str, object], ...],
    frontiers: tuple[ContainerVariantFrontier, ...],
) -> tuple[dict[str, object], ...]:
    by_group = {value.container_group_id: value for value in frontiers}
    result: list[dict[str, object]] = []
    for participant in participants:
        projected = dict(participant)
        if participant["role"] == "container":
            group_id = str(participant["container_group_id"])
            frontier = by_group.get(group_id)
            if frontier is None or not frontier.variants:
                raise ValueError(
                    f"Missing certified variant frontier for {group_id}."
                )
            projected["container_internal_variant_options_v1"] = [
                _variant_option(value, index)
                for index, value in enumerate(frontier.variants)
            ]
        result.append(projected)
    return tuple(result)


def _variant_option(
    variant: ContainerInternalVariant,
    frontier_index: int,
) -> dict[str, object]:
    return {
        "variant_id": variant.variant_id,
        "geometry_digest": variant.geometry_digest,
        "canonical": variant.canonical,
        "frontier_index": frontier_index,
        "minimum_outer_envelope_mm": dict(
            zip(_AXES, variant.draft.minimum_outer_envelope_mm)
        ),
        "cavities": [
            {
                "cavity_id": value.cavity_id,
                "local_origin_mm": dict(zip(_AXES, value.local_origin_mm)),
                "inner_dimensions_mm": dict(zip(_AXES, value.inner_dimensions_mm)),
            }
            for value in variant.draft.cavities
        ],
        "local_certificate_schema": variant.local_certificate.schema_version,
    }


def _variant_beam_budget(
    source: SolverBudget,
    variant: ContainerVariantBudget,
) -> SolverBudget:
    limits = dict(source.limits)
    limits["max_search_states"] = min(
        limits["max_search_states"],
        variant.max_variant_assignment_states,
    )
    limits["max_placement_trials"] = min(
        limits["max_placement_trials"],
        variant.max_variant_placement_trials,
    )
    limits["max_variant_options_per_expansion"] = (
        variant.max_variant_options_per_expansion
    )
    return SolverBudget(
        source.family_id,
        variant.effort_profile,
        tuple(sorted(limits.items())),
    )


def _selected_participants_for_placements(
    participants: tuple[dict[str, object], ...],
    placements: tuple[VariantFree3DPlacement, ...],
) -> tuple[dict[str, object], ...]:
    placements_by_id = {value.participant_id: value for value in placements}
    selected: list[dict[str, object]] = []
    for participant in participants:
        placement = placements_by_id[participant["id"]]
        projected = dict(participant)
        if placement.role == "container":
            options = participant.get("container_internal_variant_options_v1")
            if not isinstance(options, list):
                raise ValueError("Container participant has no variant options.")
            matches = [
                value
                for value in options
                if value["variant_id"] == placement.container_variant_id
                and value["geometry_digest"]
                == placement.container_variant_digest
            ]
            if len(matches) != 1:
                raise ValueError("Placed container variant is not in its frontier.")
            option = matches[0]
            projected["minimum_local_mm"] = dict(
                option["minimum_outer_envelope_mm"]
            )
            projected["selected_container_variant_v1"] = dict(option)
            hint = projected.get("top_inset_search_hint_v1")
            if isinstance(hint, dict):
                selected_hint = dict(hint)
                selected_hint["cavities"] = [
                    {
                        "local_origin_mm": dict(value["local_origin_mm"]),
                        "inner_dimensions_mm": dict(
                            value["inner_dimensions_mm"]
                        ),
                    }
                    for value in option["cavities"]
                ]
                projected["top_inset_search_hint_v1"] = selected_hint
        selected.append(projected)
    return tuple(selected)


def _certify_variant_beam(
    problem: Free3DPreparedProblem,
    execution: Free3DBeamExecution,
) -> tuple[tuple[CertifiedFree3DPlan, ...], tuple[str, ...]]:
    certified: list[CertifiedFree3DPlan] = []
    rejections: set[str] = set()
    for solution in execution.solutions:
        placements = tuple(solution.placements)
        if any(
            value.role == "container"
            and not isinstance(value, VariantFree3DPlacement)
            for value in placements
        ):
            rejections.add("GLOBAL_VARIANT_REFERENCE_MISSING")
            continue
        selected_participants = _selected_participants_for_placements(
            problem.participants,
            placements,  # type: ignore[arg-type]
        )
        closure = close_free_3d_residual(
            selected_participants,
            placements,
            problem.box,
            problem.storage_height_mm,
            problem.xy_clearance_mm,
            box_perimeter_xy_mm=problem.box_xy_clearance_mm,
            between_bodies_z_mm=problem.z_clearance_mm,
            budget=execution.budget,
            top_inset_zones=problem.top_inset_zones,
        )
        if closure.empty_spaces:
            rejections.add("PRINTABLE_RESIDUAL")
            continue
        telemetry = dict(execution.telemetry.__dict__)
        telemetry.update(
            {
                "variant_lane": execution.budget.effort_profile,
                "variant_search_variant": BEAM_SEARCH_INTERNAL_VARIANTS,
                "closure_status": closure.status,
                "closure_iterations": closure.iterations,
                "closure_candidates_evaluated": closure.candidates_evaluated,
                "closure_initial_residual_metric": (
                    closure.initial_residual_metric
                ),
                "closure_final_residual_metric": closure.final_residual_metric,
                "closure_aligned_face_count": closure.aligned_face_count,
            }
        )
        result, rejected = certify_free_3d_plan(
            problem,
            strategy=execution.strategy,
            budget=execution.budget,
            candidate_id=f"{solution.candidate.candidate_id}:variants:closed",
            placements=closure.placements,
            search_telemetry=telemetry,
        )
        rejections.update(rejected)
        if result is not None:
            certified.append(result)
            break
    return tuple(certified), tuple(sorted(rejections))


def _frontier_report(
    frontier: ContainerVariantFrontier,
) -> ContainerVariantFrontierReport:
    return ContainerVariantFrontierReport(
        container_group_id=frontier.container_group_id,
        generated_count=frontier.generated_count,
        certified_count=frontier.certified_count,
        rejected_count=len(frontier.rejected),
        duplicate_count=frontier.duplicate_count,
        dominated_count=frontier.dominated_count,
        retained_count=len(frontier.variants),
        retained_digests=tuple(
            value.geometry_digest for value in frontier.variants
        ),
        local_rejection_codes=tuple(
            sorted(
                {
                    code
                    for value in frontier.rejected
                    for code in value.rejection_codes
                }
            )
        ),
        generation_limit_reached=frontier.generation_limit_reached,
        certification_limit_reached=frontier.certification_limit_reached,
        retention_limit_reached=frontier.retention_limit_reached,
    )


def _lane_report(
    effort: str,
    variant_budget: ContainerVariantBudget,
    beam_budget: SolverBudget,
    frontiers: tuple[ContainerVariantFrontier, ...],
    beam: Free3DBeamExecution,
    certified: tuple[CertifiedFree3DPlan, ...],
    rejections: tuple[str, ...],
) -> ContainerVariantLaneReport:
    frontier_reports = tuple(_frontier_report(value) for value in frontiers)
    selected_digests = tuple(
        value.geometry_digest
        for candidate in certified
        for value in candidate.selected_container_variants
    )
    lane_status = (
        SOLUTION_FOUND
        if certified
        else STALE_OR_CANCELLED
        if beam.status == STALE_OR_CANCELLED
        else NO_SOLUTION_WITHIN_BUDGET
    )
    lane_stop_reason = (
        "variant_common_certified_candidate_found"
        if certified
        else beam.stop_reason
        if beam.status == STALE_OR_CANCELLED or not beam.solutions
        else "variant_geometry_not_common_certified"
    )
    payload = {
        "effort": effort,
        "variant_budget": variant_budget.to_dict(),
        "beam_budget": dict(beam_budget.limits),
        "status": lane_status,
        "stop_reason": lane_stop_reason,
        "frontiers": [
            {
                **value.__dict__,
                "retained_digests": list(value.retained_digests),
                "local_rejection_codes": list(value.local_rejection_codes),
            }
            for value in frontier_reports
        ],
        "search_states": beam.telemetry.search_states,
        "placement_trials": beam.telemetry.placement_trials,
        "candidate_digests": [
            value.candidate.digest for value in certified
        ],
        "selected_variant_digests": selected_digests,
        "rejection_codes": rejections,
    }
    return ContainerVariantLaneReport(
        effort_profile=effort,
        variant_budget=variant_budget,
        beam_budget=beam_budget,
        status=lane_status,
        stop_reason=lane_stop_reason,
        frontier_reports=frontier_reports,
        search_states=beam.telemetry.search_states,
        placement_trials=beam.telemetry.placement_trials,
        feasible_options=beam.telemetry.feasible_options,
        certified_plan_count=len(certified),
        candidate_digests=tuple(
            value.candidate.digest for value in certified
        ),
        selected_variant_digests=selected_digests,
        rejection_codes=rejections,
        state_limit_reached=(
            beam.telemetry.search_states
            >= variant_budget.max_variant_assignment_states
        ),
        placement_trial_limit_reached=(
            beam.telemetry.placement_trials
            >= variant_budget.max_variant_placement_trials
        ),
        cancelled=beam.telemetry.cancelled,
        timed_out=beam.telemetry.timed_out,
        deterministic_digest=_stable_digest(payload),
    )


def _lane_report_to_dict(
    report: ContainerVariantLaneReport,
) -> dict[str, object]:
    return {
        "effort_profile": report.effort_profile,
        "variant_budget": report.variant_budget.to_dict(),
        "beam_budget": dict(report.beam_budget.limits),
        "status": report.status,
        "stop_reason": report.stop_reason,
        "frontiers": [
            {
                "container_group_id": value.container_group_id,
                "generated_count": value.generated_count,
                "certified_count": value.certified_count,
                "rejected_count": value.rejected_count,
                "duplicate_count": value.duplicate_count,
                "dominated_count": value.dominated_count,
                "retained_count": value.retained_count,
                "retained_digests": list(value.retained_digests),
                "local_rejection_codes": list(
                    value.local_rejection_codes
                ),
                "generation_limit_reached": (
                    value.generation_limit_reached
                ),
                "certification_limit_reached": (
                    value.certification_limit_reached
                ),
                "retention_limit_reached": value.retention_limit_reached,
            }
            for value in report.frontier_reports
        ],
        "counters": {
            "variant_assignment_states": report.search_states,
            "variant_placement_trials": report.placement_trials,
            "feasible_options": report.feasible_options,
            "certified_plan_count": report.certified_plan_count,
        },
        "candidate_digests": list(report.candidate_digests),
        "selected_variant_digests": list(
            report.selected_variant_digests
        ),
        "rejection_codes": list(report.rejection_codes),
        "limits": {
            "state_limit_reached": report.state_limit_reached,
            "placement_trial_limit_reached": (
                report.placement_trial_limit_reached
            ),
        },
        "cancelled": report.cancelled,
        "timed_out": report.timed_out,
        "deterministic_digest": report.deterministic_digest,
    }


def _global_execution(
    requested_effort: str,
    status: str,
    stop_reason: str,
    candidates: tuple[CertifiedFree3DPlan, ...],
    lanes: tuple[ContainerVariantLaneReport, ...],
    preparation_rejections: tuple[str, ...],
) -> ContainerVariantGlobalExecution:
    digest = _stable_digest(
        {
            "schema_version": CONTAINER_VARIANT_GLOBAL_SEARCH_SCHEMA_V1,
            "requested_effort": requested_effort,
            "status": status,
            "stop_reason": stop_reason,
            "candidate_digests": [
                value.candidate.digest for value in candidates
            ],
            "lane_digests": [
                value.deterministic_digest for value in lanes
            ],
            "preparation_rejections": preparation_rejections,
        }
    )
    return ContainerVariantGlobalExecution(
        schema_version=CONTAINER_VARIANT_GLOBAL_SEARCH_SCHEMA_V1,
        requested_effort_profile=requested_effort,
        status=status,
        stop_reason=stop_reason,
        candidates=candidates,
        lane_reports=lanes,
        preparation_rejection_codes=preparation_rejections,
        deterministic_digest=digest,
    )


def _stable_digest(value: object) -> str:
    payload = json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()
