"""Bounded coupled finalization from one certified minimal 3D incumbent.

The finalizer preserves requested bodies and cavity-local geometry. It distributes
printable residual volume through admissible envelope faces, tries bounded local
placement repairs when direct growth stalls, and publishes a plan only after the
shared global product certificate accepts the complete result.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Mapping, Sequence

from board_game_insert_generator.container_variant_global_search import (
    _selected_participants_for_placements,
)
from board_game_insert_generator.free_3d_continuous_closure import (
    FREE_3D_CONTINUOUS_CLOSURE_VERSION,
    Free3DClosureResult,
    close_free_3d_residual,
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


COUPLED_FINALIZATION_SCHEMA_V1 = "bgig.coupled_finalization.v1"
COUPLED_FINALIZATION_FAMILY_ID = "bounded_coupled_finalization"
COUPLED_FINALIZATION_VERSION = "bgig.bounded_coupled_finalization.v1"
COUPLED_FINALIZATION_POLICY = "bounded_growth_then_local_repair"
ARTIFACT_KIND_FINALIZED = "finalized_plan"

_CLOSURE_CAPS = {
    "quick": {
        "max_closure_iterations": 64,
        "max_closure_candidates": 7_500,
        "max_local_repairs": 32,
        "max_closure_elapsed_ms": 5_000,
    },
    "normal": {
        "max_closure_iterations": 128,
        "max_closure_candidates": 37_500,
        "max_local_repairs": 64,
        "max_closure_elapsed_ms": 12_000,
    },
    "deep": {
        "max_closure_iterations": 256,
        "max_closure_candidates": 125_000,
        "max_local_repairs": 128,
        "max_closure_elapsed_ms": 30_000,
    },
}


class CoupledFinalizationError(ValueError):
    """Fail-closed finalization rejection with machine-readable evidence."""

    def __init__(self, message: str, report: Mapping[str, object]) -> None:
        super().__init__(message)
        self.report = deepcopy(dict(report))


def coupled_finalization_budget(effort_profile: str) -> SolverBudget:
    """Return the unique bounded budget shared by closure and repair."""

    if effort_profile not in _CLOSURE_CAPS:
        raise ValueError(f"Unsupported effort profile: {effort_profile}.")
    source = _minimal_budget(effort_profile)
    limits = dict(source.limits)
    limits.update(_CLOSURE_CAPS[effort_profile])
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
    """Close one minimal incumbent and return only a globally certified plan."""

    _require_certified_minimal(minimal_plan)
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

    budget = coupled_finalization_budget(effort_profile)
    closure = close_free_3d_residual(
        participants,
        placements,
        problem.box,
        problem.storage_height_mm,
        problem.xy_clearance_mm,
        box_perimeter_xy_mm=problem.box_xy_clearance_mm,
        between_bodies_z_mm=problem.z_clearance_mm,
        budget=budget,
        top_inset_zones=problem.top_inset_zones,
    )
    if closure.empty_spaces:
        raise CoupledFinalizationError(
            "La fermeture bornee n a pas produit de plan complet certifiable.",
            _closure_report(closure, stop_reason="printable_residual_remains"),
        )

    strategy = SolverStrategy(
        COUPLED_FINALIZATION_FAMILY_ID,
        COUPLED_FINALIZATION_VERSION,
    )
    certified, rejection_codes = certify_free_3d_plan(
        problem,
        strategy=strategy,
        budget=budget,
        candidate_id=(
            f"coupled-finalization:{closure.incumbent_digest[:16]}:"
            f"{closure.deterministic_digest[:16]}"
        ),
        placements=closure.placements,
        search_telemetry=_closure_telemetry(closure, problem),
    )
    if certified is None:
        raise CoupledFinalizationError(
            "Le certificat global final a rejete le plan ferme.",
            _closure_report(
                closure,
                stop_reason="global_certificate_rejected",
                rejection_codes=rejection_codes,
            ),
        )
    return _finalized_plan(
        certified,
        closure,
        source_minimal_artifact_digest=source_minimal_artifact_digest,
        source_minimal_plan_digest=str(minimal_plan.get("plan_digest", "")),
        budget=budget,
        reservation_count=len(problem.top_inset_zones),
    )


def _finalized_plan(
    certified: CertifiedFree3DPlan,
    closure: Free3DClosureResult,
    *,
    source_minimal_artifact_digest: str,
    source_minimal_plan_digest: str,
    budget: SolverBudget,
    reservation_count: int,
) -> dict[str, object]:
    plan = deepcopy(certified.plan)
    certificate = certified.certificate
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
        "closure_status": closure.status,
        "iterations": closure.iterations,
        "candidates_evaluated": closure.candidates_evaluated,
        "repair_attempts": closure.repair_attempts,
        "repairs_applied": closure.repairs_applied,
        "global_resolve_invocation_count": (closure.global_resolve_invocation_count),
        "deadline_reached": closure.deadline_reached,
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
            "continuous_closure_applied": True,
            "bounded_local_repair_before_global_resolve": True,
            "global_resolve_invocation_count": (closure.global_resolve_invocation_count),
            "materialization_from_final_certificate_only": True,
            "base_cavity_layouts_fixed": True,
        }
    )
    plan["invariants"] = invariants
    plan.pop("minimal_layout", None)
    plan.pop("plan_digest", None)
    plan["plan_digest"] = canonical_digest(plan)
    return plan


def _closure_telemetry(
    closure: Free3DClosureResult,
    problem: Free3DPreparedProblem,
) -> dict[str, object]:
    return {
        "closure_version": FREE_3D_CONTINUOUS_CLOSURE_VERSION,
        "closure_status": closure.status,
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
    closure: Free3DClosureResult,
    *,
    stop_reason: str,
    rejection_codes: Sequence[str] = (),
) -> dict[str, object]:
    return {
        "schema_version": COUPLED_FINALIZATION_SCHEMA_V1,
        "status": "no_solution_within_budget",
        "stop_reason": stop_reason,
        "rejection_codes": list(rejection_codes),
        "partial_plan_published": False,
        "materializable": False,
        "closure_status": closure.status,
        "closure_digest": closure.deterministic_digest,
        "incumbent_digest": closure.incumbent_digest,
        "iterations": closure.iterations,
        "candidates_evaluated": closure.candidates_evaluated,
        "repair_attempts": closure.repair_attempts,
        "repairs_applied": closure.repairs_applied,
        "global_resolve_invocation_count": (closure.global_resolve_invocation_count),
        "deadline_reached": closure.deadline_reached,
        "residual_metric": closure.final_residual_metric,
    }


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
