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
    """Confirm that the historical reuse gate is superseded fail-closed."""

    baseline = pocket_project()

    success_session = initial_session(baseline)
    success_project = with_insert(baseline, (8.0, 16.0, 8.0))
    success_snapshot = synchronize(success_session, success_project, engine(success_project))
    if success_snapshot["minimal_layout"]["status"] != STATUS_STALE:
        raise RuntimeError("P64-L09T-A did not leave the old layout stale.")
    if "local_reuse" in success_snapshot:
        raise RuntimeError("P64-L09T-A still exposes the historical local reuse path.")

    fallback_session = initial_session(baseline)
    fallback_project = with_insert(baseline, (20.0, 20.0, 10.0))
    fallback_snapshot = synchronize(
        fallback_session,
        fallback_project,
        engine(fallback_project),
    )
    if fallback_snapshot["minimal_layout"]["status"] != STATUS_STALE:
        raise RuntimeError("P64-L09T-A did not leave the second old layout stale.")
    if "local_reuse" in fallback_snapshot:
        raise RuntimeError("P64-L09T-A still exposes local reuse diagnostics.")

    return {
        "baseline_project": baseline,
        "status": "superseded_by_explicit_recalculation",
        "first_edit": success_snapshot["minimal_layout"],
        "second_edit": fallback_snapshot["minimal_layout"],
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
    print("AUTOMATIC_REUSE=disabled")
    print("NEXT_ACTION=calculate_layout")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
