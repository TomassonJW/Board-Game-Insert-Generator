"""Protocole fichier minimal partagé par les workers externes P64-L07."""

from __future__ import annotations

from base64 import urlsafe_b64decode, urlsafe_b64encode
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


INPUT_HEADER = ("P64L07FLOOR", "1")
OUTPUT_HEADER = ("P64L07RESULT", "1")


@dataclass(frozen=True)
class FloorItem:
    item_id: str
    width: int
    height: int


@dataclass(frozen=True)
class FloorProblem:
    bin_width: int
    bin_height: int
    time_limit_ms: int
    seed: int
    threads: int
    rotation_allowed: bool
    items: tuple[FloorItem, ...]


def decode_id(value: str) -> str:
    padding = "=" * (-len(value) % 4)
    return urlsafe_b64decode((value + padding).encode("ascii")).decode("utf-8")


def encode_id(value: str) -> str:
    return urlsafe_b64encode(value.encode("utf-8")).decode("ascii").rstrip("=")


def read_problem(path: str) -> FloorProblem:
    rows = [
        line.rstrip("\r\n").split("\t")
        for line in Path(path).read_text(encoding="utf-8").splitlines()
        if line
    ]
    if not rows or tuple(rows[0]) != INPUT_HEADER:
        raise ValueError("Unsupported floor worker input schema.")
    if len(rows) < 5 or rows[1][0] != "BIN" or rows[2][0] != "LIMIT":
        raise ValueError("Incomplete floor worker input.")
    if rows[3][0] != "ROTATE":
        raise ValueError("Missing floor rotation policy.")
    items = tuple(
        FloorItem(decode_id(row[1]), int(row[2]), int(row[3]))
        for row in rows[4:]
        if row[0] == "ITEM" and len(row) == 4
    )
    if len(items) != len(rows) - 4 or len({item.item_id for item in items}) != len(
        items
    ):
        raise ValueError("Floor worker items are invalid.")
    problem = FloorProblem(
        bin_width=int(rows[1][1]),
        bin_height=int(rows[1][2]),
        time_limit_ms=int(rows[2][1]),
        seed=int(rows[2][2]),
        threads=int(rows[2][3]),
        rotation_allowed=rows[3][1] == "1",
        items=items,
    )
    if (
        problem.bin_width <= 0
        or problem.bin_height <= 0
        or problem.time_limit_ms <= 0
        or problem.threads <= 0
        or not problem.items
        or any(item.width <= 0 or item.height <= 0 for item in problem.items)
    ):
        raise ValueError("Floor worker dimensions or limits are invalid.")
    return problem


def write_result(
    path: str,
    *,
    status: str,
    solve_ms: float,
    engine_status: str,
    placements: Iterable[tuple[str, int, int, int]] = (),
    metrics: Iterable[tuple[str, object]] = (),
) -> None:
    rows = [
        "\t".join(OUTPUT_HEADER),
        "\t".join(
            (
                "RESULT",
                status,
                f"{solve_ms:.6f}",
                encode_id(engine_status),
            )
        ),
    ]
    rows.extend(
        f"PLACEMENT\t{encode_id(item_id)}\t{x}\t{y}\t{rotation}"
        for item_id, x, y, rotation in placements
    )
    rows.extend(f"METRIC\t{name}\t{value}" for name, value in metrics)
    target = Path(path)
    temporary = target.with_suffix(target.suffix + ".tmp")
    temporary.write_text("\n".join(rows) + "\n", encoding="utf-8")
    temporary.replace(target)
