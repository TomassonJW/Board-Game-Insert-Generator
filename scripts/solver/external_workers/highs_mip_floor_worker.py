"""Worker isolé HiGHS pour le modèle sol 2D P64-L07."""

from __future__ import annotations

import sys
from time import perf_counter

import highspy

from _floor_worker_protocol import read_problem, write_result


def main(input_path: str, output_path: str) -> None:
    problem = read_problem(input_path)
    started = perf_counter()
    model = highspy.Highs()
    model.setOptionValue("output_flag", False)
    model.setOptionValue("time_limit", problem.time_limit_ms / 1000.0)
    model.setOptionValue("threads", problem.threads)
    model.setOptionValue("random_seed", problem.seed)
    integer = highspy.HighsVarType.kInteger
    xs = []
    ys = []
    rotations = []
    widths = []
    heights = []
    for index, item in enumerate(problem.items):
        x = model.addVariable(
            lb=0, ub=problem.bin_width, type=integer, name=f"x_{index}"
        )
        y = model.addVariable(
            lb=0, ub=problem.bin_height, type=integer, name=f"y_{index}"
        )
        if problem.rotation_allowed and item.width != item.height:
            rotation = model.addVariable(
                lb=0, ub=1, type=integer, name=f"r_{index}"
            )
            width = item.width + (item.height - item.width) * rotation
            height = item.height + (item.width - item.height) * rotation
        else:
            rotation = None
            width = item.width
            height = item.height
        model.addConstr(x + width <= problem.bin_width)
        model.addConstr(y + height <= problem.bin_height)
        xs.append(x)
        ys.append(y)
        rotations.append(rotation)
        widths.append(width)
        heights.append(height)
    big_m = max(problem.bin_width, problem.bin_height)
    for first in range(len(problem.items)):
        for second in range(first + 1, len(problem.items)):
            separated = [
                model.addVariable(
                    lb=0,
                    ub=1,
                    type=integer,
                    name=f"sep_{first}_{second}_{axis}",
                )
                for axis in range(4)
            ]
            model.addConstr(
                xs[first] + widths[first]
                <= xs[second] + big_m * (1 - separated[0])
            )
            model.addConstr(
                xs[second] + widths[second]
                <= xs[first] + big_m * (1 - separated[1])
            )
            model.addConstr(
                ys[first] + heights[first]
                <= ys[second] + big_m * (1 - separated[2])
            )
            model.addConstr(
                ys[second] + heights[second]
                <= ys[first] + big_m * (1 - separated[3])
            )
            model.addConstr(sum(separated) >= 1)
    model.minimize(sum(xs) + sum(ys))
    status = model.getModelStatus()
    solve_ms = (perf_counter() - started) * 1000.0
    label = str(status).split(".")[-1]
    if status == highspy.HighsModelStatus.kOptimal:
        placements = []
        for index, item in enumerate(problem.items):
            rotation = (
                int(round(model.val(rotations[index])))
                if rotations[index] is not None
                else 0
            )
            placements.append(
                (
                    item.item_id,
                    int(round(model.val(xs[index]))),
                    int(round(model.val(ys[index]))),
                    90 if rotation else 0,
                )
            )
        normalized = "feasible"
    elif status == highspy.HighsModelStatus.kInfeasible:
        placements = []
        normalized = "infeasible"
    else:
        solution = model.getSolution()
        if getattr(solution, "value_valid", False):
            placements = []
            for index, item in enumerate(problem.items):
                rotation = (
                    int(round(model.val(rotations[index])))
                    if rotations[index] is not None
                    else 0
                )
                placements.append(
                    (
                        item.item_id,
                        int(round(model.val(xs[index]))),
                        int(round(model.val(ys[index]))),
                        90 if rotation else 0,
                    )
                )
            normalized = "feasible"
        else:
            placements = []
            normalized = "unknown"
    info = model.getInfo()
    write_result(
        output_path,
        status=normalized,
        solve_ms=solve_ms,
        engine_status=label,
        placements=placements,
        metrics=(
            ("mip_node_count", getattr(info, "mip_node_count", -1)),
            ("mip_gap", getattr(info, "mip_gap", -1)),
        ),
    )


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
