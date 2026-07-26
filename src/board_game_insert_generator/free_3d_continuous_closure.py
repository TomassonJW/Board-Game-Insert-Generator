"""Bounded continuous residual closure for feasible free-3D layouts.

The free-3D search first proves that every requested minimum envelope can be
placed without touching immutable reservations.  This module then absorbs the
remaining printable EMS by expanding only Auto/Target envelope axes.  It never
adds a body, moves a cavity, changes a fixed axis or alters physical defaults.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from time import perf_counter
from typing import Iterable, Mapping

from board_game_insert_generator.free_3d_greedy_solver import (
    EmptySpace,
    Free3DPlacement,
    TopInsetZone,
    _Counters,
    _deduplicate_spaces,
    _digest,
    _mapping,
    _round,
    _rounded_point,
    _separated_from_placements,
    _spaces_intersect,
    _subtract_forbidden_spaces,
    _subtract_placement_from_spaces,
    _support_at,
    _top_inset_option_allowed,
    _upper,
    _validated_forbidden_spaces,
    _validated_top_inset_zones,
)
from board_game_insert_generator.solver_contract import (
    SolverBudget,
    validate_placement_geometry,
)


FREE_3D_CONTINUOUS_CLOSURE_VERSION = "bgig.free_3d_continuous_closure.v4"
FINISHING_OBJECTIVE_CLOSURE_ONLY = "closure_only"
FINISHING_OBJECTIVE_BALANCED_ADDED_VOLUME = "balanced_added_volume"
FINISHING_OBJECTIVE_PROPORTIONAL_EXPANSION = "proportional_expansion"
FINISHING_OBJECTIVE_BALANCED_THEN_PROPORTIONAL = "balanced_then_proportional"
_SUPPORTED_FINISHING_OBJECTIVES = {
    FINISHING_OBJECTIVE_CLOSURE_ONLY,
    FINISHING_OBJECTIVE_BALANCED_ADDED_VOLUME,
    FINISHING_OBJECTIVE_PROPORTIONAL_EXPANSION,
    FINISHING_OBJECTIVE_BALANCED_THEN_PROPORTIONAL,
}
_EPSILON = 0.0001
_AXES = ("x", "y", "z")


@dataclass(frozen=True)
class Free3DClosureResult:
    """One deterministic bounded attempt to close all printable residual EMS."""

    status: str
    placements: tuple[Free3DPlacement, ...]
    empty_spaces: tuple[EmptySpace, ...]
    iterations: int
    candidates_evaluated: int
    initial_residual_metric: tuple[float, float, int]
    final_residual_metric: tuple[float, float, int]
    aligned_face_count: int
    repair_attempts: int
    repairs_applied: int
    global_resolve_invocation_count: int
    deadline_reached: bool
    incumbent_digest: str
    finishing_objective: str
    objective_score: tuple[float, float, float, float]
    objective_candidate_count: int
    selected_objective_id: str
    deterministic_digest: str


@dataclass(frozen=True)
class _GrowthCandidate:
    placement_index: int
    axis_index: int
    direction: int
    boundary_mm: float
    placement: Free3DPlacement
    placements: tuple[Free3DPlacement, ...]
    spaces: tuple[EmptySpace, ...]
    residual_metric: tuple[float, float, int]
    aligned_faces: int
    relative_growth: float
    objective_score: tuple[float, float, float, float]
    objective_id: str
    growth_placement_ids: tuple[str, ...]
    repair_placement_id: str | None = None


def close_free_3d_residual(
    participants: Iterable[Mapping[str, object]],
    placements: Iterable[Free3DPlacement],
    box: Mapping[str, object],
    storage_height_mm: float,
    between_bodies_xy_mm: float,
    *,
    box_perimeter_xy_mm: float,
    between_bodies_z_mm: float,
    budget: SolverBudget,
    forbidden_spaces: Iterable[EmptySpace] = (),
    top_inset_zones: Iterable[TopInsetZone] = (),
    finishing_objective: str = FINISHING_OBJECTIVE_CLOSURE_ONLY,
) -> Free3DClosureResult:
    """Close printable residuals with bounded growth then local repair."""

    started = perf_counter()
    values = tuple(dict(value) for value in participants)
    participants_by_id = {str(value["id"]): value for value in values}
    current = tuple(sorted(placements, key=lambda value: value.participant_id))
    if finishing_objective not in _SUPPORTED_FINISHING_OBJECTIVES:
        raise ValueError(f"Unsupported continuous closure objective: {finishing_objective}.")
    incumbent_by_id = {value.participant_id: value for value in current}
    if set(participants_by_id) != {value.participant_id for value in current}:
        raise ValueError("Continuous closure requires one placement per participant.")

    dimensions = (
        float(box["x"]),
        float(box["y"]),
        float(storage_height_mm),
    )
    box_clearance = float(box_perimeter_xy_mm)
    xy_clearance = float(between_bodies_xy_mm)
    z_clearance = float(between_bodies_z_mm)
    forbidden = _validated_forbidden_spaces(forbidden_spaces, dimensions)
    inset_zones = _validated_top_inset_zones(top_inset_zones, dimensions)
    spaces = _empty_spaces_for(
        current,
        dimensions,
        box_clearance,
        xy_clearance,
        z_clearance,
        forbidden,
        inset_zones,
    )
    initial_metric = _residual_metric(spaces)
    incumbent_digest = _digest(
        {
            "placements": [value.__dict__ for value in current],
            "top_inset_zones": [value.__dict__ for value in inset_zones],
        }
    )
    limits = dict(budget.limits)
    default_iterations = max(12, min(256, len(current) * 8))
    max_iterations = max(1, int(limits.get("max_closure_iterations", default_iterations)))
    placement_limit = int(limits.get("max_placement_trials", 20_000))
    max_candidates = max(
        1, int(limits.get("max_closure_candidates", max(1_000, min(500_000, placement_limit // 2))))
    )
    max_repairs = max(0, int(limits.get("max_local_repairs", min(256, max(16, len(current) * 8)))))
    max_elapsed_ms = max(
        1, int(limits.get("max_closure_elapsed_ms", limits.get("max_elapsed_ms", 30_000)))
    )
    deadline = started + max_elapsed_ms / 1000.0
    candidates_evaluated = 0
    repair_attempts = 0
    repairs_applied = 0
    objective_candidate_count = 0
    selected_objective_id = "not_applied"
    iterations = 0
    deadline_reached = False
    status = "already_closed" if not spaces else "stalled"
    visited = {_placement_signature(current)}

    while spaces and iterations < max_iterations and candidates_evaluated < max_candidates:
        if perf_counter() >= deadline:
            deadline_reached = True
            status = "budget_exhausted"
            break
        baseline = _residual_metric(spaces)
        candidates, evaluated = _growth_candidates(
            current,
            participants_by_id,
            dimensions,
            box_clearance,
            xy_clearance,
            z_clearance,
            forbidden,
            inset_zones,
            baseline,
            max_candidates - candidates_evaluated,
            deadline,
            incumbent_by_id,
            finishing_objective,
            axis_indices=(2,),
        )
        candidates_evaluated += evaluated
        if (
            not candidates
            and candidates_evaluated < max_candidates
            and perf_counter() < deadline
        ):
            candidates, evaluated = _growth_candidates(
                current,
                participants_by_id,
                dimensions,
                box_clearance,
                xy_clearance,
                z_clearance,
                forbidden,
                inset_zones,
                baseline,
                max_candidates - candidates_evaluated,
                deadline,
                incumbent_by_id,
                finishing_objective,
                axis_indices=(0, 1),
            )
            candidates_evaluated += evaluated
        if not candidates and repair_attempts < max_repairs:
            repaired, attempted, evaluated = _local_repair_growth_candidates(
                current,
                participants_by_id,
                dimensions,
                box_clearance,
                xy_clearance,
                z_clearance,
                forbidden,
                inset_zones,
                baseline,
                max_repairs - repair_attempts,
                max_candidates - candidates_evaluated,
                deadline,
                visited,
                incumbent_by_id,
                finishing_objective,
            )
            repair_attempts += attempted
            candidates_evaluated += evaluated
            candidates.extend(repaired)
        if not candidates:
            if perf_counter() >= deadline:
                deadline_reached = True
            status = (
                "budget_exhausted"
                if deadline_reached
                or candidates_evaluated >= max_candidates
                or repair_attempts >= max_repairs
                else "stalled"
            )
            break
        chosen = min(
            candidates,
            key=lambda value: (
                value.residual_metric,
                _objective_rank(value.objective_score, finishing_objective),
                -value.aligned_faces,
                _round(value.relative_growth),
                value.repair_placement_id or "",
                value.objective_id,
                value.growth_placement_ids,
                value.placement.participant_id,
                value.axis_index,
                value.direction,
                value.boundary_mm,
            ),
        )
        current = chosen.placements
        spaces = list(chosen.spaces)
        visited.add(_placement_signature(current))
        repairs_applied += int(chosen.repair_placement_id is not None)
        objective_candidate_count += int(
            chosen.objective_id not in {"direct_growth", "not_applied"}
        )
        selected_objective_id = chosen.objective_id
        iterations += 1
    else:
        if not spaces:
            status = "closed"
        elif iterations >= max_iterations or candidates_evaluated >= max_candidates:
            status = "budget_exhausted"

    if not spaces and status not in {"already_closed", "closed"}:
        status = "closed"
    final_metric = _residual_metric(spaces)
    final_objective_score = _objective_score(
        current,
        incumbent_by_id,
        participants_by_id,
    )
    aligned_faces = _aligned_faces(current, dimensions, box_clearance)
    digest = _digest(
        {
            "version": FREE_3D_CONTINUOUS_CLOSURE_VERSION,
            "budget": {
                "family_id": budget.family_id,
                "effort_profile": budget.effort_profile,
                "limits": budget.limits,
            },
            "status": status,
            "iterations": iterations,
            "candidates_evaluated": candidates_evaluated,
            "repair_attempts": repair_attempts,
            "repairs_applied": repairs_applied,
            "global_resolve_invocation_count": 0,
            "deadline_reached": deadline_reached,
            "incumbent_digest": incumbent_digest,
            "finishing_objective": finishing_objective,
            "objective_score": final_objective_score,
            "objective_candidate_count": objective_candidate_count,
            "selected_objective_id": selected_objective_id,
            "initial_residual_metric": initial_metric,
            "final_residual_metric": final_metric,
            "placements": [value.__dict__ for value in current],
            "forbidden_spaces": [value.__dict__ for value in forbidden],
            "top_inset_zones": [value.__dict__ for value in inset_zones],
        }
    )
    return Free3DClosureResult(
        status=status,
        placements=current,
        empty_spaces=tuple(spaces),
        iterations=iterations,
        candidates_evaluated=candidates_evaluated,
        initial_residual_metric=initial_metric,
        final_residual_metric=final_metric,
        aligned_face_count=aligned_faces,
        repair_attempts=repair_attempts,
        repairs_applied=repairs_applied,
        global_resolve_invocation_count=0,
        deadline_reached=deadline_reached,
        incumbent_digest=incumbent_digest,
        finishing_objective=finishing_objective,
        objective_score=final_objective_score,
        objective_candidate_count=objective_candidate_count,
        selected_objective_id=selected_objective_id,
        deterministic_digest=digest,
    )


def _growth_candidates(
    current: tuple[Free3DPlacement, ...],
    participants_by_id: dict[str, dict[str, object]],
    dimensions: tuple[float, float, float],
    box_clearance: float,
    xy_clearance: float,
    z_clearance: float,
    forbidden: tuple[EmptySpace, ...],
    inset_zones: tuple[TopInsetZone, ...],
    baseline: tuple[float, float, int],
    remaining_candidates: int,
    deadline: float,
    incumbent_by_id: dict[str, Free3DPlacement],
    finishing_objective: str,
    *,
    repair_placement_id: str | None = None,
    axis_indices: tuple[int, ...] = (0, 1, 2),
) -> tuple[list[_GrowthCandidate], int]:
    candidates: list[_GrowthCandidate] = []
    evaluated = 0
    if remaining_candidates <= 0:
        return candidates, evaluated
    for placement_index, placement in enumerate(current):
        participant = participants_by_id[placement.participant_id]
        for axis_index in axis_indices:
            if not _world_axis_is_expandable(
                participant,
                placement.rotation_deg_z,
                axis_index,
            ):
                continue
            directions = (1,) if axis_index == 2 else (-1, 1)
            for direction in directions:
                if evaluated >= remaining_candidates or perf_counter() >= deadline:
                    return candidates, evaluated
                boundary = _maximal_growth_boundary(
                    placement,
                    axis_index,
                    direction,
                    current,
                    forbidden,
                    dimensions,
                    box_clearance,
                    xy_clearance,
                    z_clearance,
                    inset_zones,
                )
                origin = placement.origin_mm[axis_index]
                upper = origin + placement.world_size_mm[axis_index]
                if (
                    direction > 0
                    and boundary <= upper + _EPSILON
                    or direction < 0
                    and boundary >= origin - _EPSILON
                ):
                    continue
                grown = _grow_placement(
                    placement,
                    axis_index,
                    direction,
                    boundary,
                )
                evaluated += 1
                candidate_values = list(current)
                candidate_values[placement_index] = grown
                candidate_tuple = tuple(candidate_values)
                if not _valid_geometry(
                    candidate_tuple,
                    placement_index,
                    participants_by_id,
                    dimensions,
                    box_clearance,
                    xy_clearance,
                    z_clearance,
                    forbidden,
                    inset_zones,
                ):
                    continue
                candidate_spaces = tuple(
                    _empty_spaces_for(
                        candidate_tuple,
                        dimensions,
                        box_clearance,
                        xy_clearance,
                        z_clearance,
                        forbidden,
                        inset_zones,
                    )
                )
                metric = _residual_metric(candidate_spaces)
                if metric >= baseline:
                    continue
                candidates.append(
                    _GrowthCandidate(
                        placement_index=placement_index,
                        axis_index=axis_index,
                        direction=direction,
                        boundary_mm=_round(boundary),
                        placement=grown,
                        placements=candidate_tuple,
                        spaces=candidate_spaces,
                        residual_metric=metric,
                        aligned_faces=_aligned_faces(candidate_tuple, dimensions, box_clearance),
                        relative_growth=_relative_growth(placement, grown),
                        objective_score=_objective_score(
                            candidate_tuple,
                            incumbent_by_id,
                            participants_by_id,
                        ),
                        objective_id="direct_growth",
                        growth_placement_ids=(placement.participant_id,),
                        repair_placement_id=repair_placement_id,
                    )
                )
    if (
        finishing_objective != FINISHING_OBJECTIVE_CLOSURE_ONLY
        and evaluated < remaining_candidates
        and perf_counter() < deadline
    ):
        paired, paired_evaluated = _paired_growth_candidates(
            current,
            participants_by_id,
            dimensions,
            box_clearance,
            xy_clearance,
            z_clearance,
            forbidden,
            inset_zones,
            baseline,
            remaining_candidates - evaluated,
            deadline,
            incumbent_by_id,
            finishing_objective,
            repair_placement_id=repair_placement_id,
        )
        candidates.extend(paired)
        evaluated += paired_evaluated
    return candidates, evaluated


def _paired_growth_candidates(
    current: tuple[Free3DPlacement, ...],
    participants_by_id: dict[str, dict[str, object]],
    dimensions: tuple[float, float, float],
    box_clearance: float,
    xy_clearance: float,
    z_clearance: float,
    forbidden: tuple[EmptySpace, ...],
    inset_zones: tuple[TopInsetZone, ...],
    baseline: tuple[float, float, int],
    remaining_candidates: int,
    deadline: float,
    incumbent_by_id: dict[str, Free3DPlacement],
    finishing_objective: str,
    *,
    repair_placement_id: str | None = None,
    axis_indices: tuple[int, ...] = (0, 1, 2),
) -> tuple[list[_GrowthCandidate], int]:
    candidates: list[_GrowthCandidate] = []
    evaluated = 0
    seen: set[tuple[object, ...]] = set()
    objective_ids = _paired_objective_ids(finishing_objective)
    for first_index, first in enumerate(current):
        for second_index in range(first_index + 1, len(current)):
            second = current[second_index]
            for axis in range(3):
                if evaluated >= remaining_candidates or perf_counter() >= deadline:
                    return candidates, evaluated
                if not _projections_need_axis_separation(
                    first,
                    second,
                    axis,
                    xy_clearance,
                    z_clearance,
                ):
                    continue
                if first.origin_mm[axis] <= second.origin_mm[axis]:
                    left_index, left = first_index, first
                    right_index, right = second_index, second
                else:
                    left_index, left = second_index, second
                    right_index, right = first_index, first
                left_participant = participants_by_id[left.participant_id]
                right_participant = participants_by_id[right.participant_id]
                if not (
                    _world_axis_is_expandable(left_participant, left.rotation_deg_z, axis)
                    and _world_axis_is_expandable(right_participant, right.rotation_deg_z, axis)
                ):
                    continue
                clearance = z_clearance if axis == 2 else xy_clearance
                left_upper = _upper_of_placement(left, axis)
                gap = right.origin_mm[axis] - left_upper - clearance
                if gap <= _EPSILON:
                    continue
                left_limit = _maximal_growth_boundary(
                    left,
                    axis,
                    1,
                    current,
                    forbidden,
                    dimensions,
                    box_clearance,
                    xy_clearance,
                    z_clearance,
                    inset_zones,
                )
                right_limit = _maximal_growth_boundary(
                    right,
                    axis,
                    -1,
                    current,
                    forbidden,
                    dimensions,
                    box_clearance,
                    xy_clearance,
                    z_clearance,
                    inset_zones,
                )
                if (
                    left_limit + _EPSILON < right.origin_mm[axis] - clearance
                    or right_limit - _EPSILON > left_upper + clearance
                ):
                    continue
                for objective_id in objective_ids:
                    if evaluated >= remaining_candidates or perf_counter() >= deadline:
                        return candidates, evaluated
                    left_delta = _paired_left_delta(
                        objective_id,
                        left,
                        right,
                        gap,
                        axis,
                        incumbent_by_id,
                    )
                    right_delta = gap - left_delta
                    grown_left = _grow_placement(
                        left,
                        axis,
                        1,
                        left_upper + left_delta,
                    )
                    grown_right = _grow_placement(
                        right,
                        axis,
                        -1,
                        right.origin_mm[axis] - right_delta,
                    )
                    candidate_values = list(current)
                    candidate_values[left_index] = grown_left
                    candidate_values[right_index] = grown_right
                    candidate_tuple = tuple(candidate_values)
                    signature = _placement_signature(candidate_tuple)
                    if signature in seen:
                        continue
                    seen.add(signature)
                    evaluated += 1
                    if not (
                        _valid_geometry(
                            candidate_tuple,
                            left_index,
                            participants_by_id,
                            dimensions,
                            box_clearance,
                            xy_clearance,
                            z_clearance,
                            forbidden,
                            inset_zones,
                        )
                        and _valid_geometry(
                            candidate_tuple,
                            right_index,
                            participants_by_id,
                            dimensions,
                            box_clearance,
                            xy_clearance,
                            z_clearance,
                            forbidden,
                            inset_zones,
                        )
                    ):
                        continue
                    candidate_spaces = tuple(
                        _empty_spaces_for(
                            candidate_tuple,
                            dimensions,
                            box_clearance,
                            xy_clearance,
                            z_clearance,
                            forbidden,
                            inset_zones,
                        )
                    )
                    metric = _residual_metric(candidate_spaces)
                    if metric >= baseline:
                        continue
                    candidates.append(
                        _GrowthCandidate(
                            placement_index=left_index,
                            axis_index=axis,
                            direction=0,
                            boundary_mm=_round(left_upper + left_delta),
                            placement=grown_left,
                            placements=candidate_tuple,
                            spaces=candidate_spaces,
                            residual_metric=metric,
                            aligned_faces=_aligned_faces(
                                candidate_tuple, dimensions, box_clearance
                            ),
                            relative_growth=(
                                _relative_growth(left, grown_left)
                                + _relative_growth(right, grown_right)
                            ),
                            objective_score=_objective_score(
                                candidate_tuple,
                                incumbent_by_id,
                                participants_by_id,
                            ),
                            objective_id=objective_id,
                            growth_placement_ids=(
                                left.participant_id,
                                right.participant_id,
                            ),
                            repair_placement_id=repair_placement_id,
                        )
                    )
    return candidates, evaluated


def _paired_objective_ids(finishing_objective: str) -> tuple[str, ...]:
    if finishing_objective == FINISHING_OBJECTIVE_BALANCED_ADDED_VOLUME:
        return (FINISHING_OBJECTIVE_BALANCED_ADDED_VOLUME,)
    if finishing_objective == FINISHING_OBJECTIVE_PROPORTIONAL_EXPANSION:
        return (FINISHING_OBJECTIVE_PROPORTIONAL_EXPANSION,)
    if finishing_objective == FINISHING_OBJECTIVE_BALANCED_THEN_PROPORTIONAL:
        return (
            FINISHING_OBJECTIVE_BALANCED_ADDED_VOLUME,
            FINISHING_OBJECTIVE_PROPORTIONAL_EXPANSION,
        )
    return ()


def _paired_left_delta(
    objective_id: str,
    left: Free3DPlacement,
    right: Free3DPlacement,
    gap: float,
    axis: int,
    incumbent_by_id: dict[str, Free3DPlacement],
) -> float:
    left_base = incumbent_by_id[left.participant_id]
    right_base = incumbent_by_id[right.participant_id]
    left_area = _placement_volume(left) / left.world_size_mm[axis]
    right_area = _placement_volume(right) / right.world_size_mm[axis]
    left_added = _placement_volume(left) - _placement_volume(left_base)
    right_added = _placement_volume(right) - _placement_volume(right_base)
    if objective_id == FINISHING_OBJECTIVE_BALANCED_ADDED_VOLUME:
        denominator = left_area + right_area
        raw = (right_added - left_added + right_area * gap) / denominator
    else:
        left_base_volume = _placement_volume(left_base)
        right_base_volume = _placement_volume(right_base)
        left_ratio = left_added / left_base_volume
        right_ratio = right_added / right_base_volume
        left_rate = left_area / left_base_volume
        right_rate = right_area / right_base_volume
        raw = (right_ratio - left_ratio + right_rate * gap) / (left_rate + right_rate)
    return _round(min(gap, max(0.0, raw)))


def _local_repair_growth_candidates(
    current: tuple[Free3DPlacement, ...],
    participants_by_id: dict[str, dict[str, object]],
    dimensions: tuple[float, float, float],
    box_clearance: float,
    xy_clearance: float,
    z_clearance: float,
    forbidden: tuple[EmptySpace, ...],
    inset_zones: tuple[TopInsetZone, ...],
    baseline: tuple[float, float, int],
    remaining_repairs: int,
    remaining_candidates: int,
    deadline: float,
    visited: set[tuple[object, ...]],
    incumbent_by_id: dict[str, Free3DPlacement],
    finishing_objective: str,
) -> tuple[list[_GrowthCandidate], int, int]:
    candidates: list[_GrowthCandidate] = []
    attempted = 0
    evaluated = 0
    for repaired, changed_index, placement_id in _repair_states(
        current,
        participants_by_id,
        dimensions,
        box_clearance,
        xy_clearance,
        z_clearance,
        forbidden,
        inset_zones,
    ):
        if (
            attempted >= remaining_repairs
            or evaluated >= remaining_candidates
            or perf_counter() >= deadline
        ):
            break
        signature = _placement_signature(repaired)
        if signature in visited:
            continue
        attempted += 1
        if not _valid_geometry(
            repaired,
            changed_index,
            participants_by_id,
            dimensions,
            box_clearance,
            xy_clearance,
            z_clearance,
            forbidden,
            inset_zones,
        ):
            continue
        growths, growth_evaluated = _growth_candidates(
            repaired,
            participants_by_id,
            dimensions,
            box_clearance,
            xy_clearance,
            z_clearance,
            forbidden,
            inset_zones,
            baseline,
            remaining_candidates - evaluated,
            deadline,
            incumbent_by_id,
            finishing_objective,
            repair_placement_id=placement_id,
        )
        evaluated += growth_evaluated
        candidates.extend(growths)
    return candidates, attempted, evaluated


def _repair_states(
    current: tuple[Free3DPlacement, ...],
    participants_by_id: dict[str, dict[str, object]],
    dimensions: tuple[float, float, float],
    box_clearance: float,
    xy_clearance: float,
    z_clearance: float,
    forbidden: tuple[EmptySpace, ...],
    inset_zones: tuple[TopInsetZone, ...],
) -> Iterable[tuple[tuple[Free3DPlacement, ...], int, str]]:
    del participants_by_id, forbidden, inset_zones
    for index, placement in enumerate(current):
        for axis in range(3):
            clearance = z_clearance if axis == 2 else xy_clearance
            low = 0.0 if axis == 2 else box_clearance
            high = dimensions[axis] if axis == 2 else dimensions[axis] - box_clearance
            candidates = {
                _round(low),
                _round(high - placement.world_size_mm[axis]),
            }
            for other in current:
                if other.participant_id == placement.participant_id:
                    continue
                candidates.add(
                    _round(other.origin_mm[axis] - clearance - placement.world_size_mm[axis])
                )
                candidates.add(
                    _round(other.origin_mm[axis] + other.world_size_mm[axis] + clearance)
                )
            for candidate_origin in sorted(candidates):
                if (
                    candidate_origin < low - _EPSILON
                    or candidate_origin + placement.world_size_mm[axis] > high + _EPSILON
                    or abs(candidate_origin - placement.origin_mm[axis]) <= _EPSILON
                ):
                    continue
                origin = list(placement.origin_mm)
                origin[axis] = candidate_origin
                moved = replace(placement, origin_mm=_rounded_point(tuple(origin)))
                repaired = list(current)
                repaired[index] = moved
                yield tuple(repaired), index, placement.participant_id


def _placement_signature(
    placements: tuple[Free3DPlacement, ...],
) -> tuple[object, ...]:
    return tuple(
        (
            value.participant_id,
            value.origin_mm,
            value.world_size_mm,
            value.local_size_mm,
            value.rotation_deg_z,
        )
        for value in placements
    )


def _empty_spaces_for(
    placements: tuple[Free3DPlacement, ...],
    dimensions: tuple[float, float, float],
    box_clearance: float,
    xy_clearance: float,
    z_clearance: float,
    forbidden: tuple[EmptySpace, ...],
    inset_zones: tuple[TopInsetZone, ...] = (),
) -> list[EmptySpace]:
    root = EmptySpace(
        _rounded_point((box_clearance, box_clearance, 0.0)),
        _rounded_point(
            (
                dimensions[0] - 2.0 * box_clearance,
                dimensions[1] - 2.0 * box_clearance,
                dimensions[2],
            )
        ),
    )
    spaces = _subtract_forbidden_spaces([root], forbidden)
    reserved_top_prisms = tuple(
        EmptySpace(
            (
                zone.origin_xy_mm[0],
                zone.origin_xy_mm[1],
                zone.support_plane_z_mm,
            ),
            (
                zone.size_xy_mm[0],
                zone.size_xy_mm[1],
                max(0.0, dimensions[2] - zone.support_plane_z_mm),
            ),
        )
        for zone in inset_zones
        if zone.support_plane_z_mm < dimensions[2] - _EPSILON
    )
    spaces = _subtract_forbidden_spaces(spaces, reserved_top_prisms)
    limits = {
        "max_empty_spaces": 100_000,
        "max_extreme_points": 100_000,
        "max_placement_trials": 1,
        "max_search_states": 1,
    }
    for placement in sorted(placements, key=lambda value: value.participant_id):
        counters = _Counters()
        spaces = _subtract_placement_from_spaces(
            spaces,
            placement,
            xy_clearance,
            z_clearance,
            counters,
            limits,
        )
    spaces, _ = _deduplicate_spaces(spaces)
    return spaces


def _maximal_growth_boundary(
    placement: Free3DPlacement,
    axis: int,
    direction: int,
    placements: tuple[Free3DPlacement, ...],
    forbidden: tuple[EmptySpace, ...],
    dimensions: tuple[float, float, float],
    box_clearance: float,
    xy_clearance: float,
    z_clearance: float,
    inset_zones: tuple[TopInsetZone, ...] = (),
) -> float:
    """Return the nearest face that can stop a maximal one-axis expansion."""

    low = box_clearance if axis in {0, 1} else 0.0
    high = dimensions[axis] - box_clearance if axis in {0, 1} else dimensions[axis]
    boundary = high if direction > 0 else low
    axis_clearance = z_clearance if axis == 2 else xy_clearance
    for other in placements:
        if other.participant_id == placement.participant_id:
            continue
        if not _projections_need_axis_separation(
            placement,
            other,
            axis,
            xy_clearance,
            z_clearance,
        ):
            continue
        if direction > 0 and other.origin_mm[axis] >= placement.origin_mm[axis]:
            boundary = min(boundary, other.origin_mm[axis] - axis_clearance)
        elif direction < 0 and _upper_of_placement(other, axis) <= _upper_of_placement(
            placement, axis
        ):
            boundary = max(
                boundary,
                _upper_of_placement(other, axis) + axis_clearance,
            )
    placement_space = EmptySpace(placement.origin_mm, placement.world_size_mm)
    if axis == 2 and direction > 0:
        for zone in inset_zones:
            reserved = EmptySpace(
                (
                    zone.origin_xy_mm[0],
                    zone.origin_xy_mm[1],
                    zone.support_plane_z_mm,
                ),
                (
                    zone.size_xy_mm[0],
                    zone.size_xy_mm[1],
                    max(0.0, dimensions[2] - zone.support_plane_z_mm),
                ),
            )
            if _projected_spaces_overlap(placement_space, reserved, axis):
                boundary = min(boundary, zone.support_plane_z_mm)
    for obstacle in forbidden:
        if not _projected_spaces_overlap(placement_space, obstacle, axis):
            continue
        if direction > 0 and obstacle.origin_mm[axis] >= placement.origin_mm[axis]:
            boundary = min(boundary, obstacle.origin_mm[axis])
        elif direction < 0 and _upper(obstacle)[axis] <= _upper(placement_space)[axis]:
            boundary = max(boundary, _upper(obstacle)[axis])
    return _round(boundary)


def _projections_need_axis_separation(
    left: Free3DPlacement,
    right: Free3DPlacement,
    excluded_axis: int,
    xy_clearance: float,
    z_clearance: float,
) -> bool:
    for axis in range(3):
        if axis == excluded_axis:
            continue
        clearance = z_clearance if axis == 2 else xy_clearance
        if (
            _upper_of_placement(left, axis) + clearance <= right.origin_mm[axis] + _EPSILON
            or _upper_of_placement(right, axis) + clearance <= left.origin_mm[axis] + _EPSILON
        ):
            return False
    return True


def _projected_spaces_overlap(
    left: EmptySpace,
    right: EmptySpace,
    excluded_axis: int,
) -> bool:
    left_upper = _upper(left)
    right_upper = _upper(right)
    return all(
        left.origin_mm[axis] < right_upper[axis] - _EPSILON
        and right.origin_mm[axis] < left_upper[axis] - _EPSILON
        for axis in range(3)
        if axis != excluded_axis
    )


def _upper_of_placement(placement: Free3DPlacement, axis: int) -> float:
    return placement.origin_mm[axis] + placement.world_size_mm[axis]


def _world_axis_is_expandable(
    participant: Mapping[str, object],
    rotation_deg_z: int,
    world_axis: int,
) -> bool:
    local_axis = world_axis
    if rotation_deg_z == 90 and world_axis in {0, 1}:
        local_axis = 1 - world_axis
    modes = _mapping(participant["dimension_modes"])
    return str(modes[_AXES[local_axis]]) != "fixed"


def _grow_placement(
    placement: Free3DPlacement,
    axis: int,
    direction: int,
    boundary: float,
) -> Free3DPlacement:
    origin = list(placement.origin_mm)
    world = list(placement.world_size_mm)
    if direction > 0:
        delta = boundary - (origin[axis] + world[axis])
    else:
        delta = origin[axis] - boundary
        origin[axis] = boundary
    world[axis] += delta
    local = list(placement.local_size_mm)
    local_axis = axis
    if placement.rotation_deg_z == 90 and axis in {0, 1}:
        local_axis = 1 - axis
    local[local_axis] += delta
    return replace(
        placement,
        origin_mm=_rounded_point(tuple(origin)),
        world_size_mm=_rounded_point(tuple(world)),
        local_size_mm=_rounded_point(tuple(local)),
    )


def _valid_geometry(
    placements: tuple[Free3DPlacement, ...],
    changed_index: int,
    participants_by_id: dict[str, dict[str, object]],
    dimensions: tuple[float, float, float],
    box_clearance: float,
    xy_clearance: float,
    z_clearance: float,
    forbidden: tuple[EmptySpace, ...],
    top_inset_zones: tuple[TopInsetZone, ...],
) -> bool:
    changed = placements[changed_index]
    if any(value <= _EPSILON for value in changed.world_size_mm):
        return False
    low = (box_clearance, box_clearance, 0.0)
    high = (
        dimensions[0] - box_clearance,
        dimensions[1] - box_clearance,
        dimensions[2],
    )
    if any(
        changed.origin_mm[axis] < low[axis] - _EPSILON
        or changed.origin_mm[axis] + changed.world_size_mm[axis] > high[axis] + _EPSILON
        for axis in range(3)
    ):
        return False
    changed_space = EmptySpace(changed.origin_mm, changed.world_size_mm)
    if any(_spaces_intersect(changed_space, value) for value in forbidden):
        return False
    if not _top_inset_option_allowed(
        participants_by_id[changed.participant_id],
        changed.origin_mm,
        changed.world_size_mm,
        changed.rotation_deg_z,
        dimensions[2],
        top_inset_zones,
    ):
        return False
    others = [value for index, value in enumerate(placements) if index != changed_index]
    participant = participants_by_id[changed.participant_id]
    if not _separated_from_placements(
        changed.origin_mm,
        changed.world_size_mm,
        participant,
        others,
        xy_clearance,
        z_clearance,
    ):
        return False

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
        dict(zip(_AXES, dimensions)),
        dimensions[2],
        xy_clearance,
        box_clearance,
        z_clearance,
    )
    if not all(
        bool(geometry[name])
        for name in (
            "inside_box",
            "box_xy_clearance_respected",
            "no_collisions",
            "clearances_respected",
        )
    ):
        return False
    for index, value in enumerate(placements):
        participant = participants_by_id[value.participant_id]
        others = [item for other_index, item in enumerate(placements) if other_index != index]
        support = _support_at(
            value.origin_mm,
            value.world_size_mm,
            others,
            participant,
            participants_by_id,
            xy_clearance,
            z_clearance,
        )
        if value.origin_mm[2] > _EPSILON and not support.certified:
            return False
    return True


def _objective_score(
    placements: tuple[Free3DPlacement, ...],
    incumbent_by_id: dict[str, Free3DPlacement],
    participants_by_id: dict[str, dict[str, object]],
) -> tuple[float, float, float, float]:
    added_volumes: list[float] = []
    expansion_ratios: list[float] = []
    for placement in placements:
        participant = participants_by_id[placement.participant_id]
        modes = _mapping(participant["dimension_modes"])
        if all(str(modes[axis]) == "fixed" for axis in _AXES):
            continue
        base_volume = _placement_volume(incumbent_by_id[placement.participant_id])
        added = max(0.0, _placement_volume(placement) - base_volume)
        added_volumes.append(added)
        expansion_ratios.append(added / base_volume)
    return (
        _spread(added_volumes),
        _mean_absolute_deviation(added_volumes),
        _spread(expansion_ratios),
        _mean_absolute_deviation(expansion_ratios),
    )


def _objective_rank(
    score: tuple[float, float, float, float],
    finishing_objective: str,
) -> tuple[float, ...]:
    if finishing_objective == FINISHING_OBJECTIVE_CLOSURE_ONLY:
        return ()
    if finishing_objective == FINISHING_OBJECTIVE_PROPORTIONAL_EXPANSION:
        return (score[2], score[3], score[0], score[1])
    return score


def _placement_volume(placement: Free3DPlacement) -> float:
    return placement.world_size_mm[0] * placement.world_size_mm[1] * placement.world_size_mm[2]


def _spread(values: list[float]) -> float:
    if len(values) < 2:
        return 0.0
    return _round(max(values) - min(values))


def _mean_absolute_deviation(values: list[float]) -> float:
    if len(values) < 2:
        return 0.0
    mean = sum(values) / len(values)
    return _round(sum(abs(value - mean) for value in values) / len(values))


def _residual_metric(spaces: Iterable[EmptySpace]) -> tuple[float, float, int]:
    values = tuple(spaces)
    if not values:
        return (0.0, 0.0, 0)
    volumes = [value.volume_mm3 for value in values]
    return (_round(sum(volumes)), _round(max(volumes)), len(values))


def _aligned_faces(
    placements: tuple[Free3DPlacement, ...],
    dimensions: tuple[float, float, float],
    box_clearance: float,
) -> int:
    boundaries = (
        (box_clearance, dimensions[0] - box_clearance),
        (box_clearance, dimensions[1] - box_clearance),
        (0.0, dimensions[2]),
    )
    count = 0
    for index, placement in enumerate(placements):
        for axis in range(3):
            faces = (
                placement.origin_mm[axis],
                placement.origin_mm[axis] + placement.world_size_mm[axis],
            )
            count += sum(
                abs(face - boundary) <= _EPSILON for face in faces for boundary in boundaries[axis]
            )
            for other in placements[index + 1 :]:
                other_faces = (
                    other.origin_mm[axis],
                    other.origin_mm[axis] + other.world_size_mm[axis],
                )
                count += sum(
                    abs(face - other_face) <= _EPSILON
                    for face in faces
                    for other_face in other_faces
                )
    return count


def _relative_growth(before: Free3DPlacement, after: Free3DPlacement) -> float:
    return sum(
        max(0.0, after.world_size_mm[index] - before.world_size_mm[index])
        / max(before.world_size_mm[index], _EPSILON)
        for index in range(3)
    )
