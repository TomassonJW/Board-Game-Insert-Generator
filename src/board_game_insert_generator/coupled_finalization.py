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
    FREE_3D_CONTINUOUS_CLOSURE_VERSION,
    Free3DClosureResult,
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
)
from board_game_insert_generator.solver_contract import SolverBudget, SolverStrategy
from board_game_insert_generator.solver_settings import solver_deadline_seconds


COUPLED_FINALIZATION_SCHEMA_V1 = "bgig.coupled_finalization.v1"
COUPLED_FINALIZATION_FAMILY_ID = "bounded_coupled_finalization"
COUPLED_FINALIZATION_VERSION = "bgig.bounded_coupled_finalization.v5"
COUPLED_FINALIZATION_POLICY = "global_rectangular_then_bounded_xy_composite"
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


def finalize_coupled_volume(
    raw_project: object,
    minimal_plan: Mapping[str, object],
    *,
    source_minimal_artifact_digest: str,
    effort_profile: str,
    container_frontiers: Sequence[object] = (),
) -> dict[str, object]:
    """Finish one minimal incumbent under one independent total deadline."""

    started = perf_counter()
    budget = coupled_finalization_budget(effort_profile)
    deadline_at = started + float(
        dict(budget.limits)["max_total_elapsed_ms"]
    ) / 1000.0
    _require_certified_minimal(minimal_plan)
    if _deadline_reached(deadline_at):
        raise CoupledFinalizationError(
            "La deadline totale est atteinte avant la preparation de la finition.",
            _deadline_failure_report(
                "global_deadline_reached_before_preparation",
                budget,
            ),
        )

    preparation = prepare_free_3d_problem(raw_project)
    if preparation.problem is None:
        raise CoupledFinalizationError(
            "Le probleme produit ne peut pas etre prepare pour la finalisation.",
            _failure_report(
                "input_validation_failed",
                preparation.rejection_codes,
            ),
        )
    problem = preparation.problem
    if container_frontiers:
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
        )
        composite_certified = bool(
            composite.status == "closed"
            and composite.certificate.get("certified") is True
        )
        if composite_certified:
            raise CoupledFinalizationError(
                "La fermeture composite XY est certifiee et attend sa traduction CAD IR.",
                _xy_composite_report(
                    closure,
                    composite,
                    budget=budget,
                    stop_reason="xy_composite_candidate_ready_for_cad_ir",
                ),
            )
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
) -> dict[str, object]:
    plan = deepcopy(certified.plan)
    certificate = certified.certificate
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
        "closure_digest": closure.deterministic_digest,
        "baseline_closure_digest": baseline_closure.deterministic_digest,
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
            "certified": certificate.certified,
            "checks": [
                {
                    "name": check.name,
                    "passed": check.passed,
                    "rejection_code": check.rejection_code,
                }
                for check in certificate.checks
            ],
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
            "continuous_closure_applied": False,
            "global_rectangular_partition_by_construction": True,
            "rectangular_bodies_only": True,
            "composite_annexes_applied": False,
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
) -> dict[str, object]:
    certified = bool(
        composite.status == "closed"
        and composite.certificate.get("certified") is True
    )
    report = _closure_report(
        rectangular,
        stop_reason=stop_reason,
        budget=budget,
        deadline_reached=bool(composite.gross_closure.deadline_reached),
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
