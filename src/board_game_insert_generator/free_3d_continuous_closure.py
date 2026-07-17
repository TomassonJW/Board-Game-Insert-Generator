"""Bounded continuous residual closure for feasible free-3D layouts.

The free-3D search first proves that every requested minimum envelope can be
placed without touching immutable reservations.  This module then absorbs the
remaining printable EMS by expanding only Auto/Target envelope axes.  It never
adds a body, moves a cavity, changes a fixed axis or alters physical defaults.
"""

from __future__ import annotations

from dataclasses import dataclass
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


FREE_3D_CONTINUOUS_CLOSURE_VERSION = "bgig.free_3d_continuous_closure.v1"
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
) -> Free3DClosureResult:
    """Expand feasible requested bodies until no printable EMS remains."""

    values = tuple(dict(value) for value in participants)
    participants_by_id = {str(value["id"]): value for value in values}
    current = tuple(sorted(placements, key=lambda value: value.participant_id))
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
    )
    initial_metric = _residual_metric(spaces)
    max_iterations = max(12, min(256, len(current) * 8))
    placement_limit = int(dict(budget.limits).get("max_placement_trials", 20_000))
    max_candidates = max(1_000, min(500_000, placement_limit // 2))
    candidates_evaluated = 0
    iterations = 0
    status = "already_closed" if not spaces else "stalled"

    while spaces and iterations < max_iterations and candidates_evaluated < max_candidates:
        candidates: list[_GrowthCandidate] = []
        for placement_index, placement in enumerate(current):
            participant = participants_by_id[placement.participant_id]
            for axis_index in range(3):
                if not _world_axis_is_expandable(
                    participant,
                    placement.rotation_deg_z,
                    axis_index,
                ):
                    continue
                for direction in (-1, 1):
                    if candidates_evaluated >= max_candidates:
                        break
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
                    candidates_evaluated += 1
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
                        )
                    )
                    metric = _residual_metric(candidate_spaces)
                    if metric >= _residual_metric(spaces):
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
                        )
                    )
            if candidates_evaluated >= max_candidates:
                break

        if not candidates:
            status = "budget_exhausted" if candidates_evaluated >= max_candidates else "stalled"
            break
        chosen = min(
            candidates,
            key=lambda value: (
                value.residual_metric,
                -value.aligned_faces,
                _round(value.relative_growth),
                value.placement.participant_id,
                value.axis_index,
                value.direction,
                value.boundary_mm,
            ),
        )
        current = chosen.placements
        spaces = list(chosen.spaces)
        iterations += 1
    else:
        if not spaces:
            status = "closed"
        elif iterations >= max_iterations or candidates_evaluated >= max_candidates:
            status = "budget_exhausted"

    if not spaces and status not in {"already_closed", "closed"}:
        status = "closed"
    final_metric = _residual_metric(spaces)
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
        deterministic_digest=digest,
    )


def _empty_spaces_for(
    placements: tuple[Free3DPlacement, ...],
    dimensions: tuple[float, float, float],
    box_clearance: float,
    xy_clearance: float,
    z_clearance: float,
    forbidden: tuple[EmptySpace, ...],
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
            _upper_of_placement(left, axis) + clearance
            <= right.origin_mm[axis] + _EPSILON
            or _upper_of_placement(right, axis) + clearance
            <= left.origin_mm[axis] + _EPSILON
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
    return Free3DPlacement(
        participant_id=placement.participant_id,
        role=placement.role,
        name=placement.name,
        origin_mm=_rounded_point(tuple(origin)),
        world_size_mm=_rounded_point(tuple(world)),
        local_size_mm=_rounded_point(tuple(local)),
        rotation_deg_z=placement.rotation_deg_z,
        supporting_ids=placement.supporting_ids,
        support_coverage_ratio=placement.support_coverage_ratio,
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
        _, ratio = _support_at(
            value.origin_mm,
            value.world_size_mm,
            others,
            participant,
            z_clearance,
        )
        if value.origin_mm[2] > _EPSILON and ratio + _EPSILON < 0.25:
            return False
    return True


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
                abs(face - boundary) <= _EPSILON
                for face in faces
                for boundary in boundaries[axis]
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