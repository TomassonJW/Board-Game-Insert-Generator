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
from board_game_insert_generator.free_3d_greedy_solver import (
    Free3DPlacement,
    TopInsetZone,
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
from board_game_insert_generator.top_inset_reservation import (
    certify_top_inset_material_fragments,
)


COUPLED_FINALIZATION_SCHEMA_V1 = "bgig.coupled_finalization.v1"
COUPLED_FINALIZATION_FAMILY_ID = "bounded_coupled_finalization"
COUPLED_FINALIZATION_VERSION = "bgig.bounded_coupled_finalization.v13"
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
    """Finish only the exact certified minimal plan selected by the user."""

    budget = coupled_finalization_budget(effort_profile)
    deadline_at = perf_counter() + float(
        dict(budget.limits)["max_total_elapsed_ms"]
    ) / 1000.0
    result = _finalize_coupled_volume_candidate(
        raw_project,
        minimal_plan,
        source_minimal_artifact_digest=source_minimal_artifact_digest,
        effort_profile=effort_profile,
        container_frontiers=container_frontiers,
        _deadline_at=deadline_at,
    )
    finalization = deepcopy(_object_mapping(result.get("finalization")))
    finalization["minimal_candidate_selection"] = {
        "schema_version": "bgig.finalization_minimal_candidate_selection.v2",
        "candidate_pool_count": 1,
        "attempt_count": 1,
        "selected_candidate_index": 0,
        "selected_placement_digest": str(
            minimal_plan.get("plan_digest", "")
        ),
        "selected_lane_id": "selected_minimal_plan",
        "shared_deadline_enforced": True,
        "exact_selected_minimal_plan": True,
        "alternate_candidate_attempted": False,
        "attempts": [
            {
                "candidate_index": 0,
                "placement_digest": str(
                    minimal_plan.get("plan_digest", "")
                ),
                "lane_id": "selected_minimal_plan",
                "status": "solution_found",
                "stop_reason": "selected_minimal_finalization_certified",
            }
        ],
    }
    finalized_plan = result.get("plan")
    if isinstance(finalized_plan, Mapping):
        finalization["final_cavity_anchors"] = deepcopy(
            _object_mapping(finalized_plan.get("cavity_anchor_certificate"))
        )
    result["finalization"] = finalization
    solver = deepcopy(_object_mapping(result.get("solver")))
    telemetry = deepcopy(_object_mapping(solver.get("telemetry")))
    telemetry["minimal_candidate_pool_count"] = 1
    telemetry["minimal_candidate_attempt_count"] = 1
    telemetry["selected_minimal_candidate_index"] = 0
    telemetry["exact_selected_minimal_plan"] = True
    telemetry["alternate_candidate_attempted"] = False
    solver["telemetry"] = telemetry
    result["solver"] = solver
    result.pop("plan_digest", None)
    result["plan_digest"] = canonical_digest(result)
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
    frozen_cavities = _frozen_cavity_contracts(
        minimal_plan,
        placements,
        problem.storage_height_mm,
    )
    finishing_zones = _conservative_closure_guard_zones(
        problem.top_inset_plan,
        problem.storage_height_mm,
    )

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
        top_inset_zones=finishing_zones,
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
            top_inset_zones=finishing_zones,
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
                frozen_cavities=frozen_cavities,
                project=problem.project,
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
            top_inset_zones=finishing_zones,
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
        composite_strategy = SolverStrategy(
            COUPLED_FINALIZATION_FAMILY_ID,
            COUPLED_FINALIZATION_VERSION,
        )
        composite_plan, composite_rejections = certify_free_3d_plan(
            problem,
            strategy=composite_strategy,
            budget=budget,
            candidate_id=(
                "coupled-finalization:"
                "f_xy_composite_v2_union_cavities_insets:"
                f"{composite.deterministic_digest[:12]}"
            ),
            placements=tuple(placements),
            search_telemetry={
                "closure_phase": "f_xy_composite_v2_union_cavities_insets",
                "closure_status": composite.status,
                "closure_digest": composite.deterministic_digest,
                "composite_certificate_schema": composite.certificate.get(
                    "schema_version"
                ),
                "composite_residual_volume_mm3": composite.certificate.get(
                    "printable_residual_volume_mm3"
                ),
            },
            top_inset_mode="reserved_prisms",
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
            selected_plan_source="f_xy_composite_v2_union_cavities_insets",
            objective_fallback_reason="hybrid_composite_closure_required",
            source_minimal_artifact_digest=source_minimal_artifact_digest,
            source_minimal_plan_digest=str(minimal_plan.get("plan_digest", "")),
            budget=budget,
            reservation_count=len(problem.top_inset_zones),
            global_deadline_reached=composite.gross_closure.deadline_reached,
            composite_closure=composite,
            continuous_prefill=continuous,
            frozen_cavities=frozen_cavities,
            project=problem.project,
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
        frozen_cavities=frozen_cavities,
        project=problem.project,
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


def _frozen_cavity_contracts(
    minimal_plan: Mapping[str, object],
    placements: Sequence[Free3DPlacement],
    storage_height_mm: float,
) -> tuple[dict[str, object], ...]:
    """Freeze cavity world poses and protect their vertical removal access."""

    raw_plan_placements = minimal_plan.get("placements", ())
    if not isinstance(raw_plan_placements, (list, tuple)):
        raw_plan_placements = ()
    plan_by_id = {
        str(value["id"]): value
        for value in raw_plan_placements
        if isinstance(value, Mapping)
    }
    contracts: list[dict[str, object]] = []
    for placement in sorted(
        placements,
        key=lambda value: value.participant_id,
    ):
        plan_placement = plan_by_id.get(placement.participant_id)
        if plan_placement is None or placement.role != "container":
            continue
        cavities = plan_placement.get("cavity_layout", ())
        if not isinstance(cavities, (list, tuple)):
            continue
        final_local = plan_placement.get(
            "final_outer_dimensions_mm",
            {},
        )
        minimum_origin = plan_placement.get(
            "minimum_envelope_origin_in_final_mm",
            {},
        )
        if not isinstance(final_local, Mapping) or not isinstance(
            minimum_origin,
            Mapping,
        ):
            continue
        for cavity_index, raw_cavity in enumerate(cavities):
            if not isinstance(raw_cavity, Mapping):
                continue
            raw_origin = raw_cavity.get("local_origin_mm")
            raw_size = raw_cavity.get("inner_dimensions_mm")
            if not isinstance(raw_origin, Mapping) or not isinstance(
                raw_size,
                Mapping,
            ):
                continue
            local_origin = (
                float(minimum_origin["x"]) + float(raw_origin["x"]),
                float(minimum_origin["y"]) + float(raw_origin["y"]),
                float(final_local["z"]) - float(raw_size["z"]),
            )
            local_size = tuple(
                float(raw_size[axis]) for axis in ("x", "y", "z")
            )
            if placement.rotation_deg_z == 0:
                rotated_origin = local_origin
                rotated_size = local_size
            elif placement.rotation_deg_z == 90:
                rotated_origin = (
                    float(final_local["y"])
                    - local_origin[1]
                    - local_size[1],
                    local_origin[0],
                    local_origin[2],
                )
                rotated_size = (
                    local_size[1],
                    local_size[0],
                    local_size[2],
                )
            else:
                raise CoupledFinalizationError(
                    "Une cavite figee utilise une rotation non prise en charge.",
                    _failure_report(
                        "frozen_cavity_rotation_unsupported",
                        ("FROZEN_CAVITY_ROTATION_UNSUPPORTED",),
                    ),
                )
            world_origin = tuple(
                placement.origin_mm[axis] + rotated_origin[axis]
                for axis in range(3)
            )
            cavity_top = world_origin[2] + rotated_size[2]
            source_top = (
                placement.origin_mm[2] + placement.world_size_mm[2]
            )
            if abs(cavity_top - source_top) > 0.001:
                raise CoupledFinalizationError(
                    "La pose minimale d une cavite n est pas ouverte sur le dessus.",
                    _failure_report(
                        "frozen_cavity_not_top_open",
                        ("FROZEN_CAVITY_NOT_TOP_OPEN",),
                    ),
                )
            access_height = max(0.0, storage_height_mm - cavity_top)
            access_zone = TopInsetZone(
                origin_xy_mm=(world_origin[0], world_origin[1]),
                size_xy_mm=(rotated_size[0], rotated_size[1]),
                support_plane_z_mm=cavity_top,
                inset_depth_mm=access_height,
            )
            identity = {
                "owner_id": placement.participant_id,
                "cavity_index": cavity_index,
                "world_origin_mm": _xyz_payload(world_origin),
                "world_size_mm": _xyz_payload(rotated_size),
                "source_owner_origin_mm": _xyz_payload(
                    placement.origin_mm
                ),
                "source_owner_world_size_mm": _xyz_payload(
                    placement.world_size_mm
                ),
                "source_rotation_deg_z": placement.rotation_deg_z,
            }
            contracts.append(
                {
                    **identity,
                    "cavity_key": (
                        str(
                            raw_cavity.get(
                                "cavity_id",
                                (
                                    f"{placement.participant_id}:"
                                    f"cavity:{cavity_index:04d}"
                                ),
                            )
                        )
                    ),
                    "pose_digest": canonical_digest(identity),
                    "top_open": True,
                    "access_zone": access_zone,
                }
            )
    return tuple(contracts)


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


def _conservative_closure_guard_zones(
    top_inset_plan: Mapping[str, object],
    design_top_z: float,
) -> tuple[TopInsetZone, ...]:
    """Reserve the exact union of the local flat-item stack regions.

    Several reservations may describe the same atomic XY cell because each
    item keeps its own Z interval.  The closure only needs the union void for
    that cell, so the deepest local bottom is retained once.  Disjoint
    footprints consequently never inherit an artificial cumulative depth.
    """

    reservations = [
        value
        for value in top_inset_plan.get("reservations", ())
        if isinstance(value, Mapping)
    ]
    atomic_regions: dict[
        tuple[float, float, float, float],
        float,
    ] = {}
    for reservation in reservations:
        raw_regions = reservation.get("local_depth_regions", ())
        regions = (
            tuple(
                value
                for value in raw_regions
                if isinstance(value, Mapping)
            )
            if isinstance(raw_regions, (list, tuple))
            else ()
        )
        if not regions:
            regions = (reservation,)
        for region in regions:
            origin = _object_mapping(
                region.get(
                    "cut_origin_mm",
                    reservation["cut_origin_mm"],
                )
            )
            size = _object_mapping(
                region.get(
                    "cut_size_mm",
                    reservation["cut_size_mm"],
                )
            )
            key = (
                round(float(origin["x"]), 6),
                round(float(origin["y"]), 6),
                round(float(size["x"]), 6),
                round(float(size["y"]), 6),
            )
            layer_bottom = float(
                region.get(
                    "layer_bottom_z_mm",
                    design_top_z
                    - float(reservation["inset_depth_from_top_mm"]),
                )
            )
            atomic_regions[key] = min(
                layer_bottom,
                atomic_regions.get(key, design_top_z),
            )
    return tuple(
        TopInsetZone(
            origin_xy_mm=(key[0], key[1]),
            size_xy_mm=(key[2], key[3]),
            support_plane_z_mm=round(layer_bottom, 6),
            inset_depth_mm=round(design_top_z - layer_bottom, 6),
        )
        for key, layer_bottom in sorted(atomic_regions.items())
    )


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
    frozen_cavities: Sequence[Mapping[str, object]] = (),
    project: Mapping[str, object],
) -> dict[str, object]:
    plan = deepcopy(certified.plan)
    certificate = certified.certificate
    composite_certificate = (
        _attach_xy_composite_geometry(
            plan,
            composite_closure,
            frozen_cavities=frozen_cavities,
            project=project,
        )
        if composite_closure is not None
        else None
    )
    cavity_anchor_certificate = (
        composite_certificate.get("cavity_anchor_certificate")
        if isinstance(composite_certificate, Mapping)
        else _attach_rectangular_cavity_anchors(
            plan,
            frozen_cavities=frozen_cavities,
            project=project,
        )
    )
    if (
        not isinstance(cavity_anchor_certificate, Mapping)
        or cavity_anchor_certificate.get("certified") is not True
    ):
        raise CoupledFinalizationError(
            "L ancrage final des cavites calibrees est invalide.",
            {
                "schema_version": COUPLED_FINALIZATION_SCHEMA_V1,
                "status": "rejected",
                "stop_reason": "final_cavity_anchor_certificate_rejected",
                "cavity_anchor_certificate": cavity_anchor_certificate,
                "partial_plan_published": False,
                "materializable": False,
            },
        )
    if (
        composite_certificate is not None
        and composite_certificate.get("certified") is not True
    ):
        rejection_subcodes = composite_certificate.get(
            "rejection_subcodes",
            (),
        )
        raise CoupledFinalizationError(
            "Le contrat CAD de la fermeture composite XY est invalide.",
            {
                "schema_version": COUPLED_FINALIZATION_SCHEMA_V1,
                "status": "rejected",
                "stop_reason": "xy_composite_cad_contract_rejected",
                "composite_materialization_certificate": composite_certificate,
                "rejection_subcodes": list(rejection_subcodes)
                if isinstance(rejection_subcodes, (list, tuple))
                else [],
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
        "cavity_anchor_certificate": deepcopy(
            cavity_anchor_certificate
        ),
        "frozen_cavities": [
            {
                key: deepcopy(value[key])
                for key in (
                    "cavity_key",
                    "owner_id",
                    "cavity_index",
                    "world_origin_mm",
                    "world_size_mm",
                    "source_owner_origin_mm",
                    "source_owner_world_size_mm",
                    "source_rotation_deg_z",
                    "pose_digest",
                    "top_open",
                )
            }
            for value in frozen_cavities
        ],
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
                and cavity_anchor_certificate.get("certified") is True
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
            )
            + [
                {
                    "name": "final_cavity_calibration_and_z_anchors",
                    "passed": (
                        cavity_anchor_certificate.get("certified") is True
                    ),
                    "rejection_code": None,
                }
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
            "continuous_closure_applied": bool(
                isinstance(closure, Free3DClosureResult)
                or continuous_prefill is not None
            ),
            "global_rectangular_partition_by_construction": bool(
                not isinstance(closure, Free3DClosureResult)
                and not (
                    composite_closure is not None
                    and composite_closure.certificate.get("source_mode")
                    == "continuous_prefill_residual_cells"
                )
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
            "cavity_xy_pose_orientation_and_dimensions_frozen": True,
            "cavity_final_z_anchor_resolved": True,
            "cavity_calibrated_depths_unchanged": (
                cavity_anchor_certificate.get(
                    "calibrated_depths_unchanged"
                )
                is True
            ),
            "cavity_vertical_access_protected": False,
            "closure_search_guard_is_conservative_not_cad_geometry": True,
            "final_top_inset_geometry_uses_local_regions": True,
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
    *,
    frozen_cavities: Sequence[Mapping[str, object]],
    project: Mapping[str, object],
) -> dict[str, object]:
    placements = plan.get("placements")
    if not isinstance(placements, list):
        return _rejected_composite_materialization("composite_plan_placements_missing")
    owners = {value.owner_id: value for value in composite.owner_bodies}
    placement_ids = {
        str(value.get("id", "")) for value in placements if isinstance(value, dict)
    }
    if placement_ids != set(owners):
        return _rejected_composite_materialization(
            "composite_owner_set_does_not_match_plan"
        )
    top_insets = plan.get("top_inset_reservations")
    if not isinstance(top_insets, Mapping):
        return _rejected_composite_materialization(
            "composite_top_inset_contract_missing"
        )
    raw_reservations = top_insets.get("reservations", ())
    if not isinstance(raw_reservations, (list, tuple)):
        return _rejected_composite_materialization(
            "composite_top_inset_reservations_invalid"
        )
    reservations = tuple(
        value for value in raw_reservations if isinstance(value, Mapping)
    )
    design_top = float(top_insets.get("design_top_z_mm", 0.0))
    frozen_by_owner: dict[str, list[Mapping[str, object]]] = {}
    for value in frozen_cavities:
        frozen_by_owner.setdefault(str(value["owner_id"]), []).append(value)

    total_cad_union_volume = 0.0
    total_final_composite_volume = 0.0
    total_content_cavity_volume = 0.0
    total_cut_volume = 0.0
    total_cut_intersection_with_final = 0.0
    total_join_count = 0
    total_cavity_access_required = 0
    all_owners_connected = True
    all_frozen_calibrations_match = True
    all_cavity_access_open = True
    all_reservation_walls_certified = all(
        isinstance(value.get("wall_envelope_certificate"), Mapping)
        and value["wall_envelope_certificate"].get("certified") is True
        and value["wall_envelope_certificate"].get("cavities_unchanged") is True
        for value in reservations
    )
    minimum_wall = float(
        _mapping_value(
            _mapping_value(project, "layout"),
            "default_wall_thickness_mm",
        )
    )
    final_material_envelope_certificate = (
        certify_top_inset_material_fragments(
            list(reservations),
            _composite_owner_material_envelopes(owners),
            minimum_wall_mm=minimum_wall,
        )
    )
    all_final_material_fragments_certified = bool(
        final_material_envelope_certificate["certified"]
    )
    for placement in placements:
        if not isinstance(placement, dict):
            return _rejected_composite_materialization(
                "composite_plan_placement_invalid"
            )
        owner_id = str(placement["id"])
        owner = owners[owner_id]
        source_placement_origin = tuple(
            float(_mapping_value(placement["origin_mm"], axis))
            for axis in ("x", "y", "z")
        )
        source_placement_size = tuple(
            float(_mapping_value(placement["world_size_mm"], axis))
            for axis in ("x", "y", "z")
        )
        owner_frozen = frozen_by_owner.get(owner_id, [])
        total_content_cavity_volume += sum(
            _mapping_size_volume(value["world_size_mm"])
            for value in owner_frozen
        )
        cells = _split_composite_owner_prisms(
            owner,
            reservations,
            owner_frozen,
        )
        ordered = _ordered_composite_cad_cells(owner, cells)
        if not ordered:
            return _rejected_composite_materialization(
                "composite_prism_attachment_order_invalid"
            )
        core = ordered[0]
        core_origin = core["final_origin_mm"]
        cad_prisms: list[dict[str, object]] = []
        placement_cuts: list[dict[str, object]] = []
        placement_access_cuts: list[dict[str, object]] = []
        for prism_index, prism in enumerate(ordered):
            final_origin = prism["final_origin_mm"]
            final_size = prism["final_size_mm"]
            selected_reservation = _deepest_reservation_at_cell(
                final_origin,
                final_size,
                reservations,
                kind="footprint",
            )
            final_top = final_origin[2] + final_size[2]
            cad_top = final_top
            if (
                selected_reservation is not None
                and abs(
                    final_top
                    - float(
                        selected_reservation["support_plane_z_mm"]
                    )
                )
                <= 0.0001
            ):
                cad_top = max(cad_top, design_top)
            cad_size = (
                final_size[0],
                final_size[1],
                cad_top - final_origin[2],
            )
            if min(cad_size) <= 0.0:
                return _rejected_composite_materialization(
                    "composite_cad_prism_height_invalid"
                )
            total_cad_union_volume += _size_volume(cad_size)
            total_final_composite_volume += _size_volume(final_size)
            cad_prisms.append(
                {
                    "prism_id": prism["prism_id"],
                    "owner_id": owner_id,
                    "kind": "core" if prism_index == 0 else "annex",
                    "final_origin_mm": _xyz_payload(final_origin),
                    "final_size_mm": _xyz_payload(final_size),
                    "cad_origin_mm": _xyz_payload(final_origin),
                    "cad_size_mm": _xyz_payload(cad_size),
                    "local_origin_from_core_mm": _xyz_payload(
                        tuple(
                            final_origin[index] - core_origin[index]
                            for index in range(3)
                        )
                    ),
                    "attached_to_prism_id": prism["attached_to_prism_id"],
                    "attachment_axis": prism["attachment_axis"],
                }
            )
            cuts = _composite_cell_cuts(
                owner_id,
                prism["prism_id"],
                final_origin,
                final_size,
                cad_size,
                reservations,
                design_top,
                source_placement_origin,
                owner_frozen,
            )
            for cut in cuts:
                cut_volume = _mapping_size_volume(cut["size_mm"])
                total_cut_volume += cut_volume
                total_cut_intersection_with_final += (
                    _cut_intersection_with_final_volume(
                        cut,
                        final_origin,
                        final_size,
                    )
                )
                placement_cuts.append(cut)
        total_join_count += max(0, len(cad_prisms) - 1)
        all_owners_connected = bool(
            all_owners_connected
            and len(cad_prisms) == 1 + max(0, len(cad_prisms) - 1)
            and all(
                value["kind"] == "core"
                or (
                    value["attached_to_prism_id"]
                    and value["attachment_axis"] in {"x", "y"}
                )
                for value in cad_prisms
            )
        )
        for cavity in owner_frozen:
            expected_origin = tuple(
                float(_mapping_value(cavity["source_owner_origin_mm"], axis))
                for axis in ("x", "y", "z")
            )
            raw_cavities = placement.get("cavity_layout", ())
            cavity_index = int(cavity["cavity_index"])
            raw_cavity = (
                raw_cavities[cavity_index]
                if isinstance(raw_cavities, (list, tuple))
                and 0 <= cavity_index < len(raw_cavities)
                and isinstance(raw_cavities[cavity_index], Mapping)
                else None
            )
            raw_size = (
                tuple(
                    float(
                        _mapping_value(
                            raw_cavity["inner_dimensions_mm"],
                            axis,
                        )
                    )
                    for axis in ("x", "y", "z")
                )
                if raw_cavity is not None
                else ()
            )
            expected_cavity_size = tuple(
                float(_mapping_value(cavity["world_size_mm"], axis))
                for axis in ("x", "y", "z")
            )
            if (
                raw_size
                and int(placement.get("rotation_deg_z", 0)) == 90
            ):
                raw_size = (raw_size[1], raw_size[0], raw_size[2])
            all_frozen_calibrations_match = bool(
                all_frozen_calibrations_match
                and _tuple_close(
                    source_placement_origin[:2],
                    expected_origin[:2],
                )
                and bool(raw_size)
                and _tuple_close(raw_size, expected_cavity_size)
                and int(placement.get("rotation_deg_z", 0))
                == int(cavity["source_rotation_deg_z"])
            )
        component_origin = tuple(
            min(
                float(_mapping_value(value["cad_origin_mm"], axis))
                for value in cad_prisms
            )
            for axis in ("x", "y", "z")
        )
        component_upper = tuple(
            max(
                float(_mapping_value(value["cad_origin_mm"], axis))
                + float(_mapping_value(value["cad_size_mm"], axis))
                for value in cad_prisms
            )
            for axis in ("x", "y", "z")
        )
        component_size = tuple(
            component_upper[index] - component_origin[index]
            for index in range(3)
        )
        for cut in (*placement_cuts, *placement_access_cuts):
            world_origin = tuple(
                float(_mapping_value(cut["world_origin_mm"], axis))
                for axis in ("x", "y", "z")
            )
            cut["local_origin_mm"] = _xyz_payload(
                tuple(
                    world_origin[index] - component_origin[index]
                    for index in range(3)
                )
            )
            cut["retained_body_below_mm"] = round(
                world_origin[2] - component_origin[2],
                6,
            )
        placement["origin_mm"] = _xyz_payload(component_origin)
        placement["world_size_mm"] = _xyz_payload(component_size)
        rotation = int(placement.get("rotation_deg_z", 0))
        placement["final_outer_dimensions_mm"] = _xyz_payload(
            (
                component_size[0],
                component_size[1],
                component_size[2],
            )
            if rotation == 0
            else (
                component_size[1],
                component_size[0],
                component_size[2],
            )
        )
        placement["composite_bounds_v2"] = {
            "semantics": "bounding_box_not_solid",
            "origin_mm": _xyz_payload(component_origin),
            "size_mm": _xyz_payload(component_size),
            "source_minimum_origin_mm": _xyz_payload(
                source_placement_origin
            ),
            "source_minimum_size_mm": _xyz_payload(
                source_placement_size
            ),
        }
        placement["top_inset_cuts"] = placement_cuts
        anchor_certificate = _resolve_final_cavity_contracts(
            placement,
            owner_frozen,
            placement_cuts,
            project=project,
            cad_prisms=cad_prisms,
        )
        if anchor_certificate.get("certified") is not True:
            return _rejected_composite_materialization(
                "composite_final_cavity_anchor_rejected"
            )
        placement["frozen_cavities_v1"] = deepcopy(
            anchor_certificate["cavities"]
        )
        access_result = _build_frozen_cavity_access_cuts(
            owner_id,
            cad_prisms,
            placement_cuts,
            placement["frozen_cavities_v1"],
            component_origin,
        )
        placement_access_cuts = list(access_result["cuts"])
        total_cavity_access_required += int(
            access_result["required_count"]
        )
        all_cavity_access_open = bool(
            all_cavity_access_open
            and access_result.get("certified") is True
            and len(placement_access_cuts)
            == int(access_result["required_count"])
        )
        prisms_by_id = {
            str(value["prism_id"]): value for value in cad_prisms
        }
        for cut in placement_access_cuts:
            target_prism = prisms_by_id[str(cut["target_prism_id"])]
            cut_volume = _mapping_size_volume(cut["size_mm"])
            total_cut_volume += cut_volume
            total_cut_intersection_with_final += (
                _cut_intersection_with_final_volume(
                    cut,
                    tuple(
                        float(
                            _mapping_value(
                                target_prism["final_origin_mm"],
                                axis,
                            )
                        )
                        for axis in ("x", "y", "z")
                    ),
                    tuple(
                        float(
                            _mapping_value(
                                target_prism["final_size_mm"],
                                axis,
                            )
                        )
                        for axis in ("x", "y", "z")
                    ),
                )
            )
        composite_body = {
            "schema_version": "bgig.xy_composite_cad_body.v2",
            "policy": "hybrid_xy_composite_v2",
            "certified": True,
            "owner_id": owner_id,
            "core_prism_id": cad_prisms[0]["prism_id"],
            "prisms": cad_prisms,
            "source_owner_certificate": deepcopy(owner.certificate),
            "source_composite_digest": composite.deterministic_digest,
            "frozen_cavity_pose_digests": [
                str(value["pose_digest"])
                for value in placement["frozen_cavities_v1"]
            ],
            "frozen_cavity_access_cuts": placement_access_cuts,
            "operation_order": [
                "create_core_prism",
                "join_xy_annexes",
                "subtract_content_cavities",
                "subtract_frozen_cavity_access",
                "subtract_exact_top_insets",
            ],
        }
        composite_body["geometry_digest"] = canonical_digest(
            composite_body
        )
        placement["composite_body"] = composite_body

    certified_composite_volume = float(
        composite.certificate.get("composite_body_volume_mm3", 0.0)
    )
    composite_source_error = abs(
        total_final_composite_volume - certified_composite_volume
    )
    total_all_cut_volume = (
        total_content_cavity_volume + total_cut_volume
    )
    final_material_volume = (
        total_cad_union_volume - total_all_cut_volume
    )
    target_material_volume = (
        total_final_composite_volume
        - total_content_cavity_volume
        - total_cut_intersection_with_final
    )
    final_error = abs(final_material_volume - target_material_volume)
    additive_above_final_volume = (
        total_cad_union_volume - total_final_composite_volume
    )
    cut_above_final_volume = (
        total_cut_volume - total_cut_intersection_with_final
    )
    additive_above_final_residual = abs(
        additive_above_final_volume - cut_above_final_volume
    )
    material_volume_tolerance = max(
        0.0001,
        certified_composite_volume * 1e-9,
    )
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
        and composite.certificate.get("printable_residual_volume_mm3") == 0.0
        and composite_source_error
        <= max(0.0001, certified_composite_volume * 1e-9)
        and final_error
        <= material_volume_tolerance
        and additive_above_final_residual
        <= material_volume_tolerance
        and all_top_cuts_are_exact
        and all_owners_connected
        and all_frozen_calibrations_match
        and all_cavity_access_open
        and all_reservation_walls_certified
        and all_final_material_fragments_certified
    )
    rejection_subcodes = [
        code
        for passed, code in (
            (
                composite.certificate.get("certified") is True
                and composite.certificate.get(
                    "printable_residual_volume_mm3"
                )
                == 0.0,
                "COMPOSITE_SOURCE_CERTIFICATE_REJECTED",
            ),
            (
                composite_source_error
                <= max(0.0001, certified_composite_volume * 1e-9),
                "COMPOSITE_SOURCE_VOLUME_DIVERGENCE",
            ),
            (
                final_error
                <= material_volume_tolerance,
                "COMPOSITE_CAD_FINAL_VOLUME_DIVERGENCE",
            ),
            (
                additive_above_final_residual
                <= material_volume_tolerance,
                "COMPOSITE_ADDITIVE_ABOVE_FINAL_RESIDUAL",
            ),
            (all_top_cuts_are_exact, "COMPOSITE_TOP_CUT_INVALID"),
            (all_owners_connected, "COMPOSITE_OWNER_UNION_DISCONNECTED"),
            (
                all_frozen_calibrations_match,
                "COMPOSITE_CAVITY_CALIBRATION_DIVERGENCE",
            ),
            (
                all_cavity_access_open,
                "COMPOSITE_CAVITY_VERTICAL_ACCESS_UNCERTIFIED",
            ),
            (
                all_reservation_walls_certified,
                "COMPOSITE_RESERVATION_WALL_UNCERTIFIED",
            ),
            (
                all_final_material_fragments_certified,
                "COMPOSITE_FINAL_MATERIAL_FRAGMENT_UNCERTIFIED",
            ),
        )
        if not passed
    ]
    return {
        "schema_version": "bgig.xy_composite_cad_materialization_certificate.v2",
        "certified": certified,
        "owner_count": len(owners),
        "user_component_count": len(owners),
        "joined_annex_count": total_join_count,
        "one_user_component_per_owner": len(owners) == len(placements),
        "joins_precede_cuts": True,
        "cavities_precede_top_inset_cuts": True,
        "owner_unions_connected": all_owners_connected,
        "cavity_calibrations_match_source_contract": (
            all_frozen_calibrations_match
        ),
        "cavity_vertical_access_open": all_cavity_access_open,
        "cavity_vertical_access_required_count": (
            total_cavity_access_required
        ),
        "cavity_anchor_certificate": _aggregate_cavity_anchor_certificates(
            placements
        ),
        "minimum_reservation_wall_certified": all_reservation_walls_certified,
        "final_material_fragments_certified": (
            all_final_material_fragments_certified
        ),
        "final_material_envelope_certificate": (
            final_material_envelope_certificate
        ),
        "all_top_inset_cuts_target_exact_owner_intersections": all_top_cuts_are_exact,
        "source_composite_volume_mm3": round(
            certified_composite_volume,
            6,
        ),
        "cad_union_before_cuts_volume_mm3": round(
            total_cad_union_volume,
            6,
        ),
        "exact_cut_volume_mm3": round(total_all_cut_volume, 6),
        "content_cavity_cut_volume_mm3": round(
            total_content_cavity_volume,
            6,
        ),
        "access_and_top_cut_volume_mm3": round(
            total_cut_volume,
            6,
        ),
        "cut_intersection_with_final_volume_mm3": round(
            total_cut_intersection_with_final,
            6,
        ),
        "additive_above_final_volume_mm3": round(
            additive_above_final_volume,
            6,
        ),
        "cut_above_final_volume_mm3": round(
            cut_above_final_volume,
            6,
        ),
        "additive_above_final_residual_volume_mm3": (
            0.0
            if additive_above_final_residual
            <= material_volume_tolerance
            else round(additive_above_final_residual, 6)
        ),
        "no_additive_volume_above_final_bodies": (
            additive_above_final_residual
            <= material_volume_tolerance
        ),
        "final_material_volume_mm3": round(final_material_volume, 6),
        "coverage_error_mm3": round(final_error, 9),
        "source_composite_coverage_error_mm3": round(
            composite_source_error,
            9,
        ),
        "printable_residual_volume_mm3": 0.0 if certified else round(final_error, 6),
        "source_composite_digest": composite.deterministic_digest,
        "rejection_subcodes": rejection_subcodes,
        "stop_reason": (
            "xy_composite_cad_materialization_certified"
            if certified
            else "xy_composite_cad_materialization_rejected"
        ),
    }


def _attach_rectangular_cavity_anchors(
    plan: dict[str, object],
    *,
    frozen_cavities: Sequence[Mapping[str, object]],
    project: Mapping[str, object],
) -> dict[str, object]:
    placements = plan.get("placements")
    if not isinstance(placements, list):
        return {
            "schema_version": "bgig.final_cavity_anchor_certificate.v1",
            "certified": False,
            "rejection_codes": ["FINAL_PLACEMENTS_MISSING"],
            "cavities": [],
        }
    frozen_by_owner: dict[str, list[Mapping[str, object]]] = {}
    for value in frozen_cavities:
        frozen_by_owner.setdefault(str(value["owner_id"]), []).append(value)
    for placement in placements:
        if not isinstance(placement, dict) or placement.get("role") != "container":
            continue
        certificate = _resolve_final_cavity_contracts(
            placement,
            frozen_by_owner.get(str(placement["id"]), ()),
            tuple(
                value
                for value in placement.get("top_inset_cuts", ())
                if isinstance(value, Mapping)
            ),
            project=project,
            cad_prisms=None,
        )
        if certificate.get("certified") is not True:
            return certificate
        placement["frozen_cavities_v1"] = deepcopy(
            certificate["cavities"]
        )
    return _aggregate_cavity_anchor_certificates(placements)


def _resolve_final_cavity_contracts(
    placement: Mapping[str, object],
    frozen_cavities: Sequence[Mapping[str, object]],
    top_inset_cuts: Sequence[Mapping[str, object]],
    *,
    project: Mapping[str, object],
    cad_prisms: Sequence[Mapping[str, object]] | None,
) -> dict[str, object]:
    owner_id = str(placement["id"])
    owner_origin = tuple(
        float(_mapping_value(placement["origin_mm"], axis))
        for axis in ("x", "y", "z")
    )
    owner_size = tuple(
        float(_mapping_value(placement["world_size_mm"], axis))
        for axis in ("x", "y", "z")
    )
    _, floor = _resolved_owner_wall_and_floor(project, placement)
    contracts: list[dict[str, object]] = []
    rejection_codes: list[str] = []
    for source in sorted(
        frozen_cavities,
        key=lambda value: int(value["cavity_index"]),
    ):
        source_origin = tuple(
            float(_mapping_value(source["world_origin_mm"], axis))
            for axis in ("x", "y", "z")
        )
        calibrated_size = tuple(
            float(_mapping_value(source["world_size_mm"], axis))
            for axis in ("x", "y", "z")
        )
        cavity_rect = (
            source_origin[0],
            source_origin[1],
            source_origin[0] + calibrated_size[0],
            source_origin[1] + calibrated_size[1],
        )
        functional_top = _functional_top_at_cavity(
            cavity_rect,
            owner_origin,
            owner_size,
            cad_prisms,
        )
        overlapping_cuts = [
            value
            for value in top_inset_cuts
            if value.get("kind") == "top_inset"
            and _rectangles_overlap(
                cavity_rect,
                _world_xy_rectangle(value),
            )
        ]
        overlapping_cuts = [
            value
            for value in overlapping_cuts
            if float(
                _mapping_value(value["world_origin_mm"], "z")
            )
            < owner_origin[2] + owner_size[2] - 0.0001
        ]
        responsible: Mapping[str, object] | None = None
        if overlapping_cuts:
            responsible = min(
                overlapping_cuts,
                key=lambda value: (
                    float(_mapping_value(value["world_origin_mm"], "z")),
                    str(value.get("reservation_id", "")),
                    str(value.get("local_region_id", "")),
                ),
            )
            cut_bottom = float(
                _mapping_value(responsible["world_origin_mm"], "z")
            )
            # The removable flat item closes the cavity while installed.  Its
            # localized inset and the calibrated cavity are therefore one
            # continuous void: printable wall material must not be inserted
            # between their two matching Z planes.
            cavity_top = cut_bottom
            anchor_kind = "below_top_inset"
            separation = 0.0
            top_interface_kind = "direct_void_to_removable_top_inset"
        else:
            cavity_top = functional_top
            anchor_kind = "open_top"
            separation = 0.0
            top_interface_kind = "open_functional_face"
        final_origin = (
            source_origin[0],
            source_origin[1],
            cavity_top - calibrated_size[2],
        )
        retained_floor = final_origin[2] - owner_origin[2]
        calibrated_depth = calibrated_size[2]
        anchor_certified = bool(
            min(calibrated_size) > 0.0
            and retained_floor + 0.0001 >= floor
            and final_origin[2] >= owner_origin[2] - 0.0001
            and cavity_top
            <= owner_origin[2] + owner_size[2] + 0.0001
        )
        if not anchor_certified:
            rejection_codes.append(
                "FINAL_CAVITY_FLOOR_OR_TOP_CLEARANCE_FAILED"
            )
        identity = {
            "owner_id": owner_id,
            "cavity_index": int(source["cavity_index"]),
            "world_origin_mm": _xyz_payload(final_origin),
            "world_size_mm": _xyz_payload(calibrated_size),
            "source_owner_origin_mm": deepcopy(
                source["source_owner_origin_mm"]
            ),
            "source_owner_world_size_mm": deepcopy(
                source["source_owner_world_size_mm"]
            ),
            "source_rotation_deg_z": int(
                source["source_rotation_deg_z"]
            ),
            "minimum_world_origin_mm": deepcopy(
                source["world_origin_mm"]
            ),
            "minimum_world_size_mm": deepcopy(source["world_size_mm"]),
            "final_owner_origin_mm": _xyz_payload(owner_origin),
            "final_owner_world_size_mm": _xyz_payload(owner_size),
            "anchor_kind": anchor_kind,
            "responsible_reservation_id": (
                str(responsible.get("reservation_id", ""))
                if responsible is not None
                else ""
            ),
            "responsible_local_region_id": (
                str(responsible.get("local_region_id", ""))
                if responsible is not None
                else ""
            ),
            "calibrated_depth_source_mm": round(calibrated_depth, 6),
            "calibrated_depth_final_mm": round(calibrated_depth, 6),
            "retained_floor_mm": round(retained_floor, 6),
            "minimum_floor_mm": round(floor, 6),
            "top_separation_mm": round(separation, 6),
            "minimum_top_separation_mm": 0.0,
            "intermediate_material_thickness_mm": 0.0,
            "top_interface_kind": top_interface_kind,
            "top_void_continuity_certified": True,
            "functional_top_z_mm": round(functional_top, 6),
            "functional_top_access_certified": bool(
                anchor_kind != "open_top"
                or abs(cavity_top - functional_top) <= 0.0001
            ),
        }
        contracts.append(
            {
                **identity,
                "cavity_key": str(source["cavity_key"]),
                "pose_digest": canonical_digest(identity),
                "top_open": anchor_kind == "open_top",
                "anchor_certified": anchor_certified,
                "calibrated_dimensions_unchanged": True,
                "xy_pose_unchanged": True,
                "orientation_unchanged": True,
            }
        )
    return {
        "schema_version": "bgig.final_cavity_anchor_certificate.v1",
        "certified": not rejection_codes,
        "owner_id": owner_id,
        "cavity_count": len(contracts),
        "open_top_count": sum(
            value["anchor_kind"] == "open_top" for value in contracts
        ),
        "below_top_inset_count": sum(
            value["anchor_kind"] == "below_top_inset"
            for value in contracts
        ),
        "direct_top_inset_void_count": sum(
            value["top_interface_kind"]
            == "direct_void_to_removable_top_inset"
            for value in contracts
        ),
        "top_void_continuity_certified": all(
            value["top_void_continuity_certified"]
            for value in contracts
        ),
        "calibrated_depths_unchanged": all(
            value["calibrated_depth_source_mm"]
            == value["calibrated_depth_final_mm"]
            for value in contracts
        ),
        "rejection_codes": sorted(set(rejection_codes)),
        "cavities": contracts,
    }


def _aggregate_cavity_anchor_certificates(
    placements: Sequence[Mapping[str, object]],
) -> dict[str, object]:
    cavities = [
        value
        for placement in placements
        for value in placement.get("frozen_cavities_v1", ())
        if isinstance(value, Mapping)
    ]
    return {
        "schema_version": "bgig.final_cavity_anchor_certificate.v1",
        "certified": all(
            value.get("anchor_certified") is True
            and value.get("calibrated_dimensions_unchanged") is True
            for value in cavities
        ),
        "cavity_count": len(cavities),
        "open_top_count": sum(
            value.get("anchor_kind") == "open_top" for value in cavities
        ),
        "below_top_inset_count": sum(
            value.get("anchor_kind") == "below_top_inset"
            for value in cavities
        ),
        "direct_top_inset_void_count": sum(
            value.get("top_interface_kind")
            == "direct_void_to_removable_top_inset"
            for value in cavities
        ),
        "top_void_continuity_certified": all(
            value.get("top_void_continuity_certified") is True
            for value in cavities
        ),
        "calibrated_depths_unchanged": all(
            value.get("calibrated_depth_source_mm")
            == value.get("calibrated_depth_final_mm")
            for value in cavities
        ),
        "cavities": deepcopy(cavities),
        "rejection_codes": [],
    }


def _resolved_owner_wall_and_floor(
    project: Mapping[str, object],
    placement: Mapping[str, object],
) -> tuple[float, float]:
    layout = project.get("layout")
    if not isinstance(layout, Mapping):
        raise CoupledFinalizationError(
            "Les epaisseurs canoniques du projet sont absentes.",
            _failure_report(
                "canonical_thicknesses_missing",
                ("CANONICAL_THICKNESSES_MISSING",),
            ),
        )
    wall = float(layout["default_wall_thickness_mm"])
    floor = float(layout["default_floor_thickness_mm"])
    group_id = str(placement.get("container_group_id", ""))
    raw_groups = project.get("container_groups", ())
    if isinstance(raw_groups, (list, tuple)):
        for group in raw_groups:
            if not isinstance(group, Mapping) or str(group.get("id")) != group_id:
                continue
            if group.get("wall_thickness_mm") is not None:
                wall = float(group["wall_thickness_mm"])
            if group.get("floor_thickness_mm") is not None:
                floor = float(group["floor_thickness_mm"])
            break
    return wall, floor


def _functional_top_at_cavity(
    cavity_rect: Sequence[float],
    owner_origin: Sequence[float],
    owner_size: Sequence[float],
    cad_prisms: Sequence[Mapping[str, object]] | None,
) -> float:
    if not cad_prisms:
        return owner_origin[2] + owner_size[2]
    tops = [
        float(_mapping_value(value["cad_origin_mm"], "z"))
        + float(_mapping_value(value["cad_size_mm"], "z"))
        for value in cad_prisms
        if _rectangles_overlap(
            cavity_rect,
            _mapping_xy_rectangle(
                value["cad_origin_mm"],
                value["cad_size_mm"],
            ),
        )
    ]
    return max(tops, default=owner_origin[2] + owner_size[2])


def _mapping_xy_rectangle(
    origin: object,
    size: object,
) -> tuple[float, float, float, float]:
    if not isinstance(origin, Mapping) or not isinstance(size, Mapping):
        return (0.0, 0.0, 0.0, 0.0)
    x0, y0 = float(origin["x"]), float(origin["y"])
    return (x0, y0, x0 + float(size["x"]), y0 + float(size["y"]))


def _world_xy_rectangle(
    value: Mapping[str, object],
) -> tuple[float, float, float, float]:
    return _mapping_xy_rectangle(
        value["world_origin_mm"],
        value["size_mm"],
    )


def _rectangles_overlap(
    left: Sequence[float],
    right: Sequence[float],
) -> bool:
    return bool(
        left[0] < right[2] - 0.0001
        and right[0] < left[2] - 0.0001
        and left[1] < right[3] - 0.0001
        and right[1] < left[3] - 0.0001
    )


def _composite_owner_material_envelopes(
    owners: Mapping[str, object],
) -> list[dict[str, object]]:
    envelopes: list[dict[str, object]] = []
    for owner_id, owner in sorted(owners.items()):
        prisms = tuple(owner.prisms)
        if not prisms:
            continue
        min_x = min(float(prism.origin_mm[0]) for prism in prisms)
        min_y = min(float(prism.origin_mm[1]) for prism in prisms)
        max_x = max(
            float(prism.origin_mm[0] + prism.size_mm[0])
            for prism in prisms
        )
        max_y = max(
            float(prism.origin_mm[1] + prism.size_mm[1])
            for prism in prisms
        )
        envelopes.append(
            {
                "material_id": owner_id,
                "x": min_x,
                "y": min_y,
                "width": max_x - min_x,
                "height": max_y - min_y,
            }
        )
    return envelopes


def _split_composite_owner_prisms(
    owner: object,
    reservations: Sequence[Mapping[str, object]],
    frozen_cavities: Sequence[Mapping[str, object]],
) -> tuple[dict[str, object], ...]:
    cells: list[dict[str, object]] = []
    for prism in owner.prisms:
        x0, y0, z0 = prism.origin_mm
        x1 = x0 + prism.size_mm[0]
        y1 = y0 + prism.size_mm[1]
        xs = {x0, x1}
        ys = {y0, y1}
        for reservation in reservations:
            local_regions = reservation.get(
                "local_depth_regions",
                (),
            )
            local_rectangles = [
                _mapping_xy_rectangle(
                    value["cut_origin_mm"],
                    value["cut_size_mm"],
                )
                for value in local_regions
                if isinstance(value, Mapping)
                and _z_intervals_overlap(
                    z0,
                    z0 + prism.size_mm[2],
                    float(value["layer_bottom_z_mm"]),
                    float(value["layer_top_z_mm"]),
                )
            ]
            design_top = float(
                reservation["support_plane_z_mm"]
            ) + float(reservation["inset_depth_from_top_mm"])
            grip_bottom = design_top - float(
                reservation["total_thickness_mm"]
            )
            grip_rectangles = (
                [_reservation_rectangle(reservation, "grip")]
                if _z_intervals_overlap(
                    z0,
                    z0 + prism.size_mm[2],
                    grip_bottom,
                    design_top,
                )
                else []
            )
            for rect in (*local_rectangles, *grip_rectangles):
                rx0, ry0, rx1, ry1 = rect
                if rx0 < x1 - 0.0001 and x0 < rx1 - 0.0001:
                    xs.update({max(x0, rx0), min(x1, rx1)})
                if ry0 < y1 - 0.0001 and y0 < ry1 - 0.0001:
                    ys.update({max(y0, ry0), min(y1, ry1)})
        ordered_x = sorted(xs)
        ordered_y = sorted(ys)
        for x_index in range(len(ordered_x) - 1):
            for y_index in range(len(ordered_y) - 1):
                cell_x0, cell_x1 = (
                    ordered_x[x_index],
                    ordered_x[x_index + 1],
                )
                cell_y0, cell_y1 = (
                    ordered_y[y_index],
                    ordered_y[y_index + 1],
                )
                if (
                    cell_x1 - cell_x0 <= 0.0001
                    or cell_y1 - cell_y0 <= 0.0001
                ):
                    continue
                cells.append(
                    {
                        "final_origin_mm": (
                            cell_x0,
                            cell_y0,
                            z0,
                        ),
                        "final_size_mm": (
                            cell_x1 - cell_x0,
                            cell_y1 - cell_y0,
                            prism.size_mm[2],
                        ),
                    }
                )
    return tuple(
        sorted(
            cells,
            key=lambda value: (
                *value["final_origin_mm"],
                *value["final_size_mm"],
            ),
        )
    )


def _z_intervals_overlap(
    left_bottom: float,
    left_top: float,
    right_bottom: float,
    right_top: float,
) -> bool:
    return (
        left_bottom < right_top - 0.0001
        and right_bottom < left_top - 0.0001
    )


def _ordered_composite_cad_cells(
    owner: object,
    cells: Sequence[Mapping[str, object]],
) -> tuple[dict[str, object], ...]:
    if not cells:
        return ()
    source = owner.source_placement
    source_center = tuple(
        source.origin_mm[index] + source.world_size_mm[index] / 2.0
        for index in range(3)
    )
    core_index = max(
        range(len(cells)),
        key=lambda index: (
            _point_inside_prism_xy(source_center, cells[index]),
            _prism_overlap_volume_with_placement(cells[index], source),
            _size_volume(cells[index]["final_size_mm"]),
            tuple(-value for value in cells[index]["final_origin_mm"]),
        ),
    )
    remaining = set(range(len(cells)))
    remaining.remove(core_index)
    resolved = {core_index}
    ordered_indexes = [core_index]
    parents: dict[int, tuple[int, str]] = {}
    while remaining:
        options: list[tuple[int, int, str]] = []
        for child_index in sorted(remaining):
            for parent_index in sorted(resolved):
                axis = _cad_cell_vertical_face_axis(
                    cells[parent_index],
                    cells[child_index],
                )
                if axis:
                    options.append((child_index, parent_index, axis))
        if not options:
            return ()
        child_index, parent_index, axis = min(options)
        parents[child_index] = (parent_index, axis)
        resolved.add(child_index)
        remaining.remove(child_index)
        ordered_indexes.append(child_index)
    prism_ids = {
        cell_index: f"{owner.owner_id}:cad-prism:{order:04d}"
        for order, cell_index in enumerate(ordered_indexes)
    }
    result: list[dict[str, object]] = []
    for order, cell_index in enumerate(ordered_indexes):
        value = cells[cell_index]
        parent = parents.get(cell_index)
        result.append(
            {
                **dict(value),
                "prism_id": prism_ids[cell_index],
                "attached_to_prism_id": (
                    prism_ids[parent[0]] if parent is not None else ""
                ),
                "attachment_axis": parent[1] if parent is not None else "",
                "kind": "core" if order == 0 else "annex",
            }
        )
    return tuple(result)


def _composite_cell_cuts(
    owner_id: str,
    prism_id: str,
    final_origin: Sequence[float],
    final_size: Sequence[float],
    cad_size: Sequence[float],
    reservations: Sequence[Mapping[str, object]],
    design_top: float,
    owner_origin: Sequence[float],
    frozen_cavities: Sequence[Mapping[str, object]],
) -> tuple[dict[str, object], ...]:
    cuts: list[dict[str, object]] = []
    footprints = _reservations_at_cell(
        final_origin,
        final_size,
        reservations,
        kind="footprint",
    )
    selected: list[tuple[str, Mapping[str, object]]] = []
    if footprints:
        selected.extend(
            ("top_inset", reservation)
            for reservation in footprints
        )
    else:
        grip = _deepest_reservation_at_cell(
            final_origin,
            final_size,
            reservations,
            kind="grip",
        )
        if grip is not None:
            selected.append(("top_inset_grip", grip))
    cad_top = final_origin[2] + cad_size[2]
    for cut_index, (kind, reservation) in enumerate(selected):
        local_region = reservation.get("local_region")
        if kind == "top_inset" and isinstance(
            local_region,
            Mapping,
        ):
            cut_bottom = float(local_region["layer_bottom_z_mm"])
            cut_top = float(local_region["layer_top_z_mm"])
        else:
            cut_bottom = design_top - float(
                reservation["inset_depth_from_top_mm"]
            )
            cut_top = cad_top
        reservation_id = str(reservation["id"])
        flat_item_id = str(reservation["flat_item_id"])
        removal_order = int(reservation["removal_order"])
        cut_bottom = max(float(final_origin[2]), cut_bottom)
        cut_top = min(cad_top, cut_top)
        if cut_top <= cut_bottom + 0.0001:
            continue
        cut_size_z = cut_top - cut_bottom
        world_origin = (
            final_origin[0],
            final_origin[1],
            cut_bottom,
        )
        size = (
            final_size[0],
            final_size[1],
            cut_size_z,
        )
        cuts.append(
            {
                "id": (
                    f"{reservation_id}:{owner_id}:{prism_id}:"
                    f"{kind}:{cut_index}"
                ),
                "kind": kind,
                "reservation_id": reservation_id,
                "flat_item_id": flat_item_id,
                "placement_id": owner_id,
                "local_region_id": str(
                    reservation.get("local_region_id", "")
                ),
                "overlapping_reservation_ids": deepcopy(
                    (
                        reservation.get("local_region", {}).get(
                            "overlapping_reservation_ids",
                            [reservation_id],
                        )
                        if isinstance(
                            reservation.get("local_region"),
                            Mapping,
                        )
                        else [reservation_id]
                    )
                ),
                "removal_order": removal_order,
                "world_origin_mm": _xyz_payload(world_origin),
                "local_origin_mm": _xyz_payload(
                    tuple(
                        world_origin[index] - owner_origin[index]
                        for index in range(3)
                    )
                ),
                "size_mm": _xyz_payload(size),
                "retained_body_below_mm": round(
                    cut_bottom - final_origin[2],
                    6,
                ),
                "minimum_floor_mm": 0.0,
                "cavity_overlap_area_mm2": 0.0,
                "local_interval_z_mm": {
                    "bottom": round(cut_bottom, 6),
                    "top": round(cut_top, 6),
                },
                "non_perforating": cut_bottom
                >= final_origin[2] - 0.0001,
                "target_prism_id": prism_id,
            }
        )
    return tuple(cuts)


def _build_frozen_cavity_access_cuts(
    owner_id: str,
    cad_prisms: Sequence[Mapping[str, object]],
    top_inset_cuts: Sequence[Mapping[str, object]],
    frozen_cavities: Sequence[Mapping[str, object]],
    component_origin: Sequence[float],
) -> dict[str, object]:
    """Open only the cavity footprint between its top and the local free face.

    A cavity may be lowered as a whole because one part lies under a removable
    tray.  Every other XY part must still reach either its own local top face or
    the bottom of another local inset.  These access cuts remove only the
    cavity footprint; the surrounding canonical walls remain printable.
    """

    cuts: list[dict[str, object]] = []
    required_count = 0
    for prism in cad_prisms:
        prism_id = str(prism["prism_id"])
        prism_origin = tuple(
            float(_mapping_value(prism["cad_origin_mm"], axis))
            for axis in ("x", "y", "z")
        )
        prism_size = tuple(
            float(_mapping_value(prism["cad_size_mm"], axis))
            for axis in ("x", "y", "z")
        )
        prism_rect = (
            prism_origin[0],
            prism_origin[1],
            prism_origin[0] + prism_size[0],
            prism_origin[1] + prism_size[1],
        )
        local_opening_top = prism_origin[2] + prism_size[2]
        matching_top_cuts = [
            value
            for value in top_inset_cuts
            if str(value.get("target_prism_id", "")) == prism_id
            and value.get("kind") in {"top_inset", "top_inset_grip"}
        ]
        if matching_top_cuts:
            local_opening_top = min(
                float(_mapping_value(value["world_origin_mm"], "z"))
                for value in matching_top_cuts
            )
        for cavity in frozen_cavities:
            cavity_origin = tuple(
                float(_mapping_value(cavity["world_origin_mm"], axis))
                for axis in ("x", "y", "z")
            )
            cavity_size = tuple(
                float(_mapping_value(cavity["world_size_mm"], axis))
                for axis in ("x", "y", "z")
            )
            cavity_rect = (
                cavity_origin[0],
                cavity_origin[1],
                cavity_origin[0] + cavity_size[0],
                cavity_origin[1] + cavity_size[1],
            )
            intersection = _rectangle_intersection(
                prism_rect,
                cavity_rect,
            )
            if intersection is None:
                continue
            access_bottom = max(
                prism_origin[2],
                cavity_origin[2] + cavity_size[2],
            )
            access_top = min(
                prism_origin[2] + prism_size[2],
                local_opening_top,
            )
            if access_top <= access_bottom + 0.0001:
                continue
            required_count += 1
            world_origin = (
                intersection[0],
                intersection[1],
                access_bottom,
            )
            size = (
                intersection[2] - intersection[0],
                intersection[3] - intersection[1],
                access_top - access_bottom,
            )
            cavity_key = str(cavity["cavity_key"])
            cuts.append(
                {
                    "id": (
                        f"{cavity_key}:{owner_id}:{prism_id}:"
                        f"frozen_cavity_access:{len(cuts)}"
                    ),
                    "kind": "frozen_cavity_access",
                    "reservation_id": cavity_key,
                    "flat_item_id": "",
                    "placement_id": owner_id,
                    "removal_order": -1,
                    "world_origin_mm": _xyz_payload(world_origin),
                    "local_origin_mm": _xyz_payload(
                        tuple(
                            world_origin[index] - component_origin[index]
                            for index in range(3)
                        )
                    ),
                    "size_mm": _xyz_payload(size),
                    "retained_body_below_mm": round(
                        access_bottom - prism_origin[2],
                        6,
                    ),
                    "minimum_floor_mm": 0.0,
                    "cavity_overlap_area_mm2": round(
                        size[0] * size[1],
                        6,
                    ),
                    "local_interval_z_mm": {
                        "bottom": round(access_bottom, 6),
                        "top": round(access_top, 6),
                    },
                    "non_perforating": True,
                    "target_prism_id": prism_id,
                }
            )
    return {
        "certified": len(cuts) == required_count,
        "required_count": required_count,
        "cuts": tuple(cuts),
    }


def _rectangle_intersection(
    left: Sequence[float],
    right: Sequence[float],
) -> tuple[float, float, float, float] | None:
    intersection = (
        max(left[0], right[0]),
        max(left[1], right[1]),
        min(left[2], right[2]),
        min(left[3], right[3]),
    )
    if (
        intersection[2] - intersection[0] <= 0.0001
        or intersection[3] - intersection[1] <= 0.0001
    ):
        return None
    return intersection


def _frozen_access_at_cell(
    origin: Sequence[float],
    size: Sequence[float],
    frozen_cavities: Sequence[Mapping[str, object]],
) -> Mapping[str, object] | None:
    center = (
        origin[0] + size[0] / 2.0,
        origin[1] + size[1] / 2.0,
    )
    candidates: list[Mapping[str, object]] = []
    for value in frozen_cavities:
        zone = value.get("access_zone")
        if not isinstance(zone, TopInsetZone):
            continue
        rectangle = (
            zone.origin_xy_mm[0],
            zone.origin_xy_mm[1],
            zone.origin_xy_mm[0] + zone.size_xy_mm[0],
            zone.origin_xy_mm[1] + zone.size_xy_mm[1],
        )
        if _point_in_rectangle(center, rectangle):
            candidates.append(value)
    if not candidates:
        return None
    return min(
        candidates,
        key=lambda value: (
            float(
                value["access_zone"].support_plane_z_mm
            ),
            str(value["cavity_key"]),
        ),
    )


def _deepest_reservation_at_cell(
    origin: Sequence[float],
    size: Sequence[float],
    reservations: Sequence[Mapping[str, object]],
    *,
    kind: str,
) -> Mapping[str, object] | None:
    candidates = _reservations_at_cell(
        origin,
        size,
        reservations,
        kind=kind,
    )
    return candidates[0] if candidates else None


def _reservations_at_cell(
    origin: Sequence[float],
    size: Sequence[float],
    reservations: Sequence[Mapping[str, object]],
    *,
    kind: str,
) -> tuple[Mapping[str, object], ...]:
    center = (
        origin[0] + size[0] / 2.0,
        origin[1] + size[1] / 2.0,
    )
    candidates: list[Mapping[str, object]] = []
    for value in reservations:
        if kind != "footprint":
            if _point_in_rectangle(
                center,
                _reservation_rectangle(value, kind),
            ):
                candidates.append(value)
            continue
        raw_regions = value.get("local_depth_regions", ())
        if not isinstance(raw_regions, (list, tuple)):
            raw_regions = ()
        matched = False
        for raw_region in raw_regions:
            if not isinstance(raw_region, Mapping):
                continue
            raw_origin = raw_region.get("cut_origin_mm")
            raw_size = raw_region.get("cut_size_mm")
            if not isinstance(raw_origin, Mapping) or not isinstance(
                raw_size,
                Mapping,
            ):
                continue
            rectangle = (
                float(raw_origin["x"]),
                float(raw_origin["y"]),
                float(raw_origin["x"]) + float(raw_size["x"]),
                float(raw_origin["y"]) + float(raw_size["y"]),
            )
            if _point_in_rectangle(center, rectangle):
                candidates.append(
                    {
                        **dict(value),
                        "support_plane_z_mm": float(
                            raw_region["layer_bottom_z_mm"]
                        ),
                        "inset_depth_from_top_mm": float(
                            raw_region["inset_depth_from_top_mm"]
                        ),
                        "local_region_id": str(raw_region["id"]),
                        "local_region": deepcopy(dict(raw_region)),
                    }
                )
                matched = True
                break
        if (
            not matched
            and not raw_regions
            and _point_in_rectangle(
                center,
                _reservation_rectangle(value, kind),
            )
        ):
            candidates.append(value)
    if not candidates:
        return ()
    return tuple(sorted(
        candidates,
        key=lambda value: (
            float(value["support_plane_z_mm"]),
            str(value["id"]),
        ),
    ))


def _reservation_rectangle(
    reservation: Mapping[str, object],
    kind: str,
) -> tuple[float, float, float, float]:
    if kind == "footprint":
        raw_origin = reservation["cut_origin_mm"]
        raw_size = reservation["cut_size_mm"]
    elif kind == "grip":
        grip = reservation["grip_zone"]
        if not isinstance(grip, Mapping):
            return (0.0, 0.0, 0.0, 0.0)
        raw_origin = grip["origin_mm"]
        raw_size = grip["size_mm"]
    else:
        raise ValueError(f"Unknown reservation rectangle kind: {kind}.")
    if not isinstance(raw_origin, Mapping) or not isinstance(
        raw_size,
        Mapping,
    ):
        return (0.0, 0.0, 0.0, 0.0)
    x0 = float(raw_origin["x"])
    y0 = float(raw_origin["y"])
    return (
        x0,
        y0,
        x0 + float(raw_size["x"]),
        y0 + float(raw_size["y"]),
    )


def _point_in_rectangle(
    point: Sequence[float],
    rectangle: Sequence[float],
) -> bool:
    return bool(
        rectangle[0] - 0.0001 <= point[0] <= rectangle[2] + 0.0001
        and rectangle[1] - 0.0001 <= point[1] <= rectangle[3] + 0.0001
    )


def _cad_cell_vertical_face_axis(
    left: Mapping[str, object],
    right: Mapping[str, object],
) -> str:
    left_origin = left["final_origin_mm"]
    left_size = left["final_size_mm"]
    right_origin = right["final_origin_mm"]
    right_size = right["final_size_mm"]
    for axis in (0, 1):
        orthogonal = 1 - axis
        face_contact = bool(
            abs(
                left_origin[axis]
                + left_size[axis]
                - right_origin[axis]
            )
            <= 0.0001
            or abs(
                right_origin[axis]
                + right_size[axis]
                - left_origin[axis]
            )
            <= 0.0001
        )
        overlap_orthogonal = min(
            left_origin[orthogonal] + left_size[orthogonal],
            right_origin[orthogonal] + right_size[orthogonal],
        ) - max(left_origin[orthogonal], right_origin[orthogonal])
        overlap_z = min(
            left_origin[2] + left_size[2],
            right_origin[2] + right_size[2],
        ) - max(left_origin[2], right_origin[2])
        if face_contact and overlap_orthogonal > 0.0001 and overlap_z > 0.0001:
            return "x" if axis == 0 else "y"
    return ""


def _point_inside_prism_xy(
    point: Sequence[float],
    prism: Mapping[str, object],
) -> bool:
    origin = prism["final_origin_mm"]
    size = prism["final_size_mm"]
    return bool(
        origin[0] - 0.0001 <= point[0] <= origin[0] + size[0] + 0.0001
        and origin[1] - 0.0001 <= point[1] <= origin[1] + size[1] + 0.0001
    )


def _prism_overlap_volume_with_placement(
    prism: Mapping[str, object],
    placement: Free3DPlacement,
) -> float:
    origin = prism["final_origin_mm"]
    size = prism["final_size_mm"]
    volume = 1.0
    for axis in range(3):
        lower = max(origin[axis], placement.origin_mm[axis])
        upper = min(
            origin[axis] + size[axis],
            placement.origin_mm[axis] + placement.world_size_mm[axis],
        )
        volume *= max(0.0, upper - lower)
    return volume


def _cut_intersection_with_final_volume(
    cut: Mapping[str, object],
    final_origin: Sequence[float],
    final_size: Sequence[float],
) -> float:
    cut_origin = tuple(
        float(_mapping_value(cut["world_origin_mm"], axis))
        for axis in ("x", "y", "z")
    )
    cut_size = tuple(
        float(_mapping_value(cut["size_mm"], axis))
        for axis in ("x", "y", "z")
    )
    volume = 1.0
    for axis in range(3):
        lower = max(cut_origin[axis], final_origin[axis])
        upper = min(
            cut_origin[axis] + cut_size[axis],
            final_origin[axis] + final_size[axis],
        )
        volume *= max(0.0, upper - lower)
    return volume


def _mapping_value(value: object, key: str) -> object:
    if not isinstance(value, Mapping):
        raise TypeError(f"Expected mapping for {key}.")
    return value[key]


def _tuple_close(
    left: Sequence[float],
    right: Sequence[float],
) -> bool:
    return all(
        abs(float(left[index]) - float(right[index])) <= 0.0001
        for index in range(len(left))
    )


def _rejected_composite_materialization(reason: str) -> dict[str, object]:
    return {
        "schema_version": "bgig.xy_composite_cad_materialization_certificate.v2",
        "certified": False,
        "rejection_subcodes": [
            "COMPOSITE_CAD_CONTRACT_"
            + reason.upper().replace("-", "_")
        ],
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
