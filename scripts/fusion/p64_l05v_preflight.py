"""Deterministic baseline and preflight for the P64-L05V Fusion gate."""

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


def content(
    identifier: str,
    dimensions: tuple[float, float, float],
    group_id: str,
) -> dict[str, object]:
    return {
        "id": identifier,
        "name": identifier.upper(),
        "shape_kind": "rectangle",
        "dimensions_mm": dict(zip(("x", "y", "z"), dimensions)),
        "quantity": 1,
        "container_group_id": group_id,
        "content_clearance_mm": 0.0,
        "measurement_confidence": "exact",
    }


def global_void_project() -> dict[str, object]:
    """Return the portable project opened before the human L05V checks."""

    project = blank_project_v1()
    project["project_name"] = "P64-L05V global void baseline"
    project["box"]["inner_dimensions_mm"] = {"x": 120.0, "y": 120.0, "z": 30.0}
    project["box"]["usable_height_mm"] = 30.0
    project["container_groups"] = [
        {
            "id": "g",
            "name": "Bac initial",
            "wall_thickness_mm": 2.0,
            "floor_thickness_mm": 2.0,
        }
    ]
    project["contents"] = [content("a", (40.0, 40.0, 10.0), "g")]
    return project


def with_new_container(
    project: dict[str, object],
    dimensions: tuple[float, float, float],
) -> dict[str, object]:
    changed = deepcopy(project)
    changed["container_groups"].append(
        {
            "id": "g2",
            "name": "Nouveau bac",
            "wall_thickness_mm": 2.0,
            "floor_thickness_mm": 2.0,
        }
    )
    changed["contents"].append(content("b", dimensions, "g2"))
    return changed


def engine(project: object) -> IncrementalLocalAnalysisEngine:
    return IncrementalLocalAnalysisEngine(project, effort_profile="quick")


def synchronize(
    session: StagedCalculationSession,
    project: dict[str, object],
) -> dict[str, object]:
    analysis = engine(project)
    return session.synchronize(
        project,
        analysis.snapshot(),
        solver_settings=SETTINGS,
        container_frontiers=analysis.certified_frontiers(),
        frontier_digests=analysis.frontier_digests(),
    )


def initial_session(project: dict[str, object]) -> StagedCalculationSession:
    session = StagedCalculationSession(project, solver_settings=SETTINGS)
    synchronize(session, project)
    result = session.calculate_layout(
        request_id="p64-l05v-initial",
        request_revision=0,
    )
    minimal = result["staged_calculation"]["minimal_layout"]
    if minimal["status"] != STATUS_CURRENT or not minimal["placement_certified"]:
        raise RuntimeError("P64-L05V baseline did not produce a certified layout.")
    return session


def assert_preflight() -> dict[str, object]:
    """Exercise global-void success and explicit fallback without Fusion."""

    baseline = global_void_project()

    success_session = initial_session(baseline)
    success_snapshot = synchronize(
        success_session,
        with_new_container(baseline, (8.0, 8.0, 8.0)),
    )
    success = success_snapshot["global_void_reuse"]
    if success["status"] != "container_placed_in_global_void":
        raise RuntimeError("P64-L05V expected global-void container insertion.")
    if success["global_solver_invocation_count"] != 0:
        raise RuntimeError("P64-L05V insertion invoked the global solver.")
    if success["existing_world_placements_changed"]:
        raise RuntimeError("P64-L05V insertion moved an existing placement.")
    if success_snapshot["minimal_layout"]["status"] != STATUS_CURRENT:
        raise RuntimeError("P64-L05V insertion did not publish a current layout.")

    fallback_session = initial_session(baseline)
    fallback_snapshot = synchronize(
        fallback_session,
        with_new_container(baseline, (110.0, 110.0, 20.0)),
    )
    fallback = fallback_snapshot["global_void_reuse"]
    if fallback["status"] != "global_solve_required":
        raise RuntimeError("P64-L05V expected explicit global-solve fallback.")
    if fallback["global_solver_invocation_count"] != 0:
        raise RuntimeError("P64-L05V fallback invoked the global solver.")
    if fallback_snapshot["minimal_layout"]["status"] != STATUS_STALE:
        raise RuntimeError("P64-L05V fallback did not leave the layout stale.")

    return {
        "baseline_project": baseline,
        "global_void_success": success,
        "global_void_fallback": fallback,
    }


def write_fixture(path: Path, project: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(project, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-fixture", type=Path)
    args = parser.parse_args()

    result = assert_preflight()
    if args.write_fixture is not None:
        write_fixture(args.write_fixture, result["baseline_project"])
        print(f"P64_L05V_FIXTURE={args.write_fixture}")
    print("P64_L05V_PREFLIGHT=OK")
    print("GLOBAL_VOID_SUCCESS=container_placed_in_global_void")
    print("GLOBAL_VOID_SUCCESS_GLOBAL_SOLVER_INVOCATIONS=0")
    print("GLOBAL_VOID_FALLBACK=global_solve_required")
    print("GLOBAL_VOID_FALLBACK_GLOBAL_SOLVER_INVOCATIONS=0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
