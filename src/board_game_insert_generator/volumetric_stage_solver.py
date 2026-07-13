"""P64 bounded deterministic volumetric stage solver.

The module searches portfolios of complete XY arrangements, then composes them
bottom-to-top in Z.  It is deliberately heuristic: budgets are public, search
is deterministic and no external optimiser is required.  Residual regions are
reported and may produce suggestions, but never printable bodies.
"""

from __future__ import annotations

from copy import deepcopy
from itertools import product
from math import ceil, isclose
from typing import Any


VOLUMETRIC_STAGE_SOLVER_SCHEMA_V1 = "bgig.volumetric_stage_solver.v1"
SOLUTION_COMPLETE = "complete"
SOLUTION_WITH_RESIDUALS = "proposal_with_residuals"
SOLUTION_IMPOSSIBLE = "impossible"

MAX_ORDERINGS = 4
MAX_GROUP_SIZES_PER_ORDER = 20
MAX_CANDIDATES = 192
MAX_RETURNED_CANDIDATES = 64
MAX_ORIENTATION_COMBINATIONS = 1024
MIN_SUPPORT_RATIO = 0.25

_AXES = ("x", "y", "z")
_EPSILON = 0.0001

_SCORE_WEIGHTS = {
    "balanced": {"simplicity": 0.25, "targets": 0.30, "material": 0.25, "support": 0.20},
    "compact": {"simplicity": 0.40, "targets": 0.25, "material": 0.20, "support": 0.15},
    "accessible": {"simplicity": 0.25, "targets": 0.15, "material": 0.15, "support": 0.45},
    "print_simple": {"simplicity": 0.50, "targets": 0.15, "material": 0.20, "support": 0.15},
    "material_reduced": {"simplicity": 0.15, "targets": 0.20, "material": 0.50, "support": 0.15},
}


class VolumetricStageSolverError(ValueError):
    """Raised when the internal P64 participant contract is malformed."""


def solve_stage_portfolio(
    participants: list[dict[str, object]],
    box: dict[str, object],
    storage_height_mm: float,
    clearance_mm: float,
    *,
    preference: str = "balanced",
) -> dict[str, object]:
    """Return a bounded portfolio of complete or residual stage candidates."""

    values = [_participant(item, index) for index, item in enumerate(participants)]
    bounds = _dimension(box, "box")
    height = float(storage_height_mm)
    clearance = float(clearance_mm)
    if height <= 0.0 or clearance < 0.0:
        raise VolumetricStageSolverError("Storage height must be positive and clearance non-negative.")
    if preference not in _SCORE_WEIGHTS:
        raise VolumetricStageSolverError(f"Unknown P64 solver preference: {preference!r}.")

    budgets = {
        "max_orderings": MAX_ORDERINGS,
        "max_group_sizes_per_order": MAX_GROUP_SIZES_PER_ORDER,
        "max_candidates": MAX_CANDIDATES,
        "max_returned_candidates": MAX_RETURNED_CANDIDATES,
        "max_orientation_combinations": MAX_ORIENTATION_COMBINATIONS,
    }
    if not values:
        return _empty_result(budgets, "No requested body can participate in the stage search.")

    candidates: list[dict[str, object]] = []
    signatures: set[str] = set()
    groupings_evaluated = 0
    xy_arrangements_evaluated = 0
    truncated = False
    for order_name, ordered in _orders(values):
        for group_size in _group_sizes(len(ordered)):
            groups = [ordered[index : index + group_size] for index in range(0, len(ordered), group_size)]
            for orientation_strategy in ("width", "height", "balanced"):
                if len(candidates) >= MAX_CANDIDATES:
                    truncated = True
                    break
                groupings_evaluated += 1
                candidate, attempts = _candidate_for_groups(
                    groups,
                    bounds,
                    height,
                    clearance,
                    preference=preference,
                    order_name=order_name,
                    group_size=group_size,
                    orientation_strategy=orientation_strategy,
                )
                xy_arrangements_evaluated += attempts
                if candidate is None:
                    continue
                signature = _candidate_signature(candidate)
                if signature in signatures:
                    continue
                signatures.add(signature)
                candidates.append(candidate)
            if truncated:
                break
        if truncated:
            break

    ordered_candidates = sorted(
        candidates,
        key=lambda item: (
            item["solution_status"] != SOLUTION_COMPLETE,
            -float(item["quality_score"]),
            int(item["stage_count"]),
            str(item["candidate_id"]),
        ),
    )
    returned = ordered_candidates[:MAX_RETURNED_CANDIDATES]
    complete_count = sum(item["solution_status"] == SOLUTION_COMPLETE for item in candidates)
    partial_count = sum(item["solution_status"] == SOLUTION_WITH_RESIDUALS for item in candidates)
    if complete_count:
        status = SOLUTION_COMPLETE
    elif partial_count:
        status = SOLUTION_WITH_RESIDUALS
    else:
        status = SOLUTION_IMPOSSIBLE
    return {
        "schema_version": VOLUMETRIC_STAGE_SOLVER_SCHEMA_V1,
        "status": status,
        "candidates": returned,
        "best_candidate": deepcopy(returned[0]) if returned else None,
        "budgets": budgets,
        "search": {
            "deterministic": True,
            "globally_optimal": False,
            "truncated": truncated or len(ordered_candidates) > len(returned),
            "ordering_count": len(_orders(values)),
            "groupings_evaluated": groupings_evaluated,
            "xy_arrangements_evaluated": xy_arrangements_evaluated,
            "candidate_count": len(candidates),
            "complete_candidate_count": complete_count,
            "partial_candidate_count": partial_count,
        },
        "blockers": [] if candidates else [
            {
                "code": "NO_STAGE_COMPOSITION_FITS",
                "message": "Aucun arrangement par etages ne contient tous les corps demandes.",
                "action": "Reduis une dimension fixe/cible, un contenu ou le nombre de corps demandes.",
            }
        ],
        "invariants": {
            "requested_bodies_only": True,
            "automatic_body_count": 0,
            "suggestions_do_not_mutate": True,
            "bounded_search": True,
        },
    }


def _candidate_for_groups(
    groups: list[list[dict[str, object]]],
    box: dict[str, float],
    storage_height: float,
    clearance: float,
    *,
    preference: str,
    order_name: str,
    group_size: int,
    orientation_strategy: str,
) -> tuple[dict[str, object] | None, int]:
    height_plan = _stage_heights(groups, storage_height)
    if height_plan is None:
        return None, 0
    stage_heights, vertical_complete = height_plan
    stage_layouts: list[dict[str, object]] = []
    attempts = 0
    xy_complete = True
    for group in groups:
        full, full_attempts = _best_xy_layout(
            group, box, clearance, orientation_strategy=orientation_strategy, fill=True
        )
        attempts += full_attempts
        if full is not None:
            stage_layouts.append(full)
            continue
        partial, partial_attempts = _best_xy_layout(
            group, box, clearance, orientation_strategy=orientation_strategy, fill=False
        )
        attempts += partial_attempts
        if partial is None:
            return None, attempts
        xy_complete = False
        stage_layouts.append(partial)

    placements: list[dict[str, object]] = []
    stages: list[dict[str, object]] = []
    residual_zones: list[dict[str, object]] = []
    cursor_z = 0.0
    all_reach_stage_top = True
    for stage_index, (group, layout, stage_height) in enumerate(zip(groups, stage_layouts, stage_heights)):
        stage_id = f"stage-{stage_index + 1}"
        stage_bottom = cursor_z
        stage_top = cursor_z + stage_height
        stage_placements: list[dict[str, object]] = []
        for item_layout in _mappings(layout["placements"]):
            item = _mapping(item_layout["participant"])
            mode_z = str(_mapping(item["dimension_modes"])["z"])
            base_z = _axis_base(item, "z")
            body_height = base_z if mode_z == "fixed" else stage_height
            reaches_top = isclose(body_height, stage_height, abs_tol=0.001)
            all_reach_stage_top = all_reach_stage_top and reaches_top
            world_size = {
                "x": _round(float(item_layout["world_size_mm"]["x"])),
                "y": _round(float(item_layout["world_size_mm"]["y"])),
                "z": _round(body_height),
            }
            rotated = bool(item_layout["rotated_xy"])
            local_final = {
                "x": world_size["y"] if rotated else world_size["x"],
                "y": world_size["x"] if rotated else world_size["y"],
                "z": world_size["z"],
            }
            placement = {
                "id": item["id"],
                "role": item["role"],
                "name": item["name"],
                "origin_mm": {
                    "x": _round(float(item_layout["origin_mm"]["x"])),
                    "y": _round(float(item_layout["origin_mm"]["y"])),
                    "z": _round(stage_bottom),
                },
                "world_size_mm": world_size,
                "rotation_deg_z": 90 if rotated else 0,
                "final_outer_dimensions_mm": _rounded(local_final),
                "stage_id": stage_id,
                "stage_index": stage_index,
                "stage_bottom_z_mm": _round(stage_bottom),
                "stage_top_z_mm": _round(stage_top),
                "reaches_stage_top": reaches_top,
                "dimension_contract": _dimension_contract(item, local_final),
                "printable": True,
                "automatic": False,
            }
            for key in ("container_group_id", "requested_complement_id", "complement_kind"):
                if key in item:
                    placement[key] = item[key]
            placements.append(placement)
            stage_placements.append(placement)
            if body_height < stage_height - _EPSILON:
                residual_zones.append(
                    _residual_zone(
                        f"residual:{stage_id}:{item['id']}:above",
                        stage_id,
                        {
                            "x": placement["origin_mm"]["x"],
                            "y": placement["origin_mm"]["y"],
                            "z": _round(stage_bottom + body_height),
                        },
                        {
                            "x": world_size["x"],
                            "y": world_size["y"],
                            "z": _round(stage_height - body_height),
                        },
                        "above_fixed_body",
                    )
                )
        for zone in _mappings(layout["residual_rectangles"]):
            residual_zones.append(
                _residual_zone(
                    f"residual:{stage_id}:xy:{zone['id']}",
                    stage_id,
                    {"x": zone["x"], "y": zone["y"], "z": _round(stage_bottom)},
                    {"x": zone["width"], "y": zone["height"], "z": _round(stage_height)},
                    str(zone["kind"]),
                )
            )
        stages.append(
            {
                "id": stage_id,
                "index": stage_index,
                "origin_z_mm": _round(stage_bottom),
                "height_mm": _round(stage_height),
                "top_z_mm": _round(stage_top),
                "body_ids": [str(item["id"]) for item in stage_placements],
                "body_count": len(stage_placements),
                "row_count": int(layout["row_count"]),
                "xy_status": "complete" if layout["complete"] else "with_residuals",
            }
        )
        cursor_z = stage_top

    if cursor_z < storage_height - _EPSILON:
        inner_x = max(0.0, box["x"] - 2.0 * clearance)
        inner_y = max(0.0, box["y"] - 2.0 * clearance)
        residual_zones.append(
            _residual_zone(
                "residual:top",
                "above-stages",
                {"x": _round(clearance), "y": _round(clearance), "z": _round(cursor_z)},
                {"x": _round(inner_x), "y": _round(inner_y), "z": _round(storage_height - cursor_z)},
                "unused_height",
            )
        )

    support = _support_contract(placements, stages)
    if support["status"] == "unsupported":
        return None, attempts
    complete = xy_complete and vertical_complete and all_reach_stage_top
    solution_status = SOLUTION_COMPLETE if complete else SOLUTION_WITH_RESIDUALS
    volume = _volume_contract(placements, box, storage_height, clearance, complete)
    if complete:
        residual_zones = []
    suggestions = _suggestions(residual_zones)
    removal = _removal_sequence(placements)
    scores = _score_candidate(
        placements,
        stages,
        support,
        volume,
        preference,
        complete=complete,
    )
    candidate_id = f"{order_name}:g{group_size}:{orientation_strategy}:{len(stages)}s"
    return (
        {
            "candidate_id": candidate_id,
            "solution_status": solution_status,
            "quality_score": scores["total"],
            "score_breakdown": scores,
            "stage_count": len(stages),
            "stages": stages,
            "placements": placements,
            "support": support,
            "removal_sequence": removal,
            "residuals": {
                "status": "none" if complete else "present",
                "zones": residual_zones,
                "residual_volume_mm3": volume["residual_volume_mm3"],
                "residual_ratio": volume["residual_ratio"],
            },
            "suggestions": suggestions,
            "volume_conservation": volume,
            "metrics": {
                "row_count": sum(int(item["row_count"]) for item in stages),
                "rotation_count": sum(int(item["rotation_deg_z"] != 0) for item in placements),
                "target_deviation_count": sum(
                    int(value["status"] == "deviated")
                    for item in placements
                    for value in _mapping(item["dimension_contract"])["axes"].values()
                ),
            },
            "search_origin": {
                "order": order_name,
                "group_size": group_size,
                "orientation_strategy": orientation_strategy,
            },
            "invariants": {
                "no_collisions_by_construction": True,
                "requested_bodies_only": True,
                "automatic_body_count": 0,
                "suggestions_do_not_mutate": True,
            },
        },
        attempts,
    )


def _stage_heights(
    groups: list[list[dict[str, object]]], storage_height: float
) -> tuple[list[float], bool] | None:
    heights: list[float] = []
    complete = True
    for group in groups:
        bases = [_axis_base(item, "z") for item in group]
        stage_height = max(bases)
        fixed = [base for item, base in zip(group, bases) if _axis_mode(item, "z") == "fixed"]
        if any(not isclose(value, stage_height, abs_tol=0.001) for value in fixed):
            complete = False
        heights.append(stage_height)
    minimum_total = sum(heights)
    if minimum_total > storage_height + _EPSILON:
        return None
    extra = max(0.0, storage_height - minimum_total)
    expandable = [
        index
        for index, group in enumerate(groups)
        if all(_axis_mode(item, "z") != "fixed" for item in group)
    ]
    if extra > _EPSILON and not expandable:
        complete = False
        return heights, complete
    targets = [
        max((_axis_target(item, "z") or heights[index]) for item in group)
        for index, group in enumerate(groups)
    ]
    weights = [sum(_volume(_mapping(item["minimum_local_mm"])) for item in group) for group in groups]
    _allocate(heights, expandable, extra, targets, weights)
    return heights, complete


def _best_xy_layout(
    group: list[dict[str, object]],
    box: dict[str, float],
    clearance: float,
    *,
    orientation_strategy: str,
    fill: bool,
) -> tuple[dict[str, object] | None, int]:
    feasible: list[dict[str, object]] = []
    attempts = 0
    for columns in range(1, len(group) + 1):
        rows = [group[index : index + columns] for index in range(0, len(group), columns)]
        attempts += 1
        layout = _layout_rows(
            rows,
            box,
            clearance,
            orientation_strategy=orientation_strategy,
            fill=fill,
        )
        if layout is not None:
            feasible.append(layout)
    if not feasible:
        return None, attempts
    return min(
        feasible,
        key=lambda item: (
            -float(item["local_score"]),
            int(item["row_count"]),
            int(item["rotation_count"]),
            str(item["layout_id"]),
        ),
    ), attempts


def _layout_rows(
    row_items: list[list[dict[str, object]]],
    box: dict[str, float],
    clearance: float,
    *,
    orientation_strategy: str,
    fill: bool,
) -> dict[str, object] | None:
    inner_x = box["x"] - 2.0 * clearance
    inner_y = box["y"] - 2.0 * clearance
    if inner_x <= 0.0 or inner_y <= 0.0:
        return None
    rows: list[list[dict[str, object]]] = []
    for values in row_items:
        oriented = _orient_row(values, inner_x, inner_y, clearance, orientation_strategy)
        if oriented is None:
            return None
        rows.append(oriented)

    row_heights = [max(float(item["base_world_mm"]["y"]) for item in row) for row in rows]
    if any(
        _axis_mode(_mapping(item["participant"]), "y", rotated=bool(item["rotated_xy"])) == "fixed"
        and float(item["base_world_mm"]["y"]) < row_height - _EPSILON
        for row, row_height in zip(rows, row_heights)
        for item in row
    ) and fill:
        return None
    minimum_y = sum(row_heights) + clearance * max(0, len(rows) - 1)
    if minimum_y > inner_y + _EPSILON:
        return None
    if fill:
        extra_y = inner_y - minimum_y
        expandable_rows = [
            index
            for index, row in enumerate(rows)
            if all(
                _axis_mode(_mapping(item["participant"]), "y", rotated=bool(item["rotated_xy"])) != "fixed"
                for item in row
            )
        ]
        if extra_y > _EPSILON and not expandable_rows:
            return None
        row_targets = [
            max(
                _axis_target(_mapping(item["participant"]), "y", rotated=bool(item["rotated_xy"]))
                or row_heights[index]
                for item in row
            )
            for index, row in enumerate(rows)
        ]
        row_weights = [
            sum(_area(_mapping(item["participant"])["minimum_local_mm"]) for item in row)
            for row in rows
        ]
        _allocate(row_heights, expandable_rows, extra_y, row_targets, row_weights)

    placements: list[dict[str, object]] = []
    residuals: list[dict[str, object]] = []
    cursor_y = clearance
    rotations = 0
    for row_index, (row, row_height) in enumerate(zip(rows, row_heights)):
        widths = [float(item["base_world_mm"]["x"]) for item in row]
        occupied_with_gaps = sum(widths) + clearance * max(0, len(row) - 1)
        if occupied_with_gaps > inner_x + _EPSILON:
            return None
        if fill:
            extra_x = inner_x - occupied_with_gaps
            expandable = [
                index
                for index, item in enumerate(row)
                if _axis_mode(_mapping(item["participant"]), "x", rotated=bool(item["rotated_xy"])) != "fixed"
            ]
            if extra_x > _EPSILON and not expandable:
                return None
            targets = [
                _axis_target(_mapping(item["participant"]), "x", rotated=bool(item["rotated_xy"]))
                or widths[index]
                for index, item in enumerate(row)
            ]
            weights = [_area(_mapping(item["participant"])["minimum_local_mm"]) for item in row]
            _allocate(widths, expandable, extra_x, targets, weights)
        cursor_x = clearance
        for item_index, (item, width) in enumerate(zip(row, widths)):
            body_height = row_height if fill else float(item["base_world_mm"]["y"])
            placements.append(
                {
                    "participant": item["participant"],
                    "origin_mm": {"x": _round(cursor_x), "y": _round(cursor_y)},
                    "world_size_mm": {"x": _round(width), "y": _round(body_height)},
                    "rotated_xy": bool(item["rotated_xy"]),
                }
            )
            if not fill and body_height < row_height - _EPSILON:
                residuals.append(
                    {
                        "id": f"r{row_index}-i{item_index}-above",
                        "x": _round(cursor_x),
                        "y": _round(cursor_y + body_height),
                        "width": _round(width),
                        "height": _round(row_height - body_height),
                        "kind": "row_height_residual",
                    }
                )
            cursor_x += width + clearance
            rotations += int(bool(item["rotated_xy"]))
        used_x = cursor_x - clearance
        if not fill and used_x < box["x"] - clearance - _EPSILON:
            residuals.append(
                {
                    "id": f"r{row_index}-right",
                    "x": _round(used_x),
                    "y": _round(cursor_y),
                    "width": _round(box["x"] - clearance - used_x),
                    "height": _round(row_height),
                    "kind": "row_right_residual",
                }
            )
        cursor_y += row_height + clearance
    used_y = cursor_y - clearance
    if not fill and used_y < box["y"] - clearance - _EPSILON:
        residuals.append(
            {
                "id": "back",
                "x": _round(clearance),
                "y": _round(used_y),
                "width": _round(inner_x),
                "height": _round(box["y"] - clearance - used_y),
                "kind": "stage_back_residual",
            }
        )
    target_error = sum(
        _xy_target_error(
            _mapping(item["participant"]),
            _mapping(item["world_size_mm"]),
            rotated=bool(item["rotated_xy"]),
        )
        for item in placements
    )
    local_score = 1000.0 - len(rows) * 20.0 - rotations * 4.0 - target_error * 25.0
    return {
        "layout_id": f"{len(row_items[0]) if row_items else 0}c:{orientation_strategy}:{'full' if fill else 'partial'}",
        "complete": fill,
        "row_count": len(rows),
        "rotation_count": rotations,
        "placements": placements,
        "residual_rectangles": residuals,
        "local_score": _round(local_score),
    }


def _orient_row(
    values: list[dict[str, object]],
    inner_x: float,
    inner_y: float,
    clearance: float,
    strategy: str,
) -> list[dict[str, object]] | None:
    option_sets = [_orientation_options(value) for value in values]
    combination_count = 1
    for options in option_sets:
        combination_count *= len(options)
    if combination_count <= MAX_ORIENTATION_COMBINATIONS:
        combinations = product(*option_sets)
    else:
        combinations = [tuple(_greedy_orientation(value, strategy) for value in values)]
    feasible: list[tuple[tuple[float, float, int], list[dict[str, object]]]] = []
    for combination in combinations:
        width = sum(float(item["base_world_mm"]["x"]) for item in combination) + clearance * max(0, len(values) - 1)
        height = max(float(item["base_world_mm"]["y"]) for item in combination)
        if width > inner_x + _EPSILON or height > inner_y + _EPSILON:
            continue
        rotations = sum(int(bool(item["rotated_xy"])) for item in combination)
        if strategy == "width":
            key = (width, height, rotations)
        elif strategy == "height":
            key = (height, width, rotations)
        else:
            key = (width / inner_x + height / inner_y, rotations, width)
        feasible.append((key, [dict(item) for item in combination]))
    return min(feasible, key=lambda item: item[0])[1] if feasible else None


def _orientation_options(value: dict[str, object]) -> list[dict[str, object]]:
    base = {axis: _axis_base(value, axis) for axis in _AXES}
    options = [_oriented(value, base, False)]
    if not isclose(base["x"], base["y"], abs_tol=_EPSILON):
        options.append(_oriented(value, {"x": base["y"], "y": base["x"], "z": base["z"]}, True))
    return options


def _greedy_orientation(value: dict[str, object], strategy: str) -> dict[str, object]:
    options = _orientation_options(value)
    if strategy == "height":
        return min(options, key=lambda item: (float(item["base_world_mm"]["y"]), float(item["base_world_mm"]["x"])))
    return min(options, key=lambda item: (float(item["base_world_mm"]["x"]), float(item["base_world_mm"]["y"])))


def _oriented(value: dict[str, object], base: dict[str, float], rotated: bool) -> dict[str, object]:
    return {"participant": value, "base_world_mm": base, "rotated_xy": rotated}


def _allocate(
    values: list[float],
    indexes: list[int],
    amount: float,
    targets: list[float],
    weights: list[float],
) -> None:
    """Distribute amount toward soft targets, then proportionally by minimum size."""

    remaining = max(0.0, amount)
    if remaining <= _EPSILON or not indexes:
        return
    for index in indexes:
        deficit = max(0.0, float(targets[index]) - values[index])
        addition = min(deficit, remaining)
        values[index] += addition
        remaining -= addition
        if remaining <= _EPSILON:
            return
    positive = [max(_EPSILON, float(weights[index])) for index in indexes]
    total = sum(positive)
    distributed = 0.0
    for position, (index, weight) in enumerate(zip(indexes, positive)):
        addition = remaining - distributed if position == len(indexes) - 1 else remaining * weight / total
        values[index] += addition
        distributed += addition


def _support_contract(
    placements: list[dict[str, object]], stages: list[dict[str, object]]
) -> dict[str, object]:
    supports: list[dict[str, object]] = []
    minimum_ratio = 1.0
    for placement in placements:
        stage_index = int(placement["stage_index"])
        footprint = _area(_mapping(placement["world_size_mm"]))
        if stage_index == 0:
            ratio = 1.0
            supporting_ids = ["box-floor"]
        else:
            origin = _mapping(placement["origin_mm"])
            size = _mapping(placement["world_size_mm"])
            area = 0.0
            supporting_ids: list[str] = []
            for lower in placements:
                if int(lower["stage_index"]) != stage_index - 1:
                    continue
                lower_origin = _mapping(lower["origin_mm"])
                lower_size = _mapping(lower["world_size_mm"])
                if not isclose(
                    float(lower_origin["z"]) + float(lower_size["z"]),
                    float(origin["z"]),
                    abs_tol=0.001,
                ):
                    continue
                overlap = _xy_overlap(origin, size, lower_origin, lower_size)
                if overlap > _EPSILON:
                    area += overlap
                    supporting_ids.append(str(lower["id"]))
            ratio = min(1.0, area / footprint) if footprint else 1.0
        minimum_ratio = min(minimum_ratio, ratio)
        supports.append(
            {
                "placement_id": placement["id"],
                "stage_id": placement["stage_id"],
                "supporting_ids": supporting_ids,
                "coverage_ratio": _round(ratio),
                "supported": ratio + _EPSILON >= MIN_SUPPORT_RATIO,
            }
        )
    unsupported = [item for item in supports if not item["supported"]]
    return {
        "status": "unsupported" if unsupported else "supported",
        "minimum_coverage_ratio": _round(minimum_ratio),
        "minimum_required_ratio": MIN_SUPPORT_RATIO,
        "supports": supports,
        "unsupported_body_ids": [str(item["placement_id"]) for item in unsupported],
    }


def _removal_sequence(placements: list[dict[str, object]]) -> list[dict[str, object]]:
    ordered = sorted(
        placements,
        key=lambda item: (
            -int(item["stage_index"]),
            -float(_mapping(item["origin_mm"])["y"]),
            -float(_mapping(item["origin_mm"])["x"]),
            str(item["id"]),
        ),
    )
    return [
        {
            "order": index + 1,
            "placement_id": item["id"],
            "stage_id": item["stage_id"],
            "access_direction": "top",
        }
        for index, item in enumerate(ordered)
    ]


def _volume_contract(
    placements: list[dict[str, object]],
    box: dict[str, float],
    storage_height: float,
    clearance: float,
    complete: bool,
) -> dict[str, object]:
    storage_volume = box["x"] * box["y"] * storage_height
    body_volume = sum(_volume(_mapping(item["world_size_mm"])) for item in placements)
    inner_x = max(0.0, box["x"] - 2.0 * clearance)
    inner_y = max(0.0, box["y"] - 2.0 * clearance)
    inner_volume = inner_x * inner_y * storage_height
    residual = 0.0 if complete else max(0.0, inner_volume - body_volume)
    technical = max(0.0, storage_volume - body_volume - residual)
    classified = body_volume + residual + technical
    return {
        "storage_volume_mm3": _round(storage_volume),
        "requested_body_volume_mm3": _round(body_volume),
        "residual_volume_mm3": _round(residual),
        "technical_clearance_volume_mm3": _round(technical),
        "classified_volume_mm3": _round(classified),
        "conserved": isclose(classified, storage_volume, abs_tol=0.01),
        "residual_ratio": _round(residual / storage_volume if storage_volume else 0.0),
    }


def _score_candidate(
    placements: list[dict[str, object]],
    stages: list[dict[str, object]],
    support: dict[str, object],
    volume: dict[str, object],
    preference: str,
    *,
    complete: bool,
) -> dict[str, float]:
    rotations = sum(int(item["rotation_deg_z"] != 0) for item in placements)
    rows = sum(int(item["row_count"]) for item in stages)
    simplicity = max(0.0, 100.0 - max(0, len(stages) - 1) * 12.0 - rows * 2.0 - rotations * 2.0)
    target_errors: list[float] = []
    surplus_ratios: list[float] = []
    for placement in placements:
        contract = _mapping(placement["dimension_contract"])
        for axis in _AXES:
            value = _mapping(contract["axes"])[axis]
            if value["mode"] == "target" and value["target_mm"] is not None:
                target_errors.append(abs(float(value["calculated_mm"]) - float(value["target_mm"])) / float(value["target_mm"]))
            minimum = float(value["minimum_mm"])
            surplus_ratios.append(max(0.0, float(value["calculated_mm"]) - minimum) / minimum)
    targets = max(0.0, 100.0 - 100.0 * (sum(target_errors) / len(target_errors) if target_errors else 0.0))
    mean_surplus = sum(surplus_ratios) / len(surplus_ratios) if surplus_ratios else 0.0
    spread = max(surplus_ratios, default=0.0) - min(surplus_ratios, default=0.0)
    material = max(0.0, 100.0 - 25.0 * mean_surplus - 15.0 * spread)
    support_score = 100.0 * float(support["minimum_coverage_ratio"])
    weights = _SCORE_WEIGHTS[preference]
    total = sum(
        value * weights[key]
        for key, value in {
            "simplicity": simplicity,
            "targets": targets,
            "material": material,
            "support": support_score,
        }.items()
    )
    if not complete:
        total -= 50.0 * float(volume["residual_ratio"])
    return {
        "total": _round(max(0.0, total)),
        "simplicity": _round(simplicity),
        "target_fit": _round(targets),
        "material_distribution": _round(material),
        "support": _round(support_score),
    }


def _dimension_contract(
    participant: dict[str, object], final: dict[str, float]
) -> dict[str, object]:
    minimum = _dimension(participant["minimum_local_mm"], "participant.minimum_local_mm")
    modes = _mapping(participant["dimension_modes"])
    targets = _mapping(participant["target_local_mm"])
    axes: dict[str, object] = {}
    for axis in _AXES:
        target = targets[axis]
        calculated = float(final[axis])
        deviated = target is not None and not isclose(calculated, float(target), abs_tol=0.001)
        axes[axis] = {
            "mode": modes[axis],
            "minimum_mm": _round(minimum[axis]),
            "target_mm": _round(float(target)) if target is not None else None,
            "calculated_mm": _round(calculated),
            "status": "deviated" if deviated else "satisfied",
            "reason": (
                "La cible souple a ete ajustee pour fermer l etage."
                if deviated and modes[axis] == "target"
                else "Contrainte fixe respectee."
                if modes[axis] == "fixed"
                else "Dimension calculee automatiquement."
            ),
        }
    return {"axes": axes}


def _suggestions(residual_zones: list[dict[str, object]]) -> list[dict[str, object]]:
    usable = [
        zone
        for zone in residual_zones
        if min(float(value) for value in _mapping(zone["size_mm"]).values()) >= 1.2
    ]
    if not usable:
        return []
    largest = max(usable, key=lambda item: (_volume(_mapping(item["size_mm"])), str(item["id"])))
    return [
        {
            "id": f"suggestion:{largest['id']}",
            "kind": "solid_spacer",
            "name": "Cale optionnelle",
            "origin_mm": deepcopy(largest["origin_mm"]),
            "dimensions_mm": deepcopy(largest["size_mm"]),
            "reason": "Ce volume residuel est assez grand pour justifier une cale explicite.",
            "requires_confirmation": True,
            "automatic": False,
        }
    ]


def _residual_zone(
    identifier: str,
    stage_id: str,
    origin: dict[str, object],
    size: dict[str, object],
    kind: str,
) -> dict[str, object]:
    return {
        "id": identifier,
        "stage_id": stage_id,
        "kind": kind,
        "origin_mm": _rounded(origin),
        "size_mm": _rounded(size),
        "printable": False,
        "automatic_body_created": False,
    }


def _participant(value: dict[str, object], index: int) -> dict[str, object]:
    if not isinstance(value, dict):
        raise VolumetricStageSolverError(f"Participant {index} must be an object.")
    required = ("id", "role", "name", "minimum_local_mm", "dimension_modes", "target_local_mm")
    missing = [key for key in required if key not in value]
    if missing:
        raise VolumetricStageSolverError(f"Participant {index} misses: {', '.join(missing)}.")
    result = deepcopy(value)
    result["minimum_local_mm"] = _dimension(value["minimum_local_mm"], f"participant[{index}].minimum")
    modes = _mapping(value["dimension_modes"])
    targets = _mapping(value["target_local_mm"])
    result["dimension_modes"] = {}
    result["target_local_mm"] = {}
    for axis in _AXES:
        mode = str(modes.get(axis, "auto"))
        if mode not in {"auto", "target", "fixed"}:
            raise VolumetricStageSolverError(f"Participant {index} has invalid {axis} mode {mode!r}.")
        target = targets.get(axis)
        if target is not None and (isinstance(target, bool) or float(target) <= 0.0):
            raise VolumetricStageSolverError(f"Participant {index} has invalid {axis} target.")
        result["dimension_modes"][axis] = mode
        result["target_local_mm"][axis] = float(target) if target is not None else None
    return result


def _orders(values: list[dict[str, object]]) -> list[tuple[str, list[dict[str, object]]]]:
    orders = [
        ("input", list(values)),
        ("volume_desc", sorted(values, key=lambda item: (-_volume(_mapping(item["minimum_local_mm"])), str(item["id"])))),
        ("height_desc", sorted(values, key=lambda item: (-_axis_base(item, "z"), str(item["id"])))),
        ("area_desc", sorted(values, key=lambda item: (-_area(_mapping(item["minimum_local_mm"])), str(item["id"])))),
    ]
    unique: list[tuple[str, list[dict[str, object]]]] = []
    signatures: set[tuple[str, ...]] = set()
    for name, order in orders:
        signature = tuple(str(item["id"]) for item in order)
        if signature not in signatures:
            signatures.add(signature)
            unique.append((name, order))
    return unique[:MAX_ORDERINGS]


def _group_sizes(count: int) -> list[int]:
    if count <= MAX_GROUP_SIZES_PER_ORDER:
        return list(range(1, count + 1))
    values = {1, 2, 3, 4, count}
    for stage_count in range(2, MAX_GROUP_SIZES_PER_ORDER + 1):
        values.add(max(1, ceil(count / stage_count)))
    return sorted(values)[: MAX_GROUP_SIZES_PER_ORDER - 1] + [count]


def _axis_base(participant: dict[str, object], axis: str) -> float:
    minimum = float(_mapping(participant["minimum_local_mm"])[axis])
    target = _mapping(participant["target_local_mm"])[axis]
    if _axis_mode(participant, axis) == "fixed" and target is not None:
        return float(target)
    return minimum


def _axis_mode(
    participant: dict[str, object], axis: str, *, rotated: bool = False
) -> str:
    local_axis = _local_axis(axis, rotated)
    return str(_mapping(participant["dimension_modes"])[local_axis])


def _axis_target(
    participant: dict[str, object], axis: str, *, rotated: bool = False
) -> float | None:
    local_axis = _local_axis(axis, rotated)
    value = _mapping(participant["target_local_mm"])[local_axis]
    return float(value) if value is not None else None


def _local_axis(world_axis: str, rotated: bool) -> str:
    if not rotated or world_axis == "z":
        return world_axis
    return "y" if world_axis == "x" else "x"


def _xy_target_error(
    participant: dict[str, object], world_size: dict[str, object], *, rotated: bool
) -> float:
    error = 0.0
    for axis in ("x", "y"):
        target = _axis_target(participant, axis, rotated=rotated)
        if target is not None and _axis_mode(participant, axis, rotated=rotated) == "target":
            error += abs(float(world_size[axis]) - target) / target
    return error


def _xy_overlap(
    left_origin: dict[str, object],
    left_size: dict[str, object],
    right_origin: dict[str, object],
    right_size: dict[str, object],
) -> float:
    width = max(
        0.0,
        min(float(left_origin["x"]) + float(left_size["x"]), float(right_origin["x"]) + float(right_size["x"]))
        - max(float(left_origin["x"]), float(right_origin["x"])),
    )
    height = max(
        0.0,
        min(float(left_origin["y"]) + float(left_size["y"]), float(right_origin["y"]) + float(right_size["y"]))
        - max(float(left_origin["y"]), float(right_origin["y"])),
    )
    return width * height


def _candidate_signature(candidate: dict[str, object]) -> str:
    return "|".join(
        f"{item['id']}@{item['origin_mm']}:{item['world_size_mm']}:{item['rotation_deg_z']}"
        for item in _mappings(candidate["placements"])
    )


def _empty_result(budgets: dict[str, int], message: str) -> dict[str, object]:
    return {
        "schema_version": VOLUMETRIC_STAGE_SOLVER_SCHEMA_V1,
        "status": SOLUTION_IMPOSSIBLE,
        "candidates": [],
        "best_candidate": None,
        "budgets": budgets,
        "search": {
            "deterministic": True,
            "globally_optimal": False,
            "truncated": False,
            "ordering_count": 0,
            "groupings_evaluated": 0,
            "xy_arrangements_evaluated": 0,
            "candidate_count": 0,
            "complete_candidate_count": 0,
            "partial_candidate_count": 0,
        },
        "blockers": [{"code": "NO_PARTICIPANT", "message": message, "action": "Ajoute un conteneur constructible."}],
        "invariants": {
            "requested_bodies_only": True,
            "automatic_body_count": 0,
            "suggestions_do_not_mutate": True,
            "bounded_search": True,
        },
    }


def _dimension(value: object, field: str) -> dict[str, float]:
    raw = _mapping(value)
    try:
        result = {axis: float(raw[axis]) for axis in _AXES}
    except (KeyError, TypeError, ValueError) as exc:
        raise VolumetricStageSolverError(f"{field} must contain numeric x, y and z.") from exc
    if any(value <= 0.0 for value in result.values()):
        raise VolumetricStageSolverError(f"{field} dimensions must be positive.")
    return result


def _mapping(value: object) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise VolumetricStageSolverError("Internal P64 value must be an object.")
    return value


def _mappings(value: object) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        raise VolumetricStageSolverError("Internal P64 value must be a list.")
    return [_mapping(item) for item in value]


def _rounded(value: dict[str, object]) -> dict[str, float]:
    return {axis: _round(float(value[axis])) for axis in _AXES}


def _area(value: dict[str, object]) -> float:
    return float(value["x"]) * float(value["y"])


def _volume(value: dict[str, object]) -> float:
    return float(value["x"]) * float(value["y"]) * float(value["z"])


def _round(value: float) -> float:
    return round(float(value), 4)
