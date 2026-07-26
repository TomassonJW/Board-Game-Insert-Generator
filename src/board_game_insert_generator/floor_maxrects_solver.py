"""Deterministic floor-only MaxRects lane for dense minimal layouts.

This bounded construction is a fast path only when every minimum envelope can
stay on the box floor. Complex stacking remains owned by the 3D portfolio and
SCIP product solver.
"""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
from typing import Iterable, Mapping

from board_game_insert_generator.free_3d_greedy_solver import (
    Free3DPlacement,
    TopInsetZone,
)


FLOOR_MAXRECTS_VERSION = "bgig.floor_maxrects.v1"
_EPSILON = 0.0001
_AXES = ("x", "y", "z")


@dataclass(frozen=True)
class FloorMaxRectsResult:
    status: str
    placements: tuple[Free3DPlacement, ...]
    order_attempts: int
    placement_trials: int
    construction_mode: str
    deterministic_digest: str


@dataclass(frozen=True)
class _Rect:
    participant_id: str
    width: float
    height: float
    depth: float
    role: str
    name: str


@dataclass(frozen=True)
class _Space:
    x: float
    y: float
    width: float
    height: float


def solve_floor_maxrects(
    participants: Iterable[Mapping[str, object]],
    box: Mapping[str, object],
    storage_height_mm: float,
    between_bodies_xy_mm: float,
    *,
    box_perimeter_xy_mm: float,
    top_inset_zones: Iterable[TopInsetZone] = (),
) -> FloorMaxRectsResult:
    """Pack all immutable minimum envelopes on z=0 or fail without mutation."""

    values = tuple(dict(value) for value in participants)
    gap = float(between_bodies_xy_mm)
    margin = float(box_perimeter_xy_mm)
    usable_width = float(box["x"]) - 2.0 * margin + gap
    usable_height = float(box["y"]) - 2.0 * margin + gap
    zones = tuple(top_inset_zones)
    rectangles = tuple(_rect(value) for value in values)
    if (
        not rectangles
        or usable_width <= _EPSILON
        or usable_height <= _EPSILON
        or any(value.depth > storage_height_mm + _EPSILON for value in rectangles)
    ):
        return _result("no_solution_within_budget", (), 0, 0)

    orderings = _orderings(rectangles)
    placement_trials = 0
    shelf_orderings = (
        tuple(
            sorted(
                rectangles,
                key=lambda value: (
                    0 if max(value.width, value.height) > usable_height / 2.0 else 1,
                    0 if abs(value.width - value.height) <= _EPSILON else 1,
                    -value.width * value.height,
                    value.participant_id,
                ),
            )
        ),
        *orderings,
    )
    for order_index, ordering in enumerate(shelf_orderings, start=1):
        packed, trials = _pack_shelves(
            ordering,
            usable_width,
            usable_height,
            gap,
            margin,
            zones,
        )
        placement_trials += trials
        if packed is not None:
            return _result(
                "solution_found",
                tuple(sorted(packed, key=lambda value: value.participant_id)),
                order_index,
                placement_trials,
                construction_mode="guillotine_shelves",
            )
    for order_index, ordering in enumerate(orderings, start=1):
        for score_mode in range(3):
            packed, trials = _pack(
                ordering,
                usable_width,
                usable_height,
                gap,
                margin,
                zones,
                score_mode,
            )
            placement_trials += trials
            if packed is not None:
                return _result(
                    "solution_found",
                    tuple(sorted(packed, key=lambda value: value.participant_id)),
                    (order_index - 1) * 3 + score_mode + 1,
                    placement_trials,
                    construction_mode="maxrects",
                )
    return _result(
        "no_solution_within_budget",
        (),
        len(orderings) * 3,
        placement_trials,
        construction_mode="none",
    )


def _rect(participant: Mapping[str, object]) -> _Rect:
    minimum = _mapping(participant["minimum_local_mm"])
    return _Rect(
        participant_id=str(participant["id"]),
        width=float(minimum["x"]),
        height=float(minimum["y"]),
        depth=float(minimum["z"]),
        role=str(participant["role"]),
        name=str(participant.get("name", participant["id"])),
    )


def _orderings(values: tuple[_Rect, ...]) -> tuple[tuple[_Rect, ...], ...]:
    keys = (
        lambda value: (-value.width * value.height, -max(value.width, value.height), value.participant_id),
        lambda value: (-max(value.width, value.height), -value.width * value.height, value.participant_id),
        lambda value: (-value.width, -value.height, value.participant_id),
        lambda value: (-value.height, -value.width, value.participant_id),
        lambda value: (-(value.width + value.height), -value.width * value.height, value.participant_id),
        lambda value: (-min(value.width, value.height), -max(value.width, value.height), value.participant_id),
    )
    result: list[tuple[_Rect, ...]] = []
    for key in keys:
        ordered = tuple(sorted(values, key=key))
        if ordered not in result:
            result.append(ordered)
    return tuple(result)


def _pack_shelves(
    ordering: tuple[_Rect, ...],
    usable_width: float,
    usable_height: float,
    gap: float,
    margin: float,
    zones: tuple[TopInsetZone, ...],
) -> tuple[list[Free3DPlacement] | None, int]:
    states: list[tuple[tuple[tuple[float, float], ...], tuple[tuple[_Rect, int, float, float], ...]]] = [
        ((), ())
    ]
    trials = 0
    for value in ordering:
        candidates: list[
            tuple[
                tuple[tuple[float, float], ...],
                tuple[tuple[_Rect, int, float, float], ...],
            ]
        ] = []
        for shelves, placed in states:
            total_height = sum(shelf[0] for shelf in shelves)
            for rotation, body_width, body_height in (
                (0, value.width, value.height),
                (90, value.height, value.width),
            ):
                used_width = body_width + gap
                used_height = body_height + gap
                for shelf_index, (shelf_height, shelf_width) in enumerate(shelves):
                    trials += 1
                    y = sum(item[0] for item in shelves[:shelf_index])
                    if (
                        used_height > shelf_height + _EPSILON
                        or shelf_width + used_width > usable_width + _EPSILON
                        or not _top_insets_allow(
                            margin + shelf_width,
                            margin + y,
                            body_width,
                            body_height,
                            value.depth,
                            zones,
                        )
                    ):
                        continue
                    changed = list(shelves)
                    changed[shelf_index] = (shelf_height, shelf_width + used_width)
                    candidates.append(
                        (
                            tuple(changed),
                            placed + ((value, rotation, shelf_width, y),),
                        )
                    )
                trials += 1
                if (
                    total_height + used_height <= usable_height + _EPSILON
                    and used_width <= usable_width + _EPSILON
                    and _top_insets_allow(
                        margin,
                        margin + total_height,
                        body_width,
                        body_height,
                        value.depth,
                        zones,
                    )
                ):
                    candidates.append(
                        (
                            shelves + ((used_height, used_width),),
                            placed + ((value, rotation, 0.0, total_height),),
                        )
                    )
        if not candidates:
            return None, trials
        deduplicated: dict[
            tuple[tuple[float, float], ...],
            tuple[
                tuple[tuple[float, float], ...],
                tuple[tuple[_Rect, int, float, float], ...],
            ],
        ] = {}
        for candidate in candidates:
            signature = tuple(
                (round(height, 6), round(width, 6))
                for height, width in candidate[0]
            )
            deduplicated.setdefault(signature, candidate)
        states = sorted(
            deduplicated.values(),
            key=lambda candidate: (
                round(sum(value[0] for value in candidate[0]), 6),
                len(candidate[0]),
                round(
                    sum(
                        height * (usable_width - width)
                        for height, width in candidate[0]
                    ),
                    6,
                ),
                tuple(
                    (round(height, 6), round(width, 6))
                    for height, width in candidate[0]
                ),
            ),
        )[:512]
    if not states:
        return None, trials
    shelves, packed = min(
        states,
        key=lambda candidate: (
            round(sum(value[0] for value in candidate[0]), 6),
            len(candidate[0]),
            tuple(
                (round(height, 6), round(width, 6))
                for height, width in candidate[0]
            ),
        ),
    )
    del shelves
    placements = [
        Free3DPlacement(
            participant_id=value.participant_id,
            role=value.role,
            name=value.name,
            origin_mm=(margin + x, margin + y, 0.0),
            world_size_mm=(
                value.width if rotation == 0 else value.height,
                value.height if rotation == 0 else value.width,
                value.depth,
            ),
            local_size_mm=(value.width, value.height, value.depth),
            rotation_deg_z=rotation,
            supporting_ids=("box-floor",),
            support_coverage_ratio=1.0,
        )
        for value, rotation, x, y in packed
    ]
    return placements, trials


def _pack(
    ordering: tuple[_Rect, ...],
    usable_width: float,
    usable_height: float,
    gap: float,
    margin: float,
    zones: tuple[TopInsetZone, ...],
    score_mode: int,
) -> tuple[list[Free3DPlacement] | None, int]:
    free = [_Space(0.0, 0.0, usable_width, usable_height)]
    placements: list[Free3DPlacement] = []
    trials = 0
    for value in ordering:
        options: list[tuple[tuple[float, ...], int, _Space, float, float]] = []
        orientations = (
            (0, value.width, value.height),
            (90, value.height, value.width),
        )
        for rotation, body_width, body_height in orientations:
            used_width = body_width + gap
            used_height = body_height + gap
            for space in free:
                trials += 1
                if (
                    used_width > space.width + _EPSILON
                    or used_height > space.height + _EPSILON
                    or not _top_insets_allow(
                        margin + space.x,
                        margin + space.y,
                        body_width,
                        body_height,
                        value.depth,
                        zones,
                    )
                ):
                    continue
                short = min(space.width - used_width, space.height - used_height)
                long = max(space.width - used_width, space.height - used_height)
                area = space.width * space.height - used_width * used_height
                scores = (
                    (short, long, area, space.y, space.x, rotation),
                    (area, short, long, space.y, space.x, rotation),
                    (space.y, space.x, short, area, long, rotation),
                )
                options.append(
                    (scores[score_mode], rotation, space, used_width, used_height)
                )
        if not options:
            return None, trials
        _, rotation, selected_space, used_width, used_height = min(
            options,
            key=lambda option: option[0],
        )
        body_width = used_width - gap
        body_height = used_height - gap
        used = _Space(
            selected_space.x,
            selected_space.y,
            used_width,
            used_height,
        )
        world = (body_width, body_height, value.depth)
        local = (
            (value.width, value.height, value.depth)
            if rotation == 0
            else (value.width, value.height, value.depth)
        )
        placements.append(
            Free3DPlacement(
                participant_id=value.participant_id,
                role=value.role,
                name=value.name,
                origin_mm=(margin + used.x, margin + used.y, 0.0),
                world_size_mm=world,
                local_size_mm=local,
                rotation_deg_z=rotation,
                supporting_ids=("box-floor",),
                support_coverage_ratio=1.0,
            )
        )
        free = _prune(
            tuple(
                piece
                for source in free
                for piece in _split(source, used)
            )
        )
    return placements, trials


def _split(source: _Space, used: _Space) -> tuple[_Space, ...]:
    if not _intersects(source, used):
        return (source,)
    values: list[_Space] = []
    if used.x > source.x + _EPSILON:
        values.append(_Space(source.x, source.y, used.x - source.x, source.height))
    if used.x + used.width < source.x + source.width - _EPSILON:
        values.append(
            _Space(
                used.x + used.width,
                source.y,
                source.x + source.width - used.x - used.width,
                source.height,
            )
        )
    if used.y > source.y + _EPSILON:
        values.append(_Space(source.x, source.y, source.width, used.y - source.y))
    if used.y + used.height < source.y + source.height - _EPSILON:
        values.append(
            _Space(
                source.x,
                used.y + used.height,
                source.width,
                source.y + source.height - used.y - used.height,
            )
        )
    return tuple(values)


def _prune(values: tuple[_Space, ...]) -> list[_Space]:
    result: list[_Space] = []
    for index, value in enumerate(values):
        if any(
            index != other_index and _contained(value, other)
            for other_index, other in enumerate(values)
        ):
            continue
        if value not in result:
            result.append(value)
    return result


def _top_insets_allow(
    x: float,
    y: float,
    width: float,
    height: float,
    depth: float,
    zones: tuple[TopInsetZone, ...],
) -> bool:
    for zone in zones:
        overlap = (
            x < zone.origin_xy_mm[0] + zone.size_xy_mm[0] - _EPSILON
            and zone.origin_xy_mm[0] < x + width - _EPSILON
            and y < zone.origin_xy_mm[1] + zone.size_xy_mm[1] - _EPSILON
            and zone.origin_xy_mm[1] < y + height - _EPSILON
        )
        if overlap and depth > zone.support_plane_z_mm + _EPSILON:
            return False
    return True


def _intersects(left: _Space, right: _Space) -> bool:
    return (
        left.x < right.x + right.width - _EPSILON
        and right.x < left.x + left.width - _EPSILON
        and left.y < right.y + right.height - _EPSILON
        and right.y < left.y + left.height - _EPSILON
    )


def _contained(inner: _Space, outer: _Space) -> bool:
    return (
        inner.x >= outer.x - _EPSILON
        and inner.y >= outer.y - _EPSILON
        and inner.x + inner.width <= outer.x + outer.width + _EPSILON
        and inner.y + inner.height <= outer.y + outer.height + _EPSILON
    )


def _mapping(value: object) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        raise TypeError("Floor MaxRects dimensions must be mappings.")
    return value


def _result(
    status: str,
    placements: tuple[Free3DPlacement, ...],
    order_attempts: int,
    placement_trials: int,
    *,
    construction_mode: str,
) -> FloorMaxRectsResult:
    payload = {
        "version": FLOOR_MAXRECTS_VERSION,
        "status": status,
        "order_attempts": order_attempts,
        "placement_trials": placement_trials,
        "construction_mode": construction_mode,
        "placements": [value.__dict__ for value in placements],
    }
    digest = sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    ).hexdigest()
    return FloorMaxRectsResult(
        status=status,
        placements=placements,
        order_attempts=order_attempts,
        placement_trials=placement_trials,
        construction_mode=construction_mode,
        deterministic_digest=digest,
    )