"""Bounded multi-seed solver for P64 minimal-layout artifacts.

Only certified minimum envelopes are placed. Remaining box volume stays
unassigned. Finalization, CAD, Fusion, and scene mutation are out of scope.
Historical EMS lanes remain isolated comparators; their public APIs and budgets
are unchanged.
"""

from __future__ import annotations

from collections import Counter
from copy import deepcopy
from dataclasses import dataclass, replace
from typing import Callable, Iterable, Mapping, Sequence

from board_game_insert_generator.container_internal_variants import (
    ContainerVariantFrontier,
    INTERNAL_VARIANT_SCHEMA_V1,
    InternalVariantRun,
    derive_container_internal_variant_frontiers,
    internal_variant_run_to_dict,
    variant_budget_for_effort,
)
from board_game_insert_generator.container_variant_global_search import (
    _participants_with_variant_options,
    _variant_beam_budget,
)
from board_game_insert_generator.free_3d_beam_solver import (
    BEAM_SEARCH_BRIDGE_EMS,
    BEAM_SEARCH_INTERNAL_VARIANTS,
    BEAM_SEARCH_LEGACY_EMS,
    PROPAGATION_INWARD_CONTACT,
    PROPAGATION_LONG_AXIS_SPINE,
    PROPAGATION_LOWEST_SUPPORTED_SURFACE,
    PROPAGATION_RADIAL_COMPACT,
    Free3DBeamExecution,
    Free3DPlacement,
    VariantFree3DPlacement,
    solve_free_3d_beam,
)
from board_game_insert_generator.free_3d_greedy_solver import (
    EmptySpace,
    _Counters,
    _subtract_placement_from_spaces,
)
from board_game_insert_generator.free_3d_plan_adapter import (
    MINIMAL_LAYOUT_ARTIFACT_SCHEMA_V1,
    CertifiedFree3DPlan,
    Free3DPreparedProblem,
    certify_minimal_free_3d_plan,
    prepare_free_3d_problem,
)
from board_game_insert_generator.incremental_project_state import canonical_digest
from board_game_insert_generator.partition_solver import (
    PARTITION_PLAN_SCHEMA_V1,
    _digest,
    _mapping,
    _round,
)
from board_game_insert_generator.solver_contract import SolverBudget, SolverStrategy
from board_game_insert_generator.solver_outcome import (
    INVALID_INPUT,
    NO_SOLUTION_WITHIN_BUDGET,
    SOLVER_RESULT_SCHEMA_V1,
    SOLVER_TELEMETRY_SCHEMA_V1,
    STALE_OR_CANCELLED,
    result_label,
)
from board_game_insert_generator.solver_portfolio import (
    EFFORT_DEEP,
    EFFORT_NORMAL,
    EFFORT_QUICK,
    portfolio_effort_profiles,
)


MINIMAL_LAYOUT_FAMILY_ID = "minimal_layout_portfolio"
MINIMAL_LAYOUT_SOLVER_VERSION = "p64-l03r-b-v1"
MINIMAL_LAYOUT_PORTFOLIO_SCHEMA_V1 = "bgig.minimal_layout_portfolio.v1"
_AXES = ("x", "y", "z")
_EPSILON = 0.0001


@dataclass(frozen=True)
class MinimalLaneSpec:
    """One deterministic portfolio lane observable without running it."""

    lane_id: str
    order_id: str
    anchor_id: str
    propagation_id: str
    search_variant: str
    seed_rank: int


@dataclass(frozen=True)
class _CertifiedProposal:
    lane: MinimalLaneSpec
    seed_participant_id: str
    translation_id: str
    placements: tuple[Free3DPlacement, ...]
    empty_spaces: tuple[EmptySpace, ...]
    certified: CertifiedFree3DPlan
    rank_key: tuple[object, ...]


_LANES = (
    MinimalLaneSpec(
        "historical_legacy_corner",
        "placement_rarity",
        "compact_corner",
        PROPAGATION_INWARD_CONTACT,
        BEAM_SEARCH_LEGACY_EMS,
        0,
    ),
    MinimalLaneSpec(
        "historical_bridge_edge",
        "axis_pressure",
        "aligned_edge",
        PROPAGATION_LONG_AXIS_SPINE,
        BEAM_SEARCH_BRIDGE_EMS,
        0,
    ),
    MinimalLaneSpec(
        "variant_corner_long_side",
        "long_side_xy",
        "compact_corner",
        PROPAGATION_INWARD_CONTACT,
        BEAM_SEARCH_INTERNAL_VARIANTS,
        0,
    ),
    MinimalLaneSpec(
        "variant_center_footprint",
        "footprint_xy",
        "compact_center",
        PROPAGATION_RADIAL_COMPACT,
        BEAM_SEARCH_INTERNAL_VARIANTS,
        0,
    ),
    MinimalLaneSpec(
        "variant_lowest_height",
        "height",
        "lowest_surface",
        PROPAGATION_LOWEST_SUPPORTED_SURFACE,
        BEAM_SEARCH_INTERNAL_VARIANTS,
        0,
    ),
    MinimalLaneSpec(
        "variant_edge_interleave",
        "interleave_extremes",
        "aligned_edge",
        PROPAGATION_LONG_AXIS_SPINE,
        BEAM_SEARCH_INTERNAL_VARIANTS,
        1,
    ),
    MinimalLaneSpec(
        "variant_center_volume",
        "volume",
        "compact_center",
        PROPAGATION_RADIAL_COMPACT,
        BEAM_SEARCH_INTERNAL_VARIANTS,
        1,
    ),
    MinimalLaneSpec(
        "variant_lowest_rarity",
        "placement_rarity",
        "lowest_surface",
        PROPAGATION_LOWEST_SUPPORTED_SURFACE,
        BEAM_SEARCH_INTERNAL_VARIANTS,
        2,
    ),
    MinimalLaneSpec(
        "variant_edge_pressure",
        "axis_pressure",
        "aligned_edge",
        PROPAGATION_INWARD_CONTACT,
        BEAM_SEARCH_INTERNAL_VARIANTS,
        2,
    ),
)
_LANE_COUNTS = {
    EFFORT_QUICK: 3,
    EFFORT_NORMAL: 6,
    EFFORT_DEEP: 9,
}
_MINIMAL_CAPS = {
    EFFORT_QUICK: {
        "beam_width": 8,
        "max_search_states": 256,
        "max_placement_trials": 15_000,
        "max_elapsed_ms": 5_000,
    },
    EFFORT_NORMAL: {
        "beam_width": 24,
        "max_search_states": 1_500,
        "max_placement_trials": 75_000,
        "max_elapsed_ms": 12_000,
    },
    EFFORT_DEEP: {
        "beam_width": 64,
        "max_search_states": 5_000,
        "max_placement_trials": 250_000,
        "max_elapsed_ms": 30_000,
    },
}


def minimal_lane_specs(
    effort_profile: str = EFFORT_NORMAL,
) -> tuple[MinimalLaneSpec, ...]:
    """Return the monotone lane prefix for one explicit effort."""

    count = _LANE_COUNTS.get(effort_profile)
    if count is None:
        raise ValueError(
            "Unknown minimal-layout effort profile; expected quick, normal or deep."
        )
    return _LANES[:count]


def minimal_effort_budgets() -> tuple[SolverBudget, ...]:
    """Return Quick, Normal, and Deep hard caps in monotone order."""

    return tuple(
        _minimal_budget(effort_profile)
        for effort_profile in (EFFORT_QUICK, EFFORT_NORMAL, EFFORT_DEEP)
    )


def minimal_participant_orderings(
    participants: Iterable[Mapping[str, object]],
    box: Mapping[str, object],
    storage_height_mm: float,
    *,
    box_perimeter_xy_mm: float = 0.0,
) -> dict[str, tuple[str, ...]]:
    """Expose stable decomposed constraint orders without an opaque score."""

    values = tuple(dict(value) for value in participants)
    usable = (
        max(_EPSILON, float(box["x"]) - 2.0 * box_perimeter_xy_mm),
        max(_EPSILON, float(box["y"]) - 2.0 * box_perimeter_xy_mm),
        max(_EPSILON, float(storage_height_mm)),
    )
    facts = {
        str(value["id"]): _participant_pressure_facts(value, usable)
        for value in values
    }

    def ordered(key: Callable[[str], tuple[object, ...]]) -> tuple[str, ...]:
        return tuple(sorted(facts, key=key))

    by_volume = ordered(
        lambda participant_id: (
            -facts[participant_id]["volume_ratio"],
            participant_id,
        )
    )
    interleaved: list[str] = []
    lower = 0
    upper = len(by_volume) - 1
    while lower <= upper:
        interleaved.append(by_volume[lower])
        if lower != upper:
            interleaved.append(by_volume[upper])
        lower += 1
        upper -= 1

    return {
        "placement_rarity": ordered(
            lambda participant_id: (
                facts[participant_id]["orientation_count"],
                -facts[participant_id]["maximum_axis_pressure"],
                -facts[participant_id]["second_axis_pressure"],
                -facts[participant_id]["fixed_axis_count"],
                participant_id,
            )
        ),
        "axis_pressure": ordered(
            lambda participant_id: (
                -facts[participant_id]["maximum_axis_pressure"],
                -facts[participant_id]["second_axis_pressure"],
                facts[participant_id]["orientation_count"],
                participant_id,
            )
        ),
        "long_side_xy": ordered(
            lambda participant_id: (
                -facts[participant_id]["long_side_xy_pressure"],
                -facts[participant_id]["footprint_ratio"],
                participant_id,
            )
        ),
        "footprint_xy": ordered(
            lambda participant_id: (
                -facts[participant_id]["footprint_ratio"],
                -facts[participant_id]["long_side_xy_pressure"],
                participant_id,
            )
        ),
        "height": ordered(
            lambda participant_id: (
                -facts[participant_id]["height_ratio"],
                -facts[participant_id]["footprint_ratio"],
                participant_id,
            )
        ),
        "volume": by_volume,
        "interleave_extremes": tuple(interleaved),
    }


def solve_minimal_layout(
    raw_project: object,
    *,
    effort_profile: str = EFFORT_NORMAL,
    request_id: str | None = None,
    request_revision: int | None = None,
    cancel_check: Callable[[], bool] | None = None,
    container_frontiers: Sequence[ContainerVariantFrontier] | None = None,
    frontier_digests: Sequence[tuple[str, str]] = (),
) -> dict[str, object]:
    """Build a placement-certified minimal layout under explicit hard caps."""

    lane_specs = minimal_lane_specs(effort_profile)
    strategy = SolverStrategy(
        MINIMAL_LAYOUT_FAMILY_ID,
        MINIMAL_LAYOUT_SOLVER_VERSION,
    )
    budget = _minimal_budget(effort_profile)
    request = {
        "id": request_id or "not_applicable",
        "revision": (
            request_revision
            if request_revision is not None
            else "not_applicable"
        ),
    }
    if cancel_check is not None and cancel_check():
        return _failure_plan(
            status=STALE_OR_CANCELLED,
            stop_reason="cancelled_before_search",
            strategy=strategy,
            budget=budget,
            request=request,
            project_name="",
            requested_container_count=0,
            rejection_codes=(),
            lane_reports=(),
            frontier_source="not_loaded",
            ordered_frontier_digests=(),
        )

    preparation = prepare_free_3d_problem(raw_project)
    if preparation.problem is None:
        return _failure_plan(
            status=INVALID_INPUT,
            stop_reason="input_validation_failed",
            strategy=strategy,
            budget=budget,
            request=request,
            project_name="",
            requested_container_count=0,
            rejection_codes=preparation.rejection_codes,
            lane_reports=(),
            frontier_source="not_loaded",
            ordered_frontier_digests=(),
        )
    base_problem = preparation.problem
    frontiers, ordered_digests, frontier_source, frontier_rejections = (
        _resolve_frontiers(
            raw_project,
            base_problem,
            effort_profile,
            container_frontiers,
            frontier_digests,
        )
    )
    if frontier_rejections:
        return _failure_plan(
            status=INVALID_INPUT,
            stop_reason="local_frontier_contract_rejected",
            strategy=strategy,
            budget=budget,
            request=request,
            project_name=str(base_problem.project["project_name"]),
            requested_container_count=base_problem.requested_container_count,
            rejection_codes=frontier_rejections,
            lane_reports=(),
            frontier_source=frontier_source,
            ordered_frontier_digests=ordered_digests,
        )

    participants_with_options = _participants_with_variant_options(
        base_problem.participants,
        frontiers,
    )
    certification_problem = replace(
        base_problem,
        participants=participants_with_options,
        container_variant_frontiers=frontiers,
    )
    variant_search_participants = _force_minimum_dimensions(
        participants_with_options
    )
    canonical_search_participants = _canonical_search_participants(
        variant_search_participants
    )
    orderings = minimal_participant_orderings(
        variant_search_participants,
        certification_problem.box,
        certification_problem.storage_height_mm,
        box_perimeter_xy_mm=certification_problem.box_xy_clearance_mm,
    )
    participant_maps = {
        "variant": {
            str(value["id"]): value for value in variant_search_participants
        },
        "canonical": {
            str(value["id"]): value for value in canonical_search_participants
        },
        "certificate": {
            str(value["id"]): value
            for value in certification_problem.participants
        },
    }

    aggregate = Counter()
    lane_reports: list[dict[str, object]] = []
    proposals: list[_CertifiedProposal] = []
    rejection_codes: Counter[str] = Counter()
    for lane in lane_specs:
        if cancel_check is not None and cancel_check():
            return _failure_plan(
                status=STALE_OR_CANCELLED,
                stop_reason="cancelled_during_search",
                strategy=strategy,
                budget=budget,
                request=request,
                project_name=str(base_problem.project["project_name"]),
                requested_container_count=base_problem.requested_container_count,
                rejection_codes=tuple(sorted(rejection_codes)),
                lane_reports=tuple(lane_reports),
                frontier_source=frontier_source,
                ordered_frontier_digests=ordered_digests,
            )

        internal_variants = lane.search_variant == BEAM_SEARCH_INTERNAL_VARIANTS
        search_participants = (
            variant_search_participants
            if internal_variants
            else canonical_search_participants
        )
        search_map = (
            participant_maps["variant"]
            if internal_variants
            else participant_maps["canonical"]
        )
        participant_order = orderings[lane.order_id]
        seed_index = min(lane.seed_rank, len(participant_order) - 1)
        seed_participant_id = participant_order[seed_index]
        anchors = _anchor_points(
            lane.anchor_id,
            search_map[seed_participant_id],
            certification_problem,
        )
        lane_budget = (
            _variant_beam_budget(
                budget,
                variant_budget_for_effort(effort_profile),
            )
            if internal_variants
            else budget
        )
        execution = solve_free_3d_beam(
            search_participants,
            certification_problem.box,
            certification_problem.storage_height_mm,
            certification_problem.xy_clearance_mm,
            box_perimeter_xy_mm=certification_problem.box_xy_clearance_mm,
            between_bodies_z_mm=certification_problem.z_clearance_mm,
            budget=lane_budget,
            cancel_check=cancel_check,
            top_inset_zones=certification_problem.top_inset_zones,
            search_variant=lane.search_variant,
            participant_order=participant_order,
            seed_participant_id=seed_participant_id,
            initial_anchor_points=anchors,
            propagation_policy=lane.propagation_id,
        )
        telemetry = _telemetry_payload(execution)
        for key, value in telemetry.items():
            if isinstance(value, int) and not isinstance(value, bool):
                aggregate[key] += value

        if execution.status == STALE_OR_CANCELLED:
            lane_reports.append(
                {
                    "lane_id": lane.lane_id,
                    "order_id": lane.order_id,
                    "seed_participant_id": seed_participant_id,
                    "seed_rank": lane.seed_rank,
                    "anchor_id": lane.anchor_id,
                    "anchor_point_count": len(anchors),
                    "propagation_id": lane.propagation_id,
                    "search_variant": lane.search_variant,
                    "status": execution.status,
                    "stop_reason": execution.stop_reason,
                    "budget": dict(lane_budget.limits),
                    "telemetry": telemetry,
                    "geometric_solution_count": len(execution.solutions),
                    "certified_candidate_count": 0,
                    "rejection_code_counts": {},
                    "deterministic_digest": execution.deterministic_digest,
                }
            )
            return _failure_plan(
                status=STALE_OR_CANCELLED,
                stop_reason="cancelled_during_search",
                strategy=strategy,
                budget=budget,
                request=request,
                project_name=str(base_problem.project["project_name"]),
                requested_container_count=base_problem.requested_container_count,
                rejection_codes=tuple(sorted(rejection_codes)),
                lane_reports=tuple(lane_reports),
                frontier_source=frontier_source,
                ordered_frontier_digests=ordered_digests,
            )
        certified_before = len(proposals)
        lane_rejections: Counter[str] = Counter()
        for solution_index, solution in enumerate(execution.solutions):
            placements = solution.placements
            if not internal_variants:
                placements = _decorate_canonical_placements(
                    placements,
                    participant_maps["certificate"],
                    frontiers,
                )
            for translation_id, translated in _translation_candidates(
                placements,
                certification_problem,
            ):
                spaces = _rebuild_empty_spaces(
                    translated,
                    certification_problem,
                    lane_budget,
                )
                candidate_id = (
                    f"{lane.lane_id}-{solution_index:03d}-{translation_id}"
                )
                provisional_provenance = {
                    "portfolio_schema": MINIMAL_LAYOUT_PORTFOLIO_SCHEMA_V1,
                    "effort_profile": effort_profile,
                    "lane_id": lane.lane_id,
                    "order_id": lane.order_id,
                    "seed_participant_id": seed_participant_id,
                    "seed_rank": lane.seed_rank,
                    "anchor_id": lane.anchor_id,
                    "propagation_id": lane.propagation_id,
                    "search_variant": lane.search_variant,
                    "translation_id": translation_id,
                    "frontier_source": frontier_source,
                    "ordered_frontier_digests": [
                        {"container_group_id": key, "digest": value}
                        for key, value in ordered_digests
                    ],
                    "finalization_invocation_count": 0,
                    "fusion_materialization_invocation_count": 0,
                }
                certified, rejections = certify_minimal_free_3d_plan(
                    certification_problem,
                    strategy=strategy,
                    budget=budget,
                    candidate_id=candidate_id,
                    placements=translated,
                    empty_spaces=spaces,
                    search_telemetry=telemetry,
                    search_provenance=provisional_provenance,
                )
                if certified is None:
                    lane_rejections.update(rejections)
                    rejection_codes.update(rejections)
                    continue
                proposals.append(
                    _CertifiedProposal(
                        lane=lane,
                        seed_participant_id=seed_participant_id,
                        translation_id=translation_id,
                        placements=translated,
                        empty_spaces=spaces,
                        certified=certified,
                        rank_key=_proposal_rank_key(certified),
                    )
                )
                break

        lane_reports.append(
            {
                "lane_id": lane.lane_id,
                "order_id": lane.order_id,
                "seed_participant_id": seed_participant_id,
                "seed_rank": lane.seed_rank,
                "anchor_id": lane.anchor_id,
                "anchor_point_count": len(anchors),
                "propagation_id": lane.propagation_id,
                "search_variant": lane.search_variant,
                "status": execution.status,
                "stop_reason": execution.stop_reason,
                "budget": dict(lane_budget.limits),
                "telemetry": telemetry,
                "geometric_solution_count": len(execution.solutions),
                "certified_candidate_count": len(proposals) - certified_before,
                "rejection_code_counts": dict(sorted(lane_rejections.items())),
                "deterministic_digest": execution.deterministic_digest,
            }
        )

    if not proposals:
        return _failure_plan(
            status=NO_SOLUTION_WITHIN_BUDGET,
            stop_reason=_portfolio_stop_reason(lane_reports),
            strategy=strategy,
            budget=budget,
            request=request,
            project_name=str(base_problem.project["project_name"]),
            requested_container_count=base_problem.requested_container_count,
            rejection_codes=tuple(sorted(rejection_codes)),
            lane_reports=tuple(lane_reports),
            frontier_source=frontier_source,
            ordered_frontier_digests=ordered_digests,
        )

    deduplicated = _deduplicate_proposals(proposals)
    pareto = _pareto_frontier(deduplicated)
    selected = min(
        pareto,
        key=lambda value: (
            value.rank_key,
            value.certified.placement_digest,
            value.lane.lane_id,
        ),
    )
    portfolio = {
        "schema_version": MINIMAL_LAYOUT_PORTFOLIO_SCHEMA_V1,
        "solver_version": MINIMAL_LAYOUT_SOLVER_VERSION,
        "effort_profile": effort_profile,
        "request": request,
        "lane_prefix_ids": [lane.lane_id for lane in lane_specs],
        "quick_is_prefix_of_normal": (
            minimal_lane_specs(EFFORT_NORMAL)[
                : len(minimal_lane_specs(EFFORT_QUICK))
            ]
            == minimal_lane_specs(EFFORT_QUICK)
        ),
        "normal_is_prefix_of_deep": (
            minimal_lane_specs(EFFORT_DEEP)[
                : len(minimal_lane_specs(EFFORT_NORMAL))
            ]
            == minimal_lane_specs(EFFORT_NORMAL)
        ),
        "budget": dict(budget.limits),
        "frontier_source": frontier_source,
        "ordered_frontier_digests": [
            {"container_group_id": key, "digest": value}
            for key, value in ordered_digests
        ],
        "historical_comparator_lane_ids": [
            "historical_legacy_corner",
            "historical_bridge_edge",
        ],
        "lanes": lane_reports,
        "candidate_count_before_deduplication": len(proposals),
        "candidate_count_after_deduplication": len(deduplicated),
        "deduplicated_candidate_count": len(proposals) - len(deduplicated),
        "pareto_candidate_count": len(pareto),
        "pareto_placement_digests": [
            value.certified.placement_digest
            for value in pareto
        ],
        "ranking_axes": [
            {"name": "cluster_volume_mm3", "direction": "minimize"},
            {"name": "internal_gap_mm3", "direction": "minimize"},
            {"name": "cluster_height_mm", "direction": "minimize"},
            {"name": "cluster_footprint_mm2", "direction": "minimize"},
            {"name": "residual_fragmentation", "direction": "minimize"},
            {"name": "contact_count", "direction": "maximize"},
            {"name": "minimum_support_ratio", "direction": "maximize"},
        ],
        "selected": {
            "lane_id": selected.lane.lane_id,
            "order_id": selected.lane.order_id,
            "seed_participant_id": selected.seed_participant_id,
            "anchor_id": selected.lane.anchor_id,
            "propagation_id": selected.lane.propagation_id,
            "translation_id": selected.translation_id,
            "placement_digest": selected.certified.placement_digest,
            "statement": "best_certified_proposal_found_within_budget",
        },
        "symmetry": {
            "canonical_box_anchors_deduplicated": (
                not certification_problem.top_inset_zones
            ),
            "localized_constraints_reopened_anchors": bool(
                certification_problem.top_inset_zones
            ),
            "physical_corner_enumeration": "not_used_without_constraint",
        },
        "global_solver_trigger": "explicit_call_only",
        "finalization_invocation_count": 0,
        "fusion_materialization_invocation_count": 0,
    }
    portfolio["deterministic_digest"] = _digest(portfolio)
    aggregate["lane_count"] = len(lane_reports)
    aggregate["certified_candidates_before_deduplication"] = len(proposals)
    aggregate["certified_candidates_after_deduplication"] = len(deduplicated)
    aggregate["pareto_candidates"] = len(pareto)

    final, final_rejections = certify_minimal_free_3d_plan(
        certification_problem,
        strategy=strategy,
        budget=budget,
        candidate_id=(
            f"selected-{selected.lane.lane_id}-{selected.translation_id}"
        ),
        placements=selected.placements,
        empty_spaces=selected.empty_spaces,
        search_telemetry=dict(sorted(aggregate.items())),
        search_provenance=portfolio,
    )
    if final is None:
        return _failure_plan(
            status=NO_SOLUTION_WITHIN_BUDGET,
            stop_reason="selected_candidate_revalidation_failed",
            strategy=strategy,
            budget=budget,
            request=request,
            project_name=str(base_problem.project["project_name"]),
            requested_container_count=base_problem.requested_container_count,
            rejection_codes=final_rejections,
            lane_reports=tuple(lane_reports),
            frontier_source=frontier_source,
            ordered_frontier_digests=ordered_digests,
        )
    return final.plan


def _resolve_frontiers(
    raw_project: object,
    problem: Free3DPreparedProblem,
    effort_profile: str,
    supplied: Sequence[ContainerVariantFrontier] | None,
    supplied_digests: Sequence[tuple[str, str]],
) -> tuple[
    tuple[ContainerVariantFrontier, ...],
    tuple[tuple[str, str], ...],
    str,
    tuple[str, ...],
]:
    expected = {
        str(value["container_group_id"])
        for value in problem.participants
        if value["role"] == "container"
    }
    if supplied is None:
        run = derive_container_internal_variant_frontiers(
            raw_project,
            effort_profile=effort_profile,
            max_container_height_mm=problem.storage_height_mm,
        )
        frontiers = tuple(run.frontiers)
        source = "derived_bounded_fallback"
        if run.skipped_container_group_ids:
            return frontiers, (), source, ("LOCAL_FRONTIER_SET_INCOMPLETE",)
    else:
        frontiers = tuple(supplied)
        source = "incremental_local_analysis"

    by_group = {value.container_group_id: value for value in frontiers}
    rejections: set[str] = set()
    if len(by_group) != len(frontiers) or set(by_group) != expected:
        rejections.add("LOCAL_FRONTIER_SET_INCOMPLETE")
    if any(not value.variants for value in frontiers):
        rejections.add("LOCAL_FRONTIER_EMPTY")
    if any(
        not variant.local_certificate.certified
        for frontier in frontiers
        for variant in frontier.variants
    ):
        rejections.add("LOCAL_FRONTIER_CERTIFICATE_REJECTED")
    if any(
        frontier.budget.effort_profile != effort_profile
        for frontier in frontiers
    ):
        rejections.add("LOCAL_FRONTIER_EFFORT_MISMATCH")

    actual_digests = {
        frontier.container_group_id: _frontier_artifact_digest(frontier)
        for frontier in frontiers
    }
    if supplied_digests:
        digests = tuple(
            sorted(
                (str(key), str(value))
                for key, value in supplied_digests
            )
        )
        if (
            len(digests) != len(expected)
            or {key for key, _ in digests} != expected
        ):
            rejections.add("LOCAL_FRONTIER_DIGEST_SET_INCOMPLETE")
        elif any(
            actual_digests.get(key) != value for key, value in digests
        ):
            rejections.add("LOCAL_FRONTIER_DIGEST_MISMATCH")
    else:
        digests = tuple(sorted(actual_digests.items()))
    return frontiers, digests, source, tuple(sorted(rejections))


def _frontier_artifact_digest(frontier: ContainerVariantFrontier) -> str:
    run = InternalVariantRun(
        schema_version=INTERNAL_VARIANT_SCHEMA_V1,
        budget=frontier.budget,
        frontiers=(frontier,),
        skipped_container_group_ids=(),
    )
    return canonical_digest(internal_variant_run_to_dict(run))


def _minimal_budget(effort_profile: str) -> SolverBudget:
    source = next(
        value.beam_budget
        for value in portfolio_effort_profiles()
        if value.profile_id == effort_profile
    )
    limits = dict(source.limits)
    for key, cap in _MINIMAL_CAPS[effort_profile].items():
        limits[key] = min(int(limits[key]), cap)
    return SolverBudget(
        source.family_id,
        effort_profile,
        tuple(sorted(limits.items())),
    )


def _force_minimum_dimensions(
    participants: Iterable[Mapping[str, object]],
) -> tuple[dict[str, object], ...]:
    result: list[dict[str, object]] = []
    for participant in participants:
        projected = deepcopy(dict(participant))
        minimum = _mapping(projected["minimum_local_mm"])
        projected["dimension_modes"] = {axis: "fixed" for axis in _AXES}
        projected["target_local_mm"] = {
            axis: float(minimum[axis]) for axis in _AXES
        }
        result.append(projected)
    return tuple(result)


def _canonical_search_participants(
    participants: tuple[dict[str, object], ...],
) -> tuple[dict[str, object], ...]:
    result: list[dict[str, object]] = []
    for participant in participants:
        projected = deepcopy(participant)
        options = projected.pop("container_internal_variant_options_v1", None)
        if projected["role"] == "container":
            if not isinstance(options, list) or not options:
                raise ValueError("A canonical container frontier is required.")
            canonical = next(
                (
                    value
                    for value in options
                    if bool(_mapping(value).get("canonical"))
                ),
                options[0],
            )
            option = _mapping(canonical)
            minimum = _mapping(option["minimum_outer_envelope_mm"])
            projected["minimum_local_mm"] = {
                axis: float(minimum[axis]) for axis in _AXES
            }
            projected["target_local_mm"] = {
                axis: float(minimum[axis]) for axis in _AXES
            }
            hint = projected.get("top_inset_search_hint_v1")
            cavities = option.get("cavities")
            if isinstance(hint, dict) and isinstance(cavities, list):
                selected_hint = deepcopy(hint)
                selected_hint["cavities"] = deepcopy(cavities)
                projected["top_inset_search_hint_v1"] = selected_hint
        result.append(projected)
    return tuple(result)


def _participant_pressure_facts(
    participant: Mapping[str, object],
    usable: tuple[float, float, float],
) -> dict[str, float | int]:
    minimum = _mapping(participant["minimum_local_mm"])
    dimensions = tuple(float(minimum[axis]) for axis in _AXES)
    pressures = sorted(
        (
            dimensions[0] / usable[0],
            dimensions[1] / usable[1],
            dimensions[2] / usable[2],
        ),
        reverse=True,
    )
    orientations = int(
        dimensions[0] <= usable[0] + _EPSILON
        and dimensions[1] <= usable[1] + _EPSILON
    ) + int(
        dimensions[1] <= usable[0] + _EPSILON
        and dimensions[0] <= usable[1] + _EPSILON
    )
    modes = _mapping(participant["dimension_modes"])
    return {
        "orientation_count": orientations,
        "maximum_axis_pressure": pressures[0],
        "second_axis_pressure": pressures[1],
        "fixed_axis_count": sum(
            str(modes[axis]) == "fixed" for axis in _AXES
        ),
        "long_side_xy_pressure": max(
            dimensions[0] / usable[0],
            dimensions[1] / usable[1],
        ),
        "footprint_ratio": (
            dimensions[0] * dimensions[1] / (usable[0] * usable[1])
        ),
        "height_ratio": dimensions[2] / usable[2],
        "volume_ratio": (
            dimensions[0]
            * dimensions[1]
            * dimensions[2]
            / (usable[0] * usable[1] * usable[2])
        ),
    }


def _anchor_points(
    anchor_id: str,
    seed: Mapping[str, object],
    problem: Free3DPreparedProblem,
) -> tuple[tuple[float, float, float], ...]:
    minimum = _mapping(seed["minimum_local_mm"])
    size = (
        float(minimum["x"]),
        float(minimum["y"]),
        float(minimum["z"]),
    )
    clearance = problem.box_xy_clearance_mm
    lower_x = clearance
    lower_y = clearance
    upper_x = problem.box["x"] - clearance
    upper_y = problem.box["y"] - clearance
    candidates: set[tuple[float, float, float]] = set()
    for width, depth in ((size[0], size[1]), (size[1], size[0])):
        centered_x = _round(
            lower_x + max(0.0, upper_x - lower_x - width) / 2.0
        )
        centered_y = _round(
            lower_y + max(0.0, upper_y - lower_y - depth) / 2.0
        )
        if anchor_id == "aligned_edge":
            candidates.add((centered_x, _round(lower_y), 0.0))
            candidates.add((_round(lower_x), centered_y, 0.0))
        elif anchor_id in {"compact_center", "lowest_surface"}:
            candidates.add((centered_x, centered_y, 0.0))
    return tuple(sorted(candidates))


def _decorate_canonical_placements(
    placements: tuple[Free3DPlacement, ...],
    participants_by_id: Mapping[str, Mapping[str, object]],
    frontiers: tuple[ContainerVariantFrontier, ...],
) -> tuple[Free3DPlacement, ...]:
    by_group = {value.container_group_id: value for value in frontiers}
    result: list[Free3DPlacement] = []
    for placement in placements:
        if placement.role != "container":
            result.append(placement)
            continue
        participant = participants_by_id[placement.participant_id]
        group_id = str(participant["container_group_id"])
        variants = by_group[group_id].variants
        variant = next(
            (value for value in variants if value.canonical),
            variants[0],
        )
        if any(
            abs(
                placement.local_size_mm[index]
                - variant.draft.minimum_outer_envelope_mm[index]
            )
            > _EPSILON
            for index in range(3)
        ):
            raise ValueError(
                "Historical lane expanded a canonical envelope."
            )
        result.append(
            VariantFree3DPlacement(
                participant_id=placement.participant_id,
                role=placement.role,
                name=placement.name,
                origin_mm=placement.origin_mm,
                world_size_mm=placement.world_size_mm,
                local_size_mm=placement.local_size_mm,
                rotation_deg_z=placement.rotation_deg_z,
                supporting_ids=placement.supporting_ids,
                support_coverage_ratio=placement.support_coverage_ratio,
                container_variant_id=variant.variant_id,
                container_variant_digest=variant.geometry_digest,
                container_variant_canonical=variant.canonical,
            )
        )
    return tuple(result)


def _translation_candidates(
    placements: tuple[Free3DPlacement, ...],
    problem: Free3DPreparedProblem,
) -> tuple[tuple[str, tuple[Free3DPlacement, ...]], ...]:
    lower = [
        min(value.origin_mm[index] for value in placements)
        for index in range(2)
    ]
    upper = [
        max(
            value.origin_mm[index] + value.world_size_mm[index]
            for value in placements
        )
        for index in range(2)
    ]
    spans = [upper[index] - lower[index] for index in range(2)]
    clearance = problem.box_xy_clearance_mm
    desired = [
        clearance
        + (
            problem.box[_AXES[index]]
            - 2.0 * clearance
            - spans[index]
        )
        / 2.0
        for index in range(2)
    ]
    deltas = (
        ("centered_xy", desired[0] - lower[0], desired[1] - lower[1]),
        ("centered_x", desired[0] - lower[0], 0.0),
        ("centered_y", 0.0, desired[1] - lower[1]),
        ("search_coordinates", 0.0, 0.0),
    )
    retained: list[
        tuple[str, tuple[Free3DPlacement, ...]]
    ] = []
    signatures: set[tuple[float, float]] = set()
    for translation_id, raw_dx, raw_dy in deltas:
        dx, dy = _round(raw_dx), _round(raw_dy)
        signature = (dx, dy)
        if signature in signatures:
            continue
        signatures.add(signature)
        retained.append(
            (
                translation_id,
                tuple(
                    replace(
                        value,
                        origin_mm=(
                            _round(value.origin_mm[0] + dx),
                            _round(value.origin_mm[1] + dy),
                            value.origin_mm[2],
                        ),
                    )
                    for value in placements
                ),
            )
        )
    return tuple(retained)


def _rebuild_empty_spaces(
    placements: tuple[Free3DPlacement, ...],
    problem: Free3DPreparedProblem,
    budget: SolverBudget,
) -> tuple[EmptySpace, ...]:
    clearance = problem.box_xy_clearance_mm
    spaces = [
        EmptySpace(
            (clearance, clearance, 0.0),
            (
                _round(problem.box["x"] - 2.0 * clearance),
                _round(problem.box["y"] - 2.0 * clearance),
                _round(problem.storage_height_mm),
            ),
        )
    ]
    limits = dict(budget.limits)
    counters = _Counters()
    for placement in sorted(
        placements,
        key=lambda value: (
            value.origin_mm[2],
            value.origin_mm[1],
            value.origin_mm[0],
            value.participant_id,
        ),
    ):
        spaces = _subtract_placement_from_spaces(
            spaces,
            placement,
            problem.xy_clearance_mm,
            problem.z_clearance_mm,
            counters,
            limits,
        )
    return tuple(spaces)


def _telemetry_payload(
    execution: Free3DBeamExecution,
) -> dict[str, object]:
    return {
        **execution.telemetry.__dict__,
        "remaining_best_participant_ids": list(
            execution.remaining_best_participant_ids
        ),
    }


def _proposal_rank_key(
    certified: CertifiedFree3DPlan,
) -> tuple[object, ...]:
    metrics = _mapping(
        _mapping(certified.plan["minimal_layout"])["metrics"]
    )
    return (
        float(metrics["cluster_volume_mm3"]),
        float(metrics["internal_gap_mm3"]),
        float(metrics["cluster_height_mm"]),
        float(metrics["cluster_footprint_mm2"]),
        float(metrics["residual_fragmentation"]),
        -float(metrics["contact_count"]),
        -float(metrics["minimum_support_ratio"]),
        certified.placement_digest,
    )


def _deduplicate_proposals(
    proposals: Iterable[_CertifiedProposal],
) -> tuple[_CertifiedProposal, ...]:
    retained: dict[str, _CertifiedProposal] = {}
    for proposal in proposals:
        key = proposal.certified.placement_digest
        previous = retained.get(key)
        if previous is None or (
            proposal.rank_key,
            proposal.lane.lane_id,
        ) < (
            previous.rank_key,
            previous.lane.lane_id,
        ):
            retained[key] = proposal
    return tuple(
        sorted(
            retained.values(),
            key=lambda value: (
                value.rank_key,
                value.certified.placement_digest,
                value.lane.lane_id,
            ),
        )
    )


def _pareto_frontier(
    proposals: tuple[_CertifiedProposal, ...],
) -> tuple[_CertifiedProposal, ...]:
    vectors = {
        value.certified.placement_digest: tuple(
            float(item) for item in value.rank_key[:7]
        )
        for value in proposals
    }
    retained = [
        value
        for value in proposals
        if not any(
            other is not value
            and _dominates(
                vectors[other.certified.placement_digest],
                vectors[value.certified.placement_digest],
            )
            for other in proposals
        )
    ]
    return tuple(
        sorted(
            retained,
            key=lambda value: (
                value.rank_key,
                value.certified.placement_digest,
            ),
        )
    )


def _dominates(
    left: tuple[float, ...],
    right: tuple[float, ...],
) -> bool:
    return all(
        left[index] <= right[index] + _EPSILON
        for index in range(len(left))
    ) and any(
        left[index] < right[index] - _EPSILON
        for index in range(len(left))
    )


def _portfolio_stop_reason(
    lane_reports: Sequence[Mapping[str, object]],
) -> str:
    if any(
        str(value.get("stop_reason")) == "hard_time_budget_reached"
        for value in lane_reports
    ):
        return "hard_time_budget_reached"
    if any(
        str(value.get("stop_reason")) == "hard_budget_reached"
        for value in lane_reports
    ):
        return "hard_budget_reached"
    return "bounded_portfolio_exhausted"


def _failure_plan(
    *,
    status: str,
    stop_reason: str,
    strategy: SolverStrategy,
    budget: SolverBudget,
    request: Mapping[str, object],
    project_name: str,
    requested_container_count: int,
    rejection_codes: Sequence[str],
    lane_reports: Sequence[Mapping[str, object]],
    frontier_source: str,
    ordered_frontier_digests: Sequence[tuple[str, str]],
) -> dict[str, object]:
    result = {
        "schema_version": SOLVER_RESULT_SCHEMA_V1,
        "status": status,
        "label": result_label(status),
        "legacy_summary_status": "not_constructed",
        "proof": None,
        "materializable": False,
    }
    diagnostics = [
        {
            "code": value,
            "severity": "error",
            "message": (
                "Minimal-layout candidate rejected by a hard contract."
            ),
        }
        for value in sorted(set(rejection_codes))
    ]
    telemetry = {
        "schema_version": SOLVER_TELEMETRY_SCHEMA_V1,
        "family": {
            "id": strategy.family_id,
            "version": strategy.version,
        },
        "request": deepcopy(dict(request)),
        "elapsed_ms": "not_applicable",
        "budgets": dict(budget.limits),
        "counters": {
            "lane_count": len(lane_reports),
            "certified_complete_solutions": 0,
        },
        "prunes": {},
        "diagnostic_code_counts": dict(
            sorted(Counter(rejection_codes).items())
        ),
        "stop_reason": stop_reason,
    }
    portfolio = {
        "schema_version": MINIMAL_LAYOUT_PORTFOLIO_SCHEMA_V1,
        "solver_version": MINIMAL_LAYOUT_SOLVER_VERSION,
        "effort_profile": budget.effort_profile,
        "request": deepcopy(dict(request)),
        "lane_prefix_ids": [
            value["lane_id"] for value in lane_reports
        ],
        "budget": dict(budget.limits),
        "frontier_source": frontier_source,
        "ordered_frontier_digests": [
            {"container_group_id": key, "digest": value}
            for key, value in ordered_frontier_digests
        ],
        "lanes": deepcopy(list(lane_reports)),
        "candidate_count_before_deduplication": 0,
        "candidate_count_after_deduplication": 0,
        "pareto_candidate_count": 0,
        "global_solver_trigger": "explicit_call_only",
        "finalization_invocation_count": 0,
        "fusion_materialization_invocation_count": 0,
    }
    portfolio["deterministic_digest"] = _digest(portfolio)
    plan: dict[str, object] = {
        "schema_version": PARTITION_PLAN_SCHEMA_V1,
        "project_name": project_name,
        "placements": [],
        "diagnostics": diagnostics,
        "summary": {
            "status": "not_constructed",
            "result_status": status,
            "result_label": result["label"],
            "materializable": False,
            "placement_certified": False,
            "minimal_layout_core_ready": False,
            "requested_container_count": requested_container_count,
            "placed_container_count": 0,
            "automatic_body_count": 0,
            "complete_printable_partition": False,
            "residual_volume_mm3": None,
        },
        "solver": {
            "kind": "bounded_minimal_layout_solver",
            "family_id": strategy.family_id,
            "schema_version": strategy.version,
            "budgets": dict(budget.limits),
            "result": result,
            "telemetry": telemetry,
            "search": deepcopy(portfolio),
            "deterministic": True,
            "globally_optimal": False,
        },
        "minimal_layout": {
            "schema_version": MINIMAL_LAYOUT_ARTIFACT_SCHEMA_V1,
            "artifact_kind": "minimal_layout",
            "status": status,
            "geometry_statement": (
                "no_certified_minimum_layout_found_within_budget"
            ),
            "best_candidate_statement": None,
            "search_provenance": portfolio,
            "finalization_applied": False,
            "automatic_body_count": 0,
        },
        "invariants": {
            "minimal_layout": True,
            "minimum_outer_dimensions_only": True,
            "residual_distributed": False,
            "continuous_closure_applied": False,
            "automatic_body_count": 0,
            "free_space_materialized": False,
        },
    }
    plan["plan_digest"] = _digest(plan)
    return plan
