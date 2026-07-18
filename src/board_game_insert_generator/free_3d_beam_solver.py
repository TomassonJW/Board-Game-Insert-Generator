"""Bounded free-3D beam feasibility search with deferred continuous closure.

The greedy family keeps one minimum-envelope trajectory. This module retains
several EP/EMS states, places every requested minimum envelope first and leaves
continuous Auto/Target growth to free_3d_continuous_closure. Keeping those
phases separate prevents a large early body from pruning a feasible dense
layout. Top-inset constraints are evaluated during search, while the common
product validator remains the final authority.
"""
from __future__ import annotations

from dataclasses import dataclass
from time import perf_counter
from typing import Callable, Iterable, Mapping

from board_game_insert_generator.free_3d_greedy_solver import (
    FREE_3D_GEOMETRY_VALIDATION_V1,
    EmptySpace,
    Free3DGeometryAdmission,
    Free3DPlacement,
    TopInsetZone,
    _Counters,
    _aligned_face_count,
    _box_dimensions,
    _digest,
    _fits_in_space,
    _inside_box,
    _initial_extreme_points,
    _mapping,
    _minimum_local,
    _necessary_bound_failure,
    _non_negative,
    _orientations,
    _participant,
    _round,
    _rounded_point,
    _separated_from_placements,
    _subtract_placement_from_spaces,
    _support_at,
    _subtract_forbidden_spaces,
    _top_inset_option_allowed,
    _update_extreme_points,
    _upper,
    _validated_forbidden_spaces,
    _validated_top_inset_zones,
    _volume,
)
from board_game_insert_generator.solver_contract import (
    PlacementSnapshot,
    SolverBudget,
    SolverCandidate,
    SolverStrategy,
    ValidationCheck,
    validate_placement_geometry,
)


FREE_3D_BEAM_FAMILY_ID = "free_3d_beam"
FREE_3D_BEAM_VERSION = "bgig.free_3d_beam.v2"
BEAM_SEARCH_LEGACY_EMS = "legacy_ems_v1"
BEAM_SEARCH_BRIDGE_EMS = "bridge_ems_v2"
BEAM_SEARCH_INTERNAL_VARIANTS = "internal_variants_v1"
_EPSILON = 0.0001
_AXES = ("x", "y", "z")


class Free3DBeamError(ValueError):
    """Raised when an internal beam problem or its hard budget is malformed."""


@dataclass(frozen=True)
class Free3DBeamSolution:
    """One complete geometry retained for product-plan reconstruction."""

    candidate: SolverCandidate
    geometry_admission: Free3DGeometryAdmission
    placements: tuple[Free3DPlacement, ...]
    empty_spaces: tuple[EmptySpace, ...]
    score_key: tuple[object, ...]


@dataclass(frozen=True)
class VariantFree3DPlacement(Free3DPlacement):
    """Placement retaining the certified local variant chosen by the beam."""

    container_variant_id: str
    container_variant_digest: str
    container_variant_canonical: bool


@dataclass(frozen=True)
class Free3DBeamTelemetry:
    """Deterministic counters; wall-clock time is intentionally excluded."""

    search_states: int
    placement_trials: int
    feasible_options: int
    states_generated: int
    states_deduplicated: int
    states_pruned_by_width: int
    states_pruned_by_space_limit: int
    geometric_completions: int
    completions_with_printable_residual: int
    admitted_complete_solutions: int
    maximum_beam_width_retained: int
    maximum_depth_reached: int
    maximum_empty_spaces_retained: int
    maximum_extreme_points_retained: int
    budget_exhausted: bool
    cancelled: bool
    timed_out: bool


@dataclass(frozen=True)
class Free3DBeamExecution:
    """One bounded, deterministic-unless-time-limited beam execution."""

    strategy: SolverStrategy
    budget: SolverBudget
    status: str
    stop_reason: str
    solutions: tuple[Free3DBeamSolution, ...]
    remaining_best_participant_ids: tuple[str, ...]
    telemetry: Free3DBeamTelemetry
    deterministic_digest: str


@dataclass(frozen=True)
class _BeamState:
    placements: tuple[Free3DPlacement, ...]
    remaining_ids: tuple[str, ...]
    spaces: tuple[EmptySpace, ...]
    points: frozenset[tuple[float, float, float]]


@dataclass(frozen=True)
class _BeamOption:
    participant: dict[str, object]
    origin: tuple[float, float, float]
    world_size: tuple[float, float, float]
    local_size: tuple[float, float, float]
    rotation_deg_z: int
    supporting_ids: tuple[str, ...]
    support_ratio: float
    containing_space_volume: float
    container_variant_id: str = ""
    container_variant_digest: str = ""
    container_variant_canonical: bool = False
    container_variant_order: int = 0


@dataclass
class _BeamCounters:
    search_states: int = 0
    placement_trials: int = 0
    feasible_options: int = 0
    states_generated: int = 0
    states_deduplicated: int = 0
    states_pruned_by_width: int = 0
    states_pruned_by_space_limit: int = 0
    geometric_completions: int = 0
    completions_with_printable_residual: int = 0
    maximum_beam_width_retained: int = 1
    maximum_depth_reached: int = 0
    maximum_empty_spaces_retained: int = 1
    maximum_extreme_points_retained: int = 1
    budget_exhausted: bool = False
    cancelled: bool = False
    timed_out: bool = False


def solve_free_3d_beam(
    participants: Iterable[Mapping[str, object]],
    box: Mapping[str, object],
    storage_height_mm: float,
    between_bodies_xy_mm: float,
    *,
    box_perimeter_xy_mm: float,
    between_bodies_z_mm: float,
    budget: SolverBudget,
    cancel_check: Callable[[], bool] | None = None,
    forbidden_spaces: Iterable[EmptySpace] = (),
    top_inset_zones: Iterable[TopInsetZone] = (),
    search_variant: str = BEAM_SEARCH_BRIDGE_EMS,
) -> Free3DBeamExecution:
    """Search several minimum-envelope EP/EMS states under explicit hard limits."""

    strategy = SolverStrategy(FREE_3D_BEAM_FAMILY_ID, FREE_3D_BEAM_VERSION)
    if search_variant not in {
        BEAM_SEARCH_LEGACY_EMS,
        BEAM_SEARCH_BRIDGE_EMS,
        BEAM_SEARCH_INTERNAL_VARIANTS,
    }:
        raise Free3DBeamError(f"Unsupported beam search variant: {search_variant}.")
    limits = _budget_limits(budget)
    values = tuple(_participant(value, index) for index, value in enumerate(participants))
    dimensions = _box_dimensions(box, storage_height_mm)
    xy_clearance = _non_negative(between_bodies_xy_mm, "between_bodies_xy_mm")
    box_clearance = _non_negative(box_perimeter_xy_mm, "box_perimeter_xy_mm")
    z_clearance = _non_negative(between_bodies_z_mm, "between_bodies_z_mm")
    root_size = (
        dimensions[0] - 2.0 * box_clearance,
        dimensions[1] - 2.0 * box_clearance,
        dimensions[2],
    )
    if any(value <= _EPSILON for value in root_size):
        raise Free3DBeamError("The useful box must remain positive after perimeter clearance.")
    if not values:
        raise Free3DBeamError("At least one canonical participant is required.")

    participants_by_id = {str(value["id"]): value for value in values}
    if len(participants_by_id) != len(values):
        raise Free3DBeamError("Participant identifiers must be unique.")
    root_origin = _rounded_point((box_clearance, box_clearance, 0.0))
    root_space = EmptySpace(root_origin, _rounded_point(root_size))
    forbidden = _validated_forbidden_spaces(forbidden_spaces, dimensions)
    inset_zones = _validated_top_inset_zones(top_inset_zones, dimensions)
    initial_spaces = _subtract_forbidden_spaces([root_space], forbidden)
    if not initial_spaces:
        raise Free3DBeamError("The forbidden spaces consume the whole useful box.")
    initial = _BeamState(
        placements=(),
        remaining_ids=tuple(sorted(participants_by_id)),
        spaces=tuple(initial_spaces),
        points=(
            frozenset(space.origin_mm for space in initial_spaces)
            if search_variant == BEAM_SEARCH_LEGACY_EMS
            else frozenset(_initial_extreme_points(initial_spaces, inset_zones))
        ),
    )
    input_digest = _digest(
        {
            "strategy": strategy.__dict__,
            "search_variant": search_variant,
            "budget": {
                "family_id": budget.family_id,
                "effort_profile": budget.effort_profile,
                "limits": budget.limits,
            },
            "participants": values,
            "box": dimensions,
            "clearances": (xy_clearance, box_clearance, z_clearance),
            "forbidden_spaces": [
                {"origin_mm": item.origin_mm, "size_mm": item.size_mm}
                for item in forbidden
            ],
            "top_inset_zones": [item.__dict__ for item in inset_zones],
        }
    )
    formal_impossibility = (
        None
        if search_variant == BEAM_SEARCH_INTERNAL_VARIANTS
        else _necessary_bound_failure(values, root_size)
    )
    counters = _BeamCounters()
    if formal_impossibility is not None:
        return _execution(
            strategy,
            budget,
            "proven_impossible",
            formal_impossibility,
            (),
            initial,
            counters,
            input_digest,
        )

    started_at = perf_counter()
    beam = [initial]
    solutions: list[Free3DBeamSolution] = []
    best_state = initial
    while beam and not solutions_at_limit(solutions, limits):
        if _should_stop(cancel_check, started_at, limits, counters):
            break
        next_states: list[_BeamState] = []
        for state in beam:
            best_state = min((best_state, state), key=_state_score)
            if _should_stop(cancel_check, started_at, limits, counters):
                break
            participant_options = _participant_branches(
                state,
                participants_by_id,
                dimensions,
                xy_clearance,
                z_clearance,
                counters,
                limits,
                inset_zones,
                search_variant,
            )
            for _, options in participant_options:
                for option in options[: limits["max_options_per_participant"]]:
                    if counters.search_states >= limits["max_search_states"]:
                        counters.budget_exhausted = True
                        break
                    advanced = _advance_state(
                        state,
                        option,
                        xy_clearance,
                        z_clearance,
                        counters,
                        limits,
                    )
                    if advanced is None:
                        continue
                    if (
                        search_variant == BEAM_SEARCH_LEGACY_EMS
                        and advanced.remaining_ids
                        and not _remaining_participants_fit(advanced, participants_by_id)
                    ):
                        continue
                    counters.search_states += 1
                    counters.states_generated += 1
                    counters.maximum_depth_reached = max(
                        counters.maximum_depth_reached, len(advanced.placements)
                    )
                    if not advanced.remaining_ids:
                        counters.geometric_completions += 1
                        if advanced.spaces:
                            counters.completions_with_printable_residual += 1
                        solution = _solution(
                            strategy,
                            input_digest,
                            advanced,
                            dimensions,
                            xy_clearance,
                            box_clearance,
                            z_clearance,
                            len(solutions),
                        )
                        if solution.geometry_admission.admitted:
                            solutions.append(solution)
                        continue
                    next_states.append(advanced)
                if counters.budget_exhausted or solutions_at_limit(solutions, limits):
                    break
            if counters.budget_exhausted or solutions_at_limit(solutions, limits):
                break

        if solutions_at_limit(solutions, limits) or counters.budget_exhausted:
            break
        unique: dict[str, _BeamState] = {}
        for state in next_states:
            signature = _state_signature(state)
            previous = unique.get(signature)
            if previous is None or _state_score(state) < _state_score(previous):
                unique[signature] = state
            else:
                counters.states_deduplicated += 1
        ordered = sorted(unique.values(), key=_state_score)
        if len(ordered) > limits["beam_width"]:
            counters.states_pruned_by_width += len(ordered) - limits["beam_width"]
        beam = ordered[: limits["beam_width"]]
        counters.maximum_beam_width_retained = max(counters.maximum_beam_width_retained, len(beam))
        if beam:
            best_state = min((best_state, beam[0]), key=_state_score)

    ordered_solutions = tuple(sorted(solutions, key=lambda value: value.score_key))
    if counters.cancelled:
        status, stop_reason = "stale_or_cancelled", "cancelled_by_caller"
    elif counters.timed_out:
        status, stop_reason = "no_solution_within_budget", "hard_time_budget_reached"
    elif ordered_solutions:
        status, stop_reason = "solution_found", "beam_feasible_geometry_found"
    elif counters.budget_exhausted:
        status, stop_reason = "no_solution_within_budget", "hard_budget_reached"
    else:
        status, stop_reason = "no_solution_within_budget", "beam_frontier_exhausted"
    return _execution(
        strategy,
        budget,
        status,
        stop_reason,
        ordered_solutions,
        best_state,
        counters,
        input_digest,
    )


def solutions_at_limit(solutions: list[Free3DBeamSolution], limits: dict[str, int]) -> bool:
    return len(solutions) >= limits["max_complete_candidates"]


def _participant_branches(
    state: _BeamState,
    participants_by_id: dict[str, dict[str, object]],
    box: tuple[float, float, float],
    xy_clearance: float,
    z_clearance: float,
    counters: _BeamCounters,
    limits: dict[str, int],
    top_inset_zones: tuple[TopInsetZone, ...],
    search_variant: str,
) -> list[tuple[dict[str, object], list[_BeamOption]]]:
    evaluated: list[tuple[tuple[object, ...], dict[str, object], list[_BeamOption]]] = []
    placements = list(state.placements)
    spaces = list(state.spaces)
    points = set(state.points)
    for participant_id in state.remaining_ids:
        participant = participants_by_id[participant_id]
        options = _placement_options(
            participant,
            spaces,
            points,
            placements,
            box,
            xy_clearance,
            z_clearance,
            counters,
            limits,
            top_inset_zones,
            search_variant,
        )
        if counters.budget_exhausted:
            break
        if not options:
            continue
        modes = _mapping(participant["dimension_modes"])
        constrained_axes = sum(str(modes[axis]) == "fixed" for axis in _AXES)
        key = (
            len(options),
            -constrained_axes,
            -_volume(_minimum_local(participant)),
            participant_id,
        )
        evaluated.append((key, participant, options))
    evaluated.sort(key=lambda item: item[0])
    return [
        (participant, sorted(options, key=lambda item: _option_score(item, list(state.placements))))
        for _, participant, options in evaluated[: limits["max_participant_branches"]]
    ]


def _placement_options(
    participant: dict[str, object],
    spaces: list[EmptySpace],
    points: set[tuple[float, float, float]],
    placements: list[Free3DPlacement],
    box: tuple[float, float, float],
    xy_clearance: float,
    z_clearance: float,
    counters: _BeamCounters,
    limits: dict[str, int],
    top_inset_zones: tuple[TopInsetZone, ...],
    search_variant: str,
) -> list[_BeamOption]:
    result: dict[tuple[object, ...], _BeamOption] = {}
    for selected_participant in _variant_participants(
        participant,
        limits,
        search_variant,
    ):
        raw_variant = selected_participant.get("selected_container_variant_v1")
        variant = raw_variant if isinstance(raw_variant, dict) else {}
        for rotation, minimum_world, minimum_local in _orientations(selected_participant):
            for point in sorted(points, key=lambda value: (value[2], value[1], value[0])):
                if search_variant == BEAM_SEARCH_LEGACY_EMS:
                    search_spaces = tuple(
                        space
                        for space in spaces
                        if _fits_in_space(point, minimum_world, space)
                    )
                else:
                    # A valid body may bridge several lower supports and therefore
                    # span several EMS. EMS generate points; collision, clearance,
                    # box and support checks remain authoritative.
                    search_spaces = (
                        EmptySpace(
                            point,
                            _rounded_point(
                                tuple(box[index] - point[index] for index in range(3))
                            ),
                        ),
                    )
                for space in search_spaces:
                    for world_size, local_size in _dimension_variants(
                        selected_participant,
                        point,
                        space,
                        rotation,
                        minimum_world,
                        minimum_local,
                    ):
                        if counters.placement_trials >= limits["max_placement_trials"]:
                            counters.budget_exhausted = True
                            return []
                        counters.placement_trials += 1
                        if not _inside_box(point, world_size, box):
                            continue
                        inset_allowed = (
                            _legacy_top_inset_option_allowed(
                                selected_participant,
                                point,
                                world_size,
                                box[2],
                                top_inset_zones,
                            )
                            if search_variant == BEAM_SEARCH_LEGACY_EMS
                            else _top_inset_option_allowed(
                                selected_participant,
                                point,
                                world_size,
                                rotation,
                                box[2],
                                top_inset_zones,
                            )
                        )
                        if not inset_allowed:
                            continue
                        if not _separated_from_placements(
                            point,
                            world_size,
                            selected_participant,
                            placements,
                            xy_clearance,
                            z_clearance,
                        ):
                            continue
                        supporting_ids, support_ratio = _support_at(
                            point,
                            world_size,
                            placements,
                            selected_participant,
                            z_clearance,
                        )
                        if point[2] > _EPSILON and support_ratio + _EPSILON < 0.25:
                            continue
                        option = _BeamOption(
                            participant=selected_participant,
                            origin=point,
                            world_size=world_size,
                            local_size=local_size,
                            rotation_deg_z=rotation,
                            supporting_ids=supporting_ids,
                            support_ratio=support_ratio,
                            containing_space_volume=space.volume_mm3,
                            container_variant_id=str(variant.get("variant_id", "")),
                            container_variant_digest=str(
                                variant.get("geometry_digest", "")
                            ),
                            container_variant_canonical=bool(
                                variant.get("canonical", False)
                            ),
                            container_variant_order=int(
                                variant.get("frontier_index", 0)
                            ),
                        )
                        result[
                            (
                                point,
                                world_size,
                                rotation,
                                option.container_variant_digest,
                            )
                        ] = option
    counters.feasible_options += len(result)
    return list(result.values())


def _variant_participants(
    participant: dict[str, object],
    limits: dict[str, int],
    search_variant: str,
) -> tuple[dict[str, object], ...]:
    if search_variant != BEAM_SEARCH_INTERNAL_VARIANTS:
        return (participant,)
    raw_options = participant.get("container_internal_variant_options_v1")
    if not isinstance(raw_options, list) or not raw_options:
        return (participant,)
    maximum = max(1, int(limits.get("max_variant_options_per_expansion", 1)))
    result: list[dict[str, object]] = []
    for raw_option in raw_options[:maximum]:
        option = _mapping(raw_option)
        minimum = _mapping(option["minimum_outer_envelope_mm"])
        selected = dict(participant)
        selected["minimum_local_mm"] = {
            axis: float(minimum[axis]) for axis in _AXES
        }
        selected["selected_container_variant_v1"] = dict(option)
        hint = selected.get("top_inset_search_hint_v1")
        raw_cavities = option.get("cavities")
        if isinstance(hint, dict) and isinstance(raw_cavities, list):
            selected_hint = dict(hint)
            selected_hint["cavities"] = [
                {
                    "local_origin_mm": dict(_mapping(value)["local_origin_mm"]),
                    "inner_dimensions_mm": dict(
                        _mapping(value)["inner_dimensions_mm"]
                    ),
                }
                for value in raw_cavities
            ]
            selected["top_inset_search_hint_v1"] = selected_hint
        result.append(selected)
    return tuple(result)

def _dimension_variants(
    participant: dict[str, object],
    point: tuple[float, float, float],
    space: EmptySpace,
    rotation: int,
    minimum_world: tuple[float, float, float],
    minimum_local: tuple[float, float, float],
) -> tuple[tuple[tuple[float, float, float], tuple[float, float, float]], ...]:
    upper = _upper(space)
    maximum_world = tuple(_round(upper[index] - point[index]) for index in range(3))
    modes = _mapping(participant["dimension_modes"])
    targets = _mapping(participant["target_local_mm"])
    world_to_local = (1, 0, 2) if rotation == 90 else (0, 1, 2)

    bases = {minimum_world}
    target_world = list(minimum_world)
    for world_axis, local_axis in enumerate(world_to_local):
        target = targets[_AXES[local_axis]]
        if str(modes[_AXES[local_axis]]) == "target" and isinstance(target, (int, float)):
            target_world[world_axis] = min(
                maximum_world[world_axis], max(minimum_world[world_axis], float(target))
            )
    bases.add(_rounded_point(tuple(target_world)))
    # Feasibility search stays compact: continuous growth is handled only after
    # every requested body has a valid placement.  Mixing EMS-sized expansion
    # into this phase prunes viable dense layouts before they can complete.
    variants = set(bases)

    result = []
    for world in sorted(variants):
        local = (world[1], world[0], world[2]) if rotation == 90 else world
        if any(local[index] + _EPSILON < minimum_local[index] for index in range(3)):
            continue
        result.append((world, _rounded_point(local)))
    return tuple(result)


def _advance_state(
    state: _BeamState,
    option: _BeamOption,
    xy_clearance: float,
    z_clearance: float,
    counters: _BeamCounters,
    limits: dict[str, int],
) -> _BeamState | None:
    common = {
        "participant_id": str(option.participant["id"]),
        "role": str(option.participant["role"]),
        "name": str(option.participant["name"]),
        "origin_mm": _rounded_point(option.origin),
        "world_size_mm": _rounded_point(option.world_size),
        "local_size_mm": _rounded_point(option.local_size),
        "rotation_deg_z": option.rotation_deg_z,
        "supporting_ids": option.supporting_ids,
        "support_coverage_ratio": _round(option.support_ratio),
    }
    placement = (
        VariantFree3DPlacement(
            **common,
            container_variant_id=option.container_variant_id,
            container_variant_digest=option.container_variant_digest,
            container_variant_canonical=option.container_variant_canonical,
        )
        if option.container_variant_id
        else Free3DPlacement(**common)
    )
    scratch = _Counters()
    spaces = _subtract_placement_from_spaces(
        list(state.spaces),
        placement,
        xy_clearance,
        z_clearance,
        scratch,
        {
            "max_empty_spaces": limits["max_empty_spaces"],
            "max_extreme_points": limits["max_extreme_points"],
            "max_placement_trials": limits["max_placement_trials"],
            "max_search_states": limits["max_search_states"],
        },
    )
    if scratch.budget_exhausted:
        counters.states_pruned_by_space_limit += 1
        return None
    points = _update_extreme_points(
        set(state.points),
        placement,
        spaces,
        xy_clearance,
        z_clearance,
        scratch,
        {
            "max_empty_spaces": limits["max_empty_spaces"],
            "max_extreme_points": limits["max_extreme_points"],
            "max_placement_trials": limits["max_placement_trials"],
            "max_search_states": limits["max_search_states"],
        },
    )
    if scratch.budget_exhausted:
        counters.states_pruned_by_space_limit += 1
        return None
    counters.maximum_empty_spaces_retained = max(
        counters.maximum_empty_spaces_retained, len(spaces)
    )
    counters.maximum_extreme_points_retained = max(
        counters.maximum_extreme_points_retained, len(points)
    )
    return _BeamState(
        placements=state.placements + (placement,),
        remaining_ids=tuple(
            value for value in state.remaining_ids if value != placement.participant_id
        ),
        spaces=tuple(spaces),
        points=frozenset(points),
    )


def _remaining_participants_fit(
    state: _BeamState,
    participants_by_id: dict[str, dict[str, object]],
) -> bool:
    """Preserve the historical EMS prune only in the legacy search variant."""

    for participant_id in state.remaining_ids:
        participant = participants_by_id[participant_id]
        if not any(
            all(
                world_size[index] <= space.size_mm[index] + _EPSILON
                for index in range(3)
            )
            for _, world_size, _ in _orientations(participant)
            for space in state.spaces
        ):
            return False
    return True


def _legacy_top_inset_option_allowed(
    participant: Mapping[str, object],
    origin: tuple[float, float, float],
    world_size: tuple[float, float, float],
    storage_height_mm: float,
    zones: tuple[TopInsetZone, ...],
) -> bool:
    """Keep the validated H01 search ordering as a portfolio baseline."""

    body_top = origin[2] + world_size[2]
    minimum_height = _minimum_local(participant)[2]
    z_mode = str(_mapping(participant["dimension_modes"])["z"])
    for zone in zones:
        if not (
            origin[0] < zone.origin_xy_mm[0] + zone.size_xy_mm[0] - _EPSILON
            and zone.origin_xy_mm[0] < origin[0] + world_size[0] - _EPSILON
            and origin[1] < zone.origin_xy_mm[1] + zone.size_xy_mm[1] - _EPSILON
            and zone.origin_xy_mm[1] < origin[1] + world_size[1] - _EPSILON
        ):
            continue
        if body_top <= zone.support_plane_z_mm + _EPSILON:
            continue
        if storage_height_mm - origin[2] + _EPSILON < minimum_height + zone.inset_depth_mm:
            return False
        if z_mode == "fixed" and abs(body_top - storage_height_mm) > 0.001:
            return False
    return True


def _solution(
    strategy: SolverStrategy,
    input_digest: str,
    state: _BeamState,
    box: tuple[float, float, float],
    xy_clearance: float,
    box_clearance: float,
    z_clearance: float,
    index: int,
) -> Free3DBeamSolution:
    placements = tuple(sorted(state.placements, key=lambda item: item.participant_id))
    plan_digest = _digest(
        {
            "input_digest": input_digest,
            "placements": [value.__dict__ for value in placements],
            "printable_ems_remaining": [value.__dict__ for value in state.spaces],
        }
    )
    snapshots = tuple(
        PlacementSnapshot(
            placement_id=value.participant_id,
            role=value.role,
            origin_mm=value.origin_mm,
            size_mm=value.world_size_mm,
            rotation_deg_z=value.rotation_deg_z,
        )
        for value in placements
    )
    minimum_support = min((value.support_coverage_ratio for value in placements), default=1.0)
    z_levels = float(len({value.origin_mm[2] for value in placements}))
    body_volume = sum(_volume(value.world_size_mm) for value in placements)
    candidate = SolverCandidate(
        strategy=strategy,
        candidate_id=f"free_3d_beam:complete:{index}",
        plan_digest=plan_digest,
        placements=snapshots,
        score_breakdown=(
            ("body_volume_mm3", _round(body_volume)),
            ("minimum_support_ratio", _round(minimum_support)),
            ("printable_ems_remaining", float(len(state.spaces))),
            ("z_start_levels", z_levels),
        ),
        automatic_body_count=0,
    )
    raw = [
        {
            "id": value.participant_id,
            "role": value.role,
            "origin_mm": dict(zip(_AXES, value.origin_mm)),
            "world_size_mm": dict(zip(_AXES, value.world_size_mm)),
            "rotation_deg_z": value.rotation_deg_z,
        }
        for value in placements
    ]
    geometry = validate_placement_geometry(
        raw,
        dict(zip(_AXES, box)),
        box[2],
        xy_clearance,
        box_clearance,
        z_clearance,
    )
    checks = (
        ValidationCheck("inside_box", bool(geometry["inside_box"]), "OUTSIDE_USEFUL_BOX"),
        ValidationCheck(
            "box_xy_clearance",
            bool(geometry["box_xy_clearance_respected"]),
            "BOX_XY_CLEARANCE",
        ),
        ValidationCheck("no_collisions", bool(geometry["no_collisions"]), "BODY_COLLISION"),
        ValidationCheck(
            "between_body_clearance",
            bool(geometry["clearances_respected"]),
            "BODY_CLEARANCE",
        ),
        ValidationCheck(
            "minimum_support",
            minimum_support + _EPSILON >= 0.25,
            "SUPPORT_COVERAGE",
        ),
        ValidationCheck("requested_body_feasibility", True, "PARTICIPANT_SET_INCOMPLETE"),
        ValidationCheck("requested_bodies_only", True, "AUTOMATIC_BODY_FORBIDDEN"),
    )
    admission = Free3DGeometryAdmission(
        schema_version=FREE_3D_GEOMETRY_VALIDATION_V1,
        candidate_digest=candidate.digest,
        admitted=all(check.passed for check in checks),
        checks=checks,
    )
    score_key = (
        -_round(minimum_support),
        int(z_levels),
        -_round(body_volume),
        tuple(
            (
                value.participant_id,
                value.origin_mm,
                value.world_size_mm,
                value.rotation_deg_z,
                value.container_variant_digest,
            )
            if isinstance(value, VariantFree3DPlacement)
            else (
                value.participant_id,
                value.origin_mm,
                value.world_size_mm,
                value.rotation_deg_z,
            )
            for value in placements
        ),
    )
    return Free3DBeamSolution(
        candidate,
        admission,
        placements,
        tuple(state.spaces),
        score_key,
    )


def _option_score(option: _BeamOption, placements: list[Free3DPlacement]) -> tuple[object, ...]:
    body_volume = _volume(option.world_size)
    aligned_faces = _aligned_face_count(option, placements)  # type: ignore[arg-type]
    common = (
        -_round(option.support_ratio),
        -aligned_faces,
        _round(body_volume),
        _round(option.origin[2]),
        _round(option.origin[1]),
        _round(option.origin[0]),
    )
    if option.container_variant_digest:
        return common + (
            option.container_variant_order,
            option.rotation_deg_z,
            str(option.participant["id"]),
            option.container_variant_digest,
            option.world_size,
        )
    return common + (
        option.rotation_deg_z,
        str(option.participant["id"]),
        option.world_size,
    )


def _state_score(state: _BeamState) -> tuple[object, ...]:
    residual_upper_bound = sum(space.volume_mm3 for space in state.spaces)
    minimum_support = min((value.support_coverage_ratio for value in state.placements), default=1.0)
    return (
        len(state.remaining_ids),
        len(state.spaces),
        -_round(residual_upper_bound),
        -_round(minimum_support),
        len(state.points),
        _state_signature(state),
    )


def _state_signature(state: _BeamState) -> str:
    return _digest(
        {
            "remaining": state.remaining_ids,
            "placements": [
                {
                    "id": value.participant_id,
                    "origin": value.origin_mm,
                    "size": value.world_size_mm,
                    "rotation": value.rotation_deg_z,
                    **(
                        {
                            "container_variant_digest": (
                                value.container_variant_digest
                            )
                        }
                        if isinstance(value, VariantFree3DPlacement)
                        else {}
                    ),
                }
                for value in sorted(state.placements, key=lambda item: item.participant_id)
            ],
            "spaces": [value.__dict__ for value in state.spaces],
            "points": sorted(state.points),
        }
    )


def _should_stop(
    cancel_check: Callable[[], bool] | None,
    started_at: float,
    limits: dict[str, int],
    counters: _BeamCounters,
) -> bool:
    if cancel_check is not None and cancel_check():
        counters.cancelled = True
        return True
    if (perf_counter() - started_at) * 1000.0 >= limits["max_elapsed_ms"]:
        counters.timed_out = True
        return True
    return counters.budget_exhausted


def _execution(
    strategy: SolverStrategy,
    budget: SolverBudget,
    status: str,
    stop_reason: str,
    solutions: tuple[Free3DBeamSolution, ...],
    best_state: _BeamState,
    counters: _BeamCounters,
    input_digest: str,
) -> Free3DBeamExecution:
    telemetry = Free3DBeamTelemetry(
        search_states=counters.search_states,
        placement_trials=counters.placement_trials,
        feasible_options=counters.feasible_options,
        states_generated=counters.states_generated,
        states_deduplicated=counters.states_deduplicated,
        states_pruned_by_width=counters.states_pruned_by_width,
        states_pruned_by_space_limit=counters.states_pruned_by_space_limit,
        geometric_completions=counters.geometric_completions,
        completions_with_printable_residual=counters.completions_with_printable_residual,
        admitted_complete_solutions=len(solutions),
        maximum_beam_width_retained=counters.maximum_beam_width_retained,
        maximum_depth_reached=counters.maximum_depth_reached,
        maximum_empty_spaces_retained=counters.maximum_empty_spaces_retained,
        maximum_extreme_points_retained=counters.maximum_extreme_points_retained,
        budget_exhausted=counters.budget_exhausted,
        cancelled=counters.cancelled,
        timed_out=counters.timed_out,
    )
    digest = _digest(
        {
            "input_digest": input_digest,
            "status": status,
            "stop_reason": stop_reason,
            "solution_digests": [value.candidate.digest for value in solutions],
            "best_state": _state_signature(best_state),
            "telemetry": telemetry.__dict__,
        }
    )
    return Free3DBeamExecution(
        strategy=strategy,
        budget=budget,
        status=status,
        stop_reason=stop_reason,
        solutions=solutions,
        remaining_best_participant_ids=best_state.remaining_ids,
        telemetry=telemetry,
        deterministic_digest=digest,
    )


def _budget_limits(budget: SolverBudget) -> dict[str, int]:
    if budget.family_id != FREE_3D_BEAM_FAMILY_ID:
        raise Free3DBeamError("The budget family must be free_3d_beam.")
    limits = dict(budget.limits)
    required = {
        "beam_width",
        "max_complete_candidates",
        "max_elapsed_ms",
        "max_empty_spaces",
        "max_extreme_points",
        "max_options_per_participant",
        "max_participant_branches",
        "max_placement_trials",
        "max_search_states",
    }
    missing = sorted(required.difference(limits))
    if missing:
        raise Free3DBeamError(f"Missing hard budget limits: {', '.join(missing)}.")
    if any(limits[name] <= 0 for name in required):
        raise Free3DBeamError("Every H07 hard budget limit must be positive.")
    return limits
