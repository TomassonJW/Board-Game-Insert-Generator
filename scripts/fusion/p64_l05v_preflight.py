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
    """Confirm that the historical global-void insertion is superseded."""

    baseline = global_void_project()

    success_session = initial_session(baseline)
    success_snapshot = synchronize(
        success_session,
        with_new_container(baseline, (8.0, 8.0, 8.0)),
    )
    if success_snapshot["minimal_layout"]["status"] != STATUS_STALE:
        raise RuntimeError("P64-L09T-A republished a plan after adding a container.")
    if "global_void_reuse" in success_snapshot:
        raise RuntimeError("P64-L09T-A still exposes global-void reuse.")

    fallback_session = initial_session(baseline)
    fallback_snapshot = synchronize(
        fallback_session,
        with_new_container(baseline, (110.0, 110.0, 20.0)),
    )
    if fallback_snapshot["minimal_layout"]["status"] != STATUS_STALE:
        raise RuntimeError("P64-L09T-A did not leave the second layout stale.")
    if "global_void_reuse" in fallback_snapshot:
        raise RuntimeError("P64-L09T-A still exposes global-void diagnostics.")

    return {
        "baseline_project": baseline,
        "status": "superseded_by_explicit_recalculation",
        "small_container_edit": success_snapshot["minimal_layout"],
        "oversized_container_edit": fallback_snapshot["minimal_layout"],
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
    print("AUTOMATIC_GLOBAL_VOID_REUSE=disabled")
    print("NEXT_ACTION=calculate_layout")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
