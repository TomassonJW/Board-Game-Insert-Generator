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
from time import perf_counter
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
from board_game_insert_generator.highs_product_solver import (
    HIGHS_PRODUCT_FAMILY,
    HIGHS_PRODUCT_VERSION,
    STATUS_NOT_CONFIGURED as HIGHS_STATUS_NOT_CONFIGURED,
    STATUS_SOLUTION_FOUND as HIGHS_STATUS_SOLUTION_FOUND,
    solve_highs_product_floor,
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
    SOLUTION_FOUND,
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
MINIMAL_LAYOUT_SOLVER_VERSION = "p64-l04b-v1"
MINIMAL_LAYOUT_PORTFOLIO_SCHEMA_V1 = "bgig.minimal_layout_portfolio.v1"
_AXES = ("x", "y", "z")
_EPSILON = 0.0001
_DEEP_EXTENSION_DEADLINE_MS = 30_000


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
        "max_deep_extension_elapsed_ms": _DEEP_EXTENSION_DEADLINE_MS,
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
    initial_incumbent: Mapping[str, object] | None = None,
) -> dict[str, object]:
    """Build a placement-certified minimal layout under explicit hard caps."""

    if effort_profile != EFFORT_DEEP:
        return _solve_minimal_layout_once(
            raw_project,
            effort_profile=effort_profile,
            request_id=request_id,
            request_revision=request_revision,
            cancel_check=cancel_check,
            container_frontiers=container_frontiers,
            frontier_digests=frontier_digests,
            initial_incumbent=initial_incumbent,
        )
    return _solve_deep_anytime(
        raw_project,
        request_id=request_id,
        request_revision=request_revision,
        cancel_check=cancel_check,
        container_frontiers=container_frontiers,
        frontier_digests=frontier_digests,
        initial_incumbent=initial_incumbent,
    )


def _solve_minimal_layout_once(
    raw_project: object,
    *,
    effort_profile: str,
    request_id: str | None,
    request_revision: int | None,
    cancel_check: Callable[[], bool] | None,
    container_frontiers: Sequence[ContainerVariantFrontier] | None,
    frontier_digests: Sequence[tuple[str, str]],
    lane_specs_override: Sequence[MinimalLaneSpec] | None = None,
    deadline_at_ms: float | None = None,
    frontier_source_override: str | None = None,
    initial_incumbent: Mapping[str, object] | None = None,
    external_lane_enabled: bool = False,
) -> dict[str, object]:
    """Execute one explicit lane prefix or extension without orchestration."""

    lane_specs = tuple(
        lane_specs_override
        if lane_specs_override is not None
        else minimal_lane_specs(effort_profile)
    )
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
    if frontier_source_override is not None:
        frontier_source = frontier_source_override
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
    warm_start_proposal, warm_start_report = _certify_warm_start_incumbent(
        initial_incumbent,
        problem=certification_problem,
        strategy=strategy,
        budget=budget,
        effort_profile=effort_profile,
        frontier_source=frontier_source,
        ordered_frontier_digests=ordered_digests,
    )
    proposals: list[_CertifiedProposal] = (
        [warm_start_proposal] if warm_start_proposal is not None else []
    )
    rejection_codes: Counter[str] = Counter()
    external_lane_report: dict[str, object] | None = None
    if external_lane_enabled:
        external_execution = solve_highs_product_floor(
            canonical_search_participants,
            certification_problem,
            effort_profile=effort_profile,
            cancel_check=cancel_check,
        )
        if external_execution.status != HIGHS_STATUS_NOT_CONFIGURED:
            external_lane_report = external_execution.deterministic_report()
            external_recertification: dict[str, object] = {
                "attempted": False,
                "certified": False,
                "rejection_codes": [],
                "placement_digest": "",
            }
            if external_execution.status == HIGHS_STATUS_SOLUTION_FOUND:
                try:
                    external_placements = _decorate_canonical_placements(
                        external_execution.placements,
                        participant_maps["certificate"],
                        frontiers,
                    )
                    external_spaces = _rebuild_empty_spaces(
                        external_placements,
                        certification_problem,
                        budget,
                    )
                    external_strategy = SolverStrategy(
                        "highs_product_floor",
                        HIGHS_PRODUCT_VERSION,
                    )
                    external_budget = SolverBudget(
                        HIGHS_PRODUCT_FAMILY,
                        effort_profile,
                        tuple(
                            sorted(
                                external_execution.limits.to_dict().items()
                            )
                        ),
                    )
                    external_certified, external_rejections = (
                        certify_minimal_free_3d_plan(
                            certification_problem,
                            strategy=external_strategy,
                            budget=external_budget,
                            candidate_id="external-highs-product-floor",
                            placements=external_placements,
                            empty_spaces=external_spaces,
                            search_telemetry={
                                "external_engine_invocation_count": 1,
                                "external_network_invocation_count": 0,
                            },
                            search_provenance={
                                "portfolio_schema": (
                                    MINIMAL_LAYOUT_PORTFOLIO_SCHEMA_V1
                                ),
                                "effort_profile": effort_profile,
                                "lane_id": _HIGHS_PRODUCT_LANE.lane_id,
                                "candidate_source": "external_highs",
                                "external_report_digest": (
                                    external_lane_report["report_digest"]
                                ),
                                "frontier_source": frontier_source,
                                "ordered_frontier_digests": [
                                    {
                                        "container_group_id": key,
                                        "digest": value,
                                    }
                                    for key, value in ordered_digests
                                ],
                                "finalization_invocation_count": 0,
                                "fusion_materialization_invocation_count": 0,
                            },
                        )
                    )
                except (KeyError, TypeError, ValueError, OverflowError) as exc:
                    external_certified = None
                    external_rejections = (
                        f"external_proposal_projection_failed:{type(exc).__name__}",
                    )
                external_recertification = {
                    "attempted": True,
                    "certified": external_certified is not None,
                    "rejection_codes": list(external_rejections),
                    "placement_digest": (
                        external_certified.placement_digest
                        if external_certified is not None
                        else ""
                    ),
                }
                if external_certified is not None:
                    proposals.append(
                        _CertifiedProposal(
                            lane=_HIGHS_PRODUCT_LANE,
                            seed_participant_id="not_applicable",
                            translation_id="highs_search_coordinates",
                            placements=external_placements,
                            empty_spaces=external_spaces,
                            certified=external_certified,
                            rank_key=_proposal_rank_key(
                                external_certified
                            ),
                        )
                    )
            external_lane_report.pop("report_digest", None)
            external_lane_report["recertification"] = (
                external_recertification
            )
            external_lane_report["report_digest"] = canonical_digest(
                external_lane_report
            )
    deadline_reached = False
    for lane in lane_specs:
        deadline_remaining_ms = _remaining_deadline_ms(deadline_at_ms)
        if (
            deadline_remaining_ms is not None
            and deadline_remaining_ms < 1.0
        ):
            deadline_reached = True
            break
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
        if deadline_remaining_ms is not None:
            lane_budget = _budget_with_elapsed_cap(
                lane_budget,
                deadline_remaining_ms,
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
                    "deadline_remaining_ms_at_start": (
                        int(deadline_remaining_ms)
                        if deadline_remaining_ms is not None
                        else "not_applicable"
                    ),
                    "deadline_reached_after_lane": False,
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
        deadline_reached_after_lane = _deadline_has_expired(
            deadline_at_ms
        )
        certified_before = len(proposals)
        lane_rejections: Counter[str] = Counter()
        for solution_index, solution in enumerate(execution.solutions):
            if deadline_reached_after_lane:
                break
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
                if _deadline_has_expired(deadline_at_ms):
                    deadline_reached_after_lane = True
                    break
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

        deadline_reached_after_lane = (
            deadline_reached_after_lane
            or _deadline_has_expired(deadline_at_ms)
        )
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
                "deadline_remaining_ms_at_start": (
                    int(deadline_remaining_ms)
                    if deadline_remaining_ms is not None
                    else "not_applicable"
                ),
                "deadline_reached_after_lane": deadline_reached_after_lane,
                "telemetry": telemetry,
                "geometric_solution_count": len(execution.solutions),
                "certified_candidate_count": len(proposals) - certified_before,
                "rejection_code_counts": dict(sorted(lane_rejections.items())),
                "deterministic_digest": execution.deterministic_digest,
            }
        )
        if deadline_reached_after_lane:
            deadline_reached = True
            break

    if not proposals:
        return _failure_plan(
            status=NO_SOLUTION_WITHIN_BUDGET,
            stop_reason=(
                "deep_deadline_reached_without_candidate"
                if deadline_reached
                else _portfolio_stop_reason(lane_reports)
            ),
            strategy=strategy,
            budget=budget,
            request=request,
            project_name=str(base_problem.project["project_name"]),
            requested_container_count=base_problem.requested_container_count,
            rejection_codes=tuple(sorted(rejection_codes)),
            lane_reports=tuple(lane_reports),
            frontier_source=frontier_source,
            ordered_frontier_digests=ordered_digests,
            warm_start=warm_start_report,
            external_lane=external_lane_report,
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
    witness_selected = selected.lane.lane_id == "certified_witness_incumbent"
    external_selected = selected.lane.lane_id == _HIGHS_PRODUCT_LANE.lane_id
    warm_start_payload = {
        **warm_start_report,
        "selected": witness_selected,
        "incumbent_preserved": witness_selected,
        "search_continued": True,
        "lane_count_added": 0,
    }
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
        "wall_clock_limited": (
            deadline_at_ms is not None
            or bool(
                external_lane_report is not None
                and external_lane_report.get("invocation_count")
            )
        ),
        "deadline_reached": deadline_reached,
        "stop_reason": (
            "deep_deadline_reached_with_candidate"
            if deadline_reached
            else (
                "external_highs_proposal_selected_after_common_certification"
                if external_selected
                else (
                    "certified_witness_incumbent_preserved_after_lane_search"
                    if witness_selected
                    else "bounded_lane_prefix_completed"
                )
            )
        ),
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
        "warm_start": warm_start_payload,
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
            "candidate_source": (
                "external_highs"
                if external_selected
                else (
                    "certified_witness"
                    if witness_selected
                    else "portfolio_lane"
                )
            ),
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
    if external_lane_report is not None:
        external_lane_report["selected"] = external_selected
        external_lane_report.pop("report_digest", None)
        external_lane_report["report_digest"] = canonical_digest(
            external_lane_report
        )
        portfolio["external_lane"] = deepcopy(external_lane_report)
    portfolio["deterministic_digest"] = _digest(portfolio)
    aggregate["lane_count"] = len(lane_reports)
    aggregate["certified_candidates_before_deduplication"] = len(proposals)
    aggregate["certified_candidates_after_deduplication"] = len(deduplicated)
    aggregate["pareto_candidates"] = len(pareto)
    aggregate["warm_start_accepted"] = int(
        warm_start_report["status"] == "accepted"
    )
    aggregate["warm_start_selected"] = int(witness_selected)
    if external_lane_report is not None:
        aggregate["external_lane_invocation_count"] = int(
            external_lane_report["invocation_count"]
        )
        aggregate["external_lane_certified_candidate_count"] = int(
            bool(
                _mapping(
                    external_lane_report.get("recertification")
                ).get("certified")
            )
        )
        aggregate["external_lane_selected"] = int(external_selected)

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
            external_lane=external_lane_report,
        )
    return final.plan


def _solve_deep_anytime(
    raw_project: object,
    *,
    request_id: str | None,
    request_revision: int | None,
    cancel_check: Callable[[], bool] | None,
    container_frontiers: Sequence[ContainerVariantFrontier] | None,
    frontier_digests: Sequence[tuple[str, str]],
    initial_incumbent: Mapping[str, object] | None,
) -> dict[str, object]:
    """Run the exact Normal prefix before a deadline-bounded Deep extension."""

    strategy = SolverStrategy(
        MINIMAL_LAYOUT_FAMILY_ID,
        MINIMAL_LAYOUT_SOLVER_VERSION,
    )
    budget = _minimal_budget(EFFORT_DEEP)
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

    if container_frontiers is None:
        deep_run = derive_container_internal_variant_frontiers(
            raw_project,
            effort_profile=EFFORT_DEEP,
            max_container_height_mm=base_problem.storage_height_mm,
        )
        deep_frontiers = tuple(deep_run.frontiers)
        deep_source = "derived_bounded_fallback"
        deep_supplied_digests: tuple[tuple[str, str], ...] = tuple(
            sorted(
                (
                    frontier.container_group_id,
                    _frontier_artifact_digest(frontier),
                )
                for frontier in deep_frontiers
            )
        )
    else:
        deep_frontiers = tuple(container_frontiers)
        deep_source = "incremental_local_analysis"
        deep_supplied_digests = tuple(frontier_digests)
    deep_actual_digests = tuple(
        sorted(
            (
                frontier.container_group_id,
                _frontier_artifact_digest(frontier),
            )
            for frontier in deep_frontiers
        )
    )

    normal_run = derive_container_internal_variant_frontiers(
        raw_project,
        effort_profile=EFFORT_NORMAL,
        max_container_height_mm=base_problem.storage_height_mm,
    )
    normal_frontiers = tuple(normal_run.frontiers)
    normal_digests = tuple(
        sorted(
            (
                frontier.container_group_id,
                _frontier_artifact_digest(frontier),
            )
            for frontier in normal_frontiers
        )
    )
    normal_plan = _solve_minimal_layout_once(
        raw_project,
        effort_profile=EFFORT_NORMAL,
        request_id=request_id,
        request_revision=request_revision,
        cancel_check=cancel_check,
        container_frontiers=normal_frontiers,
        frontier_digests=normal_digests,
        frontier_source_override="derived_normal_incumbent",
    )
    normal_status = _solver_result_status(normal_plan)
    if normal_status in {INVALID_INPUT, STALE_OR_CANCELLED}:
        return _build_anytime_failure(
            base_problem=base_problem,
            status=normal_status,
            stop_reason=(
                "normal_prefix_cancelled"
                if normal_status == STALE_OR_CANCELLED
                else "normal_prefix_invalid"
            ),
            request=request,
            normal_plan=normal_plan,
            deep_plan=None,
            normal_frontiers=normal_frontiers,
            normal_digests=normal_digests,
            deep_frontiers=deep_frontiers,
            deep_digests=deep_actual_digests,
            deep_source=deep_source,
            elapsed_ms=None,
            deadline_reached=False,
        )

    deep_started_ms = _monotonic_ms()
    deep_plan = _solve_minimal_layout_once(
        raw_project,
        effort_profile=EFFORT_DEEP,
        request_id=request_id,
        request_revision=request_revision,
        cancel_check=cancel_check,
        container_frontiers=deep_frontiers,
        frontier_digests=deep_supplied_digests,
        lane_specs_override=minimal_lane_specs(EFFORT_DEEP)[
            len(minimal_lane_specs(EFFORT_NORMAL)) :
        ],
        deadline_at_ms=(
            deep_started_ms + _DEEP_EXTENSION_DEADLINE_MS
        ),
        frontier_source_override=deep_source,
        initial_incumbent=initial_incumbent,
        external_lane_enabled=False,
    )
    elapsed_ms = max(0, int(_monotonic_ms() - deep_started_ms))
    deep_status = _solver_result_status(deep_plan)
    deep_stop_reason = _solver_stop_reason(deep_plan)
    deadline_reached = "deadline_reached" in deep_stop_reason
    if deep_status in {INVALID_INPUT, STALE_OR_CANCELLED}:
        return _build_anytime_failure(
            base_problem=base_problem,
            status=deep_status,
            stop_reason=(
                "deep_extension_cancelled"
                if deep_status == STALE_OR_CANCELLED
                else "deep_frontier_invalid"
            ),
            request=request,
            normal_plan=normal_plan,
            deep_plan=deep_plan,
            normal_frontiers=normal_frontiers,
            normal_digests=normal_digests,
            deep_frontiers=deep_frontiers,
            deep_digests=deep_actual_digests,
            deep_source=deep_source,
            elapsed_ms=elapsed_ms,
            deadline_reached=deadline_reached,
        )

    return _combine_anytime_results(
        base_problem=base_problem,
        request=request,
        normal_plan=normal_plan,
        deep_plan=deep_plan,
        normal_frontiers=normal_frontiers,
        normal_digests=normal_digests,
        deep_frontiers=deep_frontiers,
        deep_digests=deep_actual_digests,
        deep_source=deep_source,
        elapsed_ms=elapsed_ms,
        deadline_reached=deadline_reached,
    )

def _solver_result_status(plan: Mapping[str, object]) -> str:
    solver = _mapping(plan.get("solver"))
    return str(_mapping(solver.get("result")).get("status", ""))


def _solver_stop_reason(plan: Mapping[str, object]) -> str:
    solver = _mapping(plan.get("solver"))
    telemetry = _mapping(solver.get("telemetry"))
    return str(
        telemetry.get(
            "search_stop_reason",
            telemetry.get("stop_reason", ""),
        )
    )


def _plan_search_provenance(
    plan: Mapping[str, object] | None,
) -> dict[str, object]:
    if plan is None:
        return {}
    minimal = _mapping(plan.get("minimal_layout"))
    return deepcopy(_mapping(minimal.get("search_provenance")))


def _plan_rank_axes(plan: Mapping[str, object]) -> tuple[float, ...]:
    metrics = _mapping(_mapping(plan.get("minimal_layout")).get("metrics"))
    return (
        float(metrics["cluster_volume_mm3"]),
        float(metrics["internal_gap_mm3"]),
        float(metrics["cluster_height_mm"]),
        float(metrics["cluster_footprint_mm2"]),
        float(metrics["residual_fragmentation"]),
        -float(metrics["contact_count"]),
        -float(metrics["minimum_support_ratio"]),
    )


def _phase_summary(
    plan: Mapping[str, object] | None,
    *,
    fallback_status: str,
) -> dict[str, object]:
    provenance = _plan_search_provenance(plan)
    status = (
        _solver_result_status(plan)
        if plan is not None
        else fallback_status
    )
    stop_reason = (
        str(provenance.get("stop_reason"))
        if provenance.get("stop_reason") is not None
        else (
            _solver_stop_reason(plan)
            if plan is not None
            else "not_started"
        )
    )
    lanes = list(_mapping_items(provenance.get("lanes")))
    return {
        "status": status,
        "stop_reason": stop_reason,
        "budget": deepcopy(_mapping(provenance.get("budget"))),
        "frontier_source": provenance.get(
            "frontier_source",
            "not_loaded",
        ),
        "ordered_frontier_digests": deepcopy(
            provenance.get("ordered_frontier_digests", [])
        ),
        "planned_lane_ids": deepcopy(
            provenance.get("lane_prefix_ids", [])
        ),
        "attempted_lane_ids": [
            str(value.get("lane_id", "")) for value in lanes
        ],
        "completed_lane_ids": [
            str(value.get("lane_id", ""))
            for value in lanes
            if not bool(value.get("deadline_reached_after_lane"))
            and str(value.get("status")) != STALE_OR_CANCELLED
        ],
        "candidate_count_before_deduplication": int(
            provenance.get("candidate_count_before_deduplication", 0)
        ),
        "candidate_count_after_deduplication": int(
            provenance.get("candidate_count_after_deduplication", 0)
        ),
        "pareto_candidate_count": int(
            provenance.get("pareto_candidate_count", 0)
        ),
        "pareto_placement_digests": deepcopy(
            provenance.get("pareto_placement_digests", [])
        ),
        "selected": deepcopy(provenance.get("selected")),
        "warm_start": deepcopy(provenance.get("warm_start", {})),
    }


def _problem_with_frontiers(
    base_problem: Free3DPreparedProblem,
    frontiers: tuple[ContainerVariantFrontier, ...],
) -> Free3DPreparedProblem:
    participants = _participants_with_variant_options(
        base_problem.participants,
        frontiers,
    )
    return replace(
        base_problem,
        participants=participants,
        container_variant_frontiers=frontiers,
    )


_CERTIFIED_WITNESS_INCUMBENT_LANE = MinimalLaneSpec(
    "certified_witness_incumbent",
    "not_applicable",
    "not_applicable",
    "not_applicable",
    "certified_witness",
    0,
)
_HIGHS_PRODUCT_LANE = MinimalLaneSpec(
    "external_highs_floor",
    "not_applicable",
    "not_applicable",
    "not_applicable",
    "external_mip_floor",
    0,
)


def _certify_warm_start_incumbent(
    initial_incumbent: Mapping[str, object] | None,
    *,
    problem: Free3DPreparedProblem,
    strategy: SolverStrategy,
    budget: SolverBudget,
    effort_profile: str,
    frontier_source: str,
    ordered_frontier_digests: Sequence[tuple[str, str]],
) -> tuple[_CertifiedProposal | None, dict[str, object]]:
    report: dict[str, object] = {
        "schema_version": "bgig.certified_witness_warm_start.v1",
        "status": "not_supplied",
        "stop_reason": "no_initial_incumbent",
        "source_plan_digest": "",
        "recertified_placement_digest": "",
        "rejection_codes": [],
        "recertification_count": 0,
        "search_continued": True,
        "lane_count_added": 0,
        "cache_hit_claimed": False,
    }
    if initial_incumbent is None:
        return None, report
    report["source_plan_digest"] = str(
        initial_incumbent.get("plan_digest", "")
    )
    try:
        placements = _placements_from_certified_plan(initial_incumbent)
        if not placements:
            raise ValueError("witness has no placements")
        empty_spaces = _rebuild_empty_spaces(placements, problem, budget)
    except (KeyError, TypeError, ValueError, OverflowError) as exc:
        report.update(
            {
                "status": "rejected",
                "stop_reason": "witness_geometry_payload_invalid",
                "rejection_codes": [type(exc).__name__],
            }
        )
        return None, report
    provisional_provenance = {
        "portfolio_schema": MINIMAL_LAYOUT_PORTFOLIO_SCHEMA_V1,
        "effort_profile": effort_profile,
        "lane_id": _CERTIFIED_WITNESS_INCUMBENT_LANE.lane_id,
        "candidate_source": "certified_witness",
        "frontier_source": frontier_source,
        "ordered_frontier_digests": [
            {"container_group_id": key, "digest": value}
            for key, value in ordered_frontier_digests
        ],
        "future_recertification_performed": True,
        "search_continued": True,
        "lane_count_added": 0,
        "finalization_invocation_count": 0,
        "fusion_materialization_invocation_count": 0,
    }
    certified, rejections = certify_minimal_free_3d_plan(
        problem,
        strategy=strategy,
        budget=budget,
        candidate_id="certified-witness-incumbent",
        placements=placements,
        empty_spaces=empty_spaces,
        search_telemetry={"warm_start_recertification_count": 1},
        search_provenance=provisional_provenance,
    )
    if certified is None:
        report.update(
            {
                "status": "rejected",
                "stop_reason": "witness_recertification_rejected",
                "rejection_codes": list(rejections),
                "recertification_count": 1,
            }
        )
        return None, report
    report.update(
        {
            "status": "accepted",
            "stop_reason": "witness_recertified_as_initial_incumbent",
            "recertified_placement_digest": certified.placement_digest,
            "rejection_codes": [],
            "recertification_count": 1,
        }
    )
    return (
        _CertifiedProposal(
            lane=_CERTIFIED_WITNESS_INCUMBENT_LANE,
            seed_participant_id="not_applicable",
            translation_id="witness_identity",
            placements=placements,
            empty_spaces=empty_spaces,
            certified=certified,
            rank_key=_proposal_rank_key(certified),
        ),
        report,
    )


def _placements_from_certified_plan(
    plan: Mapping[str, object],
) -> tuple[Free3DPlacement, ...]:
    placements: list[Free3DPlacement] = []
    for raw in _mapping_items(plan.get("placements")):
        origin = tuple(
            float(_mapping(raw.get("origin_mm"))[axis])
            for axis in _AXES
        )
        world_size = tuple(
            float(_mapping(raw.get("world_size_mm"))[axis])
            for axis in _AXES
        )
        local_size = tuple(
            float(_mapping(raw.get("final_outer_dimensions_mm"))[axis])
            for axis in _AXES
        )
        common = {
            "participant_id": str(raw["id"]),
            "role": str(raw["role"]),
            "name": str(raw["name"]),
            "origin_mm": origin,
            "world_size_mm": world_size,
            "local_size_mm": local_size,
            "rotation_deg_z": int(raw["rotation_deg_z"]),
            "supporting_ids": (),
            "support_coverage_ratio": 1.0,
        }
        if str(raw["role"]) == "container":
            variant = _mapping(raw.get("container_internal_variant_v1"))
            placements.append(
                VariantFree3DPlacement(
                    **common,
                    container_variant_id=str(variant["variant_id"]),
                    container_variant_digest=str(
                        variant["geometry_digest"]
                    ),
                    container_variant_canonical=bool(
                        variant["canonical"]
                    ),
                )
            )
        else:
            placements.append(Free3DPlacement(**common))
    return tuple(placements)


def _aggregate_lane_telemetry(
    lane_reports: Sequence[Mapping[str, object]],
    *,
    elapsed_ms: int,
    deadline_reached: bool,
) -> dict[str, object]:
    aggregate: Counter[str] = Counter()
    for report in lane_reports:
        for key, value in _mapping(report.get("telemetry")).items():
            if isinstance(value, int) and not isinstance(value, bool):
                aggregate[str(key)] += value
    aggregate["lane_count"] = len(lane_reports)
    aggregate["certified_candidates"] = sum(
        int(value.get("certified_candidate_count", 0))
        for value in lane_reports
    )
    return {
        **dict(sorted(aggregate.items())),
        "deep_extension_elapsed_ms": elapsed_ms,
        "deep_extension_deadline_ms": _DEEP_EXTENSION_DEADLINE_MS,
        "deep_extension_deadline_reached": deadline_reached,
    }

def _mapping_items(value: object) -> list[dict[str, object]]:
    if not isinstance(value, list):
        return []
    return [
        dict(item)
        for item in value
        if isinstance(item, Mapping)
    ]


def _anytime_details(
    *,
    normal_plan: Mapping[str, object],
    deep_plan: Mapping[str, object] | None,
    normal_frontier_count: int,
    deep_frontier_count: int,
    elapsed_ms: int | None,
    deadline_reached: bool,
    selected_phase: str | None,
    improved_over_normal: bool,
    stop_reason: str,
) -> dict[str, object]:
    normal_status = _solver_result_status(normal_plan)
    deep_status = (
        _solver_result_status(deep_plan)
        if deep_plan is not None
        else "not_started"
    )
    normal_provenance = _plan_search_provenance(normal_plan)
    raw_incumbent = normal_provenance.get("selected")
    incumbent = (
        dict(raw_incumbent)
        if isinstance(raw_incumbent, Mapping)
        else {}
    )
    incumbent_available = normal_status == SOLUTION_FOUND
    return {
        "policy": "normal_incumbent_then_deep_extension_v1",
        "normal_prefix_completed": normal_status in {
            SOLUTION_FOUND,
            NO_SOLUTION_WITHIN_BUDGET,
        },
        "normal_status": normal_status,
        "normal_budget": dict(_minimal_budget(EFFORT_NORMAL).limits),
        "normal_frontier_count": normal_frontier_count,
        "initial_incumbent_available": incumbent_available,
        "initial_incumbent_profile": (
            EFFORT_NORMAL if incumbent_available else None
        ),
        "initial_incumbent_placement_digest": (
            incumbent.get("placement_digest")
            if incumbent_available
            else None
        ),
        "initial_incumbent_rank_axes": (
            list(_plan_rank_axes(normal_plan))
            if incumbent_available
            else None
        ),
        "deep_status": deep_status,
        "deep_budget": dict(_minimal_budget(EFFORT_DEEP).limits),
        "deep_frontier_count": deep_frontier_count,
        "deep_extension_deadline_ms": _DEEP_EXTENSION_DEADLINE_MS,
        "deep_extension_elapsed_ms": (
            elapsed_ms if elapsed_ms is not None else "not_applicable"
        ),
        "deep_extension_deadline_reached": deadline_reached,
        "selected_phase": selected_phase,
        "improved_over_normal": improved_over_normal,
        "incumbent_preserved": (
            incumbent_available and selected_phase == "normal_incumbent"
        ),
        "stale_cancellation_fail_closed": (
            deep_status == STALE_OR_CANCELLED
            or normal_status == STALE_OR_CANCELLED
        ),
        "stop_reason": stop_reason,
    }


def _combined_anytime_provenance(
    *,
    normal_plan: Mapping[str, object],
    deep_plan: Mapping[str, object],
    normal_frontier_count: int,
    deep_frontier_count: int,
    selected_plan: Mapping[str, object],
    selected_phase: str,
    improved_over_normal: bool,
    stop_reason: str,
    request: Mapping[str, object],
    elapsed_ms: int,
    deadline_reached: bool,
) -> dict[str, object]:
    normal_provenance = _plan_search_provenance(normal_plan)
    deep_provenance = _plan_search_provenance(deep_plan)
    selected_provenance = _plan_search_provenance(selected_plan)
    normal_lanes = _mapping_items(normal_provenance.get("lanes"))
    deep_lanes = _mapping_items(deep_provenance.get("lanes"))
    lanes = normal_lanes + deep_lanes
    pareto_digests = sorted(
        {
            str(value)
            for value in (
                list(normal_provenance.get("pareto_placement_digests", []))
                + list(deep_provenance.get("pareto_placement_digests", []))
            )
        }
    )
    selected = deepcopy(_mapping(selected_provenance.get("selected")))
    selected.update(
        {
            "source_phase": selected_phase,
            "improved_over_normal": improved_over_normal,
            "statement": "best_certified_proposal_found_within_budget",
        }
    )
    provenance = {
        "schema_version": MINIMAL_LAYOUT_PORTFOLIO_SCHEMA_V1,
        "solver_version": MINIMAL_LAYOUT_SOLVER_VERSION,
        "effort_profile": EFFORT_DEEP,
        "request": deepcopy(dict(request)),
        "lane_prefix_ids": [
            lane.lane_id for lane in minimal_lane_specs(EFFORT_DEEP)
        ],
        "attempted_lane_ids": [
            str(value.get("lane_id", "")) for value in lanes
        ],
        "quick_is_prefix_of_normal": True,
        "normal_is_prefix_of_deep": True,
        "budget": dict(_minimal_budget(EFFORT_DEEP).limits),
        "wall_clock_limited": True,
        "deadline_reached": deadline_reached,
        "elapsed_ms": elapsed_ms,
        "stop_reason": stop_reason,
        "frontier_source": selected_provenance.get(
            "frontier_source",
            "not_loaded",
        ),
        "ordered_frontier_digests": deepcopy(
            selected_provenance.get("ordered_frontier_digests", [])
        ),
        "historical_comparator_lane_ids": [
            "historical_legacy_corner",
            "historical_bridge_edge",
        ],
        "lanes": lanes,
        "warm_start": deepcopy(selected_provenance.get("warm_start", {})),
        "candidate_count_before_deduplication": (
            int(
                normal_provenance.get(
                    "candidate_count_before_deduplication",
                    0,
                )
            )
            + int(
                deep_provenance.get(
                    "candidate_count_before_deduplication",
                    0,
                )
            )
        ),
        "candidate_count_after_deduplication": (
            int(
                normal_provenance.get(
                    "candidate_count_after_deduplication",
                    0,
                )
            )
            + int(
                deep_provenance.get(
                    "candidate_count_after_deduplication",
                    0,
                )
            )
        ),
        "candidate_count_scope": (
            "sum_of_phase_local_frontiers_before_cross_phase_selection"
        ),
        "deduplicated_candidate_count": (
            int(
                normal_provenance.get(
                    "deduplicated_candidate_count",
                    0,
                )
            )
            + int(
                deep_provenance.get(
                    "deduplicated_candidate_count",
                    0,
                )
            )
        ),
        "pareto_candidate_count": len(pareto_digests),
        "pareto_placement_digests": pareto_digests,
        "pareto_scope": "union_of_full_phase_pareto_frontiers",
        "ranking_axes": deepcopy(
            selected_provenance.get("ranking_axes", [])
        ),
        "selected": selected,
        "phases": {
            "normal_prefix": _phase_summary(
                normal_plan,
                fallback_status="not_started",
            ),
            "deep_extension": _phase_summary(
                deep_plan,
                fallback_status="not_started",
            ),
        },
        "anytime": _anytime_details(
            normal_plan=normal_plan,
            deep_plan=deep_plan,
            normal_frontier_count=normal_frontier_count,
            deep_frontier_count=deep_frontier_count,
            elapsed_ms=elapsed_ms,
            deadline_reached=deadline_reached,
            selected_phase=selected_phase,
            improved_over_normal=improved_over_normal,
            stop_reason=stop_reason,
        ),
        "symmetry": deepcopy(selected_provenance.get("symmetry", {})),
        "global_solver_trigger": "explicit_call_only",
        "finalization_invocation_count": 0,
        "fusion_materialization_invocation_count": 0,
    }
    external_lane = normal_provenance.get("external_lane")
    if isinstance(external_lane, Mapping):
        provenance["external_lane"] = deepcopy(dict(external_lane))
    provenance["deterministic_digest"] = _digest(provenance)
    return provenance


def _combine_anytime_results(
    *,
    base_problem: Free3DPreparedProblem,
    request: Mapping[str, object],
    normal_plan: Mapping[str, object],
    deep_plan: Mapping[str, object],
    normal_frontiers: tuple[ContainerVariantFrontier, ...],
    normal_digests: tuple[tuple[str, str], ...],
    deep_frontiers: tuple[ContainerVariantFrontier, ...],
    deep_digests: tuple[tuple[str, str], ...],
    deep_source: str,
    elapsed_ms: int,
    deadline_reached: bool,
) -> dict[str, object]:
    normal_solution = _solver_result_status(normal_plan) == SOLUTION_FOUND
    deep_solution = _solver_result_status(deep_plan) == SOLUTION_FOUND
    if not normal_solution and not deep_solution:
        return _build_anytime_failure(
            base_problem=base_problem,
            status=NO_SOLUTION_WITHIN_BUDGET,
            stop_reason=(
                "deep_deadline_reached_without_incumbent"
                if deadline_reached
                else "deep_extension_exhausted_without_incumbent"
            ),
            request=request,
            normal_plan=normal_plan,
            deep_plan=deep_plan,
            normal_frontiers=normal_frontiers,
            normal_digests=normal_digests,
            deep_frontiers=deep_frontiers,
            deep_digests=deep_digests,
            deep_source=deep_source,
            elapsed_ms=elapsed_ms,
            deadline_reached=deadline_reached,
        )

    improved_over_normal = (
        deep_solution
        and (
            not normal_solution
            or _plan_rank_axes(deep_plan) < _plan_rank_axes(normal_plan)
        )
    )
    if improved_over_normal:
        selected_plan = deep_plan
        selected_phase = "deep_extension"
        selected_frontiers = deep_frontiers
        spaces_budget = _minimal_budget(EFFORT_DEEP)
    else:
        selected_plan = normal_plan
        selected_phase = "normal_incumbent"
        selected_frontiers = normal_frontiers
        spaces_budget = _minimal_budget(EFFORT_NORMAL)

    if improved_over_normal and normal_solution:
        stop_reason = "deep_improvement_selected"
    elif improved_over_normal:
        stop_reason = "deep_first_incumbent_selected"
    elif deadline_reached:
        stop_reason = "deep_deadline_reached_incumbent_preserved"
    elif deep_solution:
        stop_reason = "deep_candidate_not_better_incumbent_preserved"
    else:
        stop_reason = "deep_extension_exhausted_incumbent_preserved"

    provenance = _combined_anytime_provenance(
        normal_plan=normal_plan,
        deep_plan=deep_plan,
        normal_frontier_count=len(normal_frontiers),
        deep_frontier_count=len(deep_frontiers),
        selected_plan=selected_plan,
        selected_phase=selected_phase,
        improved_over_normal=improved_over_normal,
        stop_reason=stop_reason,
        request=request,
        elapsed_ms=elapsed_ms,
        deadline_reached=deadline_reached,
    )
    lane_reports = _mapping_items(provenance.get("lanes"))
    selected_problem = _problem_with_frontiers(
        base_problem,
        selected_frontiers,
    )
    placements = _placements_from_certified_plan(selected_plan)
    spaces = _rebuild_empty_spaces(
        placements,
        selected_problem,
        spaces_budget,
    )
    strategy = SolverStrategy(
        MINIMAL_LAYOUT_FAMILY_ID,
        MINIMAL_LAYOUT_SOLVER_VERSION,
    )
    certified, rejections = certify_minimal_free_3d_plan(
        selected_problem,
        strategy=strategy,
        budget=_minimal_budget(EFFORT_DEEP),
        candidate_id=f"anytime-selected-{selected_phase}",
        placements=placements,
        empty_spaces=spaces,
        search_telemetry=_aggregate_lane_telemetry(
            lane_reports,
            elapsed_ms=elapsed_ms,
            deadline_reached=deadline_reached,
        ),
        search_provenance=provenance,
    )
    if certified is None:
        return _build_anytime_failure(
            base_problem=base_problem,
            status=NO_SOLUTION_WITHIN_BUDGET,
            stop_reason="anytime_selected_candidate_revalidation_failed",
            request=request,
            normal_plan=normal_plan,
            deep_plan=deep_plan,
            normal_frontiers=normal_frontiers,
            normal_digests=normal_digests,
            deep_frontiers=deep_frontiers,
            deep_digests=deep_digests,
            deep_source=deep_source,
            elapsed_ms=elapsed_ms,
            deadline_reached=deadline_reached,
            extra_rejection_codes=rejections,
        )
    return certified.plan


def _build_anytime_failure(
    *,
    base_problem: Free3DPreparedProblem,
    status: str,
    stop_reason: str,
    request: Mapping[str, object],
    normal_plan: Mapping[str, object],
    deep_plan: Mapping[str, object] | None,
    normal_frontiers: tuple[ContainerVariantFrontier, ...],
    normal_digests: tuple[tuple[str, str], ...],
    deep_frontiers: tuple[ContainerVariantFrontier, ...],
    deep_digests: tuple[tuple[str, str], ...],
    deep_source: str,
    elapsed_ms: int | None,
    deadline_reached: bool,
    extra_rejection_codes: Sequence[str] = (),
) -> dict[str, object]:
    normal_provenance = _plan_search_provenance(normal_plan)
    deep_provenance = _plan_search_provenance(deep_plan)
    lanes = (
        _mapping_items(normal_provenance.get("lanes"))
        + _mapping_items(deep_provenance.get("lanes"))
    )
    rejection_codes = {
        str(value.get("code"))
        for plan in (normal_plan, deep_plan)
        if plan is not None
        for value in _mapping_items(plan.get("diagnostics"))
        if value.get("code")
    }
    rejection_codes.update(str(value) for value in extra_rejection_codes)
    failure = _failure_plan(
        status=status,
        stop_reason=stop_reason,
        strategy=SolverStrategy(
            MINIMAL_LAYOUT_FAMILY_ID,
            MINIMAL_LAYOUT_SOLVER_VERSION,
        ),
        budget=_minimal_budget(EFFORT_DEEP),
        request=request,
        project_name=str(base_problem.project["project_name"]),
        requested_container_count=base_problem.requested_container_count,
        rejection_codes=tuple(sorted(rejection_codes)),
        lane_reports=lanes,
        frontier_source=deep_source,
        ordered_frontier_digests=deep_digests,
        external_lane=(
            normal_provenance.get("external_lane")
            if isinstance(normal_provenance.get("external_lane"), Mapping)
            else None
        ),
    )
    solver = _mapping(failure["solver"])
    portfolio = deepcopy(_mapping(solver["search"]))
    normal_phase = _phase_summary(
        normal_plan,
        fallback_status="not_started",
    )
    deep_phase = _phase_summary(
        deep_plan,
        fallback_status="not_started",
    )
    pareto_digests = sorted(
        {
            str(value)
            for value in (
                list(
                    normal_provenance.get(
                        "pareto_placement_digests",
                        [],
                    )
                )
                + list(
                    deep_provenance.get(
                        "pareto_placement_digests",
                        [],
                    )
                )
            )
        }
    )
    portfolio.update(
        {
            "solver_version": MINIMAL_LAYOUT_SOLVER_VERSION,
            "effort_profile": EFFORT_DEEP,
            "request": deepcopy(dict(request)),
            "lane_prefix_ids": [
                lane.lane_id
                for lane in minimal_lane_specs(EFFORT_DEEP)
            ],
            "attempted_lane_ids": [
                str(value.get("lane_id", "")) for value in lanes
            ],
            "budget": dict(_minimal_budget(EFFORT_DEEP).limits),
            "wall_clock_limited": elapsed_ms is not None,
            "deadline_reached": deadline_reached,
            "elapsed_ms": (
                elapsed_ms
                if elapsed_ms is not None
                else "not_applicable"
            ),
            "stop_reason": stop_reason,
            "frontier_source": deep_source,
            "ordered_frontier_digests": [
                {
                    "container_group_id": key,
                    "digest": value,
                }
                for key, value in deep_digests
            ],
            "lanes": lanes,
            "candidate_count_before_deduplication": (
                normal_phase[
                    "candidate_count_before_deduplication"
                ]
                + deep_phase[
                    "candidate_count_before_deduplication"
                ]
            ),
            "candidate_count_after_deduplication": (
                normal_phase[
                    "candidate_count_after_deduplication"
                ]
                + deep_phase[
                    "candidate_count_after_deduplication"
                ]
            ),
            "candidate_count_scope": (
                "sum_of_phase_local_frontiers_before_cross_phase_selection"
            ),
            "pareto_candidate_count": len(pareto_digests),
            "pareto_placement_digests": pareto_digests,
            "pareto_scope": "union_of_full_phase_pareto_frontiers",
            "phases": {
                "normal_prefix": normal_phase,
                "deep_extension": deep_phase,
            },
            "anytime": _anytime_details(
                normal_plan=normal_plan,
                deep_plan=deep_plan,
                normal_frontier_count=len(normal_frontiers),
                deep_frontier_count=len(deep_frontiers),
                elapsed_ms=elapsed_ms,
                deadline_reached=deadline_reached,
                selected_phase=None,
                improved_over_normal=False,
                stop_reason=stop_reason,
            ),
            "finalization_invocation_count": 0,
            "fusion_materialization_invocation_count": 0,
        }
    )
    portfolio.pop("deterministic_digest", None)
    portfolio["deterministic_digest"] = _digest(portfolio)
    solver["search"] = deepcopy(portfolio)
    solver["deterministic"] = elapsed_ms is None
    telemetry = _mapping(solver["telemetry"])
    telemetry["elapsed_ms"] = (
        elapsed_ms if elapsed_ms is not None else "not_applicable"
    )
    telemetry["search_stop_reason"] = stop_reason
    counters = _mapping(telemetry.get("counters"))
    counters["lane_count"] = len(lanes)
    counters["initial_incumbent_available"] = (
        _solver_result_status(normal_plan) == SOLUTION_FOUND
    )
    telemetry["counters"] = counters
    solver["telemetry"] = telemetry
    failure["solver"] = solver
    minimal = _mapping(failure["minimal_layout"])
    minimal["search_provenance"] = deepcopy(portfolio)
    failure["minimal_layout"] = minimal
    failure.pop("plan_digest", None)
    failure["plan_digest"] = _digest(failure)
    return failure

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
        limits[key] = (
            min(int(limits[key]), cap)
            if key in limits
            else cap
        )
    return SolverBudget(
        source.family_id,
        effort_profile,
        tuple(sorted(limits.items())),
    )


def _monotonic_ms() -> float:
    return perf_counter() * 1000.0


def _remaining_deadline_ms(
    deadline_at_ms: float | None,
) -> float | None:
    if deadline_at_ms is None:
        return None
    return max(0.0, deadline_at_ms - _monotonic_ms())


def _deadline_has_expired(deadline_at_ms: float | None) -> bool:
    remaining = _remaining_deadline_ms(deadline_at_ms)
    return remaining is not None and remaining < 1.0


def _budget_with_elapsed_cap(
    budget: SolverBudget,
    remaining_ms: float,
) -> SolverBudget:
    limits = dict(budget.limits)
    limits["max_elapsed_ms"] = min(
        int(limits["max_elapsed_ms"]),
        max(1, int(remaining_ms)),
    )
    return SolverBudget(
        budget.family_id,
        budget.effort_profile,
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
    warm_start: Mapping[str, object] | None = None,
    external_lane: Mapping[str, object] | None = None,
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
        "warm_start": deepcopy(
            dict(warm_start)
            if warm_start is not None
            else {
                "status": "not_supplied",
                "stop_reason": "no_initial_incumbent",
                "search_continued": True,
                "lane_count_added": 0,
            }
        ),
        "candidate_count_before_deduplication": 0,
        "candidate_count_after_deduplication": 0,
        "pareto_candidate_count": 0,
        "global_solver_trigger": "explicit_call_only",
        "finalization_invocation_count": 0,
        "fusion_materialization_invocation_count": 0,
    }
    if external_lane is not None:
        portfolio["external_lane"] = deepcopy(dict(external_lane))
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
