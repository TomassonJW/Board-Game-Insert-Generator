"""Worker isolé SCIP/PySCIPOpt pour le modèle sol 2D P64-L07."""

from __future__ import annotations

import sys
from time import perf_counter

from pyscipopt import Model, quicksum

from _floor_worker_protocol import read_problem, write_result


def main(input_path: str, output_path: str) -> None:
    problem = read_problem(input_path)
    started = perf_counter()
    model = Model("p64_l07_floor")
    model.hideOutput()
    model.setParam("limits/time", problem.time_limit_ms / 1000.0)
    model.setParam("parallel/maxnthreads", problem.threads)
    model.setParam("randomization/randomseedshift", problem.seed)
    xs = []
    ys = []
    rotations = []
    widths = []
    heights = []
    for index, item in enumerate(problem.items):
        x = model.addVar(f"x_{index}", vtype="I", lb=0, ub=problem.bin_width)
        y = model.addVar(f"y_{index}", vtype="I", lb=0, ub=problem.bin_height)
        if problem.rotation_allowed and item.width != item.height:
            rotation = model.addVar(f"r_{index}", vtype="B")
            width = item.width + (item.height - item.width) * rotation
            height = item.height + (item.width - item.height) * rotation
        else:
            rotation = None
            width = item.width
            height = item.height
        model.addCons(x + width <= problem.bin_width)
        model.addCons(y + height <= problem.bin_height)
        xs.append(x)
        ys.append(y)
        rotations.append(rotation)
        widths.append(width)
        heights.append(height)
    big_m = max(problem.bin_width, problem.bin_height)
    for first in range(len(problem.items)):
        for second in range(first + 1, len(problem.items)):
            separated = [
                model.addVar(f"sep_{first}_{second}_{axis}", vtype="B")
                for axis in range(4)
            ]
            model.addCons(
                xs[first] + widths[first]
                <= xs[second] + big_m * (1 - separated[0])
            )
            model.addCons(
                xs[second] + widths[second]
                <= xs[first] + big_m * (1 - separated[1])
            )
            model.addCons(
                ys[first] + heights[first]
                <= ys[second] + big_m * (1 - separated[2])
            )
            model.addCons(
                ys[second] + heights[second]
                <= ys[first] + big_m * (1 - separated[3])
            )
            model.addCons(quicksum(separated) >= 1)
    model.setObjective(quicksum(xs) + quicksum(ys), "minimize")
    model.optimize()
    status = str(model.getStatus())
    solve_ms = (perf_counter() - started) * 1000.0
    if model.getNSols() > 0:
        solution = model.getBestSol()
        placements = []
        for index, item in enumerate(problem.items):
            rotation = (
                int(round(model.getSolVal(solution, rotations[index])))
                if rotations[index] is not None
                else 0
            )
            placements.append(
                (
                    item.item_id,
                    int(round(model.getSolVal(solution, xs[index]))),
                    int(round(model.getSolVal(solution, ys[index]))),
                    90 if rotation else 0,
                )
            )
        normalized = "feasible"
    elif status == "infeasible":
        placements = []
        normalized = "infeasible"
    else:
        placements = []
        normalized = "unknown"
    write_result(
        output_path,
        status=normalized,
        solve_ms=solve_ms,
        engine_status=status,
        placements=placements,
        metrics=(
            ("nodes", model.getNNodes()),
            ("solutions", model.getNSols()),
        ),
    )


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
