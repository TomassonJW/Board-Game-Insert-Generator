"""Passerelle JSON isolee vers LAFF 4.2.1 en 3D reel."""

from __future__ import annotations

import base64
import os
from pathlib import Path
import subprocess
import sys

from _real_3d_worker_common import choices, load_input, write_output


def encode(value: str) -> str:
    return base64.urlsafe_b64encode(value.encode("utf-8")).decode("ascii").rstrip("=")


def decode(value: str) -> str:
    return base64.urlsafe_b64decode(value + "=" * ((4 - len(value) % 4) % 4)).decode("utf-8")


def overlaps_xy(left: dict[str, object], right: dict[str, object]) -> bool:
    return (
        left["x"] < right["x"] + right["size"][0]
        and right["x"] < left["x"] + left["size"][0]
        and left["y"] < right["y"] + right["size"][1]
        and right["y"] < left["y"] + left["size"][1]
    )


def main(input_path: str, output_path: str) -> None:
    payload = load_input(input_path)
    problem = payload["problem"]
    participants = {value["participant_id"]: value for value in problem["participants"]}
    run_dir = Path(output_path).resolve().parent
    native_input = run_dir / "laff-input.tsv"
    native_output = run_dir / "laff-output.tsv"
    lines = ["P64L08REAL3D\t1", "WORLD\t" + "\t".join(str(value) for value in problem["world_mm"])]
    for participant in participants.values():
        option = choices(participant)[0]
        lines.append(
            "ITEM\t"
            + encode(participant["participant_id"])
            + "\t"
            + "\t".join(str(value) for value in option["size"])
        )
    native_input.write_text("\n".join(lines) + "\n", encoding="utf-8")
    java = os.environ["BGIG_LAFF_JAVA"]
    classpath = os.environ["BGIG_LAFF_CLASSPATH"]
    completed = subprocess.run(
        [java, "-cp", classpath, "LaffReal3DWorker", str(native_input), str(native_output)],
        capture_output=True,
        check=False,
        text=True,
        timeout=max(1.0, float(payload["limits"]["wall_seconds"]) - 0.1),
    )
    if completed.returncode != 0:
        raise RuntimeError(completed.stderr)
    rows = [
        line.split("\t") for line in native_output.read_text(encoding="utf-8").splitlines() if line
    ]
    if len(rows) < 2 or rows[0] != ["P64L08REAL3DRESULT", "1"]:
        raise RuntimeError("Invalid LAFF native output.")
    status = rows[1][1]
    solve_ms = float(rows[1][2])
    placements = []
    for row in rows[2:]:
        participant_id = decode(row[1])
        participant = participants[participant_id]
        size = [int(row[5]), int(row[6]), int(row[7])]
        variants = choices(participant)
        option = next((value for value in variants if value["size"] == size), None)
        if option is None:
            raise RuntimeError("LAFF returned a forbidden rotation.")
        placements.append(
            {
                "participant_id": participant_id,
                "x": int(row[2]),
                "y": int(row[3]),
                "z": int(row[4]),
                "size": size,
                "orientation": option["orientation"],
                "selected_variant_id": option["variant_id"],
                "assigned_content_count": participant["assigned_content_count"],
                "support_ids": [],
                "removal_rank": problem["world_mm"][2] - int(row[4]),
            }
        )
    for load in placements:
        if load["z"] == 0:
            continue
        load["support_ids"] = [
            support["participant_id"]
            for support in placements
            if support["participant_id"] != load["participant_id"]
            and support["z"] + support["size"][2] == load["z"]
            and overlaps_xy(load, support)
        ]
    write_output(
        output_path,
        {
            "candidate_id": "laff",
            "input_digest": payload["input_digest"],
            "status": status,
            "proof_status": "incumbent" if status == "feasible" else "bounded",
            "engine_status": "complete_pack" if status == "feasible" else "no_complete_pack",
            "solve_milliseconds": solve_ms,
            "objective_value": None,
            "best_objective_bound": None,
            "placements": placements,
        },
    )


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
