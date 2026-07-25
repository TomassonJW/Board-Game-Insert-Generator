"""Bounded global rectangular finishing partition built by construction."""

from __future__ import annotations

from dataclasses import dataclass
from math import prod
from time import perf_counter
from typing import Mapping, Sequence

from board_game_insert_generator.free_3d_continuous_closure import (
    FINISHING_OBJECTIVE_BALANCED_THEN_PROPORTIONAL,
)
from board_game_insert_generator.free_3d_beam_solver import VariantFree3DPlacement
from board_game_insert_generator.free_3d_greedy_solver import (
    Free3DPlacement,
    TopInsetZone,
)
from board_game_insert_generator.incremental_project_state import canonical_digest
from board_game_insert_generator.solver_contract import SolverBudget


GLOBAL_RECTANGULAR_CLOSURE_VERSION = "bgig.global_rectangular_closure.v1"
GLOBAL_RECTANGULAR_CERTIFICATE_SCHEMA_V1 = (
    "bgig.global_rectangular_partition_certificate.v1"
)
_EPSILON = 0.0001
_AXES = (0, 1, 2)


@dataclass(frozen=True)
class GlobalRectangularClosureResult:
    status: str
    placements: tuple[Free3DPlacement, ...]
    empty_spaces: tuple[object, ...]
    deterministic_digest: str
    incumbent_digest: str
    iterations: int
    candidates_evaluated: int
    repair_attempts: int
    repairs_applied: int
    global_resolve_invocation_count: int
    deadline_reached: bool
    initial_residual_metric: tuple[float, float, int]
    final_residual_metric: tuple[float, float, int]
    aligned_face_count: int
    finishing_objective: str
    objective_score: tuple[float, float, float, float]
    objective_candidate_count: int
    selected_objective_id: str
    partition_certificate: dict[str, object]
    closure_version: str = GLOBAL_RECTANGULAR_CLOSURE_VERSION


@dataclass(frozen=True)
class _Bounds:
    lower: tuple[float, float, float]
    upper: tuple[float, float, float]

    def size(self) -> tuple[float, float, float]:
        return tuple(self.upper[axis] - self.lower[axis] for axis in _AXES)  # type: ignore[return-value]

    def volume(self) -> float:
        return prod(self.size())


@dataclass(frozen=True)
class _Item:
    item_id: str
    kind: str
    bounds: _Bounds
    placement: Free3DPlacement | None
    expandable_world: tuple[bool, bool, bool]


@dataclass(frozen=True)
class _Candidate:
    placements: tuple[Free3DPlacement, ...]
    technical_void_volume_mm3: float
    reservation_volume_mm3: float
    split_count: int
    max_depth: int


class _SearchState:
    def __init__(
        self,
        deadline_at: float,
        max_candidates: int,
        initial_placements: Sequence[Free3DPlacement],
    ) -> None:
        self.deadline_at = deadline_at
        self.max_candidates = max_candidates
        self.candidates = 0
        self.iterations = 0
        self.deadline_reached = False
        self.initial_placements = tuple(initial_placements)
        self.memo: dict[tuple[object, ...], _Candidate | None] = {}

    def stopped(self) -> bool:
        if perf_counter() >= self.deadline_at:
            self.deadline_reached = True
            return True
        return self.candidates >= self.max_candidates


def close_global_rectangular_partition(
    participants: Sequence[Mapping[str, object]],
    placements: Sequence[Free3DPlacement],
    box: Mapping[str, object],
    storage_height_mm: float,
    xy_clearance_mm: float,
    *,
    box_perimeter_xy_mm: float,
    between_bodies_z_mm: float,
    budget: SolverBudget,
    top_inset_zones: Sequence[TopInsetZone] = (),
) -> GlobalRectangularClosureResult:
    """Partition all printable volume into rectangular owners and fixed voids."""

    limits = dict(budget.limits)
    elapsed_ms = max(1, int(limits.get("max_closure_elapsed_ms", 1_000)))
    max_candidates = max(1, int(limits.get("max_closure_candidates", 10_000)))
    state = _SearchState(
        perf_counter() + elapsed_ms / 1000.0,
        max_candidates,
        placements,
    )
    root = _Bounds(
        (box_perimeter_xy_mm, box_perimeter_xy_mm, 0.0),
        (
            float(box["x"]) - box_perimeter_xy_mm,
            float(box["y"]) - box_perimeter_xy_mm,
            float(storage_height_mm),
        ),
    )
    incumbent_digest = canonical_digest(
        {
            "placements": [_placement_payload(value) for value in placements],
            "root": _bounds_payload(root),
        }
    )
    participant_by_id = {str(value["id"]): value for value in participants}
    items: list[_Item] = []
    for placement in placements:
        bounds = _placement_bounds(placement)
        participant = participant_by_id.get(placement.participant_id, {})
        items.append(
            _Item(
                placement.participant_id,
                "body",
                bounds,
                placement,
                _expandable_world(participant, placement),
            )
        )
    for index, zone in enumerate(top_inset_zones):
        zone_bounds = _reservation_bounds(zone, root)
        if zone_bounds is not None:
            items.append(
                _Item(
                    f"reservation:{index:04d}",
                    "reservation",
                    zone_bounds,
                    None,
                    (False, False, False),
                )
            )
    initial_body_volume = sum(
        _placement_bounds(value).volume() for value in placements
    )
    reservation_volume = sum(
        value.bounds.volume() for value in items if value.kind == "reservation"
    )
    initial_residual = max(
        0.0,
        root.volume() - reservation_volume - initial_body_volume,
    )
    failure_reason = _input_rejection(items, root)
    if failure_reason:
        return _failure_result(
            failure_reason,
            placements,
            incumbent_digest,
            state,
            initial_residual,
        )
    candidate = _solve_partition(
        tuple(items),
        root,
        state,
        depth=0,
        xy_clearance_mm=float(xy_clearance_mm),
        z_clearance_mm=float(between_bodies_z_mm),
    )
    if candidate is None:
        reason = (
            "global_rectangular_partition_deadline_reached"
            if state.deadline_reached
            else "global_rectangular_partition_not_found"
        )
        return _failure_result(
            reason,
            placements,
            incumbent_digest,
            state,
            initial_residual,
        )
    supported = _with_supports(
        candidate.placements,
        float(between_bodies_z_mm),
    )
    score = _objective_score(placements, supported)
    certificate = _partition_certificate(
        root,
        supported,
        candidate,
        body_count=len(placements),
    )
    if certificate["certified"] is not True:
        return _failure_result(
            "global_rectangular_partition_certificate_rejected",
            placements,
            incumbent_digest,
            state,
            initial_residual,
            certificate=certificate,
        )
    digest = canonical_digest(
        {
            "schema_version": GLOBAL_RECTANGULAR_CLOSURE_VERSION,
            "placements": [_placement_payload(value) for value in supported],
            "certificate": certificate,
            "objective_score": score,
        }
    )
    return GlobalRectangularClosureResult(
        status="closed",
        placements=supported,
        empty_spaces=(),
        deterministic_digest=digest,
        incumbent_digest=incumbent_digest,
        iterations=state.iterations,
        candidates_evaluated=state.candidates,
        repair_attempts=0,
        repairs_applied=0,
        global_resolve_invocation_count=1,
        deadline_reached=state.deadline_reached,
        initial_residual_metric=(initial_residual, initial_residual, len(items)),
        final_residual_metric=(0.0, 0.0, 0),
        aligned_face_count=candidate.split_count * 2,
        finishing_objective=FINISHING_OBJECTIVE_BALANCED_THEN_PROPORTIONAL,
        objective_score=score,
        objective_candidate_count=state.candidates,
        selected_objective_id="global_balanced_rectangular_partition",
        partition_certificate=certificate,
    )


def _solve_partition(
    items: tuple[_Item, ...],
    region: _Bounds,
    state: _SearchState,
    *,
    depth: int,
    xy_clearance_mm: float,
    z_clearance_mm: float,
) -> _Candidate | None:
    if state.stopped():
        return None
    state.iterations += 1
    key = (
        tuple(sorted(value.item_id for value in items)),
        tuple(round(value, 6) for value in region.lower + region.upper),
    )
    if key in state.memo:
        return state.memo[key]
    if len(items) == 1:
        leaf = _leaf_candidate(items[0], region, depth)
        state.memo[key] = leaf
        return leaf
    best: _Candidate | None = None
    seen_partitions: set[tuple[tuple[str, ...], tuple[str, ...], int]] = set()
    for axis in _AXES:
        ordered = tuple(
            sorted(
                items,
                key=lambda value: (
                    value.bounds.lower[axis],
                    value.bounds.upper[axis],
                    value.item_id,
                ),
            )
        )
        for split_index in range(1, len(ordered)):
            left_items = ordered[:split_index]
            right_items = ordered[split_index:]
            signature = (
                tuple(sorted(value.item_id for value in left_items)),
                tuple(sorted(value.item_id for value in right_items)),
                axis,
            )
            if signature in seen_partitions:
                continue
            seen_partitions.add(signature)
            gap = xy_clearance_mm if axis in (0, 1) else z_clearance_mm
            left_minimum = max(value.bounds.upper[axis] for value in left_items)
            right_maximum = min(value.bounds.lower[axis] for value in right_items) - gap
            if left_minimum > right_maximum + _EPSILON:
                continue
            for cut in _cut_candidates(
                region,
                axis,
                left_minimum,
                right_maximum,
                left_items,
                right_items,
                gap,
            ):
                if state.stopped():
                    break
                left_region, right_region = _split_region(region, axis, cut, gap)
                left = _solve_partition(
                    left_items,
                    left_region,
                    state,
                    depth=depth + 1,
                    xy_clearance_mm=xy_clearance_mm,
                    z_clearance_mm=z_clearance_mm,
                )
                if left is None:
                    continue
                right = _solve_partition(
                    right_items,
                    right_region,
                    state,
                    depth=depth + 1,
                    xy_clearance_mm=xy_clearance_mm,
                    z_clearance_mm=z_clearance_mm,
                )
                if right is None:
                    continue
                state.candidates += 1
                gap_volume = gap * prod(
                    region.size()[other] for other in _AXES if other != axis
                )
                combined = _Candidate(
                    placements=left.placements + right.placements,
                    technical_void_volume_mm3=(
                        left.technical_void_volume_mm3
                        + right.technical_void_volume_mm3
                        + gap_volume
                    ),
                    reservation_volume_mm3=(
                        left.reservation_volume_mm3
                        + right.reservation_volume_mm3
                    ),
                    split_count=left.split_count + right.split_count + 1,
                    max_depth=max(left.max_depth, right.max_depth),
                )
                if best is None or _candidate_rank(
                    combined, state.initial_placements
                ) < _candidate_rank(best, state.initial_placements):
                    best = combined
    state.memo[key] = best
    return best


def _leaf_candidate(item: _Item, region: _Bounds, depth: int) -> _Candidate | None:
    if item.kind == "reservation":
        if not _same_bounds(item.bounds, region):
            return None
        return _Candidate((), 0.0, region.volume(), 0, depth)
    placement = item.placement
    if placement is None or not _contains(region, item.bounds):
        return None
    size = region.size()
    current_size = tuple(float(value) for value in placement.world_size_mm)
    for axis in _AXES:
        if size[axis] + _EPSILON < current_size[axis]:
            return None
        if (
            not item.expandable_world[axis]
            and abs(size[axis] - current_size[axis]) > _EPSILON
        ):
            return None
    rotation = int(placement.rotation_deg_z) % 360
    local_size = (
        (size[1], size[0], size[2])
        if rotation in {90, 270}
        else size
    )
    grown = _rebuild_placement(
        placement,
        origin_mm=region.lower,
        world_size_mm=size,
        local_size_mm=local_size,
        supporting_ids=(),
        support_coverage_ratio=0.0,
    )
    return _Candidate((grown,), 0.0, 0.0, 0, depth)


def _cut_candidates(
    region: _Bounds,
    axis: int,
    lower: float,
    upper: float,
    left_items: Sequence[_Item],
    right_items: Sequence[_Item],
    gap: float,
) -> tuple[float, ...]:
    if lower > upper + _EPSILON:
        return ()
    left_weight = sum(value.bounds.volume() for value in left_items)
    right_weight = sum(value.bounds.volume() for value in right_items)
    total = max(_EPSILON, left_weight + right_weight)
    available = max(0.0, region.size()[axis] - gap)
    target = region.lower[axis] + available * left_weight / total
    values = (
        min(upper, max(lower, target)),
        (lower + upper) / 2.0,
        lower,
        upper,
    )
    unique: list[float] = []
    for value in values:
        rounded = round(value, 6)
        if (
            region.lower[axis] - _EPSILON <= rounded
            and rounded + gap <= region.upper[axis] + _EPSILON
            and all(abs(rounded - existing) > _EPSILON for existing in unique)
        ):
            unique.append(rounded)
    return tuple(unique)


def _split_region(
    region: _Bounds,
    axis: int,
    cut: float,
    gap: float,
) -> tuple[_Bounds, _Bounds]:
    left_upper = list(region.upper)
    left_upper[axis] = cut
    right_lower = list(region.lower)
    right_lower[axis] = cut + gap
    return (
        _Bounds(region.lower, tuple(left_upper)),
        _Bounds(tuple(right_lower), region.upper),
    )


def _candidate_rank(
    candidate: _Candidate,
    initial_placements: Sequence[Free3DPlacement],
) -> tuple[object, ...]:
    score = _objective_score(initial_placements, candidate.placements)
    signature = tuple(
        sorted(
            (
                value.participant_id,
                tuple(round(item, 6) for item in value.origin_mm),
                tuple(round(item, 6) for item in value.world_size_mm),
            )
            for value in candidate.placements
        )
    )
    return score + (candidate.max_depth, candidate.split_count, signature)


def _with_supports(
    placements: Sequence[Free3DPlacement],
    z_clearance_mm: float,
) -> tuple[Free3DPlacement, ...]:
    result: list[Free3DPlacement] = []
    for placement in placements:
        if placement.origin_mm[2] <= _EPSILON:
            support_ids = ("box-floor",)
            coverage = 1.0
        else:
            supports: list[str] = []
            supported_area = 0.0
            for lower in placements:
                if lower.participant_id == placement.participant_id:
                    continue
                lower_top = lower.origin_mm[2] + lower.world_size_mm[2]
                if abs(lower_top + z_clearance_mm - placement.origin_mm[2]) > _EPSILON:
                    continue
                overlap_x = _overlap(
                    placement.origin_mm[0],
                    placement.world_size_mm[0],
                    lower.origin_mm[0],
                    lower.world_size_mm[0],
                )
                overlap_y = _overlap(
                    placement.origin_mm[1],
                    placement.world_size_mm[1],
                    lower.origin_mm[1],
                    lower.world_size_mm[1],
                )
                if overlap_x * overlap_y > _EPSILON:
                    supports.append(lower.participant_id)
                    supported_area += overlap_x * overlap_y
            base_area = placement.world_size_mm[0] * placement.world_size_mm[1]
            support_ids = tuple(sorted(supports))
            coverage = min(1.0, supported_area / base_area) if base_area else 0.0
        result.append(
            _rebuild_placement(
                placement,
                origin_mm=placement.origin_mm,
                world_size_mm=placement.world_size_mm,
                local_size_mm=placement.local_size_mm,
                supporting_ids=support_ids,
                support_coverage_ratio=coverage,
            )
        )
    return tuple(sorted(result, key=lambda value: value.participant_id))


def _rebuild_placement(
    source: Free3DPlacement,
    *,
    origin_mm: tuple[float, float, float],
    world_size_mm: tuple[float, float, float],
    local_size_mm: tuple[float, float, float],
    supporting_ids: tuple[str, ...],
    support_coverage_ratio: float,
) -> Free3DPlacement:
    common = {
        "participant_id": source.participant_id,
        "role": source.role,
        "name": source.name,
        "origin_mm": origin_mm,
        "world_size_mm": world_size_mm,
        "local_size_mm": local_size_mm,
        "rotation_deg_z": source.rotation_deg_z,
        "supporting_ids": supporting_ids,
        "support_coverage_ratio": support_coverage_ratio,
    }
    if isinstance(source, VariantFree3DPlacement):
        return VariantFree3DPlacement(
            **common,
            container_variant_id=source.container_variant_id,
            container_variant_digest=source.container_variant_digest,
            container_variant_canonical=source.container_variant_canonical,
        )
    return Free3DPlacement(**common)


def _partition_certificate(
    root: _Bounds,
    placements: Sequence[Free3DPlacement],
    candidate: _Candidate,
    *,
    body_count: int,
) -> dict[str, object]:
    root_volume = root.volume()
    body_volume = sum(_placement_bounds(value).volume() for value in placements)
    accounted = (
        body_volume
        + candidate.technical_void_volume_mm3
        + candidate.reservation_volume_mm3
    )
    error = abs(root_volume - accounted)
    tolerance = max(_EPSILON, root_volume * 1e-9)
    unique_ids = len({value.participant_id for value in placements})
    certified = bool(
        len(placements) == body_count
        and unique_ids == body_count
        and error <= tolerance
    )
    return {
        "schema_version": GLOBAL_RECTANGULAR_CERTIFICATE_SCHEMA_V1,
        "certified": certified,
        "root_volume_mm3": round(root_volume, 6),
        "printable_volume_mm3": round(
            root_volume
            - candidate.technical_void_volume_mm3
            - candidate.reservation_volume_mm3,
            6,
        ),
        "body_volume_mm3": round(body_volume, 6),
        "technical_void_volume_mm3": round(
            candidate.technical_void_volume_mm3, 6
        ),
        "reserved_prism_volume_mm3": round(
            candidate.reservation_volume_mm3, 6
        ),
        "coverage_error_mm3": round(error, 9),
        "printable_residual_volume_mm3": 0.0 if certified else round(error, 6),
        "owner_count": unique_ids,
        "rectangular_body_count": len(placements),
        "every_body_owned_exactly_once": unique_ids == body_count,
        "technical_voids_certified": certified,
        "reserved_prisms_excluded": True,
        "composite_annexes_used": False,
        "partition_complete_by_construction": certified,
    }


def _failure_result(
    reason: str,
    placements: Sequence[Free3DPlacement],
    incumbent_digest: str,
    state: _SearchState,
    initial_residual: float,
    *,
    certificate: Mapping[str, object] | None = None,
) -> GlobalRectangularClosureResult:
    rejected = dict(certificate or {})
    rejected.update(
        {
            "schema_version": GLOBAL_RECTANGULAR_CERTIFICATE_SCHEMA_V1,
            "certified": False,
            "stop_reason": reason,
            "printable_residual_volume_mm3": round(initial_residual, 6),
        }
    )
    digest = canonical_digest(
        {
            "schema_version": GLOBAL_RECTANGULAR_CLOSURE_VERSION,
            "status": reason,
            "incumbent_digest": incumbent_digest,
            "certificate": rejected,
        }
    )
    score = _objective_score(placements, placements)
    return GlobalRectangularClosureResult(
        status="no_global_rectangular_partition",
        placements=tuple(placements),
        empty_spaces=(reason,),
        deterministic_digest=digest,
        incumbent_digest=incumbent_digest,
        iterations=state.iterations,
        candidates_evaluated=state.candidates,
        repair_attempts=0,
        repairs_applied=0,
        global_resolve_invocation_count=1,
        deadline_reached=state.deadline_reached,
        initial_residual_metric=(initial_residual, initial_residual, 1),
        final_residual_metric=(initial_residual, initial_residual, 1),
        aligned_face_count=0,
        finishing_objective=FINISHING_OBJECTIVE_BALANCED_THEN_PROPORTIONAL,
        objective_score=score,
        objective_candidate_count=state.candidates,
        selected_objective_id="not_found",
        partition_certificate=rejected,
    )


def _input_rejection(items: Sequence[_Item], root: _Bounds) -> str:
    if not items or any(value <= _EPSILON for value in root.size()):
        return "global_rectangular_partition_invalid_root"
    for item in items:
        if not _contains(root, item.bounds):
            return "global_rectangular_partition_item_outside_root"
    reservations = [value for value in items if value.kind == "reservation"]
    for index, left in enumerate(reservations):
        for right in reservations[index + 1 :]:
            if _intersects(left.bounds, right.bounds):
                return "global_rectangular_partition_overlapping_reservations"
    bodies = [value for value in items if value.kind == "body"]
    for body in bodies:
        for reservation in reservations:
            if _intersects(body.bounds, reservation.bounds):
                return "global_rectangular_partition_body_enters_reservation"
    return ""


def _expandable_world(
    participant: Mapping[str, object],
    placement: Free3DPlacement,
) -> tuple[bool, bool, bool]:
    if placement.role != "container":
        return (False, False, False)
    modes = participant.get("dimension_modes")
    if not isinstance(modes, Mapping):
        return (True, True, True)
    rotation = int(placement.rotation_deg_z) % 360
    local_axes = ("y", "x", "z") if rotation in {90, 270} else ("x", "y", "z")
    return tuple(
        str(modes.get(axis, "auto")) != "fixed" for axis in local_axes
    )  # type: ignore[return-value]


def _reservation_bounds(zone: TopInsetZone, root: _Bounds) -> _Bounds | None:
    lower = (
        max(root.lower[0], float(zone.origin_xy_mm[0])),
        max(root.lower[1], float(zone.origin_xy_mm[1])),
        max(root.lower[2], float(zone.support_plane_z_mm)),
    )
    upper = (
        min(root.upper[0], float(zone.origin_xy_mm[0] + zone.size_xy_mm[0])),
        min(root.upper[1], float(zone.origin_xy_mm[1] + zone.size_xy_mm[1])),
        min(
            root.upper[2],
            float(zone.support_plane_z_mm + zone.inset_depth_mm),
        ),
    )
    bounds = _Bounds(lower, upper)
    return bounds if all(value > _EPSILON for value in bounds.size()) else None


def _placement_bounds(placement: Free3DPlacement) -> _Bounds:
    return _Bounds(
        tuple(float(value) for value in placement.origin_mm),
        tuple(
            float(placement.origin_mm[axis] + placement.world_size_mm[axis])
            for axis in _AXES
        ),
    )


def _objective_score(
    before: Sequence[Free3DPlacement],
    after: Sequence[Free3DPlacement],
) -> tuple[float, float, float, float]:
    before_volume = {
        value.participant_id: _placement_bounds(value).volume() for value in before
    }
    added: list[float] = []
    ratios: list[float] = []
    for value in after:
        final_volume = _placement_bounds(value).volume()
        initial = before_volume.get(value.participant_id, final_volume)
        added.append(max(0.0, final_volume - initial))
        ratios.append(final_volume / initial - 1.0 if initial > _EPSILON else 0.0)
    return (
        _spread(added),
        _mean_absolute_deviation(added),
        _spread(ratios),
        _mean_absolute_deviation(ratios),
    )


def _spread(values: Sequence[float]) -> float:
    return max(values, default=0.0) - min(values, default=0.0)


def _mean_absolute_deviation(values: Sequence[float]) -> float:
    if not values:
        return 0.0
    mean = sum(values) / len(values)
    return sum(abs(value - mean) for value in values) / len(values)


def _contains(outer: _Bounds, inner: _Bounds) -> bool:
    return all(
        outer.lower[axis] <= inner.lower[axis] + _EPSILON
        and outer.upper[axis] + _EPSILON >= inner.upper[axis]
        for axis in _AXES
    )


def _same_bounds(left: _Bounds, right: _Bounds) -> bool:
    return all(
        abs(left.lower[axis] - right.lower[axis]) <= _EPSILON
        and abs(left.upper[axis] - right.upper[axis]) <= _EPSILON
        for axis in _AXES
    )


def _intersects(left: _Bounds, right: _Bounds) -> bool:
    return all(
        left.lower[axis] < right.upper[axis] - _EPSILON
        and right.lower[axis] < left.upper[axis] - _EPSILON
        for axis in _AXES
    )


def _overlap(
    left_origin: float,
    left_size: float,
    right_origin: float,
    right_size: float,
) -> float:
    return max(
        0.0,
        min(left_origin + left_size, right_origin + right_size)
        - max(left_origin, right_origin),
    )


def _bounds_payload(bounds: _Bounds) -> dict[str, list[float]]:
    return {
        "lower": [round(value, 6) for value in bounds.lower],
        "upper": [round(value, 6) for value in bounds.upper],
    }


def _placement_payload(placement: Free3DPlacement) -> dict[str, object]:
    return {
        "participant_id": placement.participant_id,
        "origin_mm": [round(value, 6) for value in placement.origin_mm],
        "world_size_mm": [round(value, 6) for value in placement.world_size_mm],
        "local_size_mm": [round(value, 6) for value in placement.local_size_mm],
        "rotation_deg_z": placement.rotation_deg_z,
        "supporting_ids": list(placement.supporting_ids),
        "support_coverage_ratio": round(
            placement.support_coverage_ratio, 6
        ),
        "container_variant_id": str(
            getattr(placement, "container_variant_id", "")
        ),
        "container_variant_digest": str(
            getattr(placement, "container_variant_digest", "")
        ),
    }
