from __future__ import annotations

from copy import deepcopy
import unittest
from unittest.mock import patch

from board_game_insert_generator.contextual_local_analysis import (
    IncrementalLocalAnalysisEngine,
)
from board_game_insert_generator.incremental_global_container_reuse import (
    STATUS_CONTAINER_PLACED,
    STATUS_GLOBAL_SOLVE_REQUIRED,
    attempt_incremental_global_void_container_reuse,
)
from board_game_insert_generator.incremental_layout_reuse import (
    STATUS_PLACEMENT_REUSED,
    attempt_incremental_minimal_layout_reuse,
)
from board_game_insert_generator.minimal_layout_solver import solve_minimal_layout
from board_game_insert_generator.project_v1 import blank_project_v1
from board_game_insert_generator.staged_calculation import (
    STATUS_CURRENT,
    StagedCalculationSession,
)


SETTINGS = {"method": "auto", "effort": "quick"}


def _content(
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


def _project() -> dict[str, object]:
    project = blank_project_v1()
    project["box"]["inner_dimensions_mm"] = {
        "x": 120.0,
        "y": 120.0,
        "z": 30.0,
    }
    project["box"]["usable_height_mm"] = 30.0
    project["container_groups"] = [
        {
            "id": "g",
            "name": "Bac",
            "wall_thickness_mm": 2.0,
            "floor_thickness_mm": 2.0,
        }
    ]
    project["contents"] = [_content("a", (40.0, 40.0, 10.0), "g")]
    return project


def _with_new_container(
    project: dict[str, object],
    dimensions: tuple[float, float, float] = (8.0, 8.0, 8.0),
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
    content_id = "b" if not any(
        value["id"] == "b" for value in changed["contents"]
    ) else "new-container-content"
    changed["contents"].append(_content(content_id, dimensions, "g2"))
    return changed


def _engine(project: object) -> IncrementalLocalAnalysisEngine:
    return IncrementalLocalAnalysisEngine(project, effort_profile="quick")


def _solve(
    project: dict[str, object],
    engine: IncrementalLocalAnalysisEngine,
) -> dict[str, object]:
    return solve_minimal_layout(
        project,
        effort_profile="quick",
        container_frontiers=engine.certified_frontiers(),
        frontier_digests=engine.frontier_digests(),
    )


def _world_signature(
    plan: dict[str, object],
    participant_ids: set[str] | None = None,
) -> list[dict[str, object]]:
    return [
        {
            key: deepcopy(placement[key])
            for key in (
                "id",
                "role",
                "origin_mm",
                "world_size_mm",
                "final_outer_dimensions_mm",
                "rotation_deg_z",
            )
        }
        for placement in sorted(plan["placements"], key=lambda value: value["id"])
        if participant_ids is None or placement["id"] in participant_ids
    ]


class IncrementalGlobalContainerReuseTests(unittest.TestCase):
    def test_inserts_one_new_container_without_moving_existing_world(self) -> None:
        project = _project()
        initial_engine = _engine(project)
        initial = _solve(project, initial_engine)
        changed = _with_new_container(project)
        changed_engine = _engine(changed)

        attempt = attempt_incremental_global_void_container_reuse(
            project,
            changed,
            initial,
            container_frontiers=changed_engine.certified_frontiers(),
            effort_profile="quick",
        )

        self.assertEqual(attempt.report["status"], STATUS_CONTAINER_PLACED)
        self.assertEqual(attempt.report["global_solver_invocation_count"], 0)
        self.assertTrue(attempt.report["existing_placements_reused"])
        self.assertFalse(attempt.report["existing_world_placements_changed"])
        self.assertTrue(attempt.report["new_world_placement_added"])
        self.assertEqual(attempt.report["new_container_group_id"], "g2")
        self.assertGreater(attempt.report["counters"]["position_trials"], 0)
        self.assertGreater(
            attempt.report["counters"]["global_recertification_count"],
            0,
        )
        self.assertIsNotNone(attempt.partition)
        assert attempt.partition is not None
        old_ids = {value["id"] for value in initial["placements"]}
        self.assertEqual(
            _world_signature(initial),
            _world_signature(attempt.partition, old_ids),
        )
        self.assertEqual(len(attempt.partition["placements"]), 2)
        self.assertTrue(
            attempt.partition["minimal_layout"]["global_certificate"]["certified"]
        )
        self.assertTrue(
            attempt.partition["minimal_layout"]["container_variant_certificate"][
                "certified"
            ]
        )

    def test_insertion_is_deterministic_under_observable_caps(self) -> None:
        project = _project()
        initial_engine = _engine(project)
        initial = _solve(project, initial_engine)
        changed = _with_new_container(project)
        changed_engine = _engine(changed)
        kwargs = {
            "container_frontiers": changed_engine.certified_frontiers(),
            "effort_profile": "quick",
        }

        first = attempt_incremental_global_void_container_reuse(
            project,
            changed,
            initial,
            **kwargs,
        )
        second = attempt_incremental_global_void_container_reuse(
            project,
            changed,
            initial,
            **kwargs,
        )

        self.assertEqual(first.report, second.report)
        self.assertEqual(
            first.partition["plan_digest"] if first.partition else None,
            second.partition["plan_digest"] if second.partition else None,
        )
        self.assertLessEqual(
            first.report["counters"]["position_trials"],
            first.report["budget"]["max_position_trials"],
        )

    def test_oversized_new_container_fails_closed_without_global_solve(self) -> None:
        project = _project()
        initial_engine = _engine(project)
        initial = _solve(project, initial_engine)
        changed = _with_new_container(project, (110.0, 110.0, 20.0))
        changed_engine = _engine(changed)

        attempt = attempt_incremental_global_void_container_reuse(
            project,
            changed,
            initial,
            container_frontiers=changed_engine.certified_frontiers(),
            effort_profile="quick",
        )

        self.assertIsNone(attempt.partition)
        self.assertEqual(attempt.report["status"], STATUS_GLOBAL_SOLVE_REQUIRED)
        self.assertEqual(attempt.report["global_solver_invocation_count"], 0)
        self.assertIn(
            attempt.report["stop_reason"],
            {
                "no_certified_global_void_position",
                "position_trial_budget_exhausted",
            },
        )

    def test_staged_session_promotes_new_container_without_global_solve(self) -> None:
        project = _project()
        engine = _engine(project)
        session = StagedCalculationSession(project, solver_settings=SETTINGS)
        session.synchronize(
            project,
            engine.snapshot(),
            solver_settings=SETTINGS,
            container_frontiers=engine.certified_frontiers(),
            frontier_digests=engine.frontier_digests(),
        )
        session.calculate_layout(request_id="initial", request_revision=0)

        changed = _with_new_container(project)
        changed_engine = _engine(changed)
        with patch(
            "board_game_insert_generator.minimal_layout_solver.solve_minimal_layout",
            side_effect=AssertionError("global solver must stay explicit"),
        ):
            snapshot = session.synchronize(
                changed,
                changed_engine.snapshot(),
                solver_settings=SETTINGS,
                container_frontiers=changed_engine.certified_frontiers(),
                frontier_digests=changed_engine.frontier_digests(),
            )

        self.assertEqual(snapshot["minimal_layout"]["status"], STATUS_CURRENT)
        self.assertTrue(snapshot["minimal_layout"]["placement_certified"])
        self.assertEqual(
            snapshot["minimal_layout"]["cache_status"],
            "global_void_reuse_not_cached",
        )
        self.assertEqual(
            snapshot["minimal_layout"]["calculation_timing"]["result_source"],
            "global_void_container_reuse",
        )
        self.assertEqual(
            snapshot["global_void_reuse"]["status"],
            STATUS_CONTAINER_PLACED,
        )
        self.assertEqual(
            snapshot["global_void_reuse"]["global_solver_invocation_count"],
            0,
        )
        self.assertIsNotNone(session.current_minimal_partition())

    def test_chains_after_local_fixed_envelope_reuse(self) -> None:
        project = _project()
        project["contents"].append(_content("b", (10.0, 20.0, 10.0), "g"))
        initial_engine = _engine(project)
        initial = _solve(project, initial_engine)

        local_project = deepcopy(project)
        local_project["contents"].append(
            _content("c", (8.0, 16.0, 8.0), "g")
        )
        local_engine = _engine(local_project)
        local = attempt_incremental_minimal_layout_reuse(
            project,
            local_project,
            initial,
            container_frontiers=local_engine.certified_frontiers(),
            effort_profile="quick",
        )
        self.assertEqual(local.report["status"], STATUS_PLACEMENT_REUSED)
        assert local.partition is not None

        changed = _with_new_container(local_project)
        changed_engine = _engine(changed)
        attempt = attempt_incremental_global_void_container_reuse(
            local_project,
            changed,
            local.partition,
            container_frontiers=changed_engine.certified_frontiers(),
            effort_profile="quick",
        )

        self.assertEqual(attempt.report["status"], STATUS_CONTAINER_PLACED)
        self.assertIsNotNone(attempt.partition)
        self.assertEqual(attempt.report["global_solver_invocation_count"], 0)
        old_ids = {value["id"] for value in local.partition["placements"]}
        assert attempt.partition is not None
        self.assertEqual(
            _world_signature(local.partition),
            _world_signature(attempt.partition, old_ids),
        )

    def test_global_layout_change_is_not_attempted(self) -> None:
        project = _project()
        initial_engine = _engine(project)
        initial = _solve(project, initial_engine)
        changed = _with_new_container(project)
        changed["layout"]["layout_clearance_mm"] = 0.8
        changed_engine = _engine(changed)

        attempt = attempt_incremental_global_void_container_reuse(
            project,
            changed,
            initial,
            container_frontiers=changed_engine.certified_frontiers(),
            effort_profile="quick",
        )

        self.assertIsNone(attempt.partition)
        self.assertEqual(attempt.report["status"], "not_attempted")
        self.assertEqual(attempt.report["stop_reason"], "global_dependency_changed")

    def test_existing_container_edit_is_not_accepted_as_global_void_insertion(self) -> None:
        project = _project()
        initial_engine = _engine(project)
        initial = _solve(project, initial_engine)
        changed = _with_new_container(project)
        changed["contents"][0]["dimensions_mm"]["x"] = 41.0
        changed_engine = _engine(changed)

        attempt = attempt_incremental_global_void_container_reuse(
            project,
            changed,
            initial,
            container_frontiers=changed_engine.certified_frontiers(),
            effort_profile="quick",
        )

        self.assertIsNone(attempt.partition)
        self.assertEqual(attempt.report["status"], STATUS_GLOBAL_SOLVE_REQUIRED)
        self.assertEqual(attempt.report["stop_reason"], "existing_content_changed")


if __name__ == "__main__":
    unittest.main()
