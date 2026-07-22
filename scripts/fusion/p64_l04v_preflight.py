"""Deterministic preflight checks and baseline fixture for the P64-L04V gate."""

from __future__ import annotations

import argparse
import json
from copy import deepcopy
from pathlib import Path

from board_game_insert_generator.contextual_local_analysis import (
    IncrementalLocalAnalysisEngine,
)
from board_game_insert_generator.project_v1 import blank_project_v1
from board_game_insert_generator.staged_calculation import (
    STATUS_CURRENT,
    STATUS_STALE,
    StagedCalculationSession,
)


SETTINGS = {"method": "auto", "effort": "quick"}


def pocket_project() -> dict[str, object]:
    """Return the small known-good baseline used by the human Fusion gate."""

    project = blank_project_v1()
    project["project_name"] = "P64-L04V pocket baseline"
    project["box"]["inner_dimensions_mm"] = {"x": 120.0, "y": 120.0, "z": 30.0}
    project["box"]["usable_height_mm"] = 30.0
    project["container_groups"] = [
        {
            "id": "g",
            "name": "Bac L04",
            "wall_thickness_mm": 2.0,
            "floor_thickness_mm": 2.0,
        }
    ]
    project["contents"] = [
        content("a", (40.0, 40.0, 10.0)),
        content("b", (10.0, 20.0, 10.0)),
    ]
    return project


def content(identifier: str, dimensions: tuple[float, float, float]) -> dict[str, object]:
    return {
        "id": identifier,
        "name": identifier.upper(),
        "shape_kind": "rectangle",
        "dimensions_mm": dict(zip(("x", "y", "z"), dimensions)),
        "quantity": 1,
        "container_group_id": "g",
        "content_clearance_mm": 0.0,
        "measurement_confidence": "exact",
    }


def with_insert(
    project: dict[str, object],
    dimensions: tuple[float, float, float],
) -> dict[str, object]:
    changed = deepcopy(project)
    changed["contents"].append(content("c", dimensions))
    return changed


def engine(project: object) -> IncrementalLocalAnalysisEngine:
    return IncrementalLocalAnalysisEngine(project, effort_profile="quick")


def synchronize(
    session: StagedCalculationSession,
    project: dict[str, object],
    analysis: IncrementalLocalAnalysisEngine,
) -> dict[str, object]:
    return session.synchronize(
        project,
        analysis.snapshot(),
        solver_settings=SETTINGS,
        container_frontiers=analysis.certified_frontiers(),
        frontier_digests=analysis.frontier_digests(),
    )


def initial_session(project: dict[str, object]) -> StagedCalculationSession:
    analysis = engine(project)
    session = StagedCalculationSession(project, solver_settings=SETTINGS)
    synchronize(session, project, analysis)
    result = session.calculate_layout(request_id="p64-l04v-initial", request_revision=0)
    minimal = result["staged_calculation"]["minimal_layout"]
    if minimal["status"] != STATUS_CURRENT or not minimal["placement_certified"]:
        raise RuntimeError("P64-L04V baseline did not produce a current certified layout.")
    return session


def assert_preflight() -> dict[str, object]:
    """Exercise the exact local-success and fail-closed fallback gate paths."""

    baseline = pocket_project()

    success_session = initial_session(baseline)
    success_project = with_insert(baseline, (8.0, 16.0, 8.0))
    success_snapshot = synchronize(success_session, success_project, engine(success_project))
    reuse = success_snapshot["local_reuse"]
    if reuse["status"] != "placement_reused":
        raise RuntimeError("P64-L04V expected local placement reuse.")
    if reuse["global_solver_invocation_count"] != 0:
        raise RuntimeError("P64-L04V local reuse unexpectedly invoked the global solver.")
    if reuse["world_placements_changed"]:
        raise RuntimeError("P64-L04V local reuse unexpectedly moved a world placement.")

    fallback_session = initial_session(baseline)
    fallback_project = with_insert(baseline, (20.0, 20.0, 10.0))
    fallback_snapshot = synchronize(
        fallback_session,
        fallback_project,
        engine(fallback_project),
    )
    fallback = fallback_snapshot["local_reuse"]
    if fallback["status"] != "global_solve_required":
        raise RuntimeError("P64-L04V expected an explicit global-solve fallback.")
    if fallback["global_solver_invocation_count"] != 0:
        raise RuntimeError("P64-L04V fallback invoked the global solver implicitly.")
    if fallback_snapshot["minimal_layout"]["status"] != STATUS_STALE:
        raise RuntimeError("P64-L04V fallback did not leave the old layout stale.")

    return {
        "baseline_project": baseline,
        "local_reuse": reuse,
        "fallback": fallback,
    }


def write_fixture(path: Path, project: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(project, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-fixture", type=Path)
    args = parser.parse_args()

    result = assert_preflight()
    if args.write_fixture is not None:
        write_fixture(args.write_fixture, result["baseline_project"])
        print(f"P64_L04V_FIXTURE={args.write_fixture}")
    print("P64_L04V_PREFLIGHT=OK")
    print("LOCAL_REUSE_STATUS=placement_reused")
    print("LOCAL_REUSE_GLOBAL_SOLVER_INVOCATIONS=0")
    print("FALLBACK_STATUS=global_solve_required")
    print("FALLBACK_GLOBAL_SOLVER_INVOCATIONS=0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
