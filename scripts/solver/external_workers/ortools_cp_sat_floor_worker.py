"""Worker isolé OR-Tools CP-SAT pour le modèle sol 2D P64-L07."""

from __future__ import annotations

import sys
from time import perf_counter

from _floor_worker_protocol import read_problem, write_result
from ortools.sat.python import cp_model


def main(input_path: str, output_path: str) -> None:
    problem = read_problem(input_path)
    started = perf_counter()
    model = cp_model.CpModel()
    xs = []
    ys = []
    rotations = []
    widths = []
    heights = []
    for index, item in enumerate(problem.items):
        x = model.new_int_var(0, problem.bin_width, f"x_{index}")
        y = model.new_int_var(0, problem.bin_height, f"y_{index}")
        if problem.rotation_allowed and item.width != item.height:
            rotation = model.new_bool_var(f"r_{index}")
            width = item.width + (item.height - item.width) * rotation
            height = item.height + (item.width - item.height) * rotation
        else:
            rotation = 0
            width = item.width
            height = item.height
        model.add(x + width <= problem.bin_width)
        model.add(y + height <= problem.bin_height)
        xs.append(x)
        ys.append(y)
        rotations.append(rotation)
        widths.append(width)
        heights.append(height)
    for first in range(len(problem.items)):
        for second in range(first + 1, len(problem.items)):
            separated = [
                model.new_bool_var(f"sep_{first}_{second}_{axis}")
                for axis in range(4)
            ]
            model.add(xs[first] + widths[first] <= xs[second]).only_enforce_if(
                separated[0]
            )
            model.add(xs[second] + widths[second] <= xs[first]).only_enforce_if(
                separated[1]
            )
            model.add(ys[first] + heights[first] <= ys[second]).only_enforce_if(
                separated[2]
            )
            model.add(ys[second] + heights[second] <= ys[first]).only_enforce_if(
                separated[3]
            )
            model.add_bool_or(separated)
    model.minimize(sum(xs) + sum(ys))
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = problem.time_limit_ms / 1000.0
    solver.parameters.num_search_workers = problem.threads
    solver.parameters.random_seed = problem.seed
    status = solver.solve(model)
    solve_ms = (perf_counter() - started) * 1000.0
    label = solver.status_name(status)
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        placements = []
        for index, item in enumerate(problem.items):
            rotation = (
                int(solver.value(rotations[index]))
                if not isinstance(rotations[index], int)
                else 0
            )
            placements.append(
                (
                    item.item_id,
                    int(solver.value(xs[index])),
                    int(solver.value(ys[index])),
                    90 if rotation else 0,
                )
            )
        normalized = "feasible"
    elif status == cp_model.INFEASIBLE:
        placements = []
        normalized = "infeasible"
    else:
        placements = []
        normalized = "unknown"
    write_result(
        output_path,
        status=normalized,
        solve_ms=solve_ms,
        engine_status=label,
        placements=placements,
        metrics=(
            ("branches", solver.num_branches),
            ("conflicts", solver.num_conflicts),
            ("wall_time_seconds", solver.wall_time),
        ),
    )


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
