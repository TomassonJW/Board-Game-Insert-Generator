"""Construct floor-first stacks under certified top reservations.

This lane is deliberately bounded. It builds legal vertical stacks from the
minimum container variants, packs only their bases on the box floor, and leaves
the common BGIG certificate to the portfolio orchestrator.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from hashlib import sha256

from board_game_insert_generator.floor_maxrects_solver import solve_floor_maxrects
from board_game_insert_generator.free_3d_beam_solver import VariantFree3DPlacement
from board_game_insert_generator.free_3d_greedy_solver import Free3DPlacement
from board_game_insert_generator.solver_outcome import (
    NO_SOLUTION_WITHIN_BUDGET,
    SOLUTION_FOUND,
)


RESERVED_FLOOR_STACK_VERSION = "reserved-floor-stacks-v2"
DEFAULT_MAX_STATES = 1_024
DEFAULT_MAX_PACK_ATTEMPTS = 1_024
DEFAULT_MAX_BACKTRACK_NODES = 50_000
DEFAULT_MAX_CANDIDATES = 8
_EPSILON = 0.0001

StopCheck = Callable[[], bool]


@dataclass(frozen=True)
class ReservedFloorStackExecution:
    """Bounded geometric candidates awaiting the common BGIG certificate."""

    status: str
    stop_reason: str
    candidates: tuple[tuple[Free3DPlacement, ...], ...]
    item_count: int
    completed_item_count: int
    retained_state_count: int
    search_expansion_count: int
    pack_attempt_count: int
    backtrack_node_count: int
    stopped: bool
    deterministic_digest: str

    def telemetry(self) -> dict[str, object]:
        return {
            "solver_version": RESERVED_FLOOR_STACK_VERSION,
            "item_count": self.item_count,
            "completed_item_count": self.completed_item_count,
            "retained_state_count": self.retained_state_count,
            "search_expansion_count": self.search_expansion_count,
            "pack_attempt_count": self.pack_attempt_count,
            "backtrack_node_count": self.backtrack_node_count,
            "candidate_count": len(self.candidates),
            "stopped": self.stopped,
            "minimum_envelopes_immutable": True,
            "flat_items_are_virtual_top_reservations": True,
            "floor_first_stack_bases": True,
            "complete_state_ranking_axes": [
                "elevated_container_count",
                "base_z_sum_mm",
                "elevated_volume_mm3",
                "maximum_stack_height_mm",
                "floor_footprint_mm2",
                "stack_count",
            ],
            "deterministic_digest": self.deterministic_digest,
        }


@dataclass(frozen=True)
class _Item:
    participant_id: str
    role: str
    name: str
    local_size: tuple[float, float, float]
    variant_id: str
    variant_digest: str
    variant_canonical: bool


@dataclass(frozen=True)
class _Layer:
    item: _Item
    x: float
    y: float
    z: float
    world_size: tuple[float, float, float]
    rotation: int
    support_id: str


@dataclass(frozen=True)
class _Stack:
    layers: tuple[_Layer, ...]
    base_size: tuple[float, float]
    top_origin: tuple[float, float]
    top_size: tuple[float, float]
    top_id: str
    height: float


@dataclass(frozen=True)
class _StateBuild:
    states: tuple[tuple[_Stack, ...], ...]
    completed_item_count: int
    expansion_count: int
    stopped: bool


@dataclass(frozen=True)
class _PackResult:
    placements: tuple[Free3DPlacement, ...]
    node_count: int
    stopped: bool


def _stopped(should_stop: StopCheck | None) -> bool:
    return should_stop is not None and should_stop()


def _orientations(item: _Item) -> tuple[tuple[int, float, float], ...]:
    x, y, _ = item.local_size
    values = [(0, x, y)]
    if abs(x - y) > _EPSILON:
        values.append((90, y, x))
    return tuple(values)


def _geometry_signature(stack: _Stack) -> tuple[object, ...]:
    return (
        round(stack.base_size[0], 4),
        round(stack.base_size[1], 4),
        tuple(
            (
                round(layer.x, 4),
                round(layer.y, 4),
                round(layer.z, 4),
                tuple(round(value, 4) for value in layer.world_size),
            )
            for layer in stack.layers
        ),
    )


def _state_signature(stacks: tuple[_Stack, ...]) -> tuple[object, ...]:
    return tuple(sorted(_geometry_signature(stack) for stack in stacks))


def _state_rank(stacks: tuple[_Stack, ...]) -> tuple[object, ...]:
    """Search-only rank preserving the historical diversified feasibility lane."""

    return (
        round(sum(stack.base_size[0] * stack.base_size[1] for stack in stacks), 4),
        len(stacks),
        round(max((stack.height for stack in stacks), default=0.0), 4),
        tuple(
            sorted(
                (round(stack.base_size[0], 4), round(stack.base_size[1], 4))
                for stack in stacks
            )
        ),
        _state_signature(stacks),
    )


def _complete_state_rank(stacks: tuple[_Stack, ...]) -> tuple[object, ...]:
    """Product rank applied only after every requested container is assigned."""

    layers = tuple(layer for stack in stacks for layer in stack.layers)
    elevated = tuple(layer for layer in layers if layer.z > _EPSILON)
    return (
        len(elevated),
        round(sum(layer.z for layer in layers), 4),
        round(
            sum(
                layer.world_size[0]
                * layer.world_size[1]
                * layer.world_size[2]
                for layer in elevated
            ),
            4,
        ),
        round(max((stack.height for stack in stacks), default=0.0), 4),
        round(sum(stack.base_size[0] * stack.base_size[1] for stack in stacks), 4),
        len(stacks),
        tuple(
            sorted(
                (round(stack.base_size[0], 4), round(stack.base_size[1], 4))
                for stack in stacks
            )
        ),
        _state_signature(stacks),
    )


def _new_stack(
    item: _Item,
    rotation: int,
    width: float,
    depth: float,
) -> _Stack:
    height = item.local_size[2]
    return _Stack(
        layers=(
            _Layer(
                item=item,
                x=0.0,
                y=0.0,
                z=0.0,
                world_size=(width, depth, height),
                rotation=rotation,
                support_id="box-floor",
            ),
        ),
        base_size=(width, depth),
        top_origin=(0.0, 0.0),
        top_size=(width, depth),
        top_id=item.participant_id,
        height=height,
    )


def _on_stack(
    stack: _Stack,
    item: _Item,
    rotation: int,
    width: float,
    depth: float,
    z_clearance: float,
    storage_height: float,
) -> _Stack | None:
    if width > stack.top_size[0] + _EPSILON or depth > stack.top_size[1] + _EPSILON:
        return None
    z = stack.height + z_clearance
    height = z + item.local_size[2]
    if height > storage_height + _EPSILON:
        return None
    x = stack.top_origin[0] + (stack.top_size[0] - width) / 2.0
    y = stack.top_origin[1] + (stack.top_size[1] - depth) / 2.0
    layer = _Layer(
        item=item,
        x=x,
        y=y,
        z=z,
        world_size=(width, depth, item.local_size[2]),
        rotation=rotation,
        support_id=stack.top_id,
    )
    return _Stack(
        layers=stack.layers + (layer,),
        base_size=stack.base_size,
        top_origin=(x, y),
        top_size=(width, depth),
        top_id=item.participant_id,
        height=height,
    )


def _stack_has_floor_position(
    stack: _Stack,
    box: tuple[float, float],
    margin: float,
    zones: Sequence[object],
) -> bool:
    for base_width, base_depth in (
        stack.base_size,
        (stack.base_size[1], stack.base_size[0]),
    ):
        x_values = {margin, box[0] - margin - base_width}
        y_values = {margin, box[1] - margin - base_depth}
        for zone in zones:
            zone_x, zone_y = zone.origin_xy_mm
            zone_width, zone_depth = zone.size_xy_mm
            x_values.update((zone_x - base_width, zone_x + zone_width))
            y_values.update((zone_y - base_depth, zone_y + zone_depth))
        for x in x_values:
            for y in y_values:
                if (
                    x < margin - _EPSILON
                    or y < margin - _EPSILON
                    or x + base_width > box[0] - margin + _EPSILON
                    or y + base_depth > box[1] - margin + _EPSILON
                ):
                    continue
                if all(
                    stack.height <= zone.support_plane_z_mm + _EPSILON
                    or x + base_width <= zone.origin_xy_mm[0] + _EPSILON
                    or zone.origin_xy_mm[0] + zone.size_xy_mm[0]
                    <= x + _EPSILON
                    or y + base_depth <= zone.origin_xy_mm[1] + _EPSILON
                    or zone.origin_xy_mm[1] + zone.size_xy_mm[1]
                    <= y + _EPSILON
                    for zone in zones
                ):
                    return True
    return False


def _build_states(
    item_choices: tuple[tuple[_Item, ...], ...],
    z_clearance: float,
    storage_height: float,
    box: tuple[float, float],
    margin: float,
    zones: Sequence[object],
    *,
    max_states: int,
    should_stop: StopCheck | None,
) -> _StateBuild:
    states: tuple[tuple[_Stack, ...], ...] = ((),)
    expansion_count = 0
    completed_item_count = 0
    for choices in item_choices:
        if _stopped(should_stop):
            return _StateBuild(
                states=states,
                completed_item_count=completed_item_count,
                expansion_count=expansion_count,
                stopped=True,
            )
        candidates: dict[tuple[object, ...], tuple[_Stack, ...]] = {}
        for stacks in states:
            if _stopped(should_stop):
                return _StateBuild(
                    states=states,
                    completed_item_count=completed_item_count,
                    expansion_count=expansion_count,
                    stopped=True,
                )
            for item in choices:
                for rotation, width, depth in _orientations(item):
                    expansion_count += 1
                    fresh = _new_stack(item, rotation, width, depth)
                    if _stack_has_floor_position(fresh, box, margin, zones):
                        added = tuple(
                            sorted(stacks + (fresh,), key=_geometry_signature)
                        )
                        candidates.setdefault(_state_signature(added), added)
                    seen_targets: set[tuple[object, ...]] = set()
                    for index, stack in enumerate(stacks):
                        stack_geometry = _geometry_signature(stack)
                        if stack_geometry in seen_targets:
                            continue
                        seen_targets.add(stack_geometry)
                        expansion_count += 1
                        changed = _on_stack(
                            stack,
                            item,
                            rotation,
                            width,
                            depth,
                            z_clearance,
                            storage_height,
                        )
                        if changed is None or not _stack_has_floor_position(
                            changed,
                            box,
                            margin,
                            zones,
                        ):
                            continue
                        placed = list(stacks)
                        placed[index] = changed
                        changed_state = tuple(
                            sorted(placed, key=_geometry_signature)
                        )
                        candidates.setdefault(
                            _state_signature(changed_state),
                            changed_state,
                        )
        if not candidates:
            return _StateBuild(
                states=(),
                completed_item_count=completed_item_count,
                expansion_count=expansion_count,
                stopped=False,
            )
        states = tuple(
            sorted(candidates.values(), key=_state_rank)[:max_states]
        )
        completed_item_count += 1
    return _StateBuild(
        states=states,
        completed_item_count=completed_item_count,
        expansion_count=expansion_count,
        stopped=False,
    )


def _pseudo_participants(
    stacks: tuple[_Stack, ...],
) -> tuple[list[dict[str, object]], dict[str, _Stack]]:
    values: list[dict[str, object]] = []
    by_id: dict[str, _Stack] = {}
    for index, stack in enumerate(stacks):
        digest = sha256(
            repr(_geometry_signature(stack)).encode("ascii")
        ).hexdigest()[:12]
        stack_id = f"stack:{index:03d}:{digest}"
        by_id[stack_id] = stack
        values.append(
            {
                "id": stack_id,
                "role": "container",
                "name": stack_id,
                "minimum_local_mm": {
                    "x": stack.base_size[0],
                    "y": stack.base_size[1],
                    "z": stack.height,
                },
                "dimension_modes": {"x": "fixed", "y": "fixed", "z": "fixed"},
                "target_local_mm": {
                    "x": stack.base_size[0],
                    "y": stack.base_size[1],
                    "z": stack.height,
                },
            }
        )
    return values, by_id


def _expand(
    packed: tuple[Free3DPlacement, ...],
    stacks: Mapping[str, _Stack],
) -> tuple[Free3DPlacement, ...]:
    result: list[Free3DPlacement] = []
    for base in packed:
        stack = stacks[base.participant_id]
        for layer in stack.layers:
            if base.rotation_deg_z == 0:
                x = base.origin_mm[0] + layer.x
                y = base.origin_mm[1] + layer.y
                world = layer.world_size
                rotation = layer.rotation
            else:
                x = (
                    base.origin_mm[0]
                    + stack.base_size[1]
                    - layer.y
                    - layer.world_size[1]
                )
                y = base.origin_mm[1] + layer.x
                world = (
                    layer.world_size[1],
                    layer.world_size[0],
                    layer.world_size[2],
                )
                rotation = (layer.rotation + 90) % 180
            result.append(
                VariantFree3DPlacement(
                    participant_id=layer.item.participant_id,
                    role=layer.item.role,
                    name=layer.item.name,
                    origin_mm=(
                        round(x, 6),
                        round(y, 6),
                        round(layer.z, 6),
                    ),
                    world_size_mm=tuple(round(value, 6) for value in world),
                    local_size_mm=layer.item.local_size,
                    rotation_deg_z=rotation,
                    supporting_ids=(layer.support_id,),
                    support_coverage_ratio=1.0,
                    container_variant_id=layer.item.variant_id,
                    container_variant_digest=layer.item.variant_digest,
                    container_variant_canonical=layer.item.variant_canonical,
                )
            )
    return tuple(sorted(result, key=lambda value: value.participant_id))


def _pack_floor_backtracking(
    pseudo: Sequence[Mapping[str, object]],
    box: Mapping[str, object],
    margin: float,
    gap: float,
    zones: Sequence[object],
    *,
    max_nodes: int,
    should_stop: StopCheck | None,
) -> _PackResult:
    rectangles: list[tuple[str, float, float, float]] = []
    for value in pseudo:
        size = value["minimum_local_mm"]
        if not isinstance(size, Mapping):
            return _PackResult((), 0, False)
        rectangles.append(
            (
                str(value["id"]),
                float(size["x"]),
                float(size["y"]),
                float(size["z"]),
            )
        )
    rectangles.sort(
        key=lambda value: (
            -sum(
                value[3] > zone.support_plane_z_mm + _EPSILON
                for zone in zones
            ),
            -value[1] * value[2],
            -max(value[1], value[2]),
            value[0],
        )
    )
    placed: list[tuple[str, float, float, float, float, float, int]] = []
    nodes = 0
    stopped = False
    box_x = float(box["x"])
    box_y = float(box["y"])

    def allowed(
        x: float,
        y: float,
        width: float,
        depth: float,
        height: float,
    ) -> bool:
        if (
            x < margin - _EPSILON
            or y < margin - _EPSILON
            or x + width > box_x - margin + _EPSILON
            or y + depth > box_y - margin + _EPSILON
        ):
            return False
        for _, px, py, pw, pd, _, _ in placed:
            if not (
                x + width + gap <= px + _EPSILON
                or px + pw + gap <= x + _EPSILON
                or y + depth + gap <= py + _EPSILON
                or py + pd + gap <= y + _EPSILON
            ):
                return False
        return all(
            height <= zone.support_plane_z_mm + _EPSILON
            or x + width <= zone.origin_xy_mm[0] + _EPSILON
            or zone.origin_xy_mm[0] + zone.size_xy_mm[0] <= x + _EPSILON
            or y + depth <= zone.origin_xy_mm[1] + _EPSILON
            or zone.origin_xy_mm[1] + zone.size_xy_mm[1] <= y + _EPSILON
            for zone in zones
        )

    def visit(index: int) -> bool:
        nonlocal nodes, stopped
        if index >= len(rectangles):
            return True
        if nodes >= max_nodes or _stopped(should_stop):
            stopped = _stopped(should_stop)
            return False
        participant_id, local_x, local_y, height = rectangles[index]
        orientations_xy = [(0, local_x, local_y)]
        if abs(local_x - local_y) > _EPSILON:
            orientations_xy.append((90, local_y, local_x))
        for rotation, width, depth in orientations_xy:
            x_values = {margin}
            y_values = {margin}
            for _, px, py, pw, pd, _, _ in placed:
                x_values.add(px + pw + gap)
                y_values.add(py + pd + gap)
            for zone in zones:
                x_values.update(
                    (
                        zone.origin_xy_mm[0] - width,
                        zone.origin_xy_mm[0] + zone.size_xy_mm[0],
                    )
                )
                y_values.update(
                    (
                        zone.origin_xy_mm[1] - depth,
                        zone.origin_xy_mm[1] + zone.size_xy_mm[1],
                    )
                )
            for y in sorted(y_values):
                for x in sorted(x_values):
                    nodes += 1
                    if nodes >= max_nodes or _stopped(should_stop):
                        stopped = _stopped(should_stop)
                        return False
                    if not allowed(x, y, width, depth, height):
                        continue
                    placed.append(
                        (
                            participant_id,
                            x,
                            y,
                            width,
                            depth,
                            height,
                            rotation,
                        )
                    )
                    if visit(index + 1):
                        return True
                    placed.pop()
        return False

    if not visit(0):
        return _PackResult((), nodes, stopped)
    return _PackResult(
        tuple(
            Free3DPlacement(
                participant_id=participant_id,
                role="container",
                name=participant_id,
                origin_mm=(round(x, 6), round(y, 6), 0.0),
                world_size_mm=(
                    round(width, 6),
                    round(depth, 6),
                    round(height, 6),
                ),
                local_size_mm=(
                    (
                        round(width, 6),
                        round(depth, 6),
                        round(height, 6),
                    )
                    if rotation == 0
                    else (
                        round(depth, 6),
                        round(width, 6),
                        round(height, 6),
                    )
                ),
                rotation_deg_z=rotation,
                supporting_ids=("box-floor",),
                support_coverage_ratio=1.0,
            )
            for (
                participant_id,
                x,
                y,
                width,
                depth,
                height,
                rotation,
            ) in placed
        ),
        nodes,
        stopped,
    )


def _item_choices(
    participants: Sequence[Mapping[str, object]],
) -> tuple[tuple[_Item, ...], ...]:
    choices_by_participant: list[tuple[_Item, ...]] = []
    for participant in participants:
        raw_options = participant.get("container_internal_variant_options_v1")
        if not isinstance(raw_options, Sequence) or isinstance(
            raw_options,
            (str, bytes),
        ):
            return ()
        options: list[_Item] = []
        for raw_option in raw_options:
            if not isinstance(raw_option, Mapping):
                return ()
            size = raw_option.get("minimum_outer_envelope_mm")
            if not isinstance(size, Mapping):
                return ()
            options.append(
                _Item(
                    participant_id=str(participant["id"]),
                    role=str(participant["role"]),
                    name=str(participant["name"]),
                    local_size=tuple(
                        float(size[axis]) for axis in ("x", "y", "z")
                    ),
                    variant_id=str(raw_option["variant_id"]),
                    variant_digest=str(raw_option["geometry_digest"]),
                    variant_canonical=bool(raw_option["canonical"]),
                )
            )
        if not options:
            return ()
        choices_by_participant.append(tuple(options))
    return tuple(
        sorted(
            choices_by_participant,
            key=lambda choices: (
                -max(
                    value.local_size[0] * value.local_size[1]
                    for value in choices
                ),
                -max(max(value.local_size[:2]) for value in choices),
                -max(value.local_size[2] for value in choices),
                choices[0].participant_id,
            ),
        )
    )


def _execution_digest(
    candidates: Sequence[Sequence[Free3DPlacement]],
) -> str:
    payload = tuple(
        tuple(
            (
                placement.participant_id,
                placement.origin_mm,
                placement.world_size_mm,
                placement.rotation_deg_z,
                getattr(placement, "container_variant_id", ""),
            )
            for placement in candidate
        )
        for candidate in candidates
    )
    return sha256(repr(payload).encode("utf-8")).hexdigest()


def solve_reserved_floor_stacks(
    participants: Sequence[Mapping[str, object]],
    problem: object,
    *,
    should_stop: StopCheck | None = None,
    max_states: int = DEFAULT_MAX_STATES,
    max_pack_attempts: int = DEFAULT_MAX_PACK_ATTEMPTS,
    max_backtrack_nodes: int = DEFAULT_MAX_BACKTRACK_NODES,
    max_candidates: int = DEFAULT_MAX_CANDIDATES,
) -> ReservedFloorStackExecution:
    """Return deterministic floor-stack candidates under the caller deadline."""

    choices = _item_choices(participants)
    if not choices:
        return ReservedFloorStackExecution(
            status=NO_SOLUTION_WITHIN_BUDGET,
            stop_reason="reserved_floor_stack_participants_unavailable",
            candidates=(),
            item_count=len(participants),
            completed_item_count=0,
            retained_state_count=0,
            search_expansion_count=0,
            pack_attempt_count=0,
            backtrack_node_count=0,
            stopped=False,
            deterministic_digest=_execution_digest(()),
        )
    build = _build_states(
        choices,
        float(problem.z_clearance_mm),
        float(problem.storage_height_mm),
        (float(problem.box["x"]), float(problem.box["y"])),
        float(problem.box_xy_clearance_mm),
        tuple(problem.top_inset_zones),
        max_states=max(1, int(max_states)),
        should_stop=should_stop,
    )
    candidates: list[tuple[Free3DPlacement, ...]] = []
    seen: set[str] = set()
    attempts = 0
    backtrack_nodes = 0
    stopped = build.stopped
    complete_states = sorted(build.states, key=_complete_state_rank)
    for stacks in complete_states[: max(1, int(max_pack_attempts))]:
        if _stopped(should_stop):
            stopped = True
            break
        attempts += 1
        pseudo, by_id = _pseudo_participants(stacks)
        packed = solve_floor_maxrects(
            pseudo,
            problem.box,
            problem.storage_height_mm,
            problem.xy_clearance_mm,
            box_perimeter_xy_mm=problem.box_xy_clearance_mm,
            top_inset_zones=problem.top_inset_zones,
        )
        packed_placements = packed.placements
        if not packed_placements:
            fallback = _pack_floor_backtracking(
                pseudo,
                problem.box,
                problem.box_xy_clearance_mm,
                problem.xy_clearance_mm,
                problem.top_inset_zones,
                max_nodes=max_backtrack_nodes,
                should_stop=should_stop,
            )
            backtrack_nodes += fallback.node_count
            stopped = stopped or fallback.stopped
            packed_placements = fallback.placements
        if not packed_placements:
            if stopped:
                break
            continue
        expanded = _expand(tuple(packed_placements), by_id)
        digest = _execution_digest((expanded,))
        if digest in seen:
            continue
        seen.add(digest)
        candidates.append(expanded)
        if len(candidates) >= max(1, int(max_candidates)):
            break
    status = SOLUTION_FOUND if candidates else NO_SOLUTION_WITHIN_BUDGET
    stop_reason = (
        "reserved_top_floor_stacks_found"
        if candidates
        else (
            "reserved_floor_stack_deadline_or_cancel_reached"
            if stopped
            else "reserved_floor_stack_not_found"
        )
    )
    return ReservedFloorStackExecution(
        status=status,
        stop_reason=stop_reason,
        candidates=tuple(candidates),
        item_count=len(choices),
        completed_item_count=build.completed_item_count,
        retained_state_count=len(build.states),
        search_expansion_count=build.expansion_count,
        pack_attempt_count=attempts,
        backtrack_node_count=backtrack_nodes,
        stopped=stopped,
        deterministic_digest=_execution_digest(candidates),
    )
