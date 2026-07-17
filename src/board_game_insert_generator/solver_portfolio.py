"""Bounded multi-solver portfolio with common certification.

Stage-stack, greedy and beam retain distinct search behaviour. Free-3D geometry
is admitted only after the bounded continuous closure has removed printable
residuals and the shared product validator has accepted cavities, top insets,
support, removal and conservation.
"""
from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import Callable

from board_game_insert_generator.free_3d_continuous_closure import (
    close_free_3d_residual,
)
from board_game_insert_generator.free_3d_beam_solver import (
    FREE_3D_BEAM_FAMILY_ID,
    Free3DBeamExecution,
    solve_free_3d_beam,
)
from board_game_insert_generator.free_3d_greedy_solver import (
    FREE_3D_GREEDY_FAMILY_ID,
    Free3DGreedyExecution,
    solve_free_3d_greedy,
)
from board_game_insert_generator.free_3d_plan_adapter import (
    CertifiedFree3DPlan,
    Free3DPreparedProblem,
    certify_free_3d_plan,
    prepare_free_3d_problem,
)
from board_game_insert_generator.partition_solver import solve_stage_stack_plan
from board_game_insert_generator.solver_contract import (
    STAGE_STACK_FAMILY_ID,
    SolverBudget,
    SolverCandidate,
    SolverStrategy,
    ValidationCertificate,
    inspect_stage_stack_plan,
)
from board_game_insert_generator.solver_outcome import (
    INVALID_INPUT,
    NO_SOLUTION_WITHIN_BUDGET,
    PROVEN_IMPOSSIBLE,
    SOLUTION_FOUND,
    STALE_OR_CANCELLED,
)


PORTFOLIO_AUTO_FAMILY_ID = "portfolio_auto"
PORTFOLIO_AUTO_VERSION = "bgig.portfolio_auto.v2"
EFFORT_QUICK = "quick"
EFFORT_NORMAL = "normal"
EFFORT_DEEP = "deep"
_ALLOWED_FAMILIES = (
    STAGE_STACK_FAMILY_ID,
    FREE_3D_GREEDY_FAMILY_ID,
    FREE_3D_BEAM_FAMILY_ID,
)


@dataclass(frozen=True)
class PortfolioEffortProfile:
    """One internal product effort with monotone family-specific limits."""

    profile_id: str
    product_label: str
    allowed_family_ids: tuple[str, ...]
    greedy_budget: SolverBudget
    beam_budget: SolverBudget

    def is_at_least_as_permissive_as(self, other: "PortfolioEffortProfile") -> bool:
        return (
            set(self.allowed_family_ids).issuperset(other.allowed_family_ids)
            and self.greedy_budget.is_at_least_as_permissive_as(other.greedy_budget)
            and self.beam_budget.is_at_least_as_permissive_as(other.beam_budget)
        )


@dataclass(frozen=True)
class PortfolioFamilyReport:
    """Truthful aggregate for one allowed family."""

    family_id: str
    status: str
    stop_reason: str
    proposed_candidate_count: int
    certified_candidate_count: int
    rejection_codes: tuple[str, ...]
    skipped_by_fast_path: bool = False


@dataclass(frozen=True)
class PortfolioCertifiedCandidate:
    """A plan admitted to cross-family ranking."""

    family_id: str
    plan: dict[str, object]
    candidate: SolverCandidate
    certificate: ValidationCertificate
    placement_digest: str
    rank_key: tuple[object, ...]


@dataclass(frozen=True)
class PortfolioExecution:
    """Bounded internal result consumed later by H08."""

    strategy: SolverStrategy
    effort_profile: PortfolioEffortProfile
    status: str
    stop_reason: str
    selected_family_id: str | None
    selected_plan: dict[str, object] | None
    certified_candidates: tuple[PortfolioCertifiedCandidate, ...]
    family_reports: tuple[PortfolioFamilyReport, ...]
    deduplicated_candidate_count: int
    fast_path_used: bool
    deterministic_digest: str
    fallback_plan: dict[str, object] | None
    selected_family_ids: tuple[str, ...]


def portfolio_effort_profiles() -> tuple[PortfolioEffortProfile, ...]:
    """Return Rapide, Normal and Approfondi in monotone order."""

    return (
        _profile(
            EFFORT_QUICK,
            "Rapide",
            greedy=(512, 512, 100_000, 256),
            beam=(8, 2, 1_000, 512, 512, 12, 1, 30_000, 512),
        ),
        _profile(
            EFFORT_NORMAL,
            "Normal",
            greedy=(2_048, 2_048, 500_000, 512),
            beam=(24, 6, 5_000, 2_048, 2_048, 24, 1, 250_000, 4_096),
        ),
        _profile(
            EFFORT_DEEP,
            "Approfondi",
            greedy=(4_096, 4_096, 2_000_000, 1_024),
            beam=(64, 12, 15_000, 4_096, 4_096, 48, 1, 1_000_000, 20_000),
        ),
    )


def solve_partition_portfolio(
    raw_project: object,
    *,
    effort_profile: str = EFFORT_NORMAL,
    request_id: str | None = None,
    request_revision: int | None = None,
    cancel_check: Callable[[], bool] | None = None,
    selected_family_ids: tuple[str, ...] | None = None,
) -> PortfolioExecution:
    """Run bounded families and select only allowed common-certified plans."""

    profile = _effort_profile(effort_profile)
    selected_families = (
        tuple(selected_family_ids) if selected_family_ids is not None else _ALLOWED_FAMILIES
    )
    if not selected_families or not set(selected_families).issubset(_ALLOWED_FAMILIES):
        raise ValueError("Selected portfolio families must be a non-empty supported subset.")
    strategy = SolverStrategy(PORTFOLIO_AUTO_FAMILY_ID, PORTFOLIO_AUTO_VERSION)
    if cancel_check is not None and cancel_check():
        return _portfolio_execution(
            strategy,
            profile,
            STALE_OR_CANCELLED,
            "cancelled_before_search",
            (),
            tuple(
                PortfolioFamilyReport(value, STALE_OR_CANCELLED, "not_started", 0, 0, ())
                for value in profile.allowed_family_ids
            ),
            0,
            False,
            selected_family_ids=selected_families,
        )

    stage_plan = solve_stage_stack_plan(
        raw_project,
        request_id=request_id,
        request_revision=request_revision,
    )
    stage_run = inspect_stage_stack_plan(stage_plan)
    candidates: list[PortfolioCertifiedCandidate] = []
    reports: list[PortfolioFamilyReport] = []
    if stage_run.candidates and stage_run.certificates[0].certified:
        stage_candidate = stage_run.candidates[0]
        stage_certificate = stage_run.certificates[0]
        candidates.append(
            PortfolioCertifiedCandidate(
                family_id=STAGE_STACK_FAMILY_ID,
                plan=stage_plan,
                candidate=stage_candidate,
                certificate=stage_certificate,
                placement_digest=_placement_digest(stage_candidate),
                rank_key=_rank_key(stage_plan, STAGE_STACK_FAMILY_ID, stage_candidate),
            )
        )
        reports.append(
            PortfolioFamilyReport(
                STAGE_STACK_FAMILY_ID,
                SOLUTION_FOUND,
                "validated_complete_proposal",
                1,
                1,
                (),
            )
        )
    else:
        result = _mapping(_mapping(stage_plan.get("solver", {})).get("result", {}))
        reports.append(
            PortfolioFamilyReport(
                STAGE_STACK_FAMILY_ID,
                str(result.get("status", NO_SOLUTION_WITHIN_BUDGET)),
                str(
                    _mapping(_mapping(stage_plan.get("solver", {})).get("telemetry", {})).get(
                        "stop_reason", "heuristic_search_exhausted"
                    )
                ),
                len(stage_run.candidates),
                0,
                tuple(stage_run.certificates[0].rejection_codes if stage_run.certificates else ()),
            )
        )

    if cancel_check is not None and cancel_check():
        reports.extend(
            PortfolioFamilyReport(
                family_id,
                STALE_OR_CANCELLED,
                "not_started",
                0,
                0,
                (),
            )
            for family_id in (FREE_3D_GREEDY_FAMILY_ID, FREE_3D_BEAM_FAMILY_ID)
        )
        return _portfolio_execution(
            strategy,
            profile,
            STALE_OR_CANCELLED,
            "cancelled_after_stage_search",
            (),
            tuple(reports),
            0,
            False,
            selected_family_ids=selected_families,
        )
    if (
        candidates
        and STAGE_STACK_FAMILY_ID in selected_families
        and _is_simple_stage_fast_path(stage_plan)
    ):
        reports.extend(
            PortfolioFamilyReport(
                family_id,
                "not_run",
                "stage_stack_simple_fast_path",
                0,
                0,
                (),
                skipped_by_fast_path=True,
            )
            for family_id in (FREE_3D_GREEDY_FAMILY_ID, FREE_3D_BEAM_FAMILY_ID)
        )
        return _portfolio_execution(
            strategy,
            profile,
            SOLUTION_FOUND,
            "stage_stack_simple_fast_path",
            tuple(candidates),
            tuple(reports),
            0,
            True,
            fallback_plan=stage_plan,
            selected_family_ids=selected_families,
        )

    preparation = prepare_free_3d_problem(raw_project)
    if preparation.problem is None:
        reports.extend(
            PortfolioFamilyReport(
                family_id,
                INVALID_INPUT,
                "input_validation_failed",
                0,
                0,
                preparation.rejection_codes,
            )
            for family_id in (FREE_3D_GREEDY_FAMILY_ID, FREE_3D_BEAM_FAMILY_ID)
        )
        status = SOLUTION_FOUND if candidates else INVALID_INPUT
        stop_reason = "stage_candidate_preserved" if candidates else "input_validation_failed"
        return _portfolio_execution(
            strategy,
            profile,
            status,
            stop_reason,
            tuple(candidates),
            tuple(reports),
            0,
            False,
            selected_family_ids=selected_families,
        )
    problem = preparation.problem

    greedy = solve_free_3d_greedy(
        problem.participants,
        problem.box,
        problem.storage_height_mm,
        problem.xy_clearance_mm,
        box_perimeter_xy_mm=problem.box_xy_clearance_mm,
        between_bodies_z_mm=problem.z_clearance_mm,
        budget=profile.greedy_budget,
        top_inset_zones=problem.top_inset_zones,
    )
    greedy_certified, greedy_rejections = _certify_greedy(problem, greedy)
    if greedy_certified is not None:
        candidates.append(_portfolio_candidate(greedy_certified))
    reports.append(
        PortfolioFamilyReport(
            FREE_3D_GREEDY_FAMILY_ID,
            SOLUTION_FOUND
            if greedy_certified is not None
            else PROVEN_IMPOSSIBLE
            if greedy.status == PROVEN_IMPOSSIBLE
            else NO_SOLUTION_WITHIN_BUDGET,
            (
                "validated_complete_proposal"
                if greedy_certified is not None
                else "geometry_only_candidate_not_product_certified"
                if greedy.candidate is not None
                else greedy.stop_reason
            ),
            1 if greedy.candidate is not None else 0,
            1 if greedy_certified is not None else 0,
            greedy_rejections,
        )
    )

    beam = solve_free_3d_beam(
        problem.participants,
        problem.box,
        problem.storage_height_mm,
        problem.xy_clearance_mm,
        box_perimeter_xy_mm=problem.box_xy_clearance_mm,
        between_bodies_z_mm=problem.z_clearance_mm,
        budget=profile.beam_budget,
        cancel_check=cancel_check,
        top_inset_zones=problem.top_inset_zones,
    )
    beam_candidates, beam_rejections = _certify_beam(problem, beam)
    candidates.extend(_portfolio_candidate(value) for value in beam_candidates)
    reports.append(
        PortfolioFamilyReport(
            FREE_3D_BEAM_FAMILY_ID,
            SOLUTION_FOUND if beam_candidates else beam.status,
            "validated_complete_proposal" if beam_candidates else beam.stop_reason,
            len(beam.solutions),
            len(beam_candidates),
            beam_rejections,
        )
    )

    if beam.status == STALE_OR_CANCELLED:
        return _portfolio_execution(
            strategy,
            profile,
            STALE_OR_CANCELLED,
            beam.stop_reason,
            (),
            tuple(reports),
            0,
            False,
            selected_family_ids=selected_families,
        )
    deduplicated_all, duplicate_count = _deduplicate_candidates(candidates)
    deduplicated = tuple(
        value for value in deduplicated_all if value.family_id in selected_families
    )
    if deduplicated:
        status, stop_reason = SOLUTION_FOUND, "best_common_certified_candidate_selected"
    elif all(report.status == PROVEN_IMPOSSIBLE for report in reports):
        status, stop_reason = PROVEN_IMPOSSIBLE, "all_allowed_families_formally_rejected"
    elif any(report.status == INVALID_INPUT for report in reports):
        status, stop_reason = INVALID_INPUT, "input_validation_failed"
    else:
        status, stop_reason = NO_SOLUTION_WITHIN_BUDGET, "portfolio_budget_exhausted"
    return _portfolio_execution(
        strategy,
        profile,
        status,
        stop_reason,
        deduplicated,
        tuple(reports),
        duplicate_count,
        False,
        fallback_plan=stage_plan,
        selected_family_ids=selected_families,
    )


def _certify_greedy(
    problem: Free3DPreparedProblem,
    execution: Free3DGreedyExecution,
) -> tuple[CertifiedFree3DPlan | None, tuple[str, ...]]:
    if execution.candidate is None or execution.geometry_admission is None:
        return None, ()
    closure = close_free_3d_residual(
        problem.participants,
        execution.placements,
        problem.box,
        problem.storage_height_mm,
        problem.xy_clearance_mm,
        box_perimeter_xy_mm=problem.box_xy_clearance_mm,
        between_bodies_z_mm=problem.z_clearance_mm,
        budget=execution.budget,
        top_inset_zones=problem.top_inset_zones,
    )
    if closure.empty_spaces:
        return None, ("PRINTABLE_RESIDUAL",)
    telemetry = dict(execution.telemetry.__dict__)
    telemetry.update(
        {
            "closure_status": closure.status,
            "closure_iterations": closure.iterations,
            "closure_candidates_evaluated": closure.candidates_evaluated,
            "closure_initial_residual_metric": closure.initial_residual_metric,
            "closure_final_residual_metric": closure.final_residual_metric,
            "closure_aligned_face_count": closure.aligned_face_count,
        }
    )
    return certify_free_3d_plan(
        problem,
        strategy=execution.strategy,
        budget=execution.budget,
        candidate_id=f"{execution.candidate.candidate_id}:closed",
        placements=closure.placements,
        search_telemetry=telemetry,
    )


def _certify_beam(
    problem: Free3DPreparedProblem,
    execution: Free3DBeamExecution,
) -> tuple[tuple[CertifiedFree3DPlan, ...], tuple[str, ...]]:
    certified: list[CertifiedFree3DPlan] = []
    rejection_codes: set[str] = set()
    for solution in execution.solutions:
        closure = close_free_3d_residual(
            problem.participants,
            solution.placements,
            problem.box,
            problem.storage_height_mm,
            problem.xy_clearance_mm,
            box_perimeter_xy_mm=problem.box_xy_clearance_mm,
            between_bodies_z_mm=problem.z_clearance_mm,
            budget=execution.budget,
            top_inset_zones=problem.top_inset_zones,
        )
        if closure.empty_spaces:
            rejection_codes.add("PRINTABLE_RESIDUAL")
            continue
        telemetry = dict(execution.telemetry.__dict__)
        telemetry.update(
            {
                "closure_status": closure.status,
                "closure_iterations": closure.iterations,
                "closure_candidates_evaluated": closure.candidates_evaluated,
                "closure_initial_residual_metric": closure.initial_residual_metric,
                "closure_final_residual_metric": closure.final_residual_metric,
                "closure_aligned_face_count": closure.aligned_face_count,
            }
        )
        result, rejected = certify_free_3d_plan(
            problem,
            strategy=execution.strategy,
            budget=execution.budget,
            candidate_id=f"{solution.candidate.candidate_id}:closed",
            placements=closure.placements,
            search_telemetry=telemetry,
        )
        rejection_codes.update(rejected)
        if result is not None:
            certified.append(result)
            break
    return tuple(certified), tuple(sorted(rejection_codes))


def _portfolio_candidate(value: CertifiedFree3DPlan) -> PortfolioCertifiedCandidate:
    return PortfolioCertifiedCandidate(
        family_id=value.candidate.strategy.family_id,
        plan=value.plan,
        candidate=value.candidate,
        certificate=value.certificate,
        placement_digest=value.placement_digest,
        rank_key=_rank_key(
            value.plan,
            value.candidate.strategy.family_id,
            value.candidate,
        ),
    )


def _deduplicate_candidates(
    values: list[PortfolioCertifiedCandidate],
) -> tuple[tuple[PortfolioCertifiedCandidate, ...], int]:
    unique: dict[str, PortfolioCertifiedCandidate] = {}
    duplicates = 0
    for value in sorted(values, key=lambda item: item.rank_key):
        if value.placement_digest in unique:
            duplicates += 1
            continue
        unique[value.placement_digest] = value
    return tuple(sorted(unique.values(), key=lambda item: item.rank_key)), duplicates


def _rank_key(
    plan: dict[str, object], family_id: str, candidate: SolverCandidate
) -> tuple[object, ...]:
    summary = _mapping(plan.get("summary", {}))
    quality = float(summary.get("quality_score", 0.0))
    family_priority = {
        STAGE_STACK_FAMILY_ID: 0,
        FREE_3D_GREEDY_FAMILY_ID: 1,
        FREE_3D_BEAM_FAMILY_ID: 2,
    }.get(family_id, 9)
    return (-quality, family_priority, candidate.digest)


def _is_simple_stage_fast_path(plan: dict[str, object]) -> bool:
    summary = _mapping(plan.get("summary", {}))
    search = _mapping(_mapping(plan.get("solver", {})).get("search", {}))
    return (
        bool(summary.get("materializable"))
        and int(summary.get("stage_count", 0)) == 1
        and not bool(search.get("canonical_portfolio_failed"))
    )


def _portfolio_execution(
    strategy: SolverStrategy,
    profile: PortfolioEffortProfile,
    status: str,
    stop_reason: str,
    candidates: tuple[PortfolioCertifiedCandidate, ...],
    reports: tuple[PortfolioFamilyReport, ...],
    duplicate_count: int,
    fast_path_used: bool,
    fallback_plan: dict[str, object] | None = None,
    selected_family_ids: tuple[str, ...] = _ALLOWED_FAMILIES,
) -> PortfolioExecution:
    selected = candidates[0] if candidates else None
    digest = _stable_digest(
        {
            "strategy": strategy.__dict__,
            "effort_profile": profile.profile_id,
            "status": status,
            "stop_reason": stop_reason,
            "candidate_digests": [value.candidate.digest for value in candidates],
            "family_reports": [value.__dict__ for value in reports],
            "deduplicated_candidate_count": duplicate_count,
            "fast_path_used": fast_path_used,
            "selected_family_ids": selected_family_ids,
        }
    )
    return PortfolioExecution(
        strategy=strategy,
        effort_profile=profile,
        status=status,
        stop_reason=stop_reason,
        selected_family_id=selected.family_id if selected is not None else None,
        selected_plan=deepcopy(selected.plan) if selected is not None else None,
        certified_candidates=candidates,
        family_reports=reports,
        deduplicated_candidate_count=duplicate_count,
        fast_path_used=fast_path_used,
        deterministic_digest=digest,
        fallback_plan=deepcopy(fallback_plan) if fallback_plan is not None else None,
        selected_family_ids=selected_family_ids,
    )


def _placement_digest(candidate: SolverCandidate) -> str:
    return _stable_digest(
        {
            "placements": [
                {
                    "id": item.placement_id,
                    "origin": item.origin_mm,
                    "size": item.size_mm,
                    "rotation": item.rotation_deg_z,
                }
                for item in sorted(candidate.placements, key=lambda value: value.placement_id)
            ]
        }
    )


def _profile(
    profile_id: str,
    label: str,
    *,
    greedy: tuple[int, int, int, int],
    beam: tuple[int, int, int, int, int, int, int, int, int],
) -> PortfolioEffortProfile:
    greedy_budget = SolverBudget(
        FREE_3D_GREEDY_FAMILY_ID,
        profile_id,
        tuple(
            sorted(
                {
                    "max_empty_spaces": greedy[0],
                    "max_extreme_points": greedy[1],
                    "max_placement_trials": greedy[2],
                    "max_search_states": greedy[3],
                }.items()
            )
        ),
    )
    beam_budget = SolverBudget(
        FREE_3D_BEAM_FAMILY_ID,
        profile_id,
        tuple(
            sorted(
                {
                    "beam_width": beam[0],
                    "max_complete_candidates": beam[1],
                    "max_elapsed_ms": beam[2],
                    "max_empty_spaces": beam[3],
                    "max_extreme_points": beam[4],
                    "max_options_per_participant": beam[5],
                    "max_participant_branches": beam[6],
                    "max_placement_trials": beam[7],
                    "max_search_states": beam[8],
                }.items()
            )
        ),
    )
    return PortfolioEffortProfile(
        profile_id,
        label,
        _ALLOWED_FAMILIES,
        greedy_budget,
        beam_budget,
    )


def _effort_profile(profile_id: str) -> PortfolioEffortProfile:
    for profile in portfolio_effort_profiles():
        if profile.profile_id == profile_id:
            return profile
    raise ValueError(f"Unsupported portfolio effort profile: {profile_id}.")


def _mapping(value: object) -> dict[str, object]:
    return value if isinstance(value, dict) else {}


def _stable_digest(value: object) -> str:
    import hashlib
    import json

    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()
