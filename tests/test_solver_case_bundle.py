from __future__ import annotations

import json
import unittest

from board_game_insert_generator.contextual_local_analysis import (
    IncrementalLocalAnalysisEngine,
)
from board_game_insert_generator.project_v1 import blank_project_v1
from board_game_insert_generator.solver_case_bundle import (
    MAX_INTERACTION_EVENTS,
    SOLVER_CASE_BUNDLE_SCHEMA_V1,
    build_solver_case_bundle,
    solver_case_capture_summary,
)


def _project() -> dict[str, object]:
    project = blank_project_v1()
    project["project_name"] = "Cas limite local"
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
            "name": "Pieces",
            "shape_kind": "square",
            "dimensions_mm": {"x": 12, "y": 12, "z": 3},
            "quantity": 2,
            "container_group_id": "g",
            "content_clearance_mm": None,
            "measurement_confidence": "exact",
        }
    ]
    return project


def _bundle(*, events: object, state: dict[str, object] | None = None) -> dict[str, object]:
    project = _project()
    engine = IncrementalLocalAnalysisEngine(project, effort_profile="quick")
    return build_solver_case_bundle(
        project,
        solver_settings={"method": "auto", "effort": "quick"},
        solver_case_state=state
        or {
            "staged_calculation": {
                "minimal_layout": {
                    "solver_result_status": "solution_found",
                    "stop_reason": "certified_incumbent",
                }
            },
            "observed_partition": {
                "minimal_layout": {"global_certificate": {"certified": True}}
            },
        },
        local_analysis=engine.snapshot(),
        container_frontiers=engine.certified_frontiers(),
        interaction_events=events,
        client_context={
            "scene_present": True,
            "dirty": True,
            "solved_stale": False,
            "document_path": "C:/private/Mon insert.bgig.json",
            "scene_artifact_identity": {
                "schema_version": "bgig.artifact_identity.v1",
                "artifact_kind": "minimal_layout",
                "artifact_digest": "a" * 64,
                "partition_plan_digest": "b" * 64,
                "cad_ir_digest": "c" * 64,
                "source_revision": 7,
                "document_path": "C:/private/file.f3d",
            },
        },
        capture_id="capture-1",
        captured_at_ms=123456,
        source_revision=7,
    )


class SolverCaseBundleTests(unittest.TestCase):
    def test_bundle_is_deterministic_complete_and_filters_values_and_paths(self) -> None:
        events = [
            {
                "sequence": 1,
                "event_type": "field_changed",
                "ui_field": "contents.quantity",
                "object_id": "c",
                "source_revision": 7,
                "elapsed_ms": 120,
                "value": "private value",
                "password": "must not survive",
                "document_path": "C:/private/project.bgig.json",
            }
        ]

        first = _bundle(events=events)
        second = _bundle(events=events)

        self.assertEqual(first, second)
        self.assertEqual(first["schema_version"], SOLVER_CASE_BUNDLE_SCHEMA_V1)
        self.assertEqual(len(first["bundle_digest"]), 64)
        self.assertEqual(first["summary"]["frontier_count"], 1)
        self.assertTrue(first["summary"]["has_observed_partition"])
        self.assertTrue(first["summary"]["has_certified_plan"])
        self.assertEqual(first["summary"]["stop_reason"], "certified_incumbent")
        event = first["interaction_trace"]["events"][0]
        self.assertEqual(
            set(event),
            {
                "sequence",
                "event_type",
                "ui_field",
                "object_id",
                "source_revision",
                "elapsed_ms",
            },
        )
        encoded = json.dumps(first, sort_keys=True).lower()
        self.assertNotIn("password", encoded)
        self.assertNotIn("c:/private", encoded)
        self.assertNotIn("private value", encoded)
        self.assertEqual(
            first["invariants"]["global_solver_invocation_count"], 0
        )
        self.assertFalse(first["invariants"]["automatic_solver_modification"])
        summary = solver_case_capture_summary(first)
        self.assertEqual(summary["bundle_digest"], first["bundle_digest"])
        self.assertFalse(summary["automatic_solver_modification"])

    def test_trace_is_bounded_and_keeps_the_most_recent_events(self) -> None:
        events = [
            {"event_type": "ui_action", "sequence": index, "elapsed_ms": index}
            for index in range(300)
        ]

        bundle = _bundle(events=events)
        trace = bundle["interaction_trace"]

        self.assertEqual(trace["event_count"], MAX_INTERACTION_EVENTS)
        self.assertEqual(trace["discarded_event_count"], 44)
        self.assertEqual(trace["events"][0]["sequence"], 44)
        self.assertEqual(trace["events"][-1]["sequence"], 299)

    def test_invalid_trace_and_secret_like_observed_fields_fail_closed(self) -> None:
        with self.assertRaisesRegex(TypeError, "must be a list"):
            _bundle(events={})
        with self.assertRaisesRegex(ValueError, "event_type is required"):
            _bundle(events=[{"sequence": 1}])
        with self.assertRaisesRegex(ValueError, "Secret-like field"):
            _bundle(events=[], state={"api_token": "not-allowed"})


if __name__ == "__main__":
    unittest.main()