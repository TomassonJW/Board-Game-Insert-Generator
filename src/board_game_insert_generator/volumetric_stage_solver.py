"""P64 bounded deterministic volumetric stage solver.

The module searches portfolios of complete XY arrangements, then composes them
bottom-to-top in Z.  It is deliberately heuristic: budgets are public, search
is deterministic and no external optimiser is required.  Residual regions are
reported and may produce suggestions, but never printable bodies.
"""

from __future__ import annotations

import hashlib
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
MAX_ADAPTIVE_STAGE_COUNTS = 8
MAX_STACK_PARTITIONS_PER_ORDER = 64
MAX_STRUCTURED_STACK_PARTITIONS_PER_ORDER = 128
MAX_STACK_ASSIGNMENT_BEAM = 128
MAX_CANDIDATES = 192
MAX_RETURNED_CANDIDATES = 64
MAX_ORIENTATION_COMBINATIONS = 1024
MIN_SUPPORT_RATIO = 0.25

STRUCTURED_ORDER_STRATEGIES = (
    "top_inset_headroom_asc",
    "top_inset_safe_top_asc",
    "top_inset_headroom_asc_reverse",
    "long_side_desc",
    "short_side_desc",
    "area_interleave",
    "height_interleave",
)

_AXES = ("x", "y", "z")
_EPSILON = 0.0001

_SCORE_WEIGHTS = {
    "balanced": {"simplicity": 0.05, "targets": 0.20, "material": 0.10, "support": 0.20, "spatial": 0.45},
    "compact": {"simplicity": 0.40, "targets": 0.25, "material": 0.20, "support": 0.15, "spatial": 0.0},
    "accessible": {"simplicity": 0.25, "targets": 0.15, "material": 0.15, "support": 0.45, "spatial": 0.0},
    "print_simple": {"simplicity": 0.50, "targets": 0.15, "material": 0.20, "support": 0.15, "spatial": 0.0},
    "material_reduced": {"simplicity": 0.15, "targets": 0.20, "material": 0.50, "support": 0.15, "spatial": 0.0},
}


class VolumetricStageSolverError(ValueError):
    """Raised when the internal P64 participant contract is malformed."""


def solve_stage_portfolio(
    participants: list[dict[str, object]],
    box: dict[str, object],
    storage_height_mm: float,
    clearance_mm: float,
    *,
    box_clearance_mm: float | None = None,
    vertical_clearance_mm: float | None = None,
    preference: str = "balanced",
    diversified_order_seed: int | None = None,
    structured_order_strategy: str | None = None,
    top_inset_search_context: dict[str, object] | None = None,
) -> dict[str, object]:
    """Return a bounded portfolio of complete or residual stage candidates."""

    values = [_participant(item, index) for index, item in enumerate(participants)]
    bounds = _dimension(box, "box")
    height = float(storage_height_mm)
    between_clearance = float(clearance_mm)
    box_clearance = between_clearance if box_clearance_mm is None else float(box_clearance_mm)
    vertical_clearance = between_clearance if vertical_clearance_mm is None else float(vertical_clearance_mm)
    if height <= 0.0 or between_clearance < 0.0 or box_clearance < 0.0 or vertical_clearance < 0.0:
        raise VolumetricStageSolverError(
            "Storage height must be positive and XY/Z clearances non-negative."
        )
    if preference not in _SCORE_WEIGHTS:
        raise VolumetricStageSolverError(f"Unknown P64 solver preference: {preference!r}.")
    if diversified_order_seed is not None and structured_order_strategy is not None:
        raise VolumetricStageSolverError(
            "A stage portfolio cannot combine hash diversification and a structured order."
        )
    if (
        structured_order_strategy is not None
        and structured_order_strategy not in STRUCTURED_ORDER_STRATEGIES
    ):
        raise VolumetricStageSolverError(
            f"Unknown structured order strategy: {structured_order_strategy!r}."
        )

    budgets = {
        "max_orderings": MAX_ORDERINGS,
        "max_group_sizes_per_order": MAX_GROUP_SIZES_PER_ORDER,
        "max_adaptive_stage_counts": MAX_ADAPTIVE_STAGE_COUNTS,
        "max_stack_partitions_per_order": (
            MAX_STRUCTURED_STACK_PARTITIONS_PER_ORDER
            if structured_order_strategy == "top_inset_safe_top_asc"
            else MAX_STACK_PARTITIONS_PER_ORDER
        ),
        "max_candidates": MAX_CANDIDATES,
        "max_returned_candidates": MAX_RETURNED_CANDIDATES,
        "max_orientation_combinations": MAX_ORIENTATION_COMBINATIONS,
    }
    if not values:
        return _empty_result(budgets, "No requested body can participate in the stage search.", between_clearance, box_clearance, vertical_clearance)

    orderings = _orders(
        values,
        diversified_order_seed=diversified_order_seed,
        structured_order_strategy=structured_order_strategy,
    )
    constraint_directed = (
        structured_order_strategy == "top_inset_safe_top_asc"
        and isinstance(top_inset_search_context, dict)
    )
    enforce_top_inset_headroom = False
    candidates: list[dict[str, object]] = []
    signatures: set[str] = set()
    groupings_evaluated = 0
    adaptive_partitions_evaluated = 0
    stack_partitions_evaluated = 0
    xy_arrangements_evaluated = 0
    truncated = False
    for order_name, ordered in orderings:
        for stage_count in range(2, min(len(ordered), MAX_ADAPTIVE_STAGE_COUNTS) + 1):
            if not _minimum_stage_height_fits(
                ordered,
                stage_count,
                height,
                vertical_clearance,
            ):
                continue
            adaptive_partitions_evaluated += 1
            groups = _adaptive_stage_partition(ordered, stage_count)
            for orientation_strategy in ("width", "height", "balanced"):
                if len(candidates) >= MAX_CANDIDATES:
                    truncated = True
                    break
                candidate, attempts = _candidate_for_groups(
                    groups,
                    bounds,
                    height,
                    between_clearance,
                    box_clearance,
                    vertical_clearance,
                    preference=preference,
                    order_name=order_name,
                    group_size=0,
                    orientation_strategy=orientation_strategy,
                    enforce_top_inset_headroom=enforce_top_inset_headroom,
                    constraint_directed=constraint_directed,
                    top_inset_search_context=top_inset_search_context,
                )
                xy_arrangements_evaluated += attempts
                if candidate is None:
                    continue
                candidate["candidate_id"] = (
                    f"{order_name}:adaptive{stage_count}:{orientation_strategy}:"
                    f"{len(_mappings(candidate['stages']))}s"
                )
                origin = _mapping(candidate["search_origin"])
                origin.pop("group_size", None)
                origin["adaptive_stage_count"] = stage_count
                signature = _candidate_signature(candidate)
                if signature in signatures:
                    continue
                signatures.add(signature)
                candidates.append(candidate)
            if truncated:
                break
        if truncated:
            break
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
                    between_clearance,
                    box_clearance,
                    vertical_clearance,
                    preference=preference,
                    order_name=order_name,
                    group_size=group_size,
                    orientation_strategy=orientation_strategy,
                    enforce_top_inset_headroom=enforce_top_inset_headroom,
                    constraint_directed=constraint_directed,
                    top_inset_search_context=top_inset_search_context,
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
        for stack_partition_index, stacks in enumerate(
            _stack_partitions(
                ordered,
                height,
                vertical_clearance,
                assignment_beam=constraint_directed,
                enforce_top_inset_headroom=enforce_top_inset_headroom,
            )
        ):
            stack_partitions_evaluated += 1
            for orientation_strategy in ("width", "height", "balanced"):
                if len(candidates) >= MAX_CANDIDATES:
                    truncated = True
                    break
                candidate, attempts = _candidate_for_stacks(
                    stacks,
                    bounds,
                    height,
                    between_clearance,
                    box_clearance,
                    vertical_clearance,
                    preference=preference,
                    order_name=order_name,
                    partition_index=stack_partition_index,
                    orientation_strategy=orientation_strategy,
                    enforce_top_inset_headroom=enforce_top_inset_headroom,
                    constraint_directed=constraint_directed,
                    top_inset_search_context=top_inset_search_context,
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
        key=lambda item: _candidate_sort_key(item, preference),
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
        "clearances_mm": {"xy": _round(between_clearance), "z": _round(vertical_clearance), "box_xy": _round(box_clearance), "between_xy": _round(between_clearance), "between_z": _round(vertical_clearance)},
        "search": {
            "deterministic": True,
            "globally_optimal": False,
            "truncated": truncated or len(ordered_candidates) > len(returned),
            "ordering_count": len(orderings),
            **({"diversified_order_seed": diversified_order_seed} if diversified_order_seed is not None else {}),
            **(
                {"structured_order_strategy": structured_order_strategy}
                if structured_order_strategy is not None
                else {}
            ),
            "groupings_evaluated": groupings_evaluated,
            "adaptive_partitions_evaluated": adaptive_partitions_evaluated,
            "stack_partitions_evaluated": stack_partitions_evaluated,
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


def _adaptive_stage_partition(
    values: list[dict[str, object]],
    stage_count: int,
) -> list[list[dict[str, object]]]:
    """Distribute footprints with a bounded deterministic LPT partition."""

    groups: list[list[dict[str, object]]] = [[] for _ in range(stage_count)]
    footprint_loads = [0.0 for _ in range(stage_count)]
    for value in values:
        index = min(
            range(stage_count),
            key=lambda candidate: (
                footprint_loads[candidate],
                len(groups[candidate]),
                candidate,
            ),
        )
        groups[index].append(value)
        footprint_loads[index] += _area(_mapping(value["minimum_local_mm"]))
    return groups


def _minimum_stage_height_fits(
    values: list[dict[str, object]],
    stage_count: int,
    storage_height: float,
    vertical_clearance: float,
) -> bool:
    """Reject stage counts whose optimistic Z lower bound already overflows."""

    heights = sorted(_axis_base(value, "z") for value in values)
    minimum_body_height = heights[-1] + sum(heights[: stage_count - 1])
    minimum_clearance = max(0, stage_count - 1) * vertical_clearance
    return minimum_body_height + minimum_clearance <= storage_height + _EPSILON


def _candidate_for_groups(
    groups: list[list[dict[str, object]]],
    box: dict[str, float],
    storage_height: float,
    between_clearance: float,
    box_clearance: float,
    vertical_clearance: float,
    *,
    preference: str,
    order_name: str,
    group_size: int,
    orientation_strategy: str,
    enforce_top_inset_headroom: bool,
    constraint_directed: bool,
    top_inset_search_context: dict[str, object] | None,
) -> tuple[dict[str, object] | None, int]:
    height_plan = _stage_heights(
        groups,
        storage_height,
        vertical_clearance,
        enforce_top_inset_headroom=enforce_top_inset_headroom,
    )
    if height_plan is None:
        return None, 0
    stage_heights, vertical_complete, stage_gaps = height_plan
    stage_layouts: list[dict[str, object]] = []
    attempts = 0
    xy_complete = True
    for stage_index, (group, stage_height) in enumerate(zip(groups, stage_heights)):
        spatial_reference = stage_height if preference == "balanced" else None
        search_context = (
            top_inset_search_context
            if constraint_directed and stage_index == len(groups) - 1
            else None
        )
        body_heights = {
            str(item["id"]): (
                _axis_base(item, "z")
                if _axis_mode(item, "z") == "fixed"
                else stage_height
            )
            for item in group
        }
        full, full_attempts = _best_xy_layout(
            group,
            box,
            between_clearance,
            box_clearance,
            orientation_strategy=orientation_strategy,
            fill=True,
            spatial_reference_height=spatial_reference,
            top_inset_search_context=search_context,
            top_body_heights_by_id=body_heights,
        )
        attempts += full_attempts
        if full is not None:
            stage_layouts.append(full)
            continue
        partial, partial_attempts = _best_xy_layout(
            group,
            box,
            between_clearance,
            box_clearance,
            orientation_strategy=orientation_strategy,
            fill=False,
            spatial_reference_height=spatial_reference,
            top_inset_search_context=search_context,
            top_body_heights_by_id=body_heights,
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
            if "external_clearance_effective_v1" in item:
                placement["external_clearance_effective_v1"] = deepcopy(item["external_clearance_effective_v1"])
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
                "clearance_above_mm": _round(stage_gaps[stage_index] if stage_index < len(stage_gaps) else 0.0),
            }
        )
        cursor_z = stage_top + (stage_gaps[stage_index] if stage_index < len(stage_gaps) else 0.0)

    if cursor_z < storage_height - _EPSILON:
        inner_x = max(0.0, box["x"] - 2.0 * box_clearance)
        inner_y = max(0.0, box["y"] - 2.0 * box_clearance)
        residual_zones.append(
            _residual_zone(
                "residual:top",
                "above-stages",
                {"x": _round(box_clearance), "y": _round(box_clearance), "z": _round(cursor_z)},
                {"x": _round(inner_x), "y": _round(inner_y), "z": _round(storage_height - cursor_z)},
                "unused_height",
            )
        )

    support = _support_contract(placements, stages, vertical_clearance)
    if support["status"] == "unsupported":
        return None, attempts
    complete = xy_complete and vertical_complete and all_reach_stage_top
    solution_status = SOLUTION_COMPLETE if complete else SOLUTION_WITH_RESIDUALS
    volume = _volume_contract(placements, box, storage_height, box_clearance, complete)
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
                **(
                    {
                        "top_inset_search_violation_count": int(
                            stage_layouts[-1].get("_top_inset_violation_count", 0)
                        ),
                        "top_inset_search_shortfall_mm": float(
                            stage_layouts[-1].get("_top_inset_shortfall_mm", 0.0)
                        ),
                    }
                    if constraint_directed
                    else {}
                ),
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


def _candidate_for_stacks(
    stacks: list[list[dict[str, object]]],
    box: dict[str, float],
    storage_height: float,
    between_clearance: float,
    box_clearance: float,
    vertical_clearance: float,
    *,
    preference: str,
    order_name: str,
    partition_index: int,
    orientation_strategy: str,
    enforce_top_inset_headroom: bool,
    constraint_directed: bool,
    top_inset_search_context: dict[str, object] | None,
) -> tuple[dict[str, object] | None, int]:
    """Pack independent vertical stacks in XY.

    A body may span several global Z intervals beside a stack of shorter bodies.
    This keeps the search deterministic while avoiding the old full-width slab
    assumption.
    """

    descriptors: list[dict[str, object]] = []
    for stack_index, members in enumerate(stacks):
        descriptor = _stack_descriptor(members, orientation_strategy, stack_index)
        if descriptor is None:
            return None, 0
        resolved_members = _mappings(descriptor["stack_members"])
        heights = _stack_heights(
            resolved_members,
            storage_height,
            vertical_clearance,
            enforce_top_inset_headroom=enforce_top_inset_headroom,
        )
        if heights is None:
            return None, 0
        top_member = _mapping(resolved_members[-1])
        descriptor["resolved_stack_heights"] = heights
        descriptor["top_inset_layout_subject"] = {
            "participant": top_member["participant"],
            "body_height_mm": heights[-1],
            "rotated_xy": bool(top_member["rotated_xy"]),
        }
        descriptors.append(descriptor)

    layout, attempts = _best_xy_layout(
        descriptors,
        box,
        between_clearance,
        box_clearance,
        orientation_strategy=orientation_strategy,
        fill=True,
        top_inset_search_context=(
            top_inset_search_context if constraint_directed else None
        ),
    )
    if layout is None:
        return None, attempts

    placements: list[dict[str, object]] = []
    for stack_index, item_layout in enumerate(_mappings(layout["placements"])):
        descriptor = _mapping(item_layout["participant"])
        members = _mappings(descriptor["stack_members"])
        raw_heights = descriptor["resolved_stack_heights"]
        if not isinstance(raw_heights, list):
            raise VolumetricStageSolverError("Resolved stack heights must be a list.")
        heights = [float(item) for item in raw_heights]
        if constraint_directed and top_inset_search_context is not None:
            adjusted_heights = _rebalance_stack_top_height_for_inset(
                descriptor,
                item_layout,
                heights,
                top_inset_search_context,
            )
            if adjusted_heights is None:
                return None, attempts
            heights = adjusted_heights

        world_xy = _mapping(item_layout["world_size_mm"])
        stack_origin = _mapping(item_layout["origin_mm"])
        cursor_z = 0.0
        for stack_level, (member, body_height) in enumerate(zip(members, heights)):
            participant = _mapping(member["participant"])
            rotated = bool(member["rotated_xy"])
            world_size = {
                "x": _round(float(world_xy["x"])),
                "y": _round(float(world_xy["y"])),
                "z": _round(body_height),
            }
            local_final = {
                "x": world_size["y"] if rotated else world_size["x"],
                "y": world_size["x"] if rotated else world_size["y"],
                "z": world_size["z"],
            }
            placement = {
                "id": participant["id"],
                "role": participant["role"],
                "name": participant["name"],
                "origin_mm": {
                    "x": _round(float(stack_origin["x"])),
                    "y": _round(float(stack_origin["y"])),
                    "z": _round(cursor_z),
                },
                "world_size_mm": world_size,
                "rotation_deg_z": 90 if rotated else 0,
                "final_outer_dimensions_mm": _rounded(local_final),
                "stage_id": "",
                "stage_index": -1,
                "stage_bottom_z_mm": _round(cursor_z),
                "stage_top_z_mm": _round(cursor_z + body_height),
                "reaches_stage_top": True,
                "stack_id": descriptor["id"],
                "stack_index": stack_index,
                "stack_level": stack_level,
                "dimension_contract": _dimension_contract(participant, local_final),
                "printable": True,
                "automatic": False,
            }
            if "external_clearance_effective_v1" in participant:
                placement["external_clearance_effective_v1"] = deepcopy(participant["external_clearance_effective_v1"])
            for key in ("container_group_id", "requested_complement_id", "complement_kind"):
                if key in participant:
                    placement[key] = participant[key]
            placements.append(placement)
            next_participant = (
                _mapping(members[stack_level + 1]["participant"])
                if stack_level < len(members) - 1
                else None
            )
            cursor_z += body_height + (
                _participant_pair_clearance(participant, next_participant, "z", vertical_clearance)
                if next_participant is not None
                else 0.0
            )
        if not isclose(cursor_z, storage_height, abs_tol=0.001):
            return None, attempts

    stages = _interval_stages(placements, storage_height, int(layout["row_count"]))
    support = _support_contract(placements, stages, vertical_clearance)
    if support["status"] == "unsupported":
        return None, attempts

    complete = True
    volume = _volume_contract(placements, box, storage_height, box_clearance, complete)
    scores = _score_candidate(
        placements,
        stages,
        support,
        volume,
        preference,
        complete=complete,
    )
    candidate_id = (
        f"{order_name}:stacks{partition_index}:{orientation_strategy}:"
        f"{len(stacks)}c:{len(stages)}i"
    )
    return (
        {
            "candidate_id": candidate_id,
            "solution_status": SOLUTION_COMPLETE,
            "quality_score": scores["total"],
            "score_breakdown": scores,
            "stage_count": len(stages),
            "stages": stages,
            "placements": placements,
            "support": support,
            "removal_sequence": _removal_sequence(placements),
            "residuals": {
                "status": "none",
                "zones": [],
                "residual_volume_mm3": volume["residual_volume_mm3"],
                "residual_ratio": volume["residual_ratio"],
            },
            "suggestions": [],
            "volume_conservation": volume,
            "metrics": {
                "row_count": int(layout["row_count"]),
                "rotation_count": sum(int(item["rotation_deg_z"] != 0) for item in placements),
                "target_deviation_count": sum(
                    int(value["status"] == "deviated")
                    for item in placements
                    for value in _mapping(item["dimension_contract"])["axes"].values()
                ),
            },
            "search_origin": {
                "order": order_name,
                "stack_partition_index": partition_index,
                "stack_count": len(stacks),
                "orientation_strategy": orientation_strategy,
                **(
                    {
                        "top_inset_search_violation_count": int(
                            layout.get("_top_inset_violation_count", 0)
                        ),
                        "top_inset_search_shortfall_mm": float(
                            layout.get("_top_inset_shortfall_mm", 0.0)
                        ),
                    }
                    if constraint_directed
                    else {}
                ),
            },
            "invariants": {
                "no_collisions_by_construction": True,
                "requested_bodies_only": True,
                "automatic_body_count": 0,
                "suggestions_do_not_mutate": True,
                "hybrid_vertical_stacks": True,
                "bodies_may_span_z_intervals": True,
            },
        },
        attempts,
    )


def _stack_partitions(
    values: list[dict[str, object]],
    storage_height: float,
    vertical_clearance: float,
    *,
    assignment_beam: bool = False,
    enforce_top_inset_headroom: bool = False,
) -> list[list[list[dict[str, object]]]]:
    """Return bounded contiguous or assignment-beam vertical partitions."""

    count = len(values)
    if count == 0:
        return []

    def stack_height(stack: list[dict[str, object]]) -> float:
        return _stack_minimum_height(
            stack,
            storage_height,
            vertical_clearance,
            enforce_top_inset_headroom=enforce_top_inset_headroom,
        )

    if assignment_beam:
        candidates = _beam_stack_partitions(
            values,
            storage_height,
            vertical_clearance,
            enforce_top_inset_headroom=enforce_top_inset_headroom,
        )
    else:
        candidates: list[list[list[dict[str, object]]]] = []
    if not assignment_beam and count <= 10:
        for boundary_mask in range(1 << max(0, count - 1)):
            stacks: list[list[dict[str, object]]] = []
            current: list[dict[str, object]] = []
            for index, value in enumerate(values):
                current.append(value)
                if index == count - 1 or boundary_mask & (1 << index):
                    stacks.append(current)
                    current = []
            if all(stack_height(stack) <= storage_height + _EPSILON for stack in stacks):
                candidates.append(stacks)
    elif not assignment_beam:
        for group_size in _group_sizes(count):
            stacks = [values[index : index + group_size] for index in range(0, count, group_size)]
            if all(stack_height(stack) <= storage_height + _EPSILON for stack in stacks):
                candidates.append(stacks)
        greedy: list[list[dict[str, object]]] = []
        current = []
        current_height = 0.0
        for value in values:
            height = _axis_base(value, "z")
            added_height = height + (
                _participant_pair_clearance(current[-1], value, "z", vertical_clearance)
                if current
                else 0.0
            )
            if current and current_height + added_height > storage_height + _EPSILON:
                greedy.append(current)
                current = []
                current_height = 0.0
                added_height = height
            current.append(value)
            current_height += added_height
        if current:
            greedy.append(current)
        if all(stack_height(stack) <= storage_height + _EPSILON for stack in greedy):
            candidates.append(greedy)

    unique: list[list[list[dict[str, object]]]] = []
    signatures: set[tuple[tuple[str, ...], ...]] = set()
    ordered = (
        _diverse_stack_states(
            candidates,
            storage_height,
            vertical_clearance,
            enforce_top_inset_headroom=enforce_top_inset_headroom,
            limit=len(candidates),
        )
        if assignment_beam
        else sorted(
            candidates,
            key=lambda stacks: (
                len(stacks),
                max(stack_height(stack) for stack in stacks),
                tuple(tuple(str(item["id"]) for item in stack) for stack in stacks),
            ),
        )
    )
    for stacks in ordered:
        signature = tuple(tuple(str(item["id"]) for item in stack) for stack in stacks)
        if signature in signatures:
            continue
        signatures.add(signature)
        unique.append(stacks)
        limit = (
            MAX_STRUCTURED_STACK_PARTITIONS_PER_ORDER
            if assignment_beam
            else MAX_STACK_PARTITIONS_PER_ORDER
        )
        if len(unique) >= limit:
            break
    return unique


def _stack_minimum_height(
    stack: list[dict[str, object]],
    storage_height: float,
    vertical_clearance: float,
    *,
    enforce_top_inset_headroom: bool,
) -> float:
    heights = [_axis_base(item, "z") for item in stack]
    if enforce_top_inset_headroom and stack:
        heights[-1] = max(
            heights[-1],
            _bounded_safe_top_height(stack[-1], storage_height),
        )
    gaps = [
        _participant_pair_clearance(left, right, "z", vertical_clearance)
        for left, right in zip(stack, stack[1:])
    ]
    return sum(heights) + sum(gaps)


def _beam_stack_partitions(
    values: list[dict[str, object]],
    storage_height: float,
    vertical_clearance: float,
    *,
    enforce_top_inset_headroom: bool,
) -> list[list[list[dict[str, object]]]]:
    """Assign bodies to non-contiguous stacks with a deterministic bounded beam."""

    states: list[list[list[dict[str, object]]]] = [[]]
    for value in values:
        expanded: dict[
            tuple[tuple[str, ...], ...],
            list[list[dict[str, object]]],
        ] = {}
        for stacks in states:
            proposals = [[*stack] for stack in stacks]
            proposals.append([value])
            _keep_stack_state(expanded, proposals)

            for stack_index, stack in enumerate(stacks):
                for members in ([*stack, value], [value, *stack]):
                    if (
                        _stack_minimum_height(
                            members,
                            storage_height,
                            vertical_clearance,
                            enforce_top_inset_headroom=enforce_top_inset_headroom,
                        )
                        > storage_height + _EPSILON
                    ):
                        continue
                    proposals = [[*item] for item in stacks]
                    proposals[stack_index] = members
                    _keep_stack_state(expanded, proposals)

        states = _diverse_stack_states(
            list(expanded.values()),
            storage_height,
            vertical_clearance,
            enforce_top_inset_headroom=enforce_top_inset_headroom,
            limit=MAX_STACK_ASSIGNMENT_BEAM,
        )

    return [
        sorted(
            stacks,
            key=lambda stack: (
                _top_inset_headroom_deficit(stack[-1]),
                -max(_axis_base(item, "z") for item in stack),
                tuple(str(item["id"]) for item in stack),
            ),
        )
        for stacks in states
    ]


def _diverse_stack_states(
    states: list[list[list[dict[str, object]]]],
    storage_height: float,
    vertical_clearance: float,
    *,
    enforce_top_inset_headroom: bool,
    limit: int,
) -> list[list[list[dict[str, object]]]]:
    """Keep good states for every explored stack count, not only the densest."""

    buckets: dict[int, list[list[list[dict[str, object]]]]] = {}
    for stacks in sorted(
        states,
        key=lambda item: _stack_state_key(
            item,
            storage_height,
            vertical_clearance,
            enforce_top_inset_headroom=enforce_top_inset_headroom,
        ),
    ):
        buckets.setdefault(len(stacks), []).append(stacks)

    selected: list[list[list[dict[str, object]]]] = []
    rank = 0
    while len(selected) < limit:
        added = False
        for stack_count in sorted(buckets):
            bucket = buckets[stack_count]
            if rank >= len(bucket):
                continue
            selected.append(bucket[rank])
            added = True
            if len(selected) >= limit:
                break
        if not added:
            break
        rank += 1
    return selected

def _keep_stack_state(
    states: dict[tuple[tuple[str, ...], ...], list[list[dict[str, object]]]],
    stacks: list[list[dict[str, object]]],
) -> None:
    signature = tuple(
        sorted(tuple(str(item["id"]) for item in stack) for stack in stacks)
    )
    states.setdefault(signature, stacks)


def _stack_safe_top_shortfall(
    stack: list[dict[str, object]],
    storage_height: float,
    vertical_clearance: float,
) -> float:
    """Return headroom that no Z redistribution inside this stack can recover."""

    if not stack:
        return 0.0
    top = stack[-1]
    required = _layout_top_required_height(top)
    if _axis_mode(top, "z") == "fixed":
        maximum_top_height = _axis_base(top, "z")
    else:
        lower_minimum = sum(_axis_base(item, "z") for item in stack[:-1])
        gaps = sum(
            _participant_pair_clearance(left, right, "z", vertical_clearance)
            for left, right in zip(stack, stack[1:])
        )
        maximum_top_height = max(0.0, storage_height - lower_minimum - gaps)
    return _round(max(0.0, required - maximum_top_height))

def _stack_state_key(
    stacks: list[list[dict[str, object]]],
    storage_height: float,
    vertical_clearance: float,
    *,
    enforce_top_inset_headroom: bool,
) -> tuple[object, ...]:
    heights = [
        _stack_minimum_height(
            stack,
            storage_height,
            vertical_clearance,
            enforce_top_inset_headroom=enforce_top_inset_headroom,
        )
        for stack in stacks
    ]
    footprint_area = sum(
        max(_axis_base(item, "x") for item in stack)
        * max(_axis_base(item, "y") for item in stack)
        for stack in stacks
    )
    safe_top_shortfalls = [
        _stack_safe_top_shortfall(stack, storage_height, vertical_clearance)
        for stack in stacks
    ]
    return (
        sum(int(value > _EPSILON) for value in safe_top_shortfalls),
        _round(sum(safe_top_shortfalls)),
        len(stacks),
        footprint_area,
        max(heights, default=0.0),
        max(heights, default=0.0) - min(heights, default=0.0),
        tuple(
            sorted(tuple(str(item["id"]) for item in stack) for stack in stacks)
        ),
    )


def _stack_descriptor(
    members: list[dict[str, object]],
    strategy: str,
    stack_index: int,
) -> dict[str, object] | None:
    option_sets = [_orientation_options(value) for value in members]
    combination_count = 1
    for options in option_sets:
        combination_count *= len(options)
    combinations = (
        product(*option_sets)
        if combination_count <= MAX_ORIENTATION_COMBINATIONS
        else [tuple(_greedy_orientation(value, strategy) for value in members)]
    )

    feasible: list[tuple[tuple[object, ...], dict[str, object]]] = []
    for combination in combinations:
        minimum = {
            axis: max(float(_mapping(item["base_world_mm"])[axis]) for item in combination)
            for axis in ("x", "y")
        }
        modes: dict[str, str] = {}
        targets: dict[str, float | None] = {}
        valid = True
        for axis in ("x", "y"):
            fixed_values = [
                float(_mapping(item["base_world_mm"])[axis])
                for item in combination
                if _axis_mode(
                    _mapping(item["participant"]),
                    axis,
                    rotated=bool(item["rotated_xy"]),
                )
                == "fixed"
            ]
            if fixed_values:
                fixed = fixed_values[0]
                if any(not isclose(value, fixed, abs_tol=0.001) for value in fixed_values):
                    valid = False
                    break
                if fixed + _EPSILON < minimum[axis]:
                    valid = False
                    break
                modes[axis] = "fixed"
                targets[axis] = fixed
                minimum[axis] = fixed
            else:
                soft_targets = [
                    _axis_target(
                        _mapping(item["participant"]),
                        axis,
                        rotated=bool(item["rotated_xy"]),
                    )
                    for item in combination
                ]
                soft_targets = [value for value in soft_targets if value is not None]
                modes[axis] = "target" if soft_targets else "auto"
                targets[axis] = max([minimum[axis], *soft_targets]) if soft_targets else None
        if not valid:
            continue

        rotations = sum(int(bool(item["rotated_xy"])) for item in combination)
        if strategy == "width":
            key: tuple[object, ...] = (minimum["x"], minimum["y"], rotations)
        elif strategy == "height":
            key = (minimum["y"], minimum["x"], rotations)
        else:
            key = (minimum["x"] * minimum["y"], rotations, minimum["x"])
        signature = tuple(
            (str(_mapping(item["participant"])["id"]), bool(item["rotated_xy"]))
            for item in combination
        )
        descriptor = {
            "id": f"stack:{stack_index}:" + "+".join(str(item["id"]) for item in members),
            "role": "stack_descriptor",
            "name": f"Pile {stack_index + 1}",
            "minimum_local_mm": {"x": minimum["x"], "y": minimum["y"], "z": 1.0},
            "dimension_modes": {"x": modes["x"], "y": modes["y"], "z": "fixed"},
            "target_local_mm": {"x": targets["x"], "y": targets["y"], "z": 1.0},
            "allow_xy_rotation": False,
            "stack_members": [
                {
                    "participant": item["participant"],
                    "rotated_xy": bool(item["rotated_xy"]),
                    "base_world_mm": deepcopy(item["base_world_mm"]),
                }
                for item in combination
            ],
        }
        feasible.append(((*key, signature), descriptor))
    return min(feasible, key=lambda item: item[0])[1] if feasible else None


def _stack_heights(
    members: list[dict[str, object]],
    storage_height: float,
    vertical_clearance: float,
    *,
    enforce_top_inset_headroom: bool,
) -> list[float] | None:
    participants = [_mapping(member["participant"]) for member in members]
    heights = [_axis_base(participant, "z") for participant in participants]
    if enforce_top_inset_headroom and participants:
        heights[-1] = max(
            heights[-1],
            _bounded_safe_top_height(participants[-1], storage_height),
        )
    gaps = [
        _participant_pair_clearance(left, right, "z", vertical_clearance)
        for left, right in zip(participants, participants[1:])
    ]
    gap_total = sum(gaps)
    body_height_budget = storage_height - gap_total
    if body_height_budget < -_EPSILON or sum(heights) > body_height_budget + _EPSILON:
        return None
    expandable = [
        index
        for index, participant in enumerate(participants)
        if _axis_mode(participant, "z") != "fixed"
    ]
    extra = max(0.0, body_height_budget - sum(heights))
    if extra > _EPSILON and not expandable:
        return None
    targets = [
        _axis_target(participant, "z") or heights[index]
        for index, participant in enumerate(participants)
    ]
    weights = [_volume(_mapping(participant["minimum_local_mm"])) for participant in participants]
    _allocate(heights, expandable, extra, targets, weights)
    return heights


def _interval_stages(
    placements: list[dict[str, object]],
    storage_height: float,
    row_count: int,
) -> list[dict[str, object]]:
    boundaries = {0.0, _round(storage_height)}
    for placement in placements:
        origin = _mapping(placement["origin_mm"])
        size = _mapping(placement["world_size_mm"])
        boundaries.add(_round(float(origin["z"])))
        boundaries.add(_round(float(origin["z"]) + float(size["z"])))
    ordered = sorted(boundaries)
    stages: list[dict[str, object]] = []
    for index, (bottom, top) in enumerate(zip(ordered, ordered[1:])):
        if top - bottom <= _EPSILON:
            continue
        active = [
            placement
            for placement in placements
            if float(_mapping(placement["origin_mm"])["z"]) <= bottom + _EPSILON
            and float(_mapping(placement["origin_mm"])["z"])
            + float(_mapping(placement["world_size_mm"])["z"])
            >= top - _EPSILON
        ]
        starting = [
            placement
            for placement in active
            if isclose(float(_mapping(placement["origin_mm"])["z"]), bottom, abs_tol=0.001)
        ]
        if not starting:
            continue
        stage_index = len(stages)
        stage_id = f"interval-{stage_index + 1}"
        stages.append(
            {
                "id": stage_id,
                "index": stage_index,
                "origin_z_mm": _round(bottom),
                "height_mm": _round(top - bottom),
                "top_z_mm": _round(top),
                "body_ids": [str(item["id"]) for item in active],
                "body_count": len(active),
                "starting_body_ids": [str(item["id"]) for item in starting],
                "spanning_body_ids": [
                    str(item["id"]) for item in active if item not in starting
                ],
                "row_count": row_count if index == 0 else 0,
                "xy_status": "complete",
            }
        )
    for placement in placements:
        origin_z = float(_mapping(placement["origin_mm"])["z"])
        start = next(
            stage
            for stage in stages
            if isclose(float(stage["origin_z_mm"]), origin_z, abs_tol=0.001)
        )
        placement["stage_id"] = start["id"]
        placement["stage_index"] = start["index"]
    return stages


def _group_vertical_clearance(
    lower: list[dict[str, object]],
    upper: list[dict[str, object]],
    fallback: float,
) -> float:
    """Resolve a stage interface as the maximum of its pair requirements.

    A stage has one common Z origin.  The interface must therefore satisfy every
    potentially adjacent lower/upper pair, while preserving the pair rule:
    each pair uses max(left, right), and interface values are never summed.
    """

    return max(
        (
            _participant_pair_clearance(left, right, "z", fallback)
            for left in lower
            for right in upper
        ),
        default=0.0,
    )


def _stage_heights(
    groups: list[list[dict[str, object]]],
    storage_height: float,
    vertical_clearance: float,
    *,
    enforce_top_inset_headroom: bool,
) -> tuple[list[float], bool, list[float]] | None:
    heights: list[float] = []
    complete = True
    for group_index, group in enumerate(groups):
        bases = [_axis_base(item, "z") for item in group]
        stage_height = max(bases)
        if enforce_top_inset_headroom and group_index == len(groups) - 1:
            stage_height = max(
                stage_height,
                *(
                    _bounded_safe_top_height(item, storage_height)
                    for item in group
                ),
            )
        fixed = [base for item, base in zip(group, bases) if _axis_mode(item, "z") == "fixed"]
        if any(not isclose(value, stage_height, abs_tol=0.001) for value in fixed):
            complete = False
        heights.append(stage_height)
    gaps = [
        _group_vertical_clearance(lower, upper, vertical_clearance)
        for lower, upper in zip(groups, groups[1:])
    ]
    gap_total = sum(gaps)
    body_height_budget = storage_height - gap_total
    minimum_total = sum(heights)
    if body_height_budget < -_EPSILON or minimum_total > body_height_budget + _EPSILON:
        return None
    extra = max(0.0, body_height_budget - minimum_total)
    expandable = [
        index
        for index, group in enumerate(groups)
        if all(_axis_mode(item, "z") != "fixed" for item in group)
    ]
    if extra > _EPSILON and not expandable:
        complete = False
        return heights, complete, gaps
    targets = [
        max((_axis_target(item, "z") or heights[index]) for item in group)
        for index, group in enumerate(groups)
    ]
    weights = [sum(_volume(_mapping(item["minimum_local_mm"])) for item in group) for group in groups]
    _allocate(heights, expandable, extra, targets, weights)
    return heights, complete, gaps

def _best_xy_layout(
    group: list[dict[str, object]],
    box: dict[str, float],
    between_clearance: float,
    box_clearance: float,
    *,
    orientation_strategy: str,
    fill: bool,
    spatial_reference_height: float | None = None,
    top_inset_search_context: dict[str, object] | None = None,
    top_body_heights_by_id: dict[str, float] | None = None,
) -> tuple[dict[str, object] | None, int]:
    feasible: list[dict[str, object]] = []
    attempts = 0
    order_variants = (
        _constraint_layout_orders(group)
        if top_inset_search_context is not None
        else [list(group)]
    )
    for variant_index, ordered in enumerate(order_variants):
        for columns in range(1, len(ordered) + 1):
            rows = [
                ordered[index : index + columns]
                for index in range(0, len(ordered), columns)
            ]
            attempts += 1
            layout = _layout_rows(
                rows,
                box,
                between_clearance,
                box_clearance,
                orientation_strategy=orientation_strategy,
                fill=fill,
            )
            if layout is None:
                continue
            if variant_index:
                layout["layout_id"] = f"{layout['layout_id']}:v{variant_index}"
            if top_inset_search_context is not None:
                violation_count, shortfall = _layout_top_inset_penalty(
                    layout,
                    top_inset_search_context,
                    top_body_heights_by_id,
                )
                layout["_top_inset_violation_count"] = violation_count
                layout["_top_inset_shortfall_mm"] = shortfall
            feasible.append(layout)
    if not feasible:
        return None, attempts
    return min(
        feasible,
        key=lambda item: (
            int(item.get("_top_inset_violation_count", 0)),
            float(item.get("_top_inset_shortfall_mm", 0.0)),
            -(
                _layout_spatial_balance(item, spatial_reference_height)
                if orientation_strategy == "balanced"
                and spatial_reference_height is not None
                else float(item["local_score"])
            ),
            -float(item["local_score"]),
            int(item["row_count"]),
            int(item["rotation_count"]),
            str(item["layout_id"]),
        ),
    ), attempts


def _constraint_layout_orders(
    group: list[dict[str, object]],
) -> list[list[dict[str, object]]]:
    if len(group) <= 1:
        return [list(group)]
    inset_order = sorted(
        group,
        key=lambda item: (
            _layout_top_required_height(item),
            str(item["id"]),
        ),
    )
    recoverability_order = sorted(
        group,
        key=lambda item: (
            _layout_top_unrecoverable_height(item),
            str(item["id"]),
        ),
    )
    candidates = [
        list(group),
        recoverability_order,
        inset_order,
        list(reversed(group)),
        list(reversed(recoverability_order)),
        list(reversed(inset_order)),
    ]
    geometric_orders = [
        sorted(group, key=lambda item: (_axis_base(item, "x"), str(item["id"]))),
        sorted(group, key=lambda item: (_axis_base(item, "y"), str(item["id"]))),
        sorted(
            group,
            key=lambda item: (
                _axis_base(item, "x") * _axis_base(item, "y"),
                str(item["id"]),
            ),
        ),
    ]
    for geometric_order in geometric_orders:
        candidates.extend(
            [
                geometric_order,
                list(reversed(geometric_order)),
                _interleave_extremes(geometric_order),
            ]
        )
    risky = [
        item
        for item in recoverability_order
        if _layout_top_unrecoverable_height(item) > _EPSILON
    ]
    safe = [item for item in recoverability_order if item not in risky]
    if risky and safe:
        for safe_order in (
            sorted(safe, key=lambda item: (_axis_base(item, "x"), str(item["id"]))),
            sorted(safe, key=lambda item: (_axis_base(item, "y"), str(item["id"]))),
        ):
            for split in range(1, len(safe_order) + 1):
                candidates.append(
                    [*safe_order[:split], risky[0], *safe_order[split:], *risky[1:]]
                )
    for base_order in (recoverability_order, list(group), inset_order):
        for shift in range(1, len(base_order)):
            candidates.append([*base_order[shift:], *base_order[:shift]])
    candidates.append(_interleave_extremes(list(group)))

    result: list[list[dict[str, object]]] = []
    signatures: set[tuple[str, ...]] = set()
    for candidate in candidates:
        signature = tuple(str(item["id"]) for item in candidate)
        if signature in signatures:
            continue
        signatures.add(signature)
        result.append(candidate)
        if len(result) >= 32:
            break
    return result


def _layout_top_required_height(item: dict[str, object]) -> float:
    subject_payload = item.get("top_inset_layout_subject")
    subject = (
        _mapping(subject_payload["participant"])
        if isinstance(subject_payload, dict)
        else item
    )
    hint = subject.get("top_inset_search_hint_v1")
    if not isinstance(hint, dict):
        return _axis_base(subject, "z")
    return float(hint.get("required_safe_height_mm", _axis_base(subject, "z")))


def _layout_top_unrecoverable_height(item: dict[str, object]) -> float:
    """Estimate worst-case top headroom that this stack cannot redistribute."""

    subject_payload = item.get("top_inset_layout_subject")
    if not isinstance(subject_payload, dict):
        hint = item.get("top_inset_search_hint_v1")
        return (
            float(hint.get("headroom_deficit_mm", 0.0))
            if isinstance(hint, dict)
            else 0.0
        )
    subject = _mapping(subject_payload["participant"])
    required = _layout_top_required_height(item)
    body_height = float(subject_payload["body_height_mm"])
    transferable = _layout_top_height_transfer(item, subject)
    return _round(max(0.0, required - body_height - transferable))

def _layout_top_inset_penalty(
    layout: dict[str, object],
    context: dict[str, object],
    body_heights_by_id: dict[str, float] | None,
) -> tuple[int, float]:
    violations = 0
    shortfall = 0.0
    for placement in _mappings(layout["placements"]):
        layout_participant = _mapping(placement["participant"])
        subject_data = _layout_top_subject(
            layout_participant,
            placement,
            body_heights_by_id,
        )
        if subject_data is None:
            continue
        subject, body_height, rotated = subject_data
        required = _required_top_height_for_layout(
            subject,
            placement,
            rotated,
            context,
        )
        deficit = max(0.0, required - body_height)
        transferable = _layout_top_height_transfer(layout_participant, subject)
        unresolved = max(0.0, deficit - transferable)
        if unresolved <= _EPSILON:
            continue
        violations += 1
        shortfall += unresolved
    return violations, _round(shortfall)


def _layout_top_subject(
    layout_participant: dict[str, object],
    placement: dict[str, object],
    body_heights_by_id: dict[str, float] | None,
) -> tuple[dict[str, object], float, bool] | None:
    subject_payload = layout_participant.get("top_inset_layout_subject")
    if isinstance(subject_payload, dict):
        return (
            _mapping(subject_payload["participant"]),
            float(subject_payload["body_height_mm"]),
            bool(subject_payload["rotated_xy"]),
        )
    if body_heights_by_id is None:
        return None
    identifier = str(layout_participant["id"])
    if identifier not in body_heights_by_id:
        return None
    return (
        layout_participant,
        float(body_heights_by_id[identifier]),
        bool(placement["rotated_xy"]),
    )


def _required_top_height_for_layout(
    subject: dict[str, object],
    placement: dict[str, object],
    rotated: bool,
    context: dict[str, object],
) -> float:
    hint = subject.get("top_inset_search_hint_v1")
    if not isinstance(hint, dict):
        return _axis_base(subject, "z")
    floor = float(hint.get("floor_thickness_mm", 0.0))
    body_origin = _mapping(placement["origin_mm"])
    world_size = _mapping(placement["world_size_mm"])
    minimum = _mapping(subject["minimum_local_mm"])
    final_local = {
        "x": float(world_size["y"] if rotated else world_size["x"]),
        "y": float(world_size["x"] if rotated else world_size["y"]),
    }
    minimum_origin = {
        axis: max(0.0, final_local[axis] - float(minimum[axis])) / 2.0
        for axis in ("x", "y")
    }
    required = _axis_base(subject, "z")
    reservations = _mappings(context.get("reservations", []))
    for cavity in _mappings(hint.get("cavities", [])):
        cavity_origin = _mapping(cavity["local_origin_mm"])
        cavity_size = _mapping(cavity["inner_dimensions_mm"])
        local_x = minimum_origin["x"] + float(cavity_origin["x"])
        local_y = minimum_origin["y"] + float(cavity_origin["y"])
        if rotated:
            cavity_rect = {
                "x": float(body_origin["x"]) + final_local["y"]
                - local_y - float(cavity_size["y"]),
                "y": float(body_origin["y"]) + local_x,
                "width": float(cavity_size["y"]),
                "height": float(cavity_size["x"]),
            }
        else:
            cavity_rect = {
                "x": float(body_origin["x"]) + local_x,
                "y": float(body_origin["y"]) + local_y,
                "width": float(cavity_size["x"]),
                "height": float(cavity_size["y"]),
            }
        for reservation in reservations:
            cut_origin = _mapping(reservation["cut_origin_mm"])
            cut_size = _mapping(reservation["cut_size_mm"])
            reservation_rect = {
                "x": float(cut_origin["x"]),
                "y": float(cut_origin["y"]),
                "width": float(cut_size["x"]),
                "height": float(cut_size["y"]),
            }
            if _rectangles_intersect(cavity_rect, reservation_rect):
                required = max(
                    required,
                    float(cavity_size["z"])
                    + float(reservation["inset_depth_from_top_mm"])
                    + floor,
                )
    return required


def _layout_top_height_transfer(
    layout_participant: dict[str, object],
    subject: dict[str, object],
) -> float:
    if _axis_mode(subject, "z") == "fixed":
        return 0.0
    raw_heights = layout_participant.get("resolved_stack_heights")
    raw_members = layout_participant.get("stack_members")
    if not isinstance(raw_heights, list) or not isinstance(raw_members, list):
        return 0.0
    available = 0.0
    for raw_member, raw_height in zip(raw_members[:-1], raw_heights[:-1]):
        member = _mapping(_mapping(raw_member)["participant"])
        if _axis_mode(member, "z") == "fixed":
            continue
        available += max(0.0, float(raw_height) - _axis_base(member, "z"))
    return available


def _rebalance_stack_top_height_for_inset(
    descriptor: dict[str, object],
    item_layout: dict[str, object],
    heights: list[float],
    context: dict[str, object],
) -> list[float] | None:
    """Transfer unused lower-stack height to the top body when an inset needs it."""

    subject_payload = descriptor.get("top_inset_layout_subject")
    if not isinstance(subject_payload, dict):
        return heights
    subject = _mapping(subject_payload["participant"])
    required = _required_top_height_for_layout(
        subject,
        item_layout,
        bool(subject_payload["rotated_xy"]),
        context,
    )
    deficit = max(0.0, required - heights[-1])
    if deficit <= _EPSILON:
        return heights
    if _axis_mode(subject, "z") == "fixed":
        return None

    members = _mappings(descriptor["stack_members"])
    adjusted = list(heights)
    donors: list[tuple[float, int]] = []
    for index, member in enumerate(members[:-1]):
        participant = _mapping(member["participant"])
        if _axis_mode(participant, "z") == "fixed":
            continue
        surplus = max(0.0, adjusted[index] - _axis_base(participant, "z"))
        if surplus > _EPSILON:
            donors.append((surplus, index))

    remaining = deficit
    for surplus, index in sorted(donors, key=lambda item: (-item[0], item[1])):
        transferred = min(surplus, remaining)
        adjusted[index] -= transferred
        adjusted[-1] += transferred
        remaining -= transferred
        if remaining <= _EPSILON:
            break
    if remaining > _EPSILON:
        return None
    return [_round(value) for value in adjusted]

def _rectangles_intersect(
    left: dict[str, float],
    right: dict[str, float],
) -> bool:
    return (
        left["x"] < right["x"] + right["width"] - _EPSILON
        and right["x"] < left["x"] + left["width"] - _EPSILON
        and left["y"] < right["y"] + right["height"] - _EPSILON
        and right["y"] < left["y"] + left["height"] - _EPSILON
    )


def _layout_spatial_balance(
    layout: dict[str, object],
    stage_height: float,
) -> float:
    factors = {axis: [] for axis in _AXES}
    for placement in _mappings(layout["placements"]):
        participant = _mapping(placement["participant"])
        rotated = bool(placement["rotated_xy"])
        world_size = _mapping(placement["world_size_mm"])
        for axis in ("x", "y"):
            minimum = _axis_base(
                participant,
                _local_axis(axis, rotated),
            )
            factors[axis].append(float(world_size[axis]) / minimum)
        factors["z"].append(stage_height / _axis_base(participant, "z"))
    means = [sum(factors[axis]) / len(factors[axis]) for axis in _AXES]
    return 100.0 * min(means) / max(means)


def _participant_clearance(
    participant: dict[str, object],
    vector: str,
    axis: str,
    fallback: float,
) -> float:
    policy = participant.get("external_clearance_effective_v1")
    if not isinstance(policy, dict):
        return float(fallback)
    values = policy.get(vector)
    if not isinstance(values, dict):
        return float(fallback)
    value = values.get(axis)
    return float(fallback) if value is None else float(value)


def _participant_pair_clearance(
    left: dict[str, object],
    right: dict[str, object],
    axis: str,
    fallback: float,
) -> float:
    return max(
        _participant_clearance(left, "between_mm", axis, fallback),
        _participant_clearance(right, "between_mm", axis, fallback),
    )


def _placement_pair_clearance(
    left: dict[str, object],
    right: dict[str, object],
    axis: str,
    fallback: float,
) -> float:
    return max(
        _participant_clearance(left, "between_mm", axis, fallback),
        _participant_clearance(right, "between_mm", axis, fallback),
    )


def _external_clearance(
    item: dict[str, object],
    vector: str,
    axis: str,
    fallback: float,
) -> float:
    participant = _mapping(item["participant"])
    local_axis = axis
    if axis in {"x", "y"} and bool(item.get("rotated_xy", False)):
        local_axis = "y" if axis == "x" else "x"
    return _participant_clearance(participant, vector, local_axis, fallback)


def _pair_clearance(
    left: dict[str, object],
    right: dict[str, object],
    axis: str,
    fallback: float,
) -> float:
    return max(
        _external_clearance(left, "between_mm", axis, fallback),
        _external_clearance(right, "between_mm", axis, fallback),
    )


def _row_width(
    row: list[dict[str, object]], *,
    between_clearance: float, box_clearance: float,
) -> float:
    if not row:
        return 0.0
    widths = sum(float(item["base_world_mm"]["x"]) for item in row)
    gaps = sum(
        _pair_clearance(left, right, "x", between_clearance)
        for left, right in zip(row, row[1:])
    )
    return (
        _external_clearance(row[0], "box_per_side_xy_mm", "x", box_clearance)
        + widths + gaps
        + _external_clearance(row[-1], "box_per_side_xy_mm", "x", box_clearance)
    )


def _row_y_margin(row: list[dict[str, object]], fallback: float) -> float:
    return max(
        (_external_clearance(item, "box_per_side_xy_mm", "y", fallback) for item in row),
        default=float(fallback),
    )


def _row_between_y(
    left: list[dict[str, object]], right: list[dict[str, object]], fallback: float
) -> float:
    return max(
        [
            _external_clearance(item, "between_mm", "y", fallback)
            for item in [*left, *right]
        ],
        default=float(fallback),
    )


def _layout_rows(
    row_items: list[list[dict[str, object]]],
    box: dict[str, float],
    between_clearance: float,
    box_clearance: float,
    *,
    orientation_strategy: str,
    fill: bool,
) -> dict[str, object] | None:
    if box["x"] <= 0.0 or box["y"] <= 0.0:
        return None
    rows: list[list[dict[str, object]]] = []
    for values in row_items:
        oriented = _orient_row(
            values, box, between_clearance, box_clearance, orientation_strategy
        )
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

    front_margin = _row_y_margin(rows[0], box_clearance)
    back_margin = _row_y_margin(rows[-1], box_clearance)
    row_gaps = [
        _row_between_y(left, right, between_clearance)
        for left, right in zip(rows, rows[1:])
    ]
    minimum_y = front_margin + sum(row_heights) + sum(row_gaps) + back_margin
    if minimum_y > box["y"] + _EPSILON:
        return None
    if fill:
        extra_y = box["y"] - minimum_y
        expandable_rows = [
            index for index, row in enumerate(rows)
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
                or row_heights[index] for item in row
            ) for index, row in enumerate(rows)
        ]
        row_weights = [sum(_area(_mapping(item["participant"])["minimum_local_mm"]) for item in row) for row in rows]
        _allocate(row_heights, expandable_rows, extra_y, row_targets, row_weights)

    placements: list[dict[str, object]] = []
    residuals: list[dict[str, object]] = []
    cursor_y = front_margin
    rotations = 0
    for row_index, (row, row_height) in enumerate(zip(rows, row_heights)):
        widths = [float(item["base_world_mm"]["x"]) for item in row]
        left_margin = _external_clearance(row[0], "box_per_side_xy_mm", "x", box_clearance)
        right_margin = _external_clearance(row[-1], "box_per_side_xy_mm", "x", box_clearance)
        gaps = [
            _pair_clearance(left, right, "x", between_clearance)
            for left, right in zip(row, row[1:])
        ]
        occupied = left_margin + sum(widths) + sum(gaps) + right_margin
        if occupied > box["x"] + _EPSILON:
            return None
        if fill:
            extra_x = box["x"] - occupied
            expandable = [
                index for index, item in enumerate(row)
                if _axis_mode(_mapping(item["participant"]), "x", rotated=bool(item["rotated_xy"])) != "fixed"
            ]
            if extra_x > _EPSILON and not expandable:
                return None
            targets = [
                _axis_target(_mapping(item["participant"]), "x", rotated=bool(item["rotated_xy"]))
                or widths[index] for index, item in enumerate(row)
            ]
            weights = [_area(_mapping(item["participant"])["minimum_local_mm"]) for item in row]
            _allocate(widths, expandable, extra_x, targets, weights)
        cursor_x = left_margin
        for item_index, (item, width) in enumerate(zip(row, widths)):
            body_height = row_height if fill else float(item["base_world_mm"]["y"])
            placements.append({
                "participant": item["participant"],
                "origin_mm": {"x": _round(cursor_x), "y": _round(cursor_y)},
                "world_size_mm": {"x": _round(width), "y": _round(body_height)},
                "rotated_xy": bool(item["rotated_xy"]),
            })
            if not fill and body_height < row_height - _EPSILON:
                residuals.append({
                    "id": f"r{row_index}-i{item_index}-above", "x": _round(cursor_x),
                    "y": _round(cursor_y + body_height), "width": _round(width),
                    "height": _round(row_height - body_height), "kind": "row_height_residual",
                })
            cursor_x += width + (gaps[item_index] if item_index < len(gaps) else 0.0)
            rotations += int(bool(item["rotated_xy"]))
        used_x = cursor_x
        if not fill and used_x < box["x"] - right_margin - _EPSILON:
            residuals.append({
                "id": f"r{row_index}-right", "x": _round(used_x), "y": _round(cursor_y),
                "width": _round(box["x"] - right_margin - used_x),
                "height": _round(row_height), "kind": "row_right_residual",
            })
        cursor_y += row_height + (row_gaps[row_index] if row_index < len(row_gaps) else 0.0)
    used_y = cursor_y
    if not fill and used_y < box["y"] - back_margin - _EPSILON:
        residuals.append({
            "id": "back", "x": _round(0.0), "y": _round(used_y),
            "width": _round(box["x"]), "height": _round(box["y"] - back_margin - used_y),
            "kind": "stage_back_residual",
        })
    target_error = sum(
        _xy_target_error(_mapping(item["participant"]), _mapping(item["world_size_mm"]), rotated=bool(item["rotated_xy"]))
        for item in placements
    )
    local_score = 1000.0 - len(rows) * 20.0 - rotations * 4.0 - target_error * 25.0
    return {
        "layout_id": f"{len(row_items[0]) if row_items else 0}c:{orientation_strategy}:{'full' if fill else 'partial'}",
        "complete": fill, "row_count": len(rows), "rotation_count": rotations,
        "placements": placements, "residual_rectangles": residuals, "local_score": _round(local_score),
    }


def _orient_row(
    values: list[dict[str, object]],
    box: dict[str, float],
    between_clearance: float,
    box_clearance: float,
    strategy: str,
) -> list[dict[str, object]] | None:
    option_sets = [_orientation_options(value) for value in values]
    combination_count = 1
    for options in option_sets:
        combination_count *= len(options)
    combinations = product(*option_sets) if combination_count <= MAX_ORIENTATION_COMBINATIONS else [tuple(_greedy_orientation(value, strategy) for value in values)]
    feasible: list[tuple[tuple[float, float, int], list[dict[str, object]]]] = []
    for combination_tuple in combinations:
        combination = [dict(item) for item in combination_tuple]
        width = _row_width(combination, between_clearance=between_clearance, box_clearance=box_clearance)
        height = max(float(item["base_world_mm"]["y"]) for item in combination)
        if width > box["x"] + _EPSILON or height > box["y"] + _EPSILON:
            continue
        rotations = sum(int(bool(item["rotated_xy"])) for item in combination)
        if strategy == "width": key = (width, height, rotations)
        elif strategy == "height": key = (height, width, rotations)
        else: key = (width / box["x"] + height / box["y"], rotations, width)
        feasible.append((key, combination))
    return min(feasible, key=lambda item: item[0])[1] if feasible else None


def _orientation_options(value: dict[str, object]) -> list[dict[str, object]]:
    base = {axis: _axis_base(value, axis) for axis in _AXES}
    options = [_oriented(value, base, False)]
    if (
        bool(value.get("allow_xy_rotation", True))
        and not isclose(base["x"], base["y"], abs_tol=_EPSILON)
    ):
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
    placements: list[dict[str, object]],
    stages: list[dict[str, object]],
    vertical_clearance: float,
) -> dict[str, object]:
    supports: list[dict[str, object]] = []
    minimum_ratio = 1.0
    for placement in placements:
        origin = _mapping(placement["origin_mm"])
        footprint = _area(_mapping(placement["world_size_mm"]))
        if isclose(float(origin["z"]), 0.0, abs_tol=0.001):
            ratio = 1.0
            supporting_ids = ["box-floor"]
        else:
            size = _mapping(placement["world_size_mm"])
            area = 0.0
            supporting_ids: list[str] = []
            for lower in placements:
                if lower is placement:
                    continue
                lower_origin = _mapping(lower["origin_mm"])
                lower_size = _mapping(lower["world_size_mm"])
                actual_gap = float(origin["z"]) - (
                    float(lower_origin["z"]) + float(lower_size["z"])
                )
                required_gap = _placement_pair_clearance(
                    lower, placement, "z", vertical_clearance
                )
                if actual_gap + _EPSILON < required_gap:
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
                "vertical_gap_mm": (
                    0.0
                    if not supporting_ids or supporting_ids == ["box-floor"]
                    else _round(
                        min(
                            float(origin["z"])
                            - (
                                float(_mapping(lower["origin_mm"])["z"])
                                + float(_mapping(lower["world_size_mm"])["z"])
                            )
                            for lower in placements
                            if str(lower["id"]) in supporting_ids
                        )
                    )
                ),
            }
        )
    unsupported = [item for item in supports if not item["supported"]]
    return {
        "status": "unsupported" if unsupported else "supported",
        "minimum_coverage_ratio": _round(minimum_ratio),
        "minimum_required_ratio": MIN_SUPPORT_RATIO,
        "vertical_gap_mm": _round(vertical_clearance),
        "supports": supports,
        "unsupported_body_ids": [str(item["placement_id"]) for item in unsupported],
    }


def _removal_sequence(placements: list[dict[str, object]]) -> list[dict[str, object]]:
    ordered = sorted(
        placements,
        key=lambda item: (
            -(
                float(_mapping(item["origin_mm"])["z"])
                + float(_mapping(item["world_size_mm"])["z"])
            ),
            -float(_mapping(item["origin_mm"])["z"]),
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
    conservation_tolerance = max(0.01, storage_volume * 1e-6)
    return {
        "storage_volume_mm3": _round(storage_volume),
        "requested_body_volume_mm3": _round(body_volume),
        "residual_volume_mm3": _round(residual),
        "technical_clearance_volume_mm3": _round(technical),
        "classified_volume_mm3": _round(classified),
        "conserved": isclose(classified, storage_volume, abs_tol=conservation_tolerance),
        "conservation_tolerance_mm3": _round(conservation_tolerance),
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
    hybrid_interval_penalty = 4.0 if any(
        "spanning_body_ids" in stage for stage in stages
    ) else 0.0
    simplicity = max(
        0.0,
        100.0
        - max(0, len(stages) - 1) * 12.0
        - rows * 2.0
        - rotations * 2.0
        - hybrid_interval_penalty,
    )
    target_errors: list[float] = []
    surplus_ratios: list[float] = []
    expansion_factors = {axis: [] for axis in _AXES}
    for placement in placements:
        contract = _mapping(placement["dimension_contract"])
        for axis in _AXES:
            value = _mapping(contract["axes"])[axis]
            if value["mode"] == "target" and value["target_mm"] is not None:
                target_errors.append(abs(float(value["calculated_mm"]) - float(value["target_mm"])) / float(value["target_mm"]))
            minimum = float(value["minimum_mm"])
            calculated = float(value["calculated_mm"])
            surplus_ratios.append(max(0.0, calculated - minimum) / minimum)
            expansion_factors[axis].append(calculated / minimum)
    targets = max(0.0, 100.0 - 100.0 * (sum(target_errors) / len(target_errors) if target_errors else 0.0))
    mean_surplus = sum(surplus_ratios) / len(surplus_ratios) if surplus_ratios else 0.0
    spread = max(surplus_ratios, default=0.0) - min(surplus_ratios, default=0.0)
    material = max(0.0, 100.0 - 25.0 * mean_surplus - 15.0 * spread)
    support_score = 100.0 * float(support["minimum_coverage_ratio"])
    mean_expansion = [
        sum(expansion_factors[axis]) / len(expansion_factors[axis])
        for axis in _AXES
        if expansion_factors[axis]
    ]
    axis_balance = (
        100.0 * min(mean_expansion) / max(mean_expansion)
        if mean_expansion
        else 100.0
    )
    stage_loads = {str(stage["id"]): 0.0 for stage in stages}
    for placement in placements:
        axes = _mapping(_mapping(placement["dimension_contract"])["axes"])
        minimum_area = float(_mapping(axes["x"])["minimum_mm"]) * float(
            _mapping(axes["y"])["minimum_mm"]
        )
        stage_loads[str(placement["stage_id"])] += minimum_area
    positive_loads = [value for value in stage_loads.values() if value > _EPSILON]
    stage_load_balance = (
        100.0 * min(positive_loads) / max(positive_loads)
        if positive_loads
        else 100.0
    )
    spatial = 0.70 * axis_balance + 0.30 * stage_load_balance
    weights = _SCORE_WEIGHTS[preference]
    total = sum(
        value * weights[key]
        for key, value in {
            "simplicity": simplicity,
            "targets": targets,
            "material": material,
            "support": support_score,
            "spatial": spatial,
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
        "spatial_balance": _round(spatial),
        "stage_load_balance": _round(stage_load_balance),
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


def _diversified_order_key(
    item: dict[str, object],
    seed: int,
) -> tuple[bytes, str]:
    semantic_id = str(
        item.get("container_group_id")
        or item.get("requested_complement_id")
        or item["id"]
    )
    return (
        hashlib.sha256(f"{seed}:{semantic_id}".encode("utf-8")).digest(),
        str(item["id"]),
    )


def _orders(
    values: list[dict[str, object]],
    *,
    diversified_order_seed: int | None = None,
    structured_order_strategy: str | None = None,
) -> list[tuple[str, list[dict[str, object]]]]:
    if structured_order_strategy is not None:
        structured = _structured_order(values, structured_order_strategy)
        return [(f"structured_{structured_order_strategy}", structured)]
    if diversified_order_seed is not None:
        seed = int(diversified_order_seed)
        diversified = sorted(
            values,
            key=lambda item: _diversified_order_key(item, seed),
        )
        return [(f"diversified_{seed}", diversified)]

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


def _structured_order(
    values: list[dict[str, object]],
    strategy: str,
) -> list[dict[str, object]]:
    """Build one deterministic O(n log n) order for a directed retry."""

    if strategy in {"top_inset_headroom_asc", "top_inset_safe_top_asc"}:
        return sorted(values, key=_top_inset_headroom_deficit)
    if strategy == "top_inset_headroom_asc_reverse":
        return sorted(reversed(values), key=_top_inset_headroom_deficit)
    if strategy == "long_side_desc":
        return sorted(
            values,
            key=lambda item: (
                -max(_axis_base(item, "x"), _axis_base(item, "y")),
                -min(_axis_base(item, "x"), _axis_base(item, "y")),
                str(item["id"]),
            ),
        )
    if strategy == "short_side_desc":
        return sorted(
            values,
            key=lambda item: (
                -min(_axis_base(item, "x"), _axis_base(item, "y")),
                -max(_axis_base(item, "x"), _axis_base(item, "y")),
                str(item["id"]),
            ),
        )
    if strategy == "area_interleave":
        ordered = sorted(
            values,
            key=lambda item: (
                -_area(_mapping(item["minimum_local_mm"])),
                str(item["id"]),
            ),
        )
        return _interleave_extremes(ordered)
    if strategy == "height_interleave":
        ordered = sorted(
            values,
            key=lambda item: (-_axis_base(item, "z"), str(item["id"])),
        )
        return _interleave_extremes(ordered)
    raise VolumetricStageSolverError(
        f"Unknown structured order strategy: {strategy!r}."
    )


def _bounded_safe_top_height(
    item: dict[str, object],
    storage_height: float,
) -> float:
    base = _axis_base(item, "z")
    hint = item.get("top_inset_search_hint_v1")
    if not isinstance(hint, dict):
        return base
    required = max(base, float(hint.get("required_safe_height_mm", base)))
    if required > storage_height + _EPSILON:
        return base
    return required


def _top_inset_headroom_deficit(item: dict[str, object]) -> float:
    hint = item.get("top_inset_search_hint_v1")
    if not isinstance(hint, dict):
        return 0.0
    return max(0.0, float(hint.get("headroom_deficit_mm", 0.0)))


def _interleave_extremes(
    ordered: list[dict[str, object]],
) -> list[dict[str, object]]:
    result: list[dict[str, object]] = []
    left = 0
    right = len(ordered) - 1
    while left <= right:
        result.append(ordered[left])
        left += 1
        if left <= right:
            result.append(ordered[right])
            right -= 1
    return result


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


def _candidate_sort_key(
    candidate: dict[str, object],
    preference: str,
) -> tuple[object, ...]:
    origin = _mapping(candidate["search_origin"])
    search_family_rank = int("stack_partition_index" in origin)
    common = (
        int(origin.get("top_inset_search_violation_count", 0)),
        float(origin.get("top_inset_search_shortfall_mm", 0.0)),
        candidate["solution_status"] != SOLUTION_COMPLETE,
        -float(candidate["quality_score"]),
        int(candidate["stage_count"]),
        search_family_rank,
        str(candidate["candidate_id"]),
    )
    if preference == "balanced":
        return common
    return (
        int(origin.get("top_inset_search_violation_count", 0)),
        float(origin.get("top_inset_search_shortfall_mm", 0.0)),
        candidate["solution_status"] != SOLUTION_COMPLETE,
        search_family_rank,
        -float(candidate["quality_score"]),
        int(candidate["stage_count"]),
        str(candidate["candidate_id"]),
    )


def _candidate_signature(candidate: dict[str, object]) -> str:
    return "|".join(
        f"{item['id']}@{item['origin_mm']}:{item['world_size_mm']}:{item['rotation_deg_z']}"
        for item in _mappings(candidate["placements"])
    )


def _empty_result(
    budgets: dict[str, int],
    message: str,
    between_clearance: float,
    box_clearance: float,
    vertical_clearance: float,
) -> dict[str, object]:
    return {
        "schema_version": VOLUMETRIC_STAGE_SOLVER_SCHEMA_V1,
        "status": SOLUTION_IMPOSSIBLE,
        "candidates": [],
        "best_candidate": None,
        "budgets": budgets,
        "clearances_mm": {"xy": _round(between_clearance), "z": _round(vertical_clearance), "box_xy": _round(box_clearance), "between_xy": _round(between_clearance), "between_z": _round(vertical_clearance)},
        "search": {
            "deterministic": True,
            "globally_optimal": False,
            "truncated": False,
            "ordering_count": 0,
            "groupings_evaluated": 0,
            "adaptive_partitions_evaluated": 0,
            "stack_partitions_evaluated": 0,
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
