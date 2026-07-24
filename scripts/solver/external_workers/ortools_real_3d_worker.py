"""Worker OR-Tools CP-SAT pour le modele BGIG 3D P64-L08E."""

from __future__ import annotations

import sys

from ortools.sat.python import cp_model

from _real_3d_worker_common import choices, load_input, timer, write_output


def main(input_path: str, output_path: str) -> None:
    payload = load_input(input_path)
    problem = payload["problem"]
    limits = payload["limits"]
    participants = problem["participants"]
    world = problem["world_mm"]
    model = cp_model.CpModel()
    variables = []
    for index, participant in enumerate(participants):
        options = choices(participant)
        choice = model.new_int_var(0, len(options) - 1, f"choice_{index}")
        widths = [value["size"][0] for value in options]
        depths = [value["size"][1] for value in options]
        heights = [value["size"][2] for value in options]
        areas = [value["size"][0] * value["size"][1] for value in options]
        width = model.new_int_var(min(widths), max(widths), f"w_{index}")
        depth = model.new_int_var(min(depths), max(depths), f"d_{index}")
        height = model.new_int_var(min(heights), max(heights), f"h_{index}")
        area = model.new_int_var(min(areas), max(areas), f"area_{index}")
        model.add_element(choice, widths, width)
        model.add_element(choice, depths, depth)
        model.add_element(choice, heights, height)
        model.add_element(choice, areas, area)
        x = model.new_int_var(0, world[0], f"x_{index}")
        y = model.new_int_var(0, world[1], f"y_{index}")
        z = model.new_int_var(0, world[2], f"z_{index}")
        model.add(x + width <= world[0])
        model.add(y + depth <= world[1])
        model.add(z + height <= world[2])
        variables.append(
            {
                "choice": choice,
                "options": options,
                "width": width,
                "depth": depth,
                "height": height,
                "area": area,
                "x": x,
                "y": y,
                "z": z,
            }
        )
    for left in range(len(variables)):
        for right in range(left + 1, len(variables)):
            a = variables[left]
            b = variables[right]
            separated = [model.new_bool_var(f"sep_{left}_{right}_{axis}") for axis in range(6)]
            model.add(a["x"] + a["width"] <= b["x"]).only_enforce_if(separated[0])
            model.add(b["x"] + b["width"] <= a["x"]).only_enforce_if(separated[1])
            model.add(a["y"] + a["depth"] <= b["y"]).only_enforce_if(separated[2])
            model.add(b["y"] + b["depth"] <= a["y"]).only_enforce_if(separated[3])
            model.add(a["z"] + a["height"] <= b["z"]).only_enforce_if(separated[4])
            model.add(b["z"] + b["height"] <= a["z"]).only_enforce_if(separated[5])
            model.add_bool_or(separated)
    for index, values in enumerate(variables):
        for reservation_index, reservation in enumerate(problem.get("reservation_volumes", [])):
            rx, ry, rz = reservation["x"], reservation["y"], reservation["z"]
            rw, rd, rh = reservation["size"]
            separated = [
                model.new_bool_var(f"res_{index}_{reservation_index}_{axis}") for axis in range(6)
            ]
            model.add(values["x"] + values["width"] <= rx).only_enforce_if(separated[0])
            model.add(rx + rw <= values["x"]).only_enforce_if(separated[1])
            model.add(values["y"] + values["depth"] <= ry).only_enforce_if(separated[2])
            model.add(ry + rd <= values["y"]).only_enforce_if(separated[3])
            model.add(values["z"] + values["height"] <= rz).only_enforce_if(separated[4])
            model.add(rz + rh <= values["z"]).only_enforce_if(separated[5])
            model.add_bool_or(separated)
    if "disjoint_regions" in problem.get("active_constraints", []):
        cell = problem["fragment_cell_mm"]
        stride_x = cell[0] + problem["fragment_gap_mm"]
        stride_y = cell[1] + problem["fragment_gap_mm"]
        x_count = max(1, (world[0] - 2 + stride_x - 1) // stride_x)
        y_count = max(1, (world[1] - 2 + stride_y - 1) // stride_y)
        for index, values in enumerate(variables):
            cell_x = model.new_int_var(0, x_count - 1, f"cell_x_{index}")
            cell_y = model.new_int_var(0, y_count - 1, f"cell_y_{index}")
            model.add(values["x"] >= 2 + stride_x * cell_x)
            model.add(values["x"] + values["width"] <= 2 + stride_x * cell_x + cell[0])
            model.add(values["y"] >= 2 + stride_y * cell_y)
            model.add(values["y"] + values["depth"] <= 2 + stride_y * cell_y + cell[1])
    support_variables = {}
    for load_index, load in enumerate(variables):
        ground = model.new_bool_var(f"ground_{load_index}")
        if not participants[load_index].get("ground_allowed", True):
            model.add(ground == 0)
        model.add(load["z"] == 0).only_enforce_if(ground)
        model.add(load["z"] >= 1).only_enforce_if(ground.negated())
        supports = []
        minimum = int(participants[load_index].get("minimum_support_count", 1))
        for support_index, support in enumerate(variables):
            if support_index == load_index:
                continue
            selected = model.new_bool_var(f"support_{load_index}_{support_index}")
            support_variables[(load_index, support_index)] = selected
            supports.append(selected)
            model.add(selected == 0).only_enforce_if(ground)
            model.add(load["z"] == support["z"] + support["height"]).only_enforce_if(selected)
            if minimum >= 2:
                model.add(support["x"] >= load["x"]).only_enforce_if(selected)
                model.add(support["y"] >= load["y"]).only_enforce_if(selected)
                model.add(
                    support["x"] + support["width"] <= load["x"] + load["width"]
                ).only_enforce_if(selected)
                model.add(
                    support["y"] + support["depth"] <= load["y"] + load["depth"]
                ).only_enforce_if(selected)
            else:
                model.add(support["x"] <= load["x"]).only_enforce_if(selected)
                model.add(support["y"] <= load["y"]).only_enforce_if(selected)
                model.add(
                    support["x"] + support["width"] >= load["x"] + load["width"]
                ).only_enforce_if(selected)
                model.add(
                    support["y"] + support["depth"] >= load["y"] + load["depth"]
                ).only_enforce_if(selected)
        model.add(sum(supports) >= minimum).only_enforce_if(ground.negated())
        contributions = []
        for support_index, support in enumerate(variables):
            if support_index == load_index:
                continue
            selected = support_variables[(load_index, support_index)]
            contribution = model.new_int_var(
                0, world[0] * world[1], f"support_area_{load_index}_{support_index}"
            )
            model.add(contribution == support["area"]).only_enforce_if(selected)
            model.add(contribution == 0).only_enforce_if(selected.negated())
            contributions.append(contribution)
        required_support_area = int(participants[load_index].get("required_support_area_mm2", 0))
        if required_support_area:
            model.add(sum(contributions) >= required_support_area).only_enforce_if(ground.negated())
        else:
            model.add(sum(contributions) >= load["area"]).only_enforce_if(ground.negated())
    precedence_edges = problem.get("access_precedence_edges", [])
    removal_ranks = []
    if precedence_edges:
        removal_ranks = [
            model.new_int_var(0, len(participants) - 1, f"removal_rank_{index}")
            for index in range(len(participants))
        ]
        model.add_all_different(removal_ranks)
        participant_index = {
            str(participant["participant_id"]): index
            for index, participant in enumerate(participants)
        }
        for before_id, after_id in precedence_edges:
            model.add(
                removal_ranks[participant_index[str(before_id)]]
                < removal_ranks[participant_index[str(after_id)]]
            )
    top_values = []
    right_values = []
    rear_values = []
    for index, values in enumerate(variables):
        top = model.new_int_var(0, world[2], f"top_{index}")
        right = model.new_int_var(0, world[0], f"right_{index}")
        rear = model.new_int_var(0, world[1], f"rear_{index}")
        model.add(top == values["z"] + values["height"])
        model.add(right == values["x"] + values["width"])
        model.add(rear == values["y"] + values["depth"])
        top_values.append(top)
        right_values.append(right)
        rear_values.append(rear)
    max_top = model.new_int_var(0, world[2], "max_top")
    max_right = model.new_int_var(0, world[0], "max_right")
    max_rear = model.new_int_var(0, world[1], "max_rear")
    model.add_max_equality(max_top, top_values)
    model.add_max_equality(max_right, right_values)
    model.add_max_equality(max_rear, rear_values)
    model.minimize(
        max_top * (world[0] + 1) * (world[1] + 1) + max_rear * (world[0] + 1) + max_right
    )
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = float(limits["wall_seconds"])
    solver.parameters.num_search_workers = int(limits["threads"])
    solver.parameters.random_seed = int(limits["seed"])
    solver.parameters.log_search_progress = False
    _, elapsed = timer()
    status = solver.solve(model)
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        placements = []
        for index, participant in enumerate(participants):
            values = variables[index]
            option = values["options"][solver.value(values["choice"])]
            support_ids = [
                participants[support_index]["participant_id"]
                for support_index in range(len(participants))
                if support_index != index
                and solver.value(support_variables[(index, support_index)])
            ]
            z = solver.value(values["z"])
            placements.append(
                {
                    "participant_id": participant["participant_id"],
                    "x": solver.value(values["x"]),
                    "y": solver.value(values["y"]),
                    "z": z,
                    "size": option["size"],
                    "orientation": option["orientation"],
                    "selected_variant_id": option["variant_id"],
                    "assigned_content_count": participant["assigned_content_count"],
                    "support_ids": support_ids,
                    "removal_rank": (
                        solver.value(removal_ranks[index]) if removal_ranks else world[2] - z
                    ),
                }
            )
        raw_status = "feasible"
        proof = "complete" if status == cp_model.OPTIMAL else "incumbent"
    elif status == cp_model.INFEASIBLE:
        placements = []
        raw_status = "infeasible"
        proof = "complete"
    else:
        placements = []
        raw_status = "unknown"
        proof = "bounded"
    write_output(
        output_path,
        {
            "candidate_id": "ortools_cp_sat",
            "input_digest": payload["input_digest"],
            "status": raw_status,
            "proof_status": proof,
            "engine_status": solver.status_name(status),
            "solve_milliseconds": elapsed(),
            "objective_value": solver.objective_value if placements else None,
            "best_objective_bound": solver.best_objective_bound if placements else None,
            "placements": placements,
        },
    )


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
