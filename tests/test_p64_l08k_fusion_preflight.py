"""Regression coverage for the deterministic P64-L08K Fusion handoff."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from board_game_insert_generator.incremental_project_state import canonical_digest
from board_game_insert_generator.project_v1 import normalize_project_draft
from board_game_insert_generator.scip_product_solver import (
    SCIP_PRODUCT_ARCHIVE_SHA256,
    SCIP_PRODUCT_ARTIFACT_DIGEST,
)


_SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "fusion" / "p64_l08k_preflight.py"
_SPEC = importlib.util.spec_from_file_location("p64_l08k_preflight", _SCRIPT_PATH)
assert _SPEC is not None and _SPEC.loader is not None
_PREFLIGHT = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_PREFLIGHT)


class P64L08KFusionPreflightTests(unittest.TestCase):
    def test_preflight_binds_runtime_evidence_and_real_limit_case(self) -> None:
        project, summary = _PREFLIGHT.prepare_fixture()

        self.assertEqual(summary["container_count"], 18)
        self.assertEqual(summary["content_count"], 20)
        self.assertEqual(summary["runtime_artifact_digest"], SCIP_PRODUCT_ARTIFACT_DIGEST)
        self.assertEqual(summary["runtime_archive_sha256"], SCIP_PRODUCT_ARCHIVE_SHA256)
        self.assertEqual(summary["expected_effort"], "deep")
        self.assertEqual(summary["expected_external_invocation_count"], 1)
        self.assertEqual(summary["expected_internal_lane_count_after_scip"], 0)
        self.assertFalse(summary["fusion_validated"])
        self.assertFalse(summary["print_validated"])
        supplied = summary.pop("preflight_digest")
        self.assertEqual(canonical_digest(summary), supplied)
        normalize_project_draft(project)

    def test_fixture_and_summary_are_written_without_hidden_state(self) -> None:
        project, summary = _PREFLIGHT.prepare_fixture()
        with TemporaryDirectory() as directory:
            fixture_path = Path(directory) / "p64-l08k-real-18x20.bgig.json"
            summary_path = Path(directory) / "p64-l08k-preflight.json"
            fixture_path.write_text(
                json.dumps(project, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            summary_path.write_text(
                json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            written_project = json.loads(fixture_path.read_text(encoding="utf-8"))
            written_summary = json.loads(summary_path.read_text(encoding="utf-8"))

        self.assertEqual(written_project, project)
        self.assertEqual(written_summary, summary)
        self.assertEqual(len(written_project["container_groups"]), 18)
        self.assertEqual(len(written_project["contents"]), 20)


if __name__ == "__main__":
    unittest.main()
