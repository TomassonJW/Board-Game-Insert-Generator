"""Couverture du handoff Fusion combiné P64-L09V."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from board_game_insert_generator.free_3d_plan_adapter import prepare_free_3d_problem
from board_game_insert_generator.incremental_project_state import canonical_digest
from board_game_insert_generator.project_v1 import normalize_project_draft
from board_game_insert_generator.scip_product_solver import (
    SCIP_PRODUCT_ARCHIVE_SHA256,
    SCIP_PRODUCT_ARTIFACT_DIGEST,
)


_SCRIPT_PATH = (
    Path(__file__).resolve().parents[1] / "scripts" / "fusion" / "p64_l09v_preflight.py"
)
_SPEC = importlib.util.spec_from_file_location("p64_l09v_preflight", _SCRIPT_PATH)
assert _SPEC is not None and _SPEC.loader is not None
_PREFLIGHT = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_PREFLIGHT)


class P64L09VFusionPreflightTests(unittest.TestCase):
    def test_preflight_binds_three_public_cases_and_runtime_invariants(self) -> None:
        projects, summary = _PREFLIGHT.prepare_fixtures()

        self.assertEqual(summary["addin_version"], "0.1.63")
        self.assertEqual(
            set(projects),
            {"anti_fall", "stable_bridge", "tray_finalization"},
        )
        self.assertEqual(
            summary["support_proofs"]["anti_fall_status"],
            "falls_through_opening",
        )
        self.assertTrue(summary["support_proofs"]["anti_fall_has_lid_ignored"])
        self.assertEqual(
            summary["support_proofs"]["bridge_status"],
            "bridged_on_material",
        )
        self.assertTrue(
            summary["support_proofs"]["bridge_stable_support_polygon"]
        )
        self.assertEqual(
            summary["cases"]["stable_bridge"]["quick_control_placement_count"],
            3,
        )
        self.assertEqual(
            summary["cases"]["tray_finalization"]["top_inset_zone_count"],
            1,
        )
        self.assertEqual(
            summary["expected_solver_settings"],
            {"method": "auto", "effort": "deep"},
        )
        self.assertEqual(
            summary["scip_runtime_artifact_digest"],
            SCIP_PRODUCT_ARTIFACT_DIGEST,
        )
        self.assertEqual(
            summary["scip_runtime_archive_sha256"],
            SCIP_PRODUCT_ARCHIVE_SHA256,
        )
        self.assertFalse(summary["fusion_validated"])
        self.assertFalse(summary["print_validated"])
        supplied = summary.pop("preflight_digest")
        self.assertEqual(canonical_digest(summary), supplied)
        for project in projects.values():
            normalize_project_draft(project)
            preparation = prepare_free_3d_problem(project)
            self.assertEqual(preparation.status, "ready")

    def test_fixtures_and_summary_are_written_without_private_data(self) -> None:
        projects, summary = _PREFLIGHT.prepare_fixtures()
        with TemporaryDirectory() as directory:
            output = Path(directory)
            for key, project in projects.items():
                path = output / _PREFLIGHT.FIXTURE_FILENAMES[key]
                path.write_text(
                    json.dumps(project, ensure_ascii=False, indent=2) + "\n",
                    encoding="utf-8",
                )
            summary_path = output / "p64-l09v-preflight-summary.json"
            summary_path.write_text(
                json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )

            written = {
                key: json.loads(
                    (output / _PREFLIGHT.FIXTURE_FILENAMES[key]).read_text(
                        encoding="utf-8"
                    )
                )
                for key in projects
            }
            written_summary = json.loads(summary_path.read_text(encoding="utf-8"))

        self.assertEqual(written, projects)
        self.assertEqual(written_summary, summary)
        serialized = json.dumps(written, ensure_ascii=False).lower()
        self.assertNotIn("private", serialized)
        self.assertNotIn("thomas", serialized)
        self.assertTrue(
            all(
                "p64-l09v" in value["project_name"].lower()
                for value in written.values()
            )
        )


if __name__ == "__main__":
    unittest.main()
