from __future__ import annotations

import json
import os
from pathlib import Path
from tempfile import TemporaryDirectory
import sys
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
ADDIN = ROOT / "fusion_addin" / "BoardGameInsertGenerator"
sys.path.insert(0, str(ADDIN))

from dev_action_log import (  # noqa: E402
    DEV_ACTION_LOG_EVENT_SCHEMA_V1,
    DevActionLogError,
    append_dev_action_event,
)


class DevActionLogTests(unittest.TestCase):
    def event(self, **overrides: object) -> dict[str, object]:
        value: dict[str, object] = {
            "schema": DEV_ACTION_LOG_EVENT_SCHEMA_V1,
            "session_id": "session-mrxlog01-ab12",
            "sequence": 1,
            "occurred_at_ms": 123456,
            "event_type": "button_pressed",
            "source_revision": 4,
            "active_view": "contents",
            "details": {
                "action": "add-selected-content",
                "object_id": "group:g1",
            },
        }
        value.update(overrides)
        return value

    def test_appends_compact_events_and_deduplicates_project_snapshots(self) -> None:
        project = {
            "schema_version": "bgig.project.v1",
            "project_name": "Mon insert",
            "box": {"inner_dimensions_mm": {"x": 200, "y": 150, "z": 60}},
            "container_groups": [],
            "contents": [],
        }
        with TemporaryDirectory() as temp_dir, patch.dict(
            os.environ,
            {"BGIG_USER_DATA_DIR": temp_dir},
        ):
            first = append_dev_action_event(
                self.event(project_snapshot=project),
                ADDIN,
            )
            second = append_dev_action_event(
                self.event(
                    sequence=2,
                    event_type="bridge_response",
                    project_snapshot=project,
                    details={
                        "action": "validate_project",
                        "status": "ready",
                        "global_void_reuse": {
                            "status": "global_solve_required",
                            "stop_reason": "no_fixed_world_position",
                        },
                    },
                ),
                ADDIN,
            )

            log_path = Path(str(first["log_path"]))
            lines = [
                json.loads(line)
                for line in log_path.read_text(encoding="utf-8").splitlines()
            ]
            snapshots = list((log_path.parent / "snapshots").glob("*.bgig.json"))
            log_text = log_path.read_text(encoding="utf-8")

        self.assertEqual(first["log_path"], second["log_path"])
        self.assertEqual([line["sequence"] for line in lines], [1, 2])
        self.assertEqual(len(snapshots), 1)
        self.assertEqual(
            lines[0]["project_snapshot"]["digest"],
            lines[1]["project_snapshot"]["digest"],
        )
        self.assertEqual(
            lines[1]["details"]["global_void_reuse"]["status"],
            "global_solve_required",
        )
        self.assertNotIn("Mon insert", log_text)

    def test_rejects_paths_secrets_and_unsafe_session_ids(self) -> None:
        for event in (
            self.event(details={"document_path": "C:/private/project.json"}),
            self.event(details={"api_token": "secret"}),
            self.event(session_id="../../escape"),
            self.event(project_snapshot={"file_path": "C:/private/project.json"}),
        ):
            with self.subTest(event=event), self.assertRaises(DevActionLogError):
                append_dev_action_event(event, ADDIN)


if __name__ == "__main__":
    unittest.main()
