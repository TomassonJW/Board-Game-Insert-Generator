import unittest

from board_game_insert_generator.operation_activity import (
    OPERATION_ACTIVITY_SCHEMA_V1,
    OperationActivityError,
    begin_operation_activity,
    finish_operation_activity,
    observe_operation_activity,
    refresh_terminal_operation_activity,
)


class OperationActivityTests(unittest.TestCase):
    def test_produces_deterministic_identity_step_and_elapsed_without_percentage(self) -> None:
        decision = begin_operation_activity(
            action="solve_project",
            operation_id="solve-42",
            source_revision=7,
            started_at_ms=1_000,
        )
        repeated = begin_operation_activity(
            action="solve_project",
            operation_id="solve-42",
            source_revision=7,
            started_at_ms=1_000,
        )
        observed = observe_operation_activity(
            decision.activity,
            observed_at_ms=2_250,
        )

        self.assertTrue(decision.accepted)
        self.assertEqual(decision, repeated)
        self.assertEqual(observed["schema_version"], OPERATION_ACTIVITY_SCHEMA_V1)
        self.assertEqual(observed["operation_id"], "solve-42")
        self.assertEqual(observed["operation_kind"], "minimal_layout_calculation")
        self.assertEqual(observed["elapsed_ms"], 1_250)
        self.assertNotIn("percentage", observed)
        self.assertNotIn("eta", observed)
        self.assertFalse(observed["cancel_supported"])
        self.assertFalse(observed["invariants"]["fake_percentage_exposed"])
        self.assertFalse(observed["invariants"]["eta_claimed"])

    def test_blocks_only_the_same_active_operation_kind(self) -> None:
        running = begin_operation_activity(
            action="materialize_project",
            operation_id="materialize-1",
            source_revision=3,
            started_at_ms=10,
        ).activity
        duplicate = begin_operation_activity(
            action="regenerate_project",
            operation_id="materialize-2",
            source_revision=3,
            started_at_ms=20,
            active_activities=(running,),
        )
        different = begin_operation_activity(
            action="validate_project",
            operation_id="analysis-1",
            source_revision=3,
            started_at_ms=20,
            active_activities=(running,),
        )

        self.assertFalse(duplicate.accepted)
        self.assertEqual(duplicate.stop_reason, "same_operation_already_active")
        self.assertEqual(
            duplicate.activity["conflicting_operation_id"],
            "materialize-1",
        )
        self.assertTrue(different.accepted)
        self.assertFalse(
            different.activity["invariants"]["different_operation_kinds_blocked"]
        )

    def test_solver_case_capture_has_its_own_identity_and_duplicate_guard(self) -> None:
        running = begin_operation_activity(
            action="capture_solver_case",
            operation_id="capture-1",
            source_revision=5,
            started_at_ms=100,
        ).activity
        duplicate = begin_operation_activity(
            action="capture_solver_case",
            operation_id="capture-2",
            source_revision=5,
            started_at_ms=120,
            active_activities=(running,),
        )
        different = begin_operation_activity(
            action="solve_project",
            operation_id="solve-1",
            source_revision=5,
            started_at_ms=120,
            active_activities=(running,),
        )

        self.assertEqual(running["operation_kind"], "solver_case_capture")
        self.assertFalse(duplicate.accepted)
        self.assertEqual(
            duplicate.activity["conflicting_operation_id"], "capture-1"
        )
        self.assertTrue(different.accepted)

    def test_finishes_with_exact_identity_and_explicit_stop_reason(self) -> None:
        started = begin_operation_activity(
            action="validate_project",
            operation_id="analysis-9",
            source_revision=None,
            started_at_ms=500,
        ).activity
        finished = finish_operation_activity(
            started,
            finished_at_ms=875,
            succeeded=True,
            stop_reason="local_analysis_ready",
        )

        self.assertEqual(finished["status"], "completed")
        self.assertEqual(finished["operation_id"], started["operation_id"])
        self.assertEqual(finished["current_step"], started["current_step"])
        self.assertEqual(finished["elapsed_ms"], 375)
        self.assertEqual(finished["stop_reason"], "local_analysis_ready")
        self.assertFalse(
            finished["invariants"]["stale_or_cancelled_is_user_cancellation"]
        )

    def test_refreshes_terminal_elapsed_after_adapter_work(self) -> None:
        started = begin_operation_activity(
            action="materialize_project",
            operation_id="materialize-7",
            source_revision=2,
            started_at_ms=1_000,
        ).activity
        prepared = finish_operation_activity(
            started,
            finished_at_ms=1_400,
            succeeded=True,
            stop_reason="ready_for_fusion",
        )
        synchronized = refresh_terminal_operation_activity(
            prepared,
            observed_at_ms=2_250,
            stop_reason="scene_synchronized",
        )

        self.assertEqual(synchronized["operation_id"], "materialize-7")
        self.assertEqual(synchronized["elapsed_ms"], 1_250)
        self.assertEqual(synchronized["stop_reason"], "scene_synchronized")
        self.assertEqual(synchronized["status"], "completed")


    def test_refuses_unknown_actions_and_invalid_identity(self) -> None:
        with self.assertRaises(OperationActivityError):
            begin_operation_activity(
                action="delete_everything",
                operation_id="x",
                source_revision=0,
                started_at_ms=0,
            )
        with self.assertRaises(OperationActivityError):
            begin_operation_activity(
                action="solve_project",
                operation_id="",
                source_revision=0,
                started_at_ms=0,
            )


if __name__ == "__main__":
    unittest.main()
