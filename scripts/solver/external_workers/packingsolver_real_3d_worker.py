"""Passerelle JSON vers PackingSolver box au SHA verrouille P64-L08E."""

from __future__ import annotations

import csv
import os
from pathlib import Path
import subprocess
import sys
from time import perf_counter

from _real_3d_worker_common import choices, load_input, write_output


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
    participants = list(problem["participants"])
    run_dir = Path(output_path).resolve().parent
    items_path = run_dir / "packingsolver-items.csv"
    bins_path = run_dir / "packingsolver-bins.csv"
    parameters_path = run_dir / "packingsolver-parameters.csv"
    certificate_path = run_dir / "packingsolver-certificate.csv"
    with items_path.open("w", encoding="ascii", newline="") as stream:
        writer = csv.writer(stream, lineterminator="\n")
        writer.writerow(
            (
                "ID",
                "X",
                "Y",
                "Z",
                "ROTATION_XYZ",
                "ROTATION_YXZ",
                "ROTATION_ZYX",
                "ROTATION_YZX",
                "ROTATION_XZY",
                "ROTATION_ZXY",
                "COPIES",
            )
        )
        for index, participant in enumerate(participants):
            option = choices(participant)[0]
            rotations = participant["variants"][0]["allowed_rotations"]
            writer.writerow(
                (
                    index,
                    *option["size"],
                    int("xyz" in rotations),
                    int("yxz" in rotations),
                    0,
                    0,
                    0,
                    0,
                    1,
                )
            )
    with bins_path.open("w", encoding="ascii", newline="") as stream:
        writer = csv.writer(stream, lineterminator="\n")
        writer.writerow(("ID", "X", "Y", "Z", "COPIES"))
        writer.writerow((0, *problem["world_mm"], 1))
    parameters_path.write_text("NAME,VALUE\nobjective,bin-packing\n", encoding="ascii")
    if certificate_path.exists():
        certificate_path.unlink()
    command = [
        os.environ["BGIG_PACKINGSOLVER_EXE"],
        "--items",
        str(items_path),
        "--bins",
        str(bins_path),
        "--parameters",
        str(parameters_path),
        "--certificate",
        str(certificate_path),
        "--time-limit",
        str(payload["limits"]["wall_seconds"]),
        "--memory-limit",
        str(payload["limits"]["memory_mebibytes"]),
        "--seed",
        str(payload["limits"]["seed"]),
        "--verbosity-level",
        "0",
        "--only-write-at-the-end",
    ]
    started = perf_counter()
    completed = subprocess.run(
        command,
        capture_output=True,
        check=False,
        text=True,
        timeout=max(1.0, float(payload["limits"]["wall_seconds"]) - 0.1),
    )
    solve_ms = round((perf_counter() - started) * 1000.0, 6)
    if completed.returncode != 0:
        raise RuntimeError(completed.stderr or completed.stdout)
    placements = []
    if certificate_path.is_file():
        with certificate_path.open("r", encoding="ascii", newline="") as stream:
            for row in csv.DictReader(stream):
                if row["TYPE"] != "ITEM":
                    continue
                participant_index = int(row["ID"])
                participant = participants[participant_index]
                size = [int(row["LX"]), int(row["LY"]), int(row["LZ"])]
                option = next(
                    (value for value in choices(participant) if value["size"] == size), None
                )
                if option is None:
                    raise RuntimeError("PackingSolver returned a forbidden rotation.")
                placements.append(
                    {
                        "participant_id": participant["participant_id"],
                        "x": int(row["X"]),
                        "y": int(row["Y"]),
                        "z": int(row["Z"]),
                        "size": size,
                        "orientation": option["orientation"],
                        "selected_variant_id": option["variant_id"],
                        "assigned_content_count": participant["assigned_content_count"],
                        "support_ids": [],
                        "removal_rank": problem["world_mm"][2] - int(row["Z"]),
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
    complete = len(placements) == len(participants)
    write_output(
        output_path,
        {
            "candidate_id": "packingsolver_box",
            "input_digest": payload["input_digest"],
            "status": "feasible" if complete else "unknown",
            "proof_status": "incumbent" if complete else "bounded",
            "engine_status": "complete_certificate" if complete else "incomplete_certificate",
            "solve_milliseconds": solve_ms,
            "objective_value": None,
            "best_objective_bound": None,
            "placements": placements if complete else [],
        },
    )


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
