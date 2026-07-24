"""Worker isole de la baseline BGIG courante pour P64-L08F."""

from __future__ import annotations

import os
import sys

from board_game_insert_generator.free_3d_beam_solver import (
    BEAM_SEARCH_INTERNAL_VARIANTS,
    solve_free_3d_beam,
)
from board_game_insert_generator.free_3d_greedy_solver import EmptySpace
from board_game_insert_generator.incremental_project_state import canonical_digest
from board_game_insert_generator.solver_contract import SolverBudget

from _real_3d_worker_common import load_input, timer, write_output


def main(input_path: str, output_path: str) -> None:
    payload = load_input(input_path)
    problem = payload["problem"]

    participants = [_participant(value) for value in problem["participants"]]
    profile = os.environ.get("BGIG_REAL3D_PROFILE", "balanced")
    limits = _beam_limits(payload["limits"], profile)
    budget = SolverBudget(
        family_id="free_3d_beam",
        effort_profile=f"p64_l08f_{profile}",
        limits=limits,
    )
    _, elapsed = timer()
    execution = solve_free_3d_beam(
        participants,
        {
            "x": float(problem["world_mm"][0]),
            "y": float(problem["world_mm"][1]),
            "z": float(problem["world_mm"][2]),
        },
        float(problem["world_mm"][2]),
        0.0,
        box_perimeter_xy_mm=0.0,
        between_bodies_z_mm=0.0,
        budget=budget,
        forbidden_spaces=_forbidden_spaces(problem),
        search_variant=BEAM_SEARCH_INTERNAL_VARIANTS,
    )
    placements = []
    if execution.solutions:
        selected = execution.solutions[0]
        source = {str(value["participant_id"]): value for value in problem["participants"]}
        for placement in selected.placements:
            participant = source[placement.participant_id]
            variant_id = getattr(placement, "container_variant_id", "") or str(
                participant["variants"][0]["variant_id"]
            )

            placements.append(
                {
                    "participant_id": placement.participant_id,
                    "x": _integer(placement.origin_mm[0]),
                    "y": _integer(placement.origin_mm[1]),
                    "z": _integer(placement.origin_mm[2]),
                    "size": [_integer(value) for value in placement.world_size_mm],
                    "orientation": "yxz" if placement.rotation_deg_z == 90 else "xyz",
                    "selected_variant_id": variant_id,
                    "assigned_content_count": participant["assigned_content_count"],
                    "support_ids": list(placement.supporting_ids),
                    "removal_rank": int(problem["world_mm"][2]) - _integer(placement.origin_mm[2]),
                }
            )
    status = "feasible" if placements else "unknown"
    write_output(
        output_path,
        {
            "candidate_id": "current_bgig",
            "input_digest": payload["input_digest"],
            "status": status,
            "proof_status": "incumbent" if placements else "bounded",
            "engine_status": execution.status,
            "engine_stop_reason": execution.stop_reason,
            "solve_milliseconds": elapsed(),
            "objective_value": None,
            "best_objective_bound": None,
            "telemetry": {
                "search_states": execution.telemetry.search_states,
                "placement_trials": execution.telemetry.placement_trials,
                "admitted_complete_solutions": execution.telemetry.admitted_complete_solutions,
                "budget_exhausted": execution.telemetry.budget_exhausted,
                "timed_out": execution.telemetry.timed_out,
            },
            "placements": placements,
        },
    )


def _participant(value: dict[str, object]) -> dict[str, object]:
    first = value["variants"][0]
    options = []
    for index, variant in enumerate(value["variants"]):
        size = variant["size"]
        option = {
            "variant_id": str(variant["variant_id"]),
            "geometry_digest": canonical_digest(
                {
                    "participant_id": value["participant_id"],
                    "variant": variant,
                }
            ),
            "canonical": index == 0,
            "frontier_index": index,
            "minimum_outer_envelope_mm": {
                "x": float(size[0]),
                "y": float(size[1]),
                "z": float(size[2]),
            },
        }
        options.append(option)
    return {
        "id": str(value["participant_id"]),
        "role": "container",
        "name": str(value["participant_id"]),
        "minimum_local_mm": {
            "x": float(first["size"][0]),
            "y": float(first["size"][1]),
            "z": float(first["size"][2]),
        },
        "dimension_modes": {"x": "auto", "y": "auto", "z": "auto"},
        "target_local_mm": {"x": None, "y": None, "z": None},
        "container_internal_variant_options_v1": options,
    }


def _beam_limits(limits: dict[str, object], profile: str) -> dict[str, int]:
    if profile == "wide":
        beam_width, branches, states = 64, 24, 16_000
    else:
        beam_width, branches, states = 24, 12, 8_000
    return {
        "beam_width": beam_width,
        "max_complete_candidates": 8,
        "max_elapsed_ms": max(1, int(float(limits["wall_seconds"]) * 900.0)),
        "max_empty_spaces": 512,
        "max_extreme_points": 1024,
        "max_options_per_participant": 256,
        "max_participant_branches": branches,
        "max_placement_trials": 1_000_000,
        "max_search_states": states,
        "max_variant_options_per_expansion": 8,
    }


def _forbidden_spaces(problem: dict[str, object]) -> tuple[EmptySpace, ...]:
    world = problem["world_mm"]
    result = [
        EmptySpace(
            (float(item["x"]), float(item["y"]), float(item["z"])),
            tuple(float(value) for value in item["size"]),
        )
        for item in problem.get("reservation_volumes", [])
    ]
    if "disjoint_regions" not in problem.get("active_constraints", []):
        return tuple(result)
    cell = problem["fragment_cell_mm"]
    stride_x = int(cell[0]) + int(problem["fragment_gap_mm"])
    stride_y = int(cell[1]) + int(problem["fragment_gap_mm"])
    x_starts = list(range(2, int(world[0]), stride_x))
    y_starts = list(range(2, int(world[1]), stride_y))
    x_forbidden = _complement_intervals(
        int(world[0]), [(value, min(int(world[0]), value + int(cell[0]))) for value in x_starts]
    )
    y_forbidden = _complement_intervals(
        int(world[1]), [(value, min(int(world[1]), value + int(cell[1]))) for value in y_starts]
    )
    result.extend(
        EmptySpace(
            (float(start), 0.0, 0.0),
            (float(end - start), float(world[1]), float(world[2])),
        )
        for start, end in x_forbidden
        if end > start
    )
    result.extend(
        EmptySpace(
            (0.0, float(start), 0.0),
            (float(world[0]), float(end - start), float(world[2])),
        )
        for start, end in y_forbidden
        if end > start
    )
    return tuple(result)


def _complement_intervals(limit: int, allowed: list[tuple[int, int]]) -> list[tuple[int, int]]:
    result = []
    cursor = 0
    for start, end in sorted(allowed):
        if start > cursor:
            result.append((cursor, start))
        cursor = max(cursor, end)
    if cursor < limit:
        result.append((cursor, limit))
    return result


def _integer(value: float) -> int:
    rounded = int(round(float(value)))
    if abs(float(value) - rounded) > 0.0001:
        raise RuntimeError("BGIG baseline produced a non-integer benchmark coordinate.")
    return rounded


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
