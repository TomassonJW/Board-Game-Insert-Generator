"""Bounded coupled finalization from one certified minimal 3D incumbent.

The finalizer preserves requested bodies and cavity-local geometry. It distributes
printable residual volume through admissible envelope faces, tries bounded local
placement repairs when direct growth stalls, and publishes a plan only after the
shared global product certificate accepts the complete result.
"""

from __future__ import annotations

from copy import deepcopy
from time import perf_counter
from typing import Mapping, Sequence

from board_game_insert_generator.container_variant_global_search import (
    _selected_participants_for_placements,
)
from board_game_insert_generator.free_3d_continuous_closure import (
    FINISHING_OBJECTIVE_BALANCED_THEN_PROPORTIONAL,
    FINISHING_OBJECTIVE_CLOSURE_ONLY,
    FREE_3D_CONTINUOUS_CLOSURE_VERSION,
    Free3DClosureResult,
    close_free_3d_residual,
)
from board_game_insert_generator.global_rectangular_closure import (
    GLOBAL_RECTANGULAR_CLOSURE_VERSION,
    GlobalRectangularClosureResult,
    close_global_rectangular_partition,
)
from board_game_insert_generator.xy_composite_closure import (
    XYCompositeClosureResult,
    close_xy_composite_partition,
    xy_composite_closure_to_dict,
)
from board_game_insert_generator.free_3d_plan_adapter import (
    CertifiedFree3DPlan,
    Free3DPreparedProblem,
    certify_free_3d_plan,
    prepare_free_3d_problem,
)
from board_game_insert_generator.incremental_project_state import canonical_digest
from board_game_insert_generator.minimal_layout_solver import (
    _minimal_budget,
    _placements_from_certified_plan,
    _problem_with_frontiers,
    _resolve_frontiers,
)
from board_game_insert_generator.solver_contract import SolverBudget, SolverStrategy
from board_game_insert_generator.solver_settings import solver_deadline_seconds


COUPLED_FINALIZATION_SCHEMA_V1 = "bgig.coupled_finalization.v1"
COUPLED_FINALIZATION_FAMILY_ID = "bounded_coupled_finalization"
COUPLED_FINALIZATION_VERSION = "bgig.bounded_coupled_finalization.v9"
COUPLED_FINALIZATION_POLICY = (
    "global_rectangular_then_vertical_first_continuous_then_bounded_xy_composite"
)
ARTIFACT_KIND_FINALIZED = "finalized_plan"

_CLOSURE_CAPS = {
    "quick": {
        "max_closure_iterations": 64,
        "max_closure_candidates": 7_500,
        "max_local_repairs": 32,
    },
    "short": {
        "max_closure_iterations": 96,
        "max_closure_candidates": 20_000,
        "max_local_repairs": 48,
    },
    "normal": {
        "max_closure_iterations": 128,
        "max_closure_candidates": 37_500,
        "max_local_repairs": 64,
    },
    "long": {
        "max_closure_iterations": 192,
        "max_closure_candidates": 75_000,
        "max_local_repairs": 96,
    },
    "deep": {
        "max_closure_iterations": 256,
        "max_closure_candidates": 125_000,
        "max_local_repairs": 128,
    },
}


class CoupledFinalizationError(ValueError):
    """Fail-closed finalization rejection with machine-readable evidence."""

    def __init__(self, message: str, report: Mapping[str, object]) -> None:
        super().__init__(message)
        self.report = deepcopy(dict(report))


def coupled_finalization_budget(effort_profile: str) -> SolverBudget:
    """Return one independent five-level budget for the complete finishing run."""

    if effort_profile not in _CLOSURE_CAPS:
        raise ValueError(f"Unsupported effort profile: {effort_profile}.")
    source = _minimal_budget(effort_profile)
    deadline_ms = int(solver_deadline_seconds(effort_profile) * 1000.0)
    limits = dict(source.limits)
    limits.update(_CLOSURE_CAPS[effort_profile])
    limits["max_total_elapsed_ms"] = deadline_ms
    limits["max_closure_elapsed_ms"] = deadline_ms
    return SolverBudget(
        COUPLED_FINALIZATION_FAMILY_ID,
        effort_profile,
        tuple(sorted(limits.items())),
    )


def coupled_finalization_budget_digest(effort_profile: str) -> str:
    """Identify exactly the finishing budget used in staged cache keys."""

    budget = coupled_finalization_budget(effort_profile)
    return canonical_digest(
        {
            "family_id": budget.family_id,
            "effort_profile": budget.effort_profile,
            "limits": dict(budget.limits),
        }
    )


def _object_mapping(value: object) -> dict[str, object]:
    return dict(value) if isinstance(value, Mapping) else {}


def finalize_coupled_volume(
    raw_project: object,
    minimal_plan: Mapping[str, object],
    *,
    source_minimal_artifact_digest: str,
    effort_profile: str,
    container_frontiers: Sequence[object] = (),
) -> dict[str, object]:
    """Try one bounded pool of certified minimal candidates under one deadline."""

    budget = coupled_finalization_budget(effort_profile)
    deadline_at = perf_counter() + float(
        dict(budget.limits)["max_total_elapsed_ms"]
    ) / 1000.0
    candidates = [
        {
            "candidate_index": 0,
            "placement_digest": str(minimal_plan.get("plan_digest", "")),
            "lane_id": "selected_minimal_plan",
            "plan": minimal_plan,
        },
        *_finishing_candidate_entries(minimal_plan),
    ]
    attempts: list[dict[str, object]] = []
    last_error: CoupledFinalizationError | None = None
    pool_deadline_reached = False
    for candidate in candidates:
        if attempts and _deadline_reached(deadline_at):
            pool_deadline_reached = True
            break
        candidate_plan = candidate["plan"]
        if not isinstance(candidate_plan, Mapping):
            continue
        try:
            result = _finalize_coupled_volume_candidate(
                raw_project,
                candidate_plan,
                source_minimal_artifact_digest=source_minimal_artifact_digest,
                effort_profile=effort_profile,
                container_frontiers=container_frontiers,
                _deadline_at=deadline_at,
            )
        except CoupledFinalizationError as exc:
            report = deepcopy(exc.report)
            attempts.append(
                {
                    "candidate_index": candidate["candidate_index"],
                    "placement_digest": candidate["placement_digest"],
                    "lane_id": candidate["lane_id"],
                    "status": str(report.get("status", "rejected")),
                    "stop_reason": str(report.get("stop_reason", "rejected")),
                }
            )
            last_error = exc
            fatal_stop_reasons = {
                "input_validation_failed",
                "minimal_incumbent_reconstruction_failed",
                "minimal_plan_not_certified",
            }
            if str(report.get("stop_reason", "")) in fatal_stop_reasons:
                raise
            continue

        attempts.append(
            {
                "candidate_index": candidate["candidate_index"],
                "placement_digest": candidate["placement_digest"],
                "lane_id": candidate["lane_id"],
                "status": "solution_found",
                "stop_reason": "candidate_finalization_certified",
            }
        )
        finalization = deepcopy(_object_mapping(result.get("finalization")))
        finalization["minimal_candidate_selection"] = {
            "schema_version": "bgig.finalization_minimal_candidate_selection.v1",
            "candidate_pool_count": len(candidates),
            "attempt_count": len(attempts),
            "selected_candidate_index": candidate["candidate_index"],
            "selected_placement_digest": candidate["placement_digest"],
            "selected_lane_id": candidate["lane_id"],
            "shared_deadline_enforced": True,
            "attempts": attempts,
        }
        result["finalization"] = finalization
        solver = deepcopy(_object_mapping(result.get("solver")))
        telemetry = deepcopy(_object_mapping(solver.get("telemetry")))
        telemetry["minimal_candidate_pool_count"] = len(candidates)
        telemetry["minimal_candidate_attempt_count"] = len(attempts)
        telemetry["selected_minimal_candidate_index"] = candidate["candidate_index"]
        solver["telemetry"] = telemetry
        result["solver"] = solver
        result.pop("plan_digest", None)
        result["plan_digest"] = canonical_digest(result)
        return result

    if last_error is not None:
        report = deepcopy(last_error.report)
        report["candidate_pool_count"] = len(candidates)
        report["candidate_attempt_count"] = len(attempts)
        report["candidate_pool_attempts"] = attempts
        report["shared_deadline_enforced"] = True
        if pool_deadline_reached or report.get("deadline_reached") is True:
            report["deadline_reached"] = True
        raise CoupledFinalizationError(
            "Aucun plan minimal certifie du pool borne ne permet une finition complete.",
            report,
        ) from last_error
    raise CoupledFinalizationError(
        "Aucun candidat minimal certifie n est disponible pour la finition.",
        _failure_report("minimal_candidate_pool_empty", ()),
    )


def _finishing_candidate_entries(
    minimal_plan: Mapping[str, object],
) -> list[dict[str, object]]:
    solver = _object_mapping(minimal_plan.get("solver"))
    search_origin = _object_mapping(solver.get("search_origin"))
    raw_candidates = search_origin.get("finishing_candidate_pool")
    if not isinstance(raw_candidates, list):
        return []
    result: list[dict[str, object]] = []
    seen = {str(minimal_plan.get("plan_digest", ""))}
    for raw in raw_candidates[:12]:
        if not isinstance(raw, Mapping):
            continue
        plan = raw.get("plan")
        if not isinstance(plan, Mapping):
            continue
        placement_digest = str(raw.get("placement_digest", ""))
        if not placement_digest or placement_digest in seen:
            continue
        seen.add(placement_digest)
        result.append(
            {
                "candidate_index": len(result) + 1,
                "placement_digest": placement_digest,
                "lane_id": str(raw.get("lane_id", "bounded_candidate")),
                "plan": plan,
            }
        )
    return result


def _finalize_coupled_volume_candidate(
    raw_project: object,
    minimal_plan: Mapping[str, object],
    *,
    source_minimal_artifact_digest: str,
    effort_profile: str,
    container_frontiers: Sequence[object] = (),
    _deadline_at: float | None = None,
) -> dict[str, object]:
    """Finish one minimal incumbent under one shared total deadline."""

    budget = coupled_finalization_budget(effort_profile)
    total_budget_seconds = (
        float(dict(budget.limits)["max_total_elapsed_ms"]) / 1000.0
    )
    deadline_at = (
        _deadline_at
        if _deadline_at is not None
        else perf_counter() + total_budget_seconds
    )
    _require_certified_minimal(minimal_plan)
    if _deadline_reached(deadline_at):
        raise CoupledFinalizationError(
            "La deadline totale est atteinte avant la preparation de la finition.",
            _deadline_failure_report(
                "global_deadline_reached_before_preparation",
                budget,
            ),
        )

    frozen_top_inset_plan = minimal_plan.get("top_inset_reservations")
    if not isinstance(frozen_top_inset_plan, Mapping):
        raise CoupledFinalizationError(
            "Le plan minimal ne contient pas ses reservations superieures figees.",
            _failure_report(
                "minimal_top_inset_plan_missing",
                ("MINIMAL_TOP_INSET_PLAN_MISSING",),
            ),
        )
    preparation = prepare_free_3d_problem(
        raw_project,
        top_inset_plan=frozen_top_inset_plan,
    )
    if preparation.problem is None:
        raise CoupledFinalizationError(
            "Le probleme produit ne peut pas etre prepare pour la finalisation.",
            _failure_report(
                "input_validation_failed",
                preparation.rejection_codes,
            ),
        )
    problem = preparation.problem
    if not container_frontiers:
        resolved_frontiers, _, _, frontier_rejections = _resolve_frontiers(
            raw_project,
            problem,
            effort_profile,
            None,
            (),
        )
        if frontier_rejections:
            raise CoupledFinalizationError(
                "Les variantes internes du plan minimal ne peuvent pas etre rechargees.",
                _failure_report(
                    "container_variant_frontier_reconstruction_failed",
                    frontier_rejections,
                ),
            )
        problem = _problem_with_frontiers(problem, resolved_frontiers)
    else:
        problem = _problem_with_frontiers(problem, tuple(container_frontiers))
    try:
        placements = _placements_from_certified_plan(minimal_plan)
        participants = problem.participants
        if problem.container_variant_frontiers:
            participants = _selected_participants_for_placements(
                problem.participants,
                placements,  # type: ignore[arg-type]
            )
    except (KeyError, TypeError, ValueError) as exc:
        raise CoupledFinalizationError(
            "L incumbent minimal ne peut pas etre reconstruit fidelement.",
            _failure_report(
                "minimal_incumbent_reconstruction_failed",
                (type(exc).__name__,),
            ),
        ) from exc

    closure_budget = _remaining_phase_budget(budget, deadline_at)
    if closure_budget is None:
        raise CoupledFinalizationError(
            "La deadline totale est atteinte avant la partition globale.",
            _deadline_failure_report(
                "global_deadline_reached_before_rectangular_partition",
                budget,
            ),
        )
    closure = close_global_rectangular_partition(
        participants,
        placements,
        problem.box,
        problem.storage_height_mm,
        problem.xy_clearance_mm,
        box_perimeter_xy_mm=problem.box_xy_clearance_mm,
        between_bodies_z_mm=problem.z_clearance_mm,
        budget=closure_budget,
        top_inset_zones=problem.top_inset_zones,
    )
    if closure.empty_spaces:
        deadline_reached = bool(
            closure.deadline_reached or _deadline_reached(deadline_at)
        )
        if deadline_reached:
            raise CoupledFinalizationError(
                "La deadline totale est atteinte pendant la partition rectangulaire globale.",
                _closure_report(
                    closure,
                    stop_reason="global_deadline_reached_during_rectangular_partition",
                    budget=budget,
                    deadline_reached=True,
                ),
            )
        continuous_budget = _continuous_phase_budget(budget, deadline_at)
        if continuous_budget is None:
            raise CoupledFinalizationError(
                "La deadline totale est atteinte avant la croissance continue.",
                _closure_report(
                    closure,
                    stop_reason="global_deadline_reached_before_continuous_closure",
                    budget=budget,
                    deadline_reached=True,
                ),
            )
        continuous = close_free_3d_residual(
            participants,
            placements,
            problem.box,
            problem.storage_height_mm,
            problem.xy_clearance_mm,
            box_perimeter_xy_mm=problem.box_xy_clearance_mm,
            between_bodies_z_mm=problem.z_clearance_mm,
            budget=continuous_budget,
            top_inset_zones=problem.top_inset_zones,
            finishing_objective=FINISHING_OBJECTIVE_CLOSURE_ONLY,
        )
        if not continuous.empty_spaces:
            if _deadline_reached(deadline_at):
                raise CoupledFinalizationError(
                    "La deadline totale est atteinte avant le certificat continu.",
                    _closure_report(
                        continuous,
                        stop_reason="global_deadline_reached_before_continuous_certificate",
                        budget=budget,
                        deadline_reached=True,
                    ),
                )
            continuous_strategy = SolverStrategy(
                COUPLED_FINALIZATION_FAMILY_ID,
                COUPLED_FINALIZATION_VERSION,
            )
            continuous_plan, continuous_rejections = _certify_closed_plan(
                problem,
                continuous,
                strategy=continuous_strategy,
                budget=budget,
                phase="v7_vertical_first_continuous_closure",
            )
            if continuous_plan is None:
                raise CoupledFinalizationError(
                    "Le certificat produit a rejete la fermeture continue.",
                    _closure_report(
                        continuous,
                        stop_reason="continuous_product_certificate_rejected",
                        rejection_codes=continuous_rejections,
                        budget=budget,
                    ),
                )
            return _finalized_plan(
                continuous_plan,
                continuous,
                baseline_closure=continuous,
                objective_closure=None,
                objective_attempted=True,
                objective_certified=True,
                objective_improved=False,
                selected_plan_source="v7_vertical_first_continuous_closure",
                objective_fallback_reason="vertical_first_continuous_partition_complete",
                source_minimal_artifact_digest=source_minimal_artifact_digest,
                source_minimal_plan_digest=str(minimal_plan.get("plan_digest", "")),
                budget=budget,
                reservation_count=len(problem.top_inset_zones),
                global_deadline_reached=continuous.deadline_reached,
            )
        composite_budget = _remaining_phase_budget(budget, deadline_at)
        if composite_budget is None:
            raise CoupledFinalizationError(
                "La deadline totale est atteinte avant le repli composite XY.",
                _closure_report(
                    closure,
                    stop_reason="global_deadline_reached_before_xy_composite_fallback",
                    budget=budget,
                    deadline_reached=True,
                ),
            )
        composite = close_xy_composite_partition(
            participants,
            placements,
            problem.box,
            problem.storage_height_mm,
            problem.xy_clearance_mm,
            box_perimeter_xy_mm=problem.box_xy_clearance_mm,
            between_bodies_z_mm=problem.z_clearance_mm,
            budget=composite_budget,
            top_inset_zones=problem.top_inset_zones,
            rectangular_attempt=closure,
            continuous_prefill=continuous,
        )
        composite_certified = bool(
            composite.status == "closed"
            and composite.certificate.get("certified") is True
        )
        if not composite_certified:
            raise CoupledFinalizationError(
                "Aucune fermeture complete rectangulaire ou composite XY n a ete certifiee.",
                _xy_composite_report(
                    closure,
                    composite,
                    budget=budget,
                    stop_reason=(
                        "global_deadline_reached_during_xy_composite_fallback"
                        if composite.gross_closure.deadline_reached
                        else composite.stop_reason
                    ),
                ),
            )
        if _deadline_reached(deadline_at):
            raise CoupledFinalizationError(
                "La deadline totale est atteinte avant la recertification composite.",
                _xy_composite_report(
                    closure,
                    composite,
                    budget=budget,
                    stop_reason="global_deadline_reached_before_xy_composite_certificate",
                ),
            )
        if (
            composite.certificate.get("source_mode")
            == "continuous_prefill_residual_cells"
        ):
            hybrid_candidate = composite
            composite = close_xy_composite_partition(
                participants,
                placements,
                problem.box,
                problem.storage_height_mm,
                problem.xy_clearance_mm,
                box_perimeter_xy_mm=problem.box_xy_clearance_mm,
                between_bodies_z_mm=problem.z_clearance_mm,
                budget=composite_budget,
                top_inset_zones=problem.top_inset_zones,
            )
            if not (
                composite.status == "closed"
                and composite.certificate.get("certified") is True
            ):
                raise CoupledFinalizationError(
                    "La fermeture hybride est certifiee, mais son certificat produit et CAD IR relevent de la mission F.",
                    _xy_composite_report(
                        closure,
                        hybrid_candidate,
                        budget=budget,
                        stop_reason="xy_composite_product_certificate_v2_required",
                    ),
                )
        composite_strategy = SolverStrategy(
            COUPLED_FINALIZATION_FAMILY_ID,
            COUPLED_FINALIZATION_VERSION,
        )
        composite_plan, composite_rejections = _certify_closed_plan(
            problem,
            composite.gross_closure,
            strategy=composite_strategy,
            budget=budget,
            phase="e_xy_composite_gross_partition_with_exact_insets",
        )
        if composite_plan is None:
            raise CoupledFinalizationError(
                "Le certificat produit a rejete la fermeture composite XY.",
                _xy_composite_report(
                    closure,
                    composite,
                    budget=budget,
                    stop_reason="xy_composite_product_certificate_rejected",
                    rejection_codes=composite_rejections,
                ),
            )
        return _finalized_plan(
            composite_plan,
            composite.gross_closure,
            baseline_closure=composite.gross_closure,
            objective_closure=None,
            objective_attempted=True,
            objective_certified=True,
            objective_improved=False,
            selected_plan_source="e_xy_composite_union_and_exact_insets",
            objective_fallback_reason="bounded_xy_composite_required",
            source_minimal_artifact_digest=source_minimal_artifact_digest,
            source_minimal_plan_digest=str(minimal_plan.get("plan_digest", "")),
            budget=budget,
            reservation_count=len(problem.top_inset_zones),
            global_deadline_reached=composite.gross_closure.deadline_reached,
            composite_closure=composite,
            continuous_prefill=continuous,
        )
    if closure.partition_certificate.get("certified") is not True:
        raise CoupledFinalizationError(
            "Le certificat de partition rectangulaire globale est invalide.",
            _closure_report(
                closure,
                stop_reason="global_rectangular_partition_certificate_rejected",
                budget=budget,
            ),
        )
    if _deadline_reached(deadline_at):
        raise CoupledFinalizationError(
            "La deadline totale est atteinte avant le certificat produit final.",
            _closure_report(
                closure,
                stop_reason="global_deadline_reached_before_final_certificate",
                budget=budget,
                deadline_reached=True,
            ),
        )

    strategy = SolverStrategy(
        COUPLED_FINALIZATION_FAMILY_ID,
        COUPLED_FINALIZATION_VERSION,
    )
    certified, rejection_codes = _certify_closed_plan(
        problem,
        closure,
        strategy=strategy,
        budget=budget,
        phase="c_global_rectangular_partition",
    )
    if _deadline_reached(deadline_at):
        raise CoupledFinalizationError(
            "La deadline totale est atteinte pendant le certificat produit final.",
            _closure_report(
                closure,
                stop_reason="global_deadline_reached_during_final_certificate",
                rejection_codes=rejection_codes,
                budget=budget,
                deadline_reached=True,
            ),
        )
    if certified is None:
        raise CoupledFinalizationError(
            "Le certificat produit final a rejete la partition globale.",
            _closure_report(
                closure,
                stop_reason="global_certificate_rejected",
                rejection_codes=rejection_codes,
                budget=budget,
            ),
        )

    return _finalized_plan(
        certified,
        closure,
        baseline_closure=closure,
        objective_closure=None,
        objective_attempted=True,
        objective_certified=True,
        objective_improved=False,
        selected_plan_source="c_global_rectangular_partition",
        objective_fallback_reason="global_partition_complete_by_construction",
        source_minimal_artifact_digest=source_minimal_artifact_digest,
        source_minimal_plan_digest=str(minimal_plan.get("plan_digest", "")),
        budget=budget,
        reservation_count=len(problem.top_inset_zones),
        global_deadline_reached=closure.deadline_reached,
    )

def _certify_closed_plan(
    problem: Free3DPreparedProblem,
    closure: Free3DClosureResult | GlobalRectangularClosureResult,
    *,
    strategy: SolverStrategy,
    budget: SolverBudget,
    phase: str,
) -> tuple[CertifiedFree3DPlan | None, tuple[str, ...]]:
    return certify_free_3d_plan(
        problem,
        strategy=strategy,
        budget=budget,
        candidate_id=(
            f"coupled-finalization:{phase}:"
            f"{closure.incumbent_digest[:12]}:"
            f"{closure.deterministic_digest[:12]}"
        ),
        placements=closure.placements,
        search_telemetry=_closure_telemetry(
            closure,
            problem,
            phase=phase,
        ),
    )


def _remaining_objective_budget(
    budget: SolverBudget,
    baseline: Free3DClosureResult | GlobalRectangularClosureResult,
    *,
    remaining_elapsed_ms: int,
) -> SolverBudget | None:
    limits = dict(budget.limits)
    remaining_iterations = int(limits["max_closure_iterations"]) - (
        baseline.iterations
    )
    remaining_candidates = int(limits["max_closure_candidates"]) - (
        baseline.candidates_evaluated
    )
    remaining_repairs = int(limits["max_local_repairs"]) - (
        baseline.repair_attempts
    )
    if (
        remaining_iterations <= 0
        or remaining_candidates <= 0
        or remaining_elapsed_ms <= 0
    ):
        return None
    limits.update(
        {
            "max_closure_iterations": remaining_iterations,
            "max_closure_candidates": remaining_candidates,
            "max_local_repairs": max(0, remaining_repairs),
            "max_closure_elapsed_ms": remaining_elapsed_ms,
        }
    )
    return SolverBudget(
        budget.family_id,
        budget.effort_profile,
        tuple(sorted(limits.items())),
    )


def _remaining_phase_budget(
    budget: SolverBudget,
    deadline_at: float,
) -> SolverBudget | None:
    remaining_elapsed_ms = _remaining_deadline_ms(deadline_at)
    if remaining_elapsed_ms <= 0:
        return None
    limits = dict(budget.limits)
    limits["max_closure_elapsed_ms"] = remaining_elapsed_ms
    return SolverBudget(
        budget.family_id,
        budget.effort_profile,
        tuple(sorted(limits.items())),
    )


def _continuous_phase_budget(
    budget: SolverBudget,
    deadline_at: float,
) -> SolverBudget | None:
    phase = _remaining_phase_budget(budget, deadline_at)
    if phase is None:
        return None
    limits = dict(phase.limits)
    available_ms = int(limits["max_closure_elapsed_ms"])
    reserve_ms = min(1_000, max(100, available_ms // 10))
    limits["max_closure_elapsed_ms"] = max(1, available_ms - reserve_ms)
    return SolverBudget(
        budget.family_id,
        budget.effort_profile,
        tuple(sorted(limits.items())),
    )


def _remaining_deadline_ms(deadline_at: float) -> int:
    return max(0, int((deadline_at - perf_counter()) * 1000.0))


def _deadline_reached(deadline_at: float) -> bool:
    return perf_counter() >= deadline_at


def _finalized_plan(
    certified: CertifiedFree3DPlan,
    closure: Free3DClosureResult | GlobalRectangularClosureResult,
    *,
    baseline_closure: Free3DClosureResult | GlobalRectangularClosureResult,
    objective_closure: Free3DClosureResult | GlobalRectangularClosureResult | None,
    objective_attempted: bool,
    objective_certified: bool,
    objective_improved: bool,
    selected_plan_source: str,
    objective_fallback_reason: str,
    source_minimal_artifact_digest: str,
    source_minimal_plan_digest: str,
    budget: SolverBudget,
    reservation_count: int,
    global_deadline_reached: bool,
    composite_closure: XYCompositeClosureResult | None = None,
    continuous_prefill: Free3DClosureResult | None = None,
) -> dict[str, object]:
    plan = deepcopy(certified.plan)
    certificate = certified.certificate
    composite_certificate = (
        _attach_xy_composite_geometry(plan, composite_closure)
        if composite_closure is not None
        else None
    )
    if (
        composite_certificate is not None
        and composite_certificate.get("certified") is not True
    ):
        raise CoupledFinalizationError(
            "Le contrat CAD de la fermeture composite XY est invalide.",
            {
                "schema_version": COUPLED_FINALIZATION_SCHEMA_V1,
                "status": "rejected",
                "stop_reason": "xy_composite_cad_contract_rejected",
                "composite_materialization_certificate": composite_certificate,
                "partial_plan_published": False,
                "materializable": False,
            },
        )
    objective_iterations = objective_closure.iterations if objective_closure is not None else 0
    objective_candidates = (
        objective_closure.candidates_evaluated if objective_closure is not None else 0
    )
    objective_repairs = objective_closure.repair_attempts if objective_closure is not None else 0
    plan["finalization"] = {
        "schema_version": COUPLED_FINALIZATION_SCHEMA_V1,
        "artifact_kind": ARTIFACT_KIND_FINALIZED,
        "policy": COUPLED_FINALIZATION_POLICY,
        "finalizer_id": COUPLED_FINALIZATION_FAMILY_ID,
        "finalizer_version": COUPLED_FINALIZATION_VERSION,
        "source_minimal_artifact_digest": source_minimal_artifact_digest,
        "source_minimal_plan_digest": source_minimal_plan_digest,
        "incumbent_digest": closure.incumbent_digest,
        "closure_digest": (
            composite_closure.deterministic_digest
            if composite_closure is not None
            else closure.deterministic_digest
        ),
        "baseline_closure_digest": baseline_closure.deterministic_digest,
        "xy_composite_closure": (
            xy_composite_closure_to_dict(composite_closure)
            if composite_closure is not None
            else None
        ),
        "continuous_prefill": (
            _continuous_closure_payload(continuous_prefill)
            if continuous_prefill is not None
            else None
        ),
        "composite_materialization_certificate": composite_certificate,
        "objective_closure_digest": (
            objective_closure.deterministic_digest if objective_closure is not None else ""
        ),
        "closure_status": closure.status,
        "global_partition_certificate": deepcopy(
            getattr(closure, "partition_certificate", {})
        ),
        "iterations": baseline_closure.iterations + objective_iterations,
        "candidates_evaluated": (baseline_closure.candidates_evaluated + objective_candidates),
        "repair_attempts": (baseline_closure.repair_attempts + objective_repairs),
        "repairs_applied": (
            baseline_closure.repairs_applied
            + (objective_closure.repairs_applied if objective_closure is not None else 0)
        ),
        "global_resolve_invocation_count": (
            baseline_closure.global_resolve_invocation_count
            + (
                objective_closure.global_resolve_invocation_count
                if objective_closure is not None
                else 0
            )
        ),
        "deadline_reached": bool(
            global_deadline_reached
            or baseline_closure.deadline_reached
            or (objective_closure is not None and objective_closure.deadline_reached)
        ),
        "global_deadline_enforced": True,
        "calculation_budget_independent": True,
        "selected_plan_source": selected_plan_source,
        "secondary_objectives": {
            "schema_version": "bgig.finalization_secondary_objectives.v1",
            "requested": [
                "balanced_added_volume",
                "proportional_expansion",
            ],
            "selection_order": [
                "hard_constraints",
                "complete_residual_closure",
                "balanced_added_volume",
                "proportional_expansion",
            ],
            "attempted": objective_attempted,
            "candidate_certified": objective_certified,
            "strict_improvement": objective_improved,
            "fallback_reason": objective_fallback_reason,
            "baseline_score": _objective_score_payload(baseline_closure.objective_score),
            "candidate_score": (
                _objective_score_payload(objective_closure.objective_score)
                if objective_closure is not None
                else None
            ),
            "selected_score": _objective_score_payload(closure.objective_score),
            "selected_objective_id": closure.selected_objective_id,
            "incumbent_preserved_without_strict_improvement": (not objective_improved),
            "hard_constraints_weakened": False,
            "modular_harmonization_attempted": False,
            "modular_harmonization_status": "deferred",
        },
        "active_top_inset_reservation_count": reservation_count,
        "active_certified_mechanism_envelope_count": 0,
        "budget": {
            "family_id": budget.family_id,
            "effort_profile": budget.effort_profile,
            "limits": dict(budget.limits),
        },
        "certificate": {
            "schema_version": certificate.schema_version,
            "candidate_digest": certificate.candidate_digest,
            "certified": bool(
                certificate.certified
                and (
                    composite_certificate is None
                    or composite_certificate.get("certified") is True
                )
            ),
            "checks": [
                {
                    "name": check.name,
                    "passed": check.passed,
                    "rejection_code": check.rejection_code,
                }
                for check in certificate.checks
            ]
            + (
                [
                    {
                        "name": "xy_composite_partition_and_cad_materialization",
                        "passed": composite_certificate.get("certified") is True,
                        "rejection_code": None,
                    }
                ]
                if composite_certificate is not None
                else []
            ),
        },
    }
    summary = dict(plan["summary"])
    summary["materializable"] = True
    summary["finalization_applied"] = True
    plan["summary"] = summary
    invariants = dict(plan["invariants"])
    invariants.update(
        {
            "minimal_layout": False,
            "residual_distributed": True,
            "continuous_closure_applied": isinstance(
                closure,
                Free3DClosureResult,
            ),
            "global_rectangular_partition_by_construction": not isinstance(
                closure,
                Free3DClosureResult,
            ),
            "rectangular_bodies_only": composite_closure is None,
            "composite_annexes_applied": composite_closure is not None,
            "bounded_local_repair_before_global_resolve": False,
            "global_resolve_invocation_count": (closure.global_resolve_invocation_count),
            "materialization_from_final_certificate_only": True,
            "base_cavity_layouts_fixed": True,
            "secondary_objectives_are_soft": True,
            "f01b_baseline_preserved_without_strict_improvement": True,
            "finishing_budget_independent_from_calculation": True,
            "global_finishing_deadline_enforced": True,
            "minimal_incumbent_preserved_by_value": True,
            "modular_harmonization_applied": False,
        }
    )
    plan["invariants"] = invariants
    plan.pop("minimal_layout", None)
    plan.pop("plan_digest", None)
    plan["plan_digest"] = canonical_digest(plan)
    return plan


def _continuous_closure_payload(
    closure: Free3DClosureResult,
) -> dict[str, object]:
    return {
        "schema_version": FREE_3D_CONTINUOUS_CLOSURE_VERSION,
        "status": closure.status,
        "iterations": closure.iterations,
        "candidates_evaluated": closure.candidates_evaluated,
        "repair_attempts": closure.repair_attempts,
        "repairs_applied": closure.repairs_applied,
        "deadline_reached": closure.deadline_reached,
        "initial_residual_metric": closure.initial_residual_metric,
        "final_residual_metric": closure.final_residual_metric,
        "deterministic_digest": closure.deterministic_digest,
        "vertical_first": True,
    }


def _attach_xy_composite_geometry(
    plan: dict[str, object],
    composite: XYCompositeClosureResult,
) -> dict[str, object]:
    placements = plan.get("placements")
    if not isinstance(placements, list):
        return _rejected_composite_materialization("composite_plan_placements_missing")
    owners = {value.owner_id: value for value in composite.owner_bodies}
    gross_by_id = {
        value.participant_id: value for value in composite.gross_closure.placements
    }
    placement_ids = {
        str(value.get("id", "")) for value in placements if isinstance(value, dict)
    }
    if placement_ids != set(owners) or placement_ids != set(gross_by_id):
        return _rejected_composite_materialization(
            "composite_owner_set_does_not_match_plan"
        )

    total_cad_gross_volume = 0.0
    total_join_count = 0
    for placement in placements:
        if not isinstance(placement, dict):
            return _rejected_composite_materialization(
                "composite_plan_placement_invalid"
            )
        owner_id = str(placement["id"])
        owner = owners[owner_id]
        gross = gross_by_id[owner_id]
        ordered = _ordered_composite_prisms(owner)
        if not ordered:
            return _rejected_composite_materialization(
                "composite_prism_attachment_order_invalid"
            )
        core = ordered[0]
        gross_top = gross.origin_mm[2] + gross.world_size_mm[2]
        core_origin = core.origin_mm
        cad_prisms: list[dict[str, object]] = []
        for prism in ordered:
            cad_height = gross_top - prism.origin_mm[2]
            if cad_height <= 0.0:
                return _rejected_composite_materialization(
                    "composite_cad_prism_height_invalid"
                )
            cad_size = (prism.size_mm[0], prism.size_mm[1], cad_height)
            total_cad_gross_volume += _size_volume(cad_size)
            cad_prisms.append(
                {
                    "prism_id": prism.prism_id,
                    "owner_id": prism.owner_id,
                    "kind": prism.kind,
                    "final_origin_mm": _xyz_payload(prism.origin_mm),
                    "final_size_mm": _xyz_payload(prism.size_mm),
                    "cad_origin_mm": _xyz_payload(prism.origin_mm),
                    "cad_size_mm": _xyz_payload(cad_size),
                    "local_origin_from_core_mm": _xyz_payload(
                        tuple(
                            prism.origin_mm[index] - core_origin[index]
                            for index in range(3)
                        )
                    ),
                    "attached_to_prism_id": prism.attached_to_prism_id,
                    "attachment_axis": prism.attachment_axis,
                }
            )
        total_join_count += max(0, len(cad_prisms) - 1)
        placement["composite_body"] = {
            "schema_version": "bgig.xy_composite_cad_body.v1",
            "policy": "bounded_xy_composite_v1",
            "certified": True,
            "owner_id": owner_id,
            "core_prism_id": owner.core_prism_id,
            "gross_origin_mm": _xyz_payload(gross.origin_mm),
            "gross_size_mm": _xyz_payload(gross.world_size_mm),
            "prisms": cad_prisms,
            "source_owner_certificate": deepcopy(owner.certificate),
            "operation_order": [
                "create_core_prism",
                "join_xy_annexes",
                "subtract_content_cavities",
                "subtract_exact_top_insets",
            ],
        }

    gross_body_volume = float(
        composite.certificate.get("gross_body_volume_mm3", 0.0)
    )
    reserved_volume = float(
        composite.certificate.get("reserved_subtraction_volume_mm3", 0.0)
    )
    composite_volume = float(
        composite.certificate.get("composite_body_volume_mm3", 0.0)
    )
    grip_void_volume = sum(
        _mapping_size_volume(cut.get("size_mm"))
        for placement in placements
        if isinstance(placement, dict)
        for cut in placement.get("top_inset_cuts", [])
        if isinstance(cut, dict) and cut.get("kind") == "top_inset_grip"
    )
    cad_gross_error = abs(total_cad_gross_volume - gross_body_volume)
    final_material_volume = composite_volume - grip_void_volume
    target_material_volume = gross_body_volume - reserved_volume - grip_void_volume
    final_error = abs(final_material_volume - target_material_volume)
    all_top_cuts_are_exact = all(
        isinstance(cut, dict)
        and cut.get("non_perforating") is True
        and str(cut.get("placement_id", "")) == str(placement.get("id", ""))
        for placement in placements
        if isinstance(placement, dict)
        for cut in placement.get("top_inset_cuts", [])
    )
    certified = bool(
        composite.certificate.get("certified") is True
        and cad_gross_error <= max(0.0001, gross_body_volume * 1e-9)
        and final_error <= max(0.0001, gross_body_volume * 1e-9)
        and all_top_cuts_are_exact
    )
    return {
        "schema_version": "bgig.xy_composite_cad_materialization_certificate.v1",
        "certified": certified,
        "owner_count": len(owners),
        "user_component_count": len(owners),
        "joined_annex_count": total_join_count,
        "one_user_component_per_owner": len(owners) == len(placements),
        "joins_precede_cuts": True,
        "all_top_inset_cuts_target_exact_owner_intersections": all_top_cuts_are_exact,
        "gross_body_volume_mm3": round(gross_body_volume, 6),
        "cad_union_gross_volume_mm3": round(total_cad_gross_volume, 6),
        "reserved_subtraction_volume_mm3": round(reserved_volume, 6),
        "certified_grip_technical_void_volume_mm3": round(grip_void_volume, 6),
        "final_material_volume_mm3": round(final_material_volume, 6),
        "coverage_error_mm3": round(final_error, 9),
        "cad_gross_coverage_error_mm3": round(cad_gross_error, 9),
        "printable_residual_volume_mm3": 0.0 if certified else round(final_error, 6),
        "stop_reason": (
            "xy_composite_cad_materialization_certified"
            if certified
            else "xy_composite_cad_materialization_rejected"
        ),
    }


def _ordered_composite_prisms(owner: object) -> tuple[object, ...]:
    prisms = {value.prism_id: value for value in owner.prisms}
    core = prisms.get(owner.core_prism_id)
    if core is None or core.kind != "core":
        return ()
    ordered = [core]
    resolved = {core.prism_id}
    remaining = {
        prism_id: value
        for prism_id, value in prisms.items()
        if prism_id != core.prism_id
    }
    while remaining:
        candidates = sorted(
            (
                value
                for value in remaining.values()
                if value.attached_to_prism_id in resolved
                and value.attachment_axis in {"x", "y"}
            ),
            key=lambda value: value.prism_id,
        )
        if not candidates:
            return ()
        selected = candidates[0]
        ordered.append(selected)
        resolved.add(selected.prism_id)
        remaining.pop(selected.prism_id)
    return tuple(ordered)


def _rejected_composite_materialization(reason: str) -> dict[str, object]:
    return {
        "schema_version": "bgig.xy_composite_cad_materialization_certificate.v1",
        "certified": False,
        "stop_reason": reason,
    }


def _xyz_payload(values: Sequence[float]) -> dict[str, float]:
    return {
        axis: round(float(values[index]), 6)
        for index, axis in enumerate(("x", "y", "z"))
    }


def _size_volume(values: Sequence[float]) -> float:
    return float(values[0]) * float(values[1]) * float(values[2])


def _mapping_size_volume(value: object) -> float:
    if not isinstance(value, Mapping):
        return 0.0
    try:
        return float(value["x"]) * float(value["y"]) * float(value["z"])
    except (KeyError, TypeError, ValueError):
        return 0.0

def _objective_score_payload(
    score: tuple[float, float, float, float],
) -> dict[str, float]:
    return {
        "added_volume_spread_mm3": score[0],
        "added_volume_mean_absolute_deviation_mm3": score[1],
        "expansion_ratio_spread": score[2],
        "expansion_ratio_mean_absolute_deviation": score[3],
    }


def _closure_telemetry(
    closure: Free3DClosureResult | GlobalRectangularClosureResult,
    problem: Free3DPreparedProblem,
    *,
    phase: str,
) -> dict[str, object]:
    return {
        "closure_version": getattr(
            closure,
            "closure_version",
            FREE_3D_CONTINUOUS_CLOSURE_VERSION,
        ),
        "global_rectangular_closure_version": (
            GLOBAL_RECTANGULAR_CLOSURE_VERSION
        ),
        "global_partition_certificate": deepcopy(
            getattr(closure, "partition_certificate", {})
        ),
        "closure_phase": phase,
        "closure_status": closure.status,
        "global_partition_certificate": deepcopy(
            getattr(closure, "partition_certificate", {})
        ),
        "finishing_objective": closure.finishing_objective,
        "objective_score": _objective_score_payload(closure.objective_score),
        "global_partition_certificate": deepcopy(
            getattr(closure, "partition_certificate", {})
        ),
        "objective_candidate_count": closure.objective_candidate_count,
        "selected_objective_id": closure.selected_objective_id,
        "closure_iterations": closure.iterations,
        "closure_candidates_evaluated": closure.candidates_evaluated,
        "closure_repair_attempts": closure.repair_attempts,
        "closure_repairs_applied": closure.repairs_applied,
        "global_resolve_invocation_count": (closure.global_resolve_invocation_count),
        "closure_deadline_reached": closure.deadline_reached,
        "closure_initial_residual_metric": closure.initial_residual_metric,
        "closure_final_residual_metric": closure.final_residual_metric,
        "closure_aligned_face_count": closure.aligned_face_count,
        "active_top_inset_reservation_count": len(problem.top_inset_zones),
        "active_certified_mechanism_envelope_count": 0,
        "admitted_complete_solutions": 1,
        "search_states": closure.iterations,
    }


def _closure_report(
    closure: Free3DClosureResult | GlobalRectangularClosureResult,
    *,
    stop_reason: str,
    rejection_codes: Sequence[str] = (),
    budget: SolverBudget | None = None,
    deadline_reached: bool | None = None,
) -> dict[str, object]:
    report: dict[str, object] = {
        "schema_version": COUPLED_FINALIZATION_SCHEMA_V1,
        "status": "no_solution_within_budget",
        "stop_reason": stop_reason,
        "rejection_codes": list(rejection_codes),
        "partial_plan_published": False,
        "materializable": False,
        "closure_status": closure.status,
        "global_partition_certificate": deepcopy(
            getattr(closure, "partition_certificate", {})
        ),
        "closure_digest": closure.deterministic_digest,
        "incumbent_digest": closure.incumbent_digest,
        "iterations": closure.iterations,
        "candidates_evaluated": closure.candidates_evaluated,
        "repair_attempts": closure.repair_attempts,
        "repairs_applied": closure.repairs_applied,
        "global_resolve_invocation_count": closure.global_resolve_invocation_count,
        "deadline_reached": (
            closure.deadline_reached
            if deadline_reached is None
            else deadline_reached
        ),
        "residual_metric": closure.final_residual_metric,
        "finishing_objective": closure.finishing_objective,
        "objective_score": _objective_score_payload(closure.objective_score),
        "global_partition_certificate": deepcopy(
            getattr(closure, "partition_certificate", {})
        ),
    }
    if budget is not None:
        report["budget"] = {
            "family_id": budget.family_id,
            "effort_profile": budget.effort_profile,
            "limits": dict(budget.limits),
        }
    return report


def _xy_composite_report(
    rectangular: GlobalRectangularClosureResult,
    composite: XYCompositeClosureResult,
    *,
    budget: SolverBudget,
    stop_reason: str,
    rejection_codes: Sequence[str] = (),
) -> dict[str, object]:
    certified = bool(
        composite.status == "closed"
        and composite.certificate.get("certified") is True
    )
    report = _closure_report(
        rectangular,
        stop_reason=stop_reason,
        rejection_codes=rejection_codes,
        budget=budget,
        deadline_reached=bool(
            composite.gross_closure.deadline_reached
            or composite.stop_reason == "xy_composite_deadline_reached"
        ),
    )
    report.update(
        {
            "status": (
                "certified_candidate_not_materializable"
                if certified
                else "no_solution_within_budget"
            ),
            "stop_reason": stop_reason,
            "partial_plan_published": False,
            "materializable": False,
            "composite_candidate_certified": certified,
            "xy_composite_closure": xy_composite_closure_to_dict(composite),
            "cad_ir_union_required": True,
            "reservation_notches_required": True,
        }
    )
    return report

def _deadline_failure_report(
    stop_reason: str,
    budget: SolverBudget,
    rejection_codes: Sequence[str] = (),
) -> dict[str, object]:
    report = _failure_report(stop_reason, rejection_codes)
    report.update(
        {
            "status": "no_solution_within_budget",
            "deadline_reached": True,
            "budget": {
                "family_id": budget.family_id,
                "effort_profile": budget.effort_profile,
                "limits": dict(budget.limits),
            },
        }
    )
    return report


def _failure_report(
    stop_reason: str,
    rejection_codes: Sequence[str],
) -> dict[str, object]:
    return {
        "schema_version": COUPLED_FINALIZATION_SCHEMA_V1,
        "status": "rejected",
        "stop_reason": stop_reason,
        "rejection_codes": list(rejection_codes),
        "partial_plan_published": False,
        "materializable": False,
        "global_resolve_invocation_count": 0,
    }


def _require_certified_minimal(plan: Mapping[str, object]) -> None:
    summary = plan.get("summary")
    minimal = plan.get("minimal_layout")
    if not isinstance(summary, Mapping) or not isinstance(minimal, Mapping):
        raise CoupledFinalizationError(
            "Le plan source n est pas un artefact minimal certifie.",
            _failure_report("minimal_incumbent_not_certified", ()),
        )
    certificate = minimal.get("global_certificate")
    if not (
        summary.get("placement_certified") is True
        and minimal.get("artifact_kind") == "minimal_layout"
        and minimal.get("finalization_applied") is False
        and isinstance(certificate, Mapping)
        and certificate.get("certified") is True
    ):
        raise CoupledFinalizationError(
            "Le plan source n est pas un artefact minimal certifie.",
            _failure_report("minimal_incumbent_not_certified", ()),
        )
