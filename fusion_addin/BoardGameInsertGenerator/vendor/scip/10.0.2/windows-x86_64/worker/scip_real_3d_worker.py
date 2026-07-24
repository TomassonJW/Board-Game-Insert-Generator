"""Worker SCIP/PySCIPOpt pour le modele BGIG 3D P64-L08E."""

from __future__ import annotations

import sys

from pyscipopt import Model, quicksum

from _real_3d_worker_common import choices, load_input, timer, write_output


def main(input_path: str, output_path: str) -> None:
    payload = load_input(input_path)
    problem = payload["problem"]
    limits = payload["limits"]
    participants = problem["participants"]
    world = problem["world_mm"]
    model = Model("bgig-real-3d")
    model.hideOutput(True)
    model.setParam("limits/time", float(limits["wall_seconds"]))
    model.setParam("limits/memory", float(limits["memory_mebibytes"]))
    model.setParam("parallel/maxnthreads", int(limits["threads"]))
    model.setParam("randomization/randomseedshift", int(limits["seed"]))
    big_m = max(world) * 3 + 1
    variables = []
    for index, participant in enumerate(participants):
        options = choices(participant)
        selectors = [
            model.addVar(vtype="B", name=f"choice_{index}_{choice}")
            for choice in range(len(options))
        ]
        model.addCons(quicksum(selectors) == 1)
        width = model.addVar(
            vtype="I",
            lb=min(value["size"][0] for value in options),
            ub=max(value["size"][0] for value in options),
            name=f"w_{index}",
        )
        depth = model.addVar(
            vtype="I",
            lb=min(value["size"][1] for value in options),
            ub=max(value["size"][1] for value in options),
            name=f"d_{index}",
        )
        height = model.addVar(
            vtype="I",
            lb=min(value["size"][2] for value in options),
            ub=max(value["size"][2] for value in options),
            name=f"h_{index}",
        )
        area = model.addVar(
            vtype="I",
            lb=min(value["size"][0] * value["size"][1] for value in options),
            ub=max(value["size"][0] * value["size"][1] for value in options),
            name=f"area_{index}",
        )
        model.addCons(
            width
            == quicksum(
                selectors[choice] * options[choice]["size"][0] for choice in range(len(options))
            )
        )
        model.addCons(
            depth
            == quicksum(
                selectors[choice] * options[choice]["size"][1] for choice in range(len(options))
            )
        )
        model.addCons(
            height
            == quicksum(
                selectors[choice] * options[choice]["size"][2] for choice in range(len(options))
            )
        )
        model.addCons(
            area
            == quicksum(
                selectors[choice] * options[choice]["size"][0] * options[choice]["size"][1]
                for choice in range(len(options))
            )
        )
        x = model.addVar(vtype="I", lb=0, ub=world[0], name=f"x_{index}")
        y = model.addVar(vtype="I", lb=0, ub=world[1], name=f"y_{index}")
        z = model.addVar(vtype="I", lb=0, ub=world[2], name=f"z_{index}")
        model.addCons(x + width <= world[0])
        model.addCons(y + depth <= world[1])
        model.addCons(z + height <= world[2])
        variables.append(
            {
                "selectors": selectors,
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
            separated = [
                model.addVar(vtype="B", name=f"sep_{left}_{right}_{axis}") for axis in range(6)
            ]
            model.addCons(a["x"] + a["width"] <= b["x"] + big_m * (1 - separated[0]))
            model.addCons(b["x"] + b["width"] <= a["x"] + big_m * (1 - separated[1]))
            model.addCons(a["y"] + a["depth"] <= b["y"] + big_m * (1 - separated[2]))
            model.addCons(b["y"] + b["depth"] <= a["y"] + big_m * (1 - separated[3]))
            model.addCons(a["z"] + a["height"] <= b["z"] + big_m * (1 - separated[4]))
            model.addCons(b["z"] + b["height"] <= a["z"] + big_m * (1 - separated[5]))
            model.addCons(quicksum(separated) >= 1)
    for index, values in enumerate(variables):
        for reservation_index, reservation in enumerate(problem.get("reservation_volumes", [])):
            rx, ry, rz = reservation["x"], reservation["y"], reservation["z"]
            rw, rd, rh = reservation["size"]
            separated = [
                model.addVar(vtype="B", name=f"res_{index}_{reservation_index}_{axis}")
                for axis in range(6)
            ]
            model.addCons(values["x"] + values["width"] <= rx + big_m * (1 - separated[0]))
            model.addCons(rx + rw <= values["x"] + big_m * (1 - separated[1]))
            model.addCons(values["y"] + values["depth"] <= ry + big_m * (1 - separated[2]))
            model.addCons(ry + rd <= values["y"] + big_m * (1 - separated[3]))
            model.addCons(values["z"] + values["height"] <= rz + big_m * (1 - separated[4]))
            model.addCons(rz + rh <= values["z"] + big_m * (1 - separated[5]))
            model.addCons(quicksum(separated) >= 1)
    if "disjoint_regions" in problem.get("active_constraints", []):
        cell = problem["fragment_cell_mm"]
        stride_x = cell[0] + problem["fragment_gap_mm"]
        stride_y = cell[1] + problem["fragment_gap_mm"]
        x_count = max(1, (world[0] - 2 + stride_x - 1) // stride_x)
        y_count = max(1, (world[1] - 2 + stride_y - 1) // stride_y)
        cells = [(x, y) for x in range(x_count) for y in range(y_count)]
        for index, values in enumerate(variables):
            selectors = [
                model.addVar(vtype="B", name=f"cell_{index}_{ordinal}")
                for ordinal in range(len(cells))
            ]
            model.addCons(quicksum(selectors) == 1)
            for ordinal, (cell_x, cell_y) in enumerate(cells):
                selected = selectors[ordinal]
                left = 2 + stride_x * cell_x
                front = 2 + stride_y * cell_y
                model.addCons(values["x"] >= left - big_m * (1 - selected))
                model.addCons(
                    values["x"] + values["width"] <= left + cell[0] + big_m * (1 - selected)
                )
                model.addCons(values["y"] >= front - big_m * (1 - selected))
                model.addCons(
                    values["y"] + values["depth"] <= front + cell[1] + big_m * (1 - selected)
                )
    support_variables = {}
    ground_variables = []
    for load_index, load in enumerate(variables):
        ground = model.addVar(vtype="B", name=f"ground_{load_index}")
        ground_variables.append(ground)
        if not participants[load_index].get("ground_allowed", True):
            model.addCons(ground == 0)
        model.addCons(load["z"] <= world[2] * (1 - ground))
        model.addCons(load["z"] >= 1 - ground)
        supports = []
        minimum = int(participants[load_index].get("minimum_support_count", 1))
        for support_index, support in enumerate(variables):
            if support_index == load_index:
                continue
            selected = model.addVar(vtype="B", name=f"support_{load_index}_{support_index}")
            support_variables[(load_index, support_index)] = selected
            supports.append(selected)
            model.addCons(selected <= 1 - ground)
            model.addCons(load["z"] - support["z"] - support["height"] <= big_m * (1 - selected))
            model.addCons(load["z"] - support["z"] - support["height"] >= -big_m * (1 - selected))
            if minimum >= 2:
                model.addCons(support["x"] >= load["x"] - big_m * (1 - selected))
                model.addCons(support["y"] >= load["y"] - big_m * (1 - selected))
                model.addCons(
                    support["x"] + support["width"]
                    <= load["x"] + load["width"] + big_m * (1 - selected)
                )
                model.addCons(
                    support["y"] + support["depth"]
                    <= load["y"] + load["depth"] + big_m * (1 - selected)
                )
            else:
                model.addCons(support["x"] <= load["x"] + big_m * (1 - selected))
                model.addCons(support["y"] <= load["y"] + big_m * (1 - selected))
                model.addCons(
                    support["x"] + support["width"]
                    >= load["x"] + load["width"] - big_m * (1 - selected)
                )
                model.addCons(
                    support["y"] + support["depth"]
                    >= load["y"] + load["depth"] - big_m * (1 - selected)
                )
        model.addCons(quicksum(supports) >= minimum * (1 - ground))
        contributions = []
        for support_index, support in enumerate(variables):
            if support_index == load_index:
                continue
            selected = support_variables[(load_index, support_index)]
            for choice_index, choice in enumerate(support["options"]):
                combined = model.addVar(
                    vtype="B",
                    name=f"support_choice_{load_index}_{support_index}_{choice_index}",
                )
                choice_selected = support["selectors"][choice_index]
                model.addCons(combined <= selected)
                model.addCons(combined <= choice_selected)
                model.addCons(combined >= selected + choice_selected - 1)
                contributions.append(combined * choice["size"][0] * choice["size"][1])
        required_support_area = int(participants[load_index].get("required_support_area_mm2", 0))
        support_requirement = required_support_area if required_support_area else load["area"]
        model.addCons(
            quicksum(contributions)
            >= support_requirement - world[0] * world[1] * len(participants) * ground
        )
    precedence_edges = problem.get("access_precedence_edges", [])
    removal_ranks = []
    if precedence_edges:
        removal_ranks = [
            model.addVar(
                vtype="I",
                lb=0,
                ub=len(participants) - 1,
                name=f"removal_rank_{index}",
            )
            for index in range(len(participants))
        ]
        participant_index = {
            str(participant["participant_id"]): index
            for index, participant in enumerate(participants)
        }

        for before_id, after_id in precedence_edges:
            model.addCons(
                removal_ranks[participant_index[str(before_id)]]
                < removal_ranks[participant_index[str(after_id)]]
            )
    max_top = model.addVar(vtype="I", lb=0, ub=world[2], name="max_top")
    max_right = model.addVar(vtype="I", lb=0, ub=world[0], name="max_right")
    max_rear = model.addVar(vtype="I", lb=0, ub=world[1], name="max_rear")
    for values in variables:
        model.addCons(max_top >= values["z"] + values["height"])
        model.addCons(max_right >= values["x"] + values["width"])
        model.addCons(max_rear >= values["y"] + values["depth"])
    model.setObjective(
        max_top * (world[0] + 1) * (world[1] + 1) + max_rear * (world[0] + 1) + max_right,
        "minimize",
    )
    _, elapsed = timer()
    model.optimize()
    status = str(model.getStatus())
    has_solution = model.getNSols() > 0
    if has_solution:
        placements = []
        for index, participant in enumerate(participants):
            values = variables[index]
            choice_index = max(
                range(len(values["selectors"])),
                key=lambda value: model.getVal(values["selectors"][value]),
            )
            option = values["options"][choice_index]
            support_ids = [
                participants[support_index]["participant_id"]
                for support_index in range(len(participants))
                if support_index != index
                and model.getVal(support_variables[(index, support_index)]) > 0.5
            ]
            z = int(round(model.getVal(values["z"])))
            placements.append(
                {
                    "participant_id": participant["participant_id"],
                    "x": int(round(model.getVal(values["x"]))),
                    "y": int(round(model.getVal(values["y"]))),
                    "z": z,
                    "size": option["size"],
                    "orientation": option["orientation"],
                    "selected_variant_id": option["variant_id"],
                    "assigned_content_count": participant["assigned_content_count"],
                    "support_ids": support_ids,
                    "removal_rank": (
                        int(round(model.getVal(removal_ranks[index])))
                        if removal_ranks
                        else world[2] - z
                    ),
                }
            )
        raw_status = "feasible"
        proof = "complete" if status == "optimal" else "incumbent"
    elif status == "infeasible":
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
            "candidate_id": "scip",
            "input_digest": payload["input_digest"],
            "status": raw_status,
            "proof_status": proof,
            "engine_status": status,
            "solve_milliseconds": elapsed(),
            "objective_value": model.getObjVal() if has_solution else None,
            "best_objective_bound": model.getDualbound() if has_solution else None,
            "placements": placements,
        },
    )


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
