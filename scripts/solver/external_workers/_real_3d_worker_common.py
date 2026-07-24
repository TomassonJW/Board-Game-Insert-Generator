"""Protocole commun des workers externes 3D P64-L08E."""

from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
from time import perf_counter
from typing import Mapping


INPUT_SCHEMA = "bgig.real_3d_worker_input.v1"
OUTPUT_SCHEMA = "bgig.real_3d_worker_output.v1"


def load_input(path: str) -> dict[str, object]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    supplied = payload.pop("input_digest", None)
    if payload.get("schema_version") != INPUT_SCHEMA or supplied != canonical_digest(payload):
        raise ValueError("Invalid real-3D worker input binding.")
    payload["input_digest"] = supplied
    return payload


def write_output(path: str, payload: Mapping[str, object]) -> None:
    result = dict(payload)
    result["schema_version"] = OUTPUT_SCHEMA
    result["output_digest"] = canonical_digest(result)
    target = Path(path)
    temporary = target.with_suffix(".tmp")
    temporary.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(target)


def choices(participant: Mapping[str, object]) -> list[dict[str, object]]:
    result = []
    for variant in participant["variants"]:
        for orientation in variant["allowed_rotations"]:
            size = list(variant["size"])
            if orientation == "yxz":
                size[0], size[1] = size[1], size[0]
            candidate = {
                "variant_id": variant["variant_id"],
                "orientation": orientation,
                "size": size,
            }
            if candidate not in result:
                result.append(candidate)
    return result


def canonical_digest(value: object) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return sha256(payload.encode("utf-8")).hexdigest()


def timer() -> tuple[float, callable]:
    started = perf_counter()
    return started, lambda: round((perf_counter() - started) * 1000.0, 6)
