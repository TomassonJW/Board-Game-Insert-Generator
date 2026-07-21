from __future__ import annotations

from copy import deepcopy
import unittest

from board_game_insert_generator.contextual_local_analysis import (
    build_contextual_local_analysis,
)
from board_game_insert_generator.partition_solver import solve_partition_plan
from board_game_insert_generator.project_v1 import blank_project_v1
from board_game_insert_generator.staged_calculation import (
    STATUS_CURRENT,
    STATUS_STALE,
    StagedCalculationError,
    StagedCalculationSession,
)


SETTINGS = {"method": "stage_stack", "effort": "quick"}


def _project() -> dict[str, object]:
    project = blank_project_v1()
    project["container_groups"] = [
        {
            "id": "g",
            "name": "Bac",
            "wall_thickness_mm": None,
            "floor_thickness_mm": None,
        }
    ]
    project["contents"] = [
        {
            "id": "c",
            "name": "Pièces",
            "shape_kind": "square",
            "dimensions_mm": {"x": 12, "y": 12, "z": 3},
            "quantity": 2,
            "container_group_id": "g",
            "content_clearance_mm": None,
            "measurement_confidence": "exact",
        }
    ]
    return project


def _analysis(project: object) -> dict[str, object]:
    return build_contextual_local_analysis(project, effort_profile="quick")


class StagedCalculationTests(unittest.TestCase):
    def test_synchronization_never_invokes_the_global_solver(self) -> None:
        project = _project()
        session = StagedCalculationSession(project, solver_settings=SETTINGS)

        initial = session.synchronize(project, _analysis(project), solver_settings=SETTINGS)
        changed = deepcopy(project)
        changed["contents"][0]["quantity"] = 3
        refreshed = session.synchronize(
            changed,
            _analysis(changed),
            solver_settings=SETTINGS,
        )

        self.assertEqual(initial["global_layout"]["status"], "not_computed")
        self.assertEqual(refreshed["global_layout"]["status"], "not_computed")
        self.assertEqual(refreshed["next_action"], "calculate_layout")
        self.assertTrue(
            refreshed["invariants"]["global_solve_is_explicit"]
        )

    def test_calculate_then_finalize_gates_materialization_without_geometry_change(
        self,
    ) -> None:
        project = _project()
        session = StagedCalculationSession(project, solver_settings=SETTINGS)
        session.synchronize(project, _analysis(project), solver_settings=SETTINGS)

        calculated = session.calculate_layout(
            request_id="solve-1",
            request_revision=0,
        )

        self.assertEqual(
            calculated["solver_result"]["status"],
            "solution_found",
        )
        self.assertTrue(
            calculated["staged_calculation"]["global_layout"][
                "placement_certified"
            ]
        )
        self.assertTrue(
            calculated["staged_calculation"]["global_layout"][
                "finalization_required"
            ]
        )
        with self.assertRaises(StagedCalculationError):
            session.materializable_partition()

        finalized = session.finalize_volume()
        materializable = session.materializable_partition()

        self.assertEqual(
            finalized["staged_calculation"]["finalized_plan"]["status"],
            STATUS_CURRENT,
        )
        self.assertFalse(
            finalized["staged_calculation"]["finalized_plan"][
                "geometry_changed"
            ]
        )
        self.assertEqual(
            calculated["partition"]["plan_digest"],
            materializable["plan_digest"],
        )
        self.assertEqual(
            finalized["staged_calculation"]["next_action"],
            "materialize_in_fusion",
        )

    def test_identical_explicit_calculation_reuses_the_complete_global_key(self) -> None:
        project = _project()
        session = StagedCalculationSession(project, solver_settings=SETTINGS)
        analysis = _analysis(project)
        session.synchronize(project, analysis, solver_settings=SETTINGS)
        calls = 0

        def counted_solver(raw_project: object, **kwargs: object) -> dict[str, object]:
            nonlocal calls
            calls += 1
            return solve_partition_plan(raw_project, **kwargs)

        first = session.calculate_layout(
            request_id="solve-1",
            request_revision=0,
            solver=counted_solver,
        )
        second = session.calculate_layout(
            request_id="solve-2",
            request_revision=0,
            solver=counted_solver,
        )

        self.assertEqual(calls, 1)
        self.assertEqual(
            first["partition"]["plan_digest"],
            second["partition"]["plan_digest"],
        )
        self.assertEqual(
            second["staged_calculation"]["global_layout"]["cache_status"],
            "hit",
        )

    def test_mutation_during_global_run_is_rejected_as_stale(self) -> None:
        project = _project()
        session = StagedCalculationSession(project, solver_settings=SETTINGS)
        session.synchronize(project, _analysis(project), solver_settings=SETTINGS)

        def mutating_solver(raw_project: object, **kwargs: object) -> dict[str, object]:
            result = solve_partition_plan(raw_project, **kwargs)
            changed = deepcopy(project)
            changed["contents"][0]["quantity"] = 3
            session.synchronize(
                changed,
                _analysis(changed),
                solver_settings=SETTINGS,
            )
            return result

        result = session.calculate_layout(
            request_id="solve-stale",
            request_revision=4,
            solver=mutating_solver,
        )

        self.assertIsNone(result["partition"])
        self.assertEqual(result["solver_result"]["status"], "stale_or_cancelled")
        self.assertEqual(
            result["solver_result"]["telemetry"]["stop_reason"],
            "dependencies_changed_during_global_run",
        )
        self.assertEqual(
            result["staged_calculation"]["global_layout"]["status"],
            "not_computed",
        )

    def test_source_and_solver_setting_changes_stale_both_downstream_stages(
        self,
    ) -> None:
        project = _project()
        session = StagedCalculationSession(project, solver_settings=SETTINGS)
        analysis = _analysis(project)
        session.synchronize(project, analysis, solver_settings=SETTINGS)
        session.calculate_layout(request_id="solve-1", request_revision=0)
        session.finalize_volume()

        settings_changed = session.synchronize(
            project,
            analysis,
            solver_settings={"method": "stage_stack", "effort": "normal"},
        )

        self.assertEqual(
            settings_changed["global_layout"]["status"],
            STATUS_STALE,
        )
        self.assertEqual(
            settings_changed["finalized_plan"]["status"],
            STATUS_STALE,
        )
        self.assertEqual(settings_changed["next_action"], "calculate_layout")
        with self.assertRaises(StagedCalculationError):
            session.materializable_partition()

    def test_failed_finalization_preserves_the_current_base_layout(self) -> None:
        project = _project()
        session = StagedCalculationSession(project, solver_settings=SETTINGS)
        session.synchronize(project, _analysis(project), solver_settings=SETTINGS)
        calculated = session.calculate_layout(
            request_id="solve-1",
            request_revision=0,
        )

        with self.assertRaises(StagedCalculationError):
            session.finalize_volume(certify=lambda _partition: False)

        snapshot = session.snapshot()
        self.assertEqual(snapshot["global_layout"]["status"], STATUS_CURRENT)
        self.assertEqual(
            snapshot["global_layout"]["artifact_digest"],
            calculated["staged_calculation"]["global_layout"][
                "artifact_digest"
            ],
        )
        self.assertEqual(
            snapshot["finalized_plan"]["status"],
            "not_finalized",
        )

    def test_cad_ready_is_observable_without_claiming_fusion_validation(self) -> None:
        project = _project()
        session = StagedCalculationSession(project, solver_settings=SETTINGS)
        session.synchronize(project, _analysis(project), solver_settings=SETTINGS)
        session.calculate_layout(request_id="solve-1", request_revision=0)
        session.finalize_volume()

        session.record_cad_ready(
            {
                "status": "ready_for_fusion",
                "cad_ir_digest": "a" * 64,
            }
        )
        snapshot = session.snapshot()

        self.assertEqual(snapshot["materialization"]["status"], "cad_ready")
        self.assertFalse(snapshot["materialization"]["fusion_observed"])
        self.assertEqual(snapshot["next_action"], "none")


if __name__ == "__main__":
    unittest.main()
