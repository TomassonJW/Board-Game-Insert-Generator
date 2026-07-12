from __future__ import annotations

import json
from pathlib import Path
import unittest

from board_game_insert_generator.volume_cad import build_functional_cad
from fusion_addin.BoardGameInsertGenerator.fusion_skeleton import (
    FUSION_GENERATION_MODE_COMPACT_ONLY,
    generation_plan_from_cad_ir,
)


ROOT = Path(__file__).resolve().parents[1]
FIXTURE_PATH = ROOT / "examples" / "p43_v01_functional_project.json"


class P43FunctionalSmokeFixtureTests(unittest.TestCase):
    def test_fixture_builds_a_constructible_compact_fusion_scene(self) -> None:
        project = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))

        result = build_functional_cad(project)

        self.assertEqual(result["status"], "planned_for_fusion_smoke")
        self.assertEqual(result["volume_plan"]["support"]["status"], "planned_continuous_with_hollow_fillers")
        materialization = result["materialization"]
        self.assertEqual(materialization["container_component_count"], 3)
        self.assertGreaterEqual(materialization["hollow_fill_component_count"], 1)
        self.assertGreaterEqual(materialization["solid_component_count"], 1)
        self.assertGreater(materialization["cavity_count"], 3)
        self.assertLessEqual(materialization["component_count"], 24)

        plan = generation_plan_from_cad_ir(result["cad_ir"], FUSION_GENERATION_MODE_COMPACT_ONLY)

        self.assertEqual(len(plan.blanks), materialization["component_count"])
        self.assertEqual(len(plan.cavity_cuts), materialization["cavity_count"])
        self.assertEqual(len(plan.exploded_occurrences), 0)
        self.assertEqual(len({blank.body_name for blank in plan.blanks}), len(plan.blanks))

    def test_preparation_script_uses_the_same_fixture_and_compact_mode(self) -> None:
        source = (ROOT / "scripts" / "fusion" / "prepare_p43_v01_functional_test.ps1").read_text(encoding="utf-8")

        self.assertIn("p43_v01_functional_project.json", source)
        self.assertIn("export-project-v1-cad", source)
        self.assertIn('generation_mode = "compact_only"', source)
        self.assertIn("Write-BgigFusionUiSettings", source)
        self.assertIn("install_addin.ps1", source)


if __name__ == "__main__":
    unittest.main()
