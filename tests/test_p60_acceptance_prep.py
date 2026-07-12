from __future__ import annotations

import json
from pathlib import Path
import unittest

from board_game_insert_generator.partition_cad import PARTITION_CAD_STATUS_READY, build_partition_cad
from board_game_insert_generator.partition_solver import solve_partition_plan
from board_game_insert_generator.project_v1 import normalize_project_draft
from fusion_addin.BoardGameInsertGenerator.fusion_skeleton import (
    FUSION_GENERATION_MODE_COMPACT_ONLY,
    generation_plan_from_cad_ir,
)


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "scripts" / "fusion" / "p60_mvp_project.json"
PREPARE = ROOT / "scripts" / "fusion" / "prepare_p60_mvp_acceptance.ps1"
DOC = ROOT / "docs" / "P60_FUSION_MVP_ACCEPTANCE.md"


class P60AcceptancePreparationTests(unittest.TestCase):
    def test_fixture_builds_the_exact_two_body_zero_automatic_scene(self) -> None:
        project = normalize_project_draft(json.loads(FIXTURE.read_text(encoding="utf-8"))).project
        plan = solve_partition_plan(project)
        cad = build_partition_cad(project, partition=plan)
        fusion = generation_plan_from_cad_ir(cad["cad_ir"], FUSION_GENERATION_MODE_COMPACT_ONLY)

        self.assertEqual(plan["summary"]["status"], "constructed")
        self.assertEqual(plan["summary"]["final_body_count"], 2)
        self.assertEqual(plan["summary"]["explicit_complement_count"], 0)
        self.assertEqual(plan["summary"]["automatic_body_count"], 0)
        self.assertEqual(cad["status"], PARTITION_CAD_STATUS_READY)
        self.assertEqual(cad["materialization"]["component_count"], 2)
        self.assertEqual(cad["materialization"]["cavity_count"], 3)
        self.assertEqual(fusion.module_component_count, 2)
        self.assertEqual(len(fusion.compact_occurrences), 2)
        self.assertEqual(len(fusion.exploded_occurrences), 0)

    def test_preparer_installs_exact_commit_and_leaves_only_fusion_actions(self) -> None:
        script = PREPARE.read_text(encoding="utf-8")
        for marker in (
            "install_addin.ps1", "Assert-BgigPaletteProjectRuntime",
            "bgig_installed_commit.txt", "p60_mvp_project.json",
            "Materialiser dans Fusion", "Regenerer la scene BGIG",
            "Exporter les imprimables", "P60 Fusion OK",
        ):
            self.assertIn(marker, script)
        self.assertNotIn("localhost", script)
        self.assertNotIn("navigateur externe", script)

    def test_acceptance_document_keeps_fusion_and_print_status_honest(self) -> None:
        document = DOC.read_text(encoding="utf-8")
        self.assertIn("uniquement l add-in Fusion 360", document)
        self.assertIn("human-fusion-observation-required", document)
        self.assertIn("print-validated: false", document)
        self.assertIn("deux STL", document)


if __name__ == "__main__":
    unittest.main()