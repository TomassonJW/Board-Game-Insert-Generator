"""Audit R7 derived layout lengths across replay artifacts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Iterable

from board_game_insert_generator.product_grid import is_on_product_grid


_AUDITED_DIAGNOSTIC_ROOTS = {
    "minimal_plan.top_inset_reservations": (
        "minimal_plan",
        "top_inset_reservations",
    ),
    "minimal_plan.placements": ("minimal_plan", "placements"),
    "cad_ir": ("cad_ir",),
    "fusion_plan": ("fusion_plan",),
}
_SOURCE_OR_PREGRID_SEGMENTS = {
    "numeric_epsilon_mm",
    "source_physical_dimensions_mm",
    "required_cut_size_before_grid_mm",
    "required_initial_origin_before_grid_mm",
    "required_total_thickness_before_grid_mm",
}


def audit_replay_summary(payload: dict[str, Any]) -> dict[str, Any]:
    results = payload.get("results")
    if not isinstance(results, list):
        raise ValueError("Replay summary must contain a results list.")
    audited_length_count = 0
    off_grid: list[dict[str, object]] = []
    for result_index, result in enumerate(results):
        if not isinstance(result, dict):
            raise ValueError("Replay result must be an object.")
        diagnostics = result.get("diagnostics")
        if not isinstance(diagnostics, dict):
            raise ValueError(
                "Replay result must include diagnostics for grid audit."
            )
        for root_name, segments in _AUDITED_DIAGNOSTIC_ROOTS.items():
            root = _nested_value(diagnostics, segments)
            for path, number in _walk_numbers(root):
                if not _is_derived_length(path):
                    continue
                audited_length_count += 1
                if not is_on_product_grid(number):
                    off_grid.append(
                        {
                            "result_index": result_index,
                            "path": ".".join((root_name, *path)),
                            "value": number,
                        }
                    )
    return {
        "schema_version": "bgig.p64_l09u_r7_grid_audit.v1",
        "status": "passed" if not off_grid else "failed",
        "product_grid_step_mm": 0.1,
        "audited_length_count": audited_length_count,
        "off_grid_count": len(off_grid),
        "off_grid": off_grid,
        "source_values_excluded_from_effective_geometry_audit": True,
    }


def _nested_value(
    value: dict[str, Any],
    segments: tuple[str, ...],
) -> Any:
    current: Any = value
    for segment in segments:
        if not isinstance(current, dict) or segment not in current:
            raise ValueError(
                f"Replay diagnostics are missing {'.'.join(segments)}."
            )
        current = current[segment]
    return current


def _walk_numbers(
    value: Any,
    path: tuple[str, ...] = (),
) -> Iterable[tuple[tuple[str, ...], float]]:
    if isinstance(value, dict):
        for key, child in value.items():
            yield from _walk_numbers(child, (*path, str(key)))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from _walk_numbers(child, (*path, str(index)))
    elif isinstance(value, (int, float)) and not isinstance(value, bool):
        yield path, float(value)


def _is_derived_length(path: tuple[str, ...]) -> bool:
    if not path or any(
        segment in _SOURCE_OR_PREGRID_SEGMENTS for segment in path
    ):
        return False
    key = path[-1]
    parent = path[-2] if len(path) > 1 else ""
    if key.endswith("_ms") or key.endswith("_mm2") or key.endswith("_mm3"):
        return False
    return bool(
        key.endswith("_mm")
        or parent.endswith("_mm")
        or parent
        in {
            "origin",
            "size",
            "box_per_side_xy_mm",
            "between_mm",
            "values_mm",
        }
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("summary", type=Path)
    arguments = parser.parse_args()
    payload = json.loads(
        arguments.summary.read_text(encoding="utf-8")
    )
    report = audit_replay_summary(payload)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
