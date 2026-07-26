"""Validate the deterministic P64-V2H03V Fusion gate projects locally.

This preflight uses only the pure Python engine. It neither imports ``adsk`` nor
persists a project or materializes a Fusion scene.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
for candidate in (ROOT / "src", ROOT):
    candidate_text = str(candidate)
    if candidate_text not in sys.path:
        sys.path.insert(0, candidate_text)

from board_game_insert_generator.partition_solver import solve_partition_plan  # noqa: E402
from board_game_insert_generator.project_v1 import normalize_project_draft  # noqa: E402


P64_V2H03V_PREFLIGHT_SCHEMA = "bgig.p64_v2h03v.preflight.v1"


def _solve(raw_project: object) -> dict[str, object]:
    project = normalize_project_draft(raw_project).project
    return solve_partition_plan(
        project,
        solver_method="auto",
        effort_profile="quick",
    )


def build_preflight(variant_project: object, control_project: object) -> dict[str, object]:
    """Reclassify the old shrinking-variant gate and keep its canonical control."""

    variant_plan = _solve(variant_project)
    variant_summary = variant_plan["summary"]
    variant_solver = variant_plan["solver"]
    variant_portfolio = variant_solver["portfolio"]
    if variant_summary["status"] == "constructed":
        raise AssertionError("H03V must not construct a plan by reducing source minima.")
    if variant_solver["result"]["status"] != "no_solution_within_budget":
        raise AssertionError("H03V shrinking-variant fixture must fail honestly.")
    trace = variant_portfolio.get("container_variant_search")
    selected_variants = trace.get("selected_variants", []) if isinstance(trace, dict) else []
    if selected_variants:
        raise AssertionError("H03V must not select an undersized internal variant.")

    control_plan = _solve(control_project)
    control_summary = control_plan["summary"]
    control_solver = control_plan["solver"]
    control_portfolio = control_solver["portfolio"]
    if control_summary["status"] != "constructed":
        raise AssertionError("H03V canonical control must remain constructed.")
    if control_solver["result"]["status"] != "solution_found":
        raise AssertionError("H03V canonical control must expose solution_found.")
    if control_portfolio["selected_family_id"] != "stage_stack":
        raise AssertionError("H03V canonical control must retain stage_stack.")
    if "container_variant_search" in control_portfolio:
        raise AssertionError("H03V canonical control must not expose a fallback trace.")

    return {
        "schema_version": P64_V2H03V_PREFLIGHT_SCHEMA,
        "variant": {
            "status": variant_solver["result"]["status"],
            "selected_family_id": variant_portfolio.get("selected_family_id"),
            "selected_variant_count": len(selected_variants),
            "source_minimum_floor_enforced": True,
            "plan_digest": variant_plan["plan_digest"],
        },
        "control": {
            "status": control_solver["result"]["status"],
            "selected_family_id": control_portfolio["selected_family_id"],
            "variant_trace_absent": True,
            "plan_digest": control_plan["plan_digest"],
        },
        "fusion_materialized": False,
        "print_validated": False,
    }

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("variant_fixture", type=Path)
    parser.add_argument("control_fixture", type=Path)
    args = parser.parse_args()
    variant_raw: Any = json.loads(args.variant_fixture.read_text(encoding="utf-8"))
    control_raw: Any = json.loads(args.control_fixture.read_text(encoding="utf-8"))
    report = build_preflight(variant_raw, control_raw)
    print(json.dumps(report, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
