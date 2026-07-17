"""Bounded free-3D greedy solver based on extreme points and EMS.

P64-H06 deliberately exposes a second *internal* strategy family without
changing the public project schema or the stage-stack default.  The engine
packs one already-derived canonical envelope per requested body.  It maintains
maximal empty spaces (EMS), derives extreme points from placed faces, chooses
the currently most constrained participant and follows one deterministic
greedy trajectory.  P64-H07 remains responsible for beam search and portfolio
orchestration.

The engine proposes geometry; the common validator remains authoritative.  A
geometric admission report is therefore included here, while a materializable
partition still has to pass ``certify_partition_candidate`` after the adapter
has restored cavities, reservations, removal and conservation contracts.
"""

from __future__ import annotations

from dataclasses import dataclass
from copy import deepcopy
import hashlib
import json
from typing import Any, Iterable, Mapping

from board_game_insert_generator.solver_contract import (
    PlacementSnapshot,
    SolverBudget,
    SolverCandidate,
    SolverStrategy,
    ValidationCheck,
    validate_placement_geometry,
)


FREE_3D_GREEDY_FAMILY_ID = "free_3d_greedy"
FREE_3D_GREEDY_VERSION = "bgig.free_3d_greedy.v1"
FREE_3D_GEOMETRY_VALIDATION_V1 = "bgig.free_3d_geometry_validation.v1"
_EPSILON = 0.0001
_AXES = ("x", "y", "z")


class Free3DGreedyError(ValueError):
    """Raised when the internal H06 problem or budget is malformed."""


@dataclass(frozen=True)
class EmptySpace:
    """One deduplicated maximal empty orthogonal space."""

    origin_mm: tuple[float, float, float]
    size_mm: tuple[float, float, float]

    @property
    def volume_mm3(self) -> float:
        return self.size_mm[0] * self.size_mm[1] * self.size_mm[2]


@dataclass(frozen=True)
class Free3DPlacement:
    """Immutable placement retaining enough metadata for a future adapter."""

    participant_id: str
    role: str
    name: str
    origin_mm: tuple[float, float, float]
    world_size_mm: tuple[float, float, float]
    local_size_mm: tuple[float, float, float]
    rotation_deg_z: int
    supporting_ids: tuple[str, ...]
    support_coverage_ratio: float


@dataclass(frozen=True)
class Free3DSearchTelemetry:
    """Deterministic H06 counters; elapsed time deliberately lives elsewhere."""

    search_states: int
    placement_trials: int
    feasible_options: int
    extreme_points_generated: int
    extreme_points_deduplicated: int
    empty_spaces_generated: int
    empty_spaces_deduplicated: int
    maximum_empty_spaces_retained: int
    maximum_extreme_points_retained: int
    budget_exhausted: bool


@dataclass(frozen=True)
class Free3DGeometryAdmission:
    """Common geometric checks, explicitly narrower than product certification."""

    schema_version: str
    candidate_digest: str
    admitted: bool
    checks: tuple[ValidationCheck, ...]

    @property
    def rejection_codes(self) -> tuple[str, ...]:
        return tuple(
            check.rejection_code
            for check in self.checks
            if not check.passed and check.rejection_code is not None
        )


@dataclass(frozen=True)
class Free3DGreedyExecution:
    """One bounded deterministic execution of the H06 strategy."""

    strategy: SolverStrategy
    budget: SolverBudget
    status: str
    stop_reason: str
    candidate: SolverCandidate | None
    geometry_admission: Free3DGeometryAdmission | None
    placements: tuple[Free3DPlacement, ...]
    remaining_participant_ids: tuple[str, ...]
    empty_spaces: tuple[EmptySpace, ...]
    extreme_points_mm: tuple[tuple[float, float, float], ...]
    telemetry: Free3DSearchTelemetry
    deterministic_digest: str


@dataclass
class _Counters:
    search_states: int = 0
    placement_trials: int = 0
    feasible_options: int = 0
    extreme_points_generated: int = 1
    extreme_points_deduplicated: int = 0
    empty_spaces_generated: int = 1
    empty_spaces_deduplicated: int = 0
    maximum_empty_spaces_retained: int = 1
    maximum_extreme_points_retained: int = 1
    budget_exhausted: bool = False


@dataclass(frozen=True)
class _Option:
    participant: dict[str, object]
    origin: tuple[float, float, float]
    world_size: tuple[float, float, float]
    local_size: tuple[float, float, float]
    rotation_deg_z: int
    supporting_ids: tuple[str, ...]
    support_ratio: float
    containing_space_volume: float


def solve_free_3d_greedy(
    participants: Iterable[Mapping[str, object]],
    box: Mapping[str, object],
    storage_height_mm: float,
    between_bodies_xy_mm: float,
    *,
    box_perimeter_xy_mm: float,
    between_bodies_z_mm: float,
    budget: SolverBudget,
) -> Free3DGreedyExecution:
    """Pack canonical envelopes through one deterministic greedy trajectory.

    No implicit budget is provided: H06 benchmarks explicit laboratory limits
    before H07 defines product effort profiles.  Exhaustion is always reported
    as ``no_solution_within_budget`` and never as a proof of impossibility.
    """

    strategy = SolverStrategy(FREE_3D_GREEDY_FAMILY_ID, FREE_3D_GREEDY_VERSION)
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
        raise Free3DGreedyError("The useful box must remain positive after perimeter clearance.")
    if not values:
        raise Free3DGreedyError("At least one canonical participant is required.")

    placements: list[Free3DPlacement] = []
    remaining = list(values)
    spaces = [EmptySpace(_rounded_point((box_clearance, box_clearance, 0.0)), _rounded_point(root_size))]
    points = {_rounded_point((box_clearance, box_clearance, 0.0))}
    counters = _Counters()
    input_digest = _digest(
        {
            "strategy": strategy.__dict__,
            "budget": {
                "family_id": budget.family_id,
                "effort_profile": budget.effort_profile,
                "limits": budget.limits,
            },
            "participants": values,
            "box": dimensions,
            "clearances": (xy_clearance, box_clearance, z_clearance),
        }
    )
    formal_impossibility = _necessary_bound_failure(values, root_size)
    if formal_impossibility is not None:
        return _execution(
            strategy,
            budget,
            "proven_impossible",
            formal_impossibility,
            input_digest,
            values,
            placements,
            spaces,
            points,
            counters,
            dimensions,
            xy_clearance,
            box_clearance,
            z_clearance,
        )

    while remaining:
        if counters.budget_exhausted or counters.search_states >= limits["max_search_states"]:
            counters.budget_exhausted = True
            break
        selected, options = _most_constrained_current_participant(
            remaining,
            spaces,
            points,
            placements,
            dimensions,
            xy_clearance,
            z_clearance,
            counters,
            limits,
        )
        if counters.budget_exhausted:
            break
        if selected is None or not options:
            break

        chosen = min(options, key=lambda item: _option_sort_key(item, placements))
        placement = Free3DPlacement(
            participant_id=str(chosen.participant["id"]),
            role=str(chosen.participant["role"]),
            name=str(chosen.participant["name"]),
            origin_mm=_rounded_point(chosen.origin),
            world_size_mm=_rounded_point(chosen.world_size),
            local_size_mm=_rounded_point(chosen.local_size),
            rotation_deg_z=chosen.rotation_deg_z,
            supporting_ids=chosen.supporting_ids,
            support_coverage_ratio=_round(chosen.support_ratio),
        )
        placements.append(placement)
        remaining.remove(selected)
        counters.search_states += 1
        spaces = _subtract_placement_from_spaces(
            spaces,
            placement,
            xy_clearance,
            z_clearance,
            counters,
            limits,
        )
        points = _update_extreme_points(
            points,
            placement,
            spaces,
            xy_clearance,
            z_clearance,
            counters,
            limits,
        )

    if not remaining:
        status = "solution_found"
        stop_reason = "greedy_trajectory_complete"
    elif counters.budget_exhausted:
        status = "no_solution_within_budget"
        stop_reason = "hard_budget_reached"
    else:
        status = "no_solution_within_budget"
        stop_reason = "greedy_dead_end"
    return _execution(
        strategy,
        budget,
        status,
        stop_reason,
        input_digest,
        remaining,
        placements,
        spaces,
        points,
        counters,
        dimensions,
        xy_clearance,
        box_clearance,
        z_clearance,
    )


def _most_constrained_current_participant(
    remaining: list[dict[str, object]],
    spaces: list[EmptySpace],
    points: set[tuple[float, float, float]],
    placements: list[Free3DPlacement],
    box: tuple[float, float, float],
    xy_clearance: float,
    z_clearance: float,
    counters: _Counters,
    limits: dict[str, int],
) -> tuple[dict[str, object] | None, list[_Option]]:
    """Choose the fewest-current-options participant, deferring zero-option ones.

    A currently blocked upper body may become placeable after another support is
    inserted.  Treating zero current options as a formal failure would recreate
    an order-dependent false impossibility, so only participants with at least
    one option compete in this greedy step.
    """

    evaluated: list[tuple[tuple[object, ...], dict[str, object], list[_Option]]] = []
    for participant in remaining:
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
        )
        if counters.budget_exhausted:
            return None, []
        if not options:
            continue
        minimum = _minimum_local(participant)
        constrained_axes = sum(
            str(_mapping(participant["dimension_modes"])[axis]) == "fixed"
            for axis in _AXES
        )
        key = (
            len(options),
            -constrained_axes,
            -_volume(minimum),
            str(participant["id"]),
        )
        evaluated.append((key, participant, options))
    if not evaluated:
        return None, []
    _, participant, options = min(evaluated, key=lambda item: item[0])
    return participant, options


def _placement_options(
    participant: dict[str, object],
    spaces: list[EmptySpace],
    points: set[tuple[float, float, float]],
    placements: list[Free3DPlacement],
    box: tuple[float, float, float],
    xy_clearance: float,
    z_clearance: float,
    counters: _Counters,
    limits: dict[str, int],
) -> list[_Option]:
    result: dict[tuple[object, ...], _Option] = {}
    for rotation, world_size, local_size in _orientations(participant):
        for point in sorted(points, key=lambda value: (value[2], value[1], value[0])):
            containing = [space for space in spaces if _fits_in_space(point, world_size, space)]
            if not containing:
                continue
            for space in containing:
                if counters.placement_trials >= limits["max_placement_trials"]:
                    counters.budget_exhausted = True
                    return []
                counters.placement_trials += 1
                if not _inside_box(point, world_size, box):
                    continue
                if not _separated_from_placements(
                    point,
                    world_size,
                    participant,
                    placements,
                    xy_clearance,
                    z_clearance,
                ):
                    continue
                supporting_ids, support_ratio = _support_at(
                    point,
                    world_size,
                    placements,
                    participant,
                    z_clearance,
                )
                if point[2] > _EPSILON and support_ratio + _EPSILON < 0.25:
                    continue
                option = _Option(
                    participant=participant,
                    origin=point,
                    world_size=world_size,
                    local_size=local_size,
                    rotation_deg_z=rotation,
                    supporting_ids=supporting_ids,
                    support_ratio=support_ratio,
                    containing_space_volume=space.volume_mm3,
                )
                key = (point, world_size, rotation)
                result[key] = option
    counters.feasible_options += len(result)
    return list(result.values())


def _orientations(
    participant: dict[str, object],
) -> tuple[tuple[int, tuple[float, float, float], tuple[float, float, float]], ...]:
    local = _minimum_local(participant)
    values = [(0, local, local)]
    rotated = (local[1], local[0], local[2])
    if abs(local[0] - local[1]) > _EPSILON:
        values.append((90, rotated, local))
    return tuple(values)


def _option_sort_key(
    option: _Option,
    placements: list[Free3DPlacement],
) -> tuple[object, ...]:
    body_volume = option.world_size[0] * option.world_size[1] * option.world_size[2]
    waste_ratio = max(0.0, option.containing_space_volume - body_volume) / max(
        option.containing_space_volume, _EPSILON
    )
    aligned_faces = _aligned_face_count(option, placements)
    return (
        -_round(option.support_ratio),
        -aligned_faces,
        _round(waste_ratio),
        _round(option.origin[2]),
        _round(option.origin[1]),
        _round(option.origin[0]),
        option.rotation_deg_z,
        str(option.participant["id"]),
    )


def _aligned_face_count(option: _Option, placements: list[Free3DPlacement]) -> int:
    faces = {
        axis: (option.origin[index], option.origin[index] + option.world_size[index])
        for index, axis in enumerate(_AXES)
    }
    count = 0
    for placement in placements:
        for index, axis in enumerate(_AXES):
            other = (
                placement.origin_mm[index],
                placement.origin_mm[index] + placement.world_size_mm[index],
            )
            count += sum(abs(value - candidate) <= _EPSILON for value in faces[axis] for candidate in other)
    return count


def _subtract_placement_from_spaces(
    spaces: list[EmptySpace],
    placement: Free3DPlacement,
    xy_clearance: float,
    z_clearance: float,
    counters: _Counters,
    limits: dict[str, int],
) -> list[EmptySpace]:
    reserved = EmptySpace(
        placement.origin_mm,
        (
            placement.world_size_mm[0] + xy_clearance,
            placement.world_size_mm[1] + xy_clearance,
            placement.world_size_mm[2] + z_clearance,
        ),
    )
    generated: list[EmptySpace] = []
    for space in spaces:
        if not _spaces_intersect(space, reserved):
            generated.append(space)
            continue
        generated.extend(_split_space(space, reserved))
    counters.empty_spaces_generated += len(generated)
    deduplicated, removed = _deduplicate_spaces(generated)
    counters.empty_spaces_deduplicated += removed
    if len(deduplicated) > limits["max_empty_spaces"]:
        counters.budget_exhausted = True
        deduplicated = deduplicated[: limits["max_empty_spaces"]]
    counters.maximum_empty_spaces_retained = max(
        counters.maximum_empty_spaces_retained, len(deduplicated)
    )
    return deduplicated


def _split_space(space: EmptySpace, occupied: EmptySpace) -> list[EmptySpace]:
    sx0, sy0, sz0 = space.origin_mm
    sx1, sy1, sz1 = _upper(space)
    ox0, oy0, oz0 = occupied.origin_mm
    ox1, oy1, oz1 = _upper(occupied)
    ix0, iy0, iz0 = max(sx0, ox0), max(sy0, oy0), max(sz0, oz0)
    ix1, iy1, iz1 = min(sx1, ox1), min(sy1, oy1), min(sz1, oz1)
    candidates = (
        _space((sx0, sy0, sz0), (ix0 - sx0, sy1 - sy0, sz1 - sz0)),
        _space((ix1, sy0, sz0), (sx1 - ix1, sy1 - sy0, sz1 - sz0)),
        _space((sx0, sy0, sz0), (sx1 - sx0, iy0 - sy0, sz1 - sz0)),
        _space((sx0, iy1, sz0), (sx1 - sx0, sy1 - iy1, sz1 - sz0)),
        _space((sx0, sy0, sz0), (sx1 - sx0, sy1 - sy0, iz0 - sz0)),
        _space((sx0, sy0, iz1), (sx1 - sx0, sy1 - sy0, sz1 - iz1)),
    )
    return [value for value in candidates if value is not None]


def _deduplicate_spaces(spaces: list[EmptySpace]) -> tuple[list[EmptySpace], int]:
    unique = sorted(
        set(spaces),
        key=lambda item: (
            item.origin_mm[2],
            item.origin_mm[1],
            item.origin_mm[0],
            item.volume_mm3,
            item.size_mm,
        ),
    )
    kept: list[EmptySpace] = []
    for candidate in unique:
        if any(_contains(space, candidate) for space in unique if space != candidate):
            continue
        kept.append(candidate)
    kept.sort(
        key=lambda item: (
            item.origin_mm[2],
            item.origin_mm[1],
            item.origin_mm[0],
            item.volume_mm3,
            item.size_mm,
        )
    )
    return kept, len(spaces) - len(kept)


def _update_extreme_points(
    current: set[tuple[float, float, float]],
    placement: Free3DPlacement,
    spaces: list[EmptySpace],
    xy_clearance: float,
    z_clearance: float,
    counters: _Counters,
    limits: dict[str, int],
) -> set[tuple[float, float, float]]:
    origin = placement.origin_mm
    size = placement.world_size_mm
    generated = {
        _rounded_point((origin[0] + size[0] + xy_clearance, origin[1], origin[2])),
        _rounded_point((origin[0], origin[1] + size[1] + xy_clearance, origin[2])),
        _rounded_point((origin[0], origin[1], origin[2] + size[2] + z_clearance)),
    }
    generated.update(space.origin_mm for space in spaces)
    counters.extreme_points_generated += len(generated)
    candidates = current.union(generated)
    retained = {
        point
        for point in candidates
        if any(_point_inside_space(point, space) for space in spaces)
    }
    counters.extreme_points_deduplicated += len(candidates) - len(retained)
    ordered = sorted(retained, key=lambda value: (value[2], value[1], value[0]))
    if len(ordered) > limits["max_extreme_points"]:
        counters.budget_exhausted = True
        ordered = ordered[: limits["max_extreme_points"]]
    counters.maximum_extreme_points_retained = max(
        counters.maximum_extreme_points_retained, len(ordered)
    )
    return set(ordered)


def _support_at(
    origin: tuple[float, float, float],
    size: tuple[float, float, float],
    placements: list[Free3DPlacement],
    participant: dict[str, object],
    fallback_z_clearance: float,
) -> tuple[tuple[str, ...], float]:
    if origin[2] <= _EPSILON:
        return ("box-floor",), 1.0
    rectangles: list[tuple[float, float, float, float, str]] = []
    for lower in placements:
        clearance = max(
            _participant_clearance(participant, "z", fallback_z_clearance),
            _placement_clearance(lower, "z", fallback_z_clearance),
        )
        lower_top = lower.origin_mm[2] + lower.world_size_mm[2]
        if abs(origin[2] - (lower_top + clearance)) > 0.001:
            continue
        x0 = max(origin[0], lower.origin_mm[0])
        y0 = max(origin[1], lower.origin_mm[1])
        x1 = min(origin[0] + size[0], lower.origin_mm[0] + lower.world_size_mm[0])
        y1 = min(origin[1] + size[1], lower.origin_mm[1] + lower.world_size_mm[1])
        if x1 > x0 + _EPSILON and y1 > y0 + _EPSILON:
            rectangles.append((x0, y0, x1, y1, lower.participant_id))
    area = _rectangle_union_area(rectangles)
    footprint = size[0] * size[1]
    ratio = min(1.0, area / footprint) if footprint > _EPSILON else 1.0
    support_ids = tuple(sorted({value[4] for value in rectangles}))
    return support_ids, ratio


def _rectangle_union_area(rectangles: list[tuple[float, float, float, float, str]]) -> float:
    if not rectangles:
        return 0.0
    xs = sorted({value for rectangle in rectangles for value in (rectangle[0], rectangle[2])})
    area = 0.0
    for left, right in zip(xs, xs[1:]):
        if right <= left + _EPSILON:
            continue
        intervals = sorted(
            (rectangle[1], rectangle[3])
            for rectangle in rectangles
            if rectangle[0] < right - _EPSILON and rectangle[2] > left + _EPSILON
        )
        if not intervals:
            continue
        covered = 0.0
        start, end = intervals[0]
        for next_start, next_end in intervals[1:]:
            if next_start <= end + _EPSILON:
                end = max(end, next_end)
            else:
                covered += end - start
                start, end = next_start, next_end
        covered += end - start
        area += (right - left) * covered
    return area


def _separated_from_placements(
    origin: tuple[float, float, float],
    size: tuple[float, float, float],
    participant: dict[str, object],
    placements: list[Free3DPlacement],
    fallback_xy: float,
    fallback_z: float,
) -> bool:
    for placement in placements:
        separated = False
        for index, axis in enumerate(_AXES):
            fallback = fallback_z if axis == "z" else fallback_xy
            clearance = max(
                _participant_clearance(participant, axis, fallback),
                _placement_clearance(placement, axis, fallback),
            )
            if (
                origin[index] + size[index] + clearance <= placement.origin_mm[index] + 0.001
                or placement.origin_mm[index] + placement.world_size_mm[index] + clearance
                <= origin[index] + 0.001
            ):
                separated = True
                break
        if not separated:
            return False
    return True


def _execution(
    strategy: SolverStrategy,
    budget: SolverBudget,
    status: str,
    stop_reason: str,
    input_digest: str,
    remaining: Iterable[dict[str, object]],
    placements: list[Free3DPlacement],
    spaces: list[EmptySpace],
    points: set[tuple[float, float, float]],
    counters: _Counters,
    box: tuple[float, float, float],
    xy_clearance: float,
    box_clearance: float,
    z_clearance: float,
) -> Free3DGreedyExecution:
    problem_digest = _digest(
        {
            "input_digest": input_digest,
            "strategy": strategy.__dict__,
            "budget": {
                "family_id": budget.family_id,
                "effort_profile": budget.effort_profile,
                "limits": budget.limits,
            },
            "box": box,
            "clearances": (xy_clearance, box_clearance, z_clearance),
            "placements": [placement.__dict__ for placement in placements],
            "remaining": sorted(str(value["id"]) for value in remaining),
        }
    )
    candidate: SolverCandidate | None = None
    admission: Free3DGeometryAdmission | None = None
    if status == "solution_found":
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
        minimum_support = min(
            (value.support_coverage_ratio for value in placements), default=1.0
        )
        candidate = SolverCandidate(
            strategy=strategy,
            candidate_id="free_3d_greedy:complete",
            plan_digest=problem_digest,
            placements=snapshots,
            score_breakdown=(
                ("minimum_support_ratio", _round(minimum_support)),
                ("z_start_levels", float(len({value.origin_mm[2] for value in placements}))),
            ),
            automatic_body_count=0,
        )
        raw_placements = [
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
            raw_placements,
            dict(zip(_AXES, box)),
            box[2],
            xy_clearance,
            box_clearance,
            z_clearance,
        )
        support_ok = all(
            value.support_coverage_ratio + _EPSILON >= 0.25 for value in placements
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
            ValidationCheck("minimum_support", support_ok, "SUPPORT_COVERAGE"),
            ValidationCheck("requested_bodies_only", True, "AUTOMATIC_BODY_FORBIDDEN"),
        )
        admission = Free3DGeometryAdmission(
            schema_version=FREE_3D_GEOMETRY_VALIDATION_V1,
            candidate_digest=candidate.digest,
            admitted=all(check.passed for check in checks),
            checks=checks,
        )
        if not admission.admitted:
            status = "no_solution_within_budget"
            stop_reason = "common_geometry_validation_rejected"
            candidate = None
    telemetry = Free3DSearchTelemetry(
        search_states=counters.search_states,
        placement_trials=counters.placement_trials,
        feasible_options=counters.feasible_options,
        extreme_points_generated=counters.extreme_points_generated,
        extreme_points_deduplicated=counters.extreme_points_deduplicated,
        empty_spaces_generated=counters.empty_spaces_generated,
        empty_spaces_deduplicated=counters.empty_spaces_deduplicated,
        maximum_empty_spaces_retained=counters.maximum_empty_spaces_retained,
        maximum_extreme_points_retained=counters.maximum_extreme_points_retained,
        budget_exhausted=counters.budget_exhausted,
    )
    digest = _digest(
        {
            "problem_digest": problem_digest,
            "status": status,
            "stop_reason": stop_reason,
            "candidate_digest": candidate.digest if candidate is not None else None,
            "telemetry": telemetry.__dict__,
            "spaces": [space.__dict__ for space in spaces],
            "points": sorted(points),
        }
    )
    return Free3DGreedyExecution(
        strategy=strategy,
        budget=budget,
        status=status,
        stop_reason=stop_reason,
        candidate=candidate,
        geometry_admission=admission,
        placements=tuple(placements),
        remaining_participant_ids=tuple(sorted(str(value["id"]) for value in remaining)),
        empty_spaces=tuple(spaces),
        extreme_points_mm=tuple(sorted(points, key=lambda value: (value[2], value[1], value[0]))),
        telemetry=telemetry,
        deterministic_digest=digest,
    )


def _necessary_bound_failure(
    participants: tuple[dict[str, object], ...],
    root_size: tuple[float, float, float],
) -> str | None:
    root_volume = root_size[0] * root_size[1] * root_size[2]
    if sum(_volume(_minimum_local(value)) for value in participants) > root_volume + _EPSILON:
        return "minimum_body_volume_exceeds_useful_box"
    for participant in participants:
        if not any(
            all(size[index] <= root_size[index] + _EPSILON for index in range(3))
            for _, size, _ in _orientations(participant)
        ):
            return f"minimum_envelope_exceeds_axis:{participant['id']}"
    return None


def _budget_limits(budget: SolverBudget) -> dict[str, int]:
    if budget.family_id != FREE_3D_GREEDY_FAMILY_ID:
        raise Free3DGreedyError("The budget family must be free_3d_greedy.")
    limits = dict(budget.limits)
    required = {
        "max_empty_spaces",
        "max_extreme_points",
        "max_placement_trials",
        "max_search_states",
    }
    missing = sorted(required.difference(limits))
    if missing:
        raise Free3DGreedyError(f"Missing hard budget limits: {', '.join(missing)}.")
    if any(limits[name] <= 0 for name in required):
        raise Free3DGreedyError("Every H06 hard budget limit must be positive.")
    return limits


def _participant(value: Mapping[str, object], index: int) -> dict[str, object]:
    required = ("id", "role", "name", "minimum_local_mm", "dimension_modes", "target_local_mm")
    missing = [name for name in required if name not in value]
    if missing:
        raise Free3DGreedyError(
            f"Participant {index} is missing required fields: {', '.join(missing)}."
        )
    result = deepcopy(dict(value))
    minimum = _dimension(result["minimum_local_mm"], f"participants[{index}].minimum_local_mm")
    if any(minimum[axis] <= 0.0 for axis in _AXES):
        raise Free3DGreedyError(f"Participant {index} dimensions must be positive.")
    modes = _mapping(result["dimension_modes"])
    if any(str(modes.get(axis)) not in {"auto", "target", "fixed"} for axis in _AXES):
        raise Free3DGreedyError(f"Participant {index} has an unsupported dimension mode.")
    targets = _mapping(result["target_local_mm"])
    for axis in _AXES:
        target = targets.get(axis)
        if str(modes[axis]) != "fixed":
            continue
        if not isinstance(target, (int, float)) or isinstance(target, bool):
            raise Free3DGreedyError(f"Participant {index} fixed axis {axis} needs a numeric target.")
        if float(target) + _EPSILON < minimum[axis]:
            raise Free3DGreedyError(f"Participant {index} fixed axis {axis} is smaller than its minimum.")
    result["minimum_local_mm"] = minimum
    return result


def _box_dimensions(
    box: Mapping[str, object], storage_height_mm: float
) -> tuple[float, float, float]:
    dimensions = _dimension(box, "box")
    height = float(storage_height_mm)
    result = (dimensions["x"], dimensions["y"], height)
    if any(value <= 0.0 for value in result):
        raise Free3DGreedyError("Box and storage dimensions must be positive.")
    return result


def _fits_in_space(
    point: tuple[float, float, float],
    size: tuple[float, float, float],
    space: EmptySpace,
) -> bool:
    upper = _upper(space)
    return _point_inside_space(point, space) and all(
        point[index] + size[index] <= upper[index] + _EPSILON for index in range(3)
    )


def _point_inside_space(point: tuple[float, float, float], space: EmptySpace) -> bool:
    upper = _upper(space)
    return all(
        space.origin_mm[index] - _EPSILON <= point[index] < upper[index] - _EPSILON
        for index in range(3)
    )


def _inside_box(
    origin: tuple[float, float, float],
    size: tuple[float, float, float],
    box: tuple[float, float, float],
) -> bool:
    return all(
        origin[index] >= -_EPSILON
        and origin[index] + size[index] <= box[index] + _EPSILON
        for index in range(3)
    )


def _spaces_intersect(left: EmptySpace, right: EmptySpace) -> bool:
    left_upper, right_upper = _upper(left), _upper(right)
    return all(
        left.origin_mm[index] < right_upper[index] - _EPSILON
        and right.origin_mm[index] < left_upper[index] - _EPSILON
        for index in range(3)
    )


def _contains(outer: EmptySpace, inner: EmptySpace) -> bool:
    outer_upper, inner_upper = _upper(outer), _upper(inner)
    return all(
        outer.origin_mm[index] <= inner.origin_mm[index] + _EPSILON
        and outer_upper[index] + _EPSILON >= inner_upper[index]
        for index in range(3)
    )


def _space(
    origin: tuple[float, float, float], size: tuple[float, float, float]
) -> EmptySpace | None:
    if any(value <= _EPSILON for value in size):
        return None
    return EmptySpace(_rounded_point(origin), _rounded_point(size))


def _upper(space: EmptySpace) -> tuple[float, float, float]:
    return tuple(
        space.origin_mm[index] + space.size_mm[index] for index in range(3)
    )  # type: ignore[return-value]


def _minimum_local(participant: Mapping[str, object]) -> tuple[float, float, float]:
    minimum = _mapping(participant["minimum_local_mm"])
    modes = _mapping(participant["dimension_modes"])
    targets = _mapping(participant["target_local_mm"])
    return tuple(
        float(targets[axis])
        if str(modes[axis]) == "fixed"
        else float(minimum[axis])
        for axis in _AXES
    )  # type: ignore[return-value]


def _participant_clearance(
    participant: Mapping[str, object], axis: str, fallback: float
) -> float:
    policy = participant.get("external_clearance_effective_v1")
    if not isinstance(policy, dict):
        return fallback
    between = policy.get("between_mm")
    if not isinstance(between, dict):
        return fallback
    value = between.get(axis)
    return float(value) if isinstance(value, (int, float)) and not isinstance(value, bool) else fallback


def _placement_clearance(
    placement: Free3DPlacement, axis: str, fallback: float
) -> float:
    # The immutable placement intentionally carries only resolved geometry.  The
    # adapter already passes the maximum participant fallback, so this remains
    # conservative without duplicating mutable policy mappings in search state.
    return fallback


def _dimension(value: object, field: str) -> dict[str, float]:
    if not isinstance(value, Mapping):
        raise Free3DGreedyError(f"{field} must be an object.")
    try:
        result = {axis: float(value[axis]) for axis in _AXES}
    except (KeyError, TypeError, ValueError) as exc:
        raise Free3DGreedyError(f"{field} must define numeric x, y and z.") from exc
    if any(number < 0.0 for number in result.values()):
        raise Free3DGreedyError(f"{field} cannot contain a negative dimension.")
    return result


def _mapping(value: object) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise Free3DGreedyError("Internal H06 value must be an object.")
    return value


def _non_negative(value: float, field: str) -> float:
    result = float(value)
    if result < 0.0:
        raise Free3DGreedyError(f"{field} must be non-negative.")
    return result


def _volume(value: tuple[float, float, float]) -> float:
    return value[0] * value[1] * value[2]


def _rounded_point(value: tuple[float, float, float]) -> tuple[float, float, float]:
    return tuple(_round(number) for number in value)  # type: ignore[return-value]


def _round(value: float) -> float:
    return round(float(value), 4)


def _digest(value: object) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()
