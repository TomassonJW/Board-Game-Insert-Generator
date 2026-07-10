from __future__ import annotations

import json
import unittest

from context import ROOT

from board_game_insert_generator.cad_ir import build_blank_cad_scene
from board_game_insert_generator.config_loader import load_config
from board_game_insert_generator.layout import generate_basic_layout
from board_game_insert_generator.report import layout_to_json, layout_to_markdown


class BoxFillPlanReportingTests(unittest.TestCase):
    def setUp(self) -> None:
        self.config = load_config(ROOT / "examples" / "box_fill_manual_v0.json")
        self.layout = generate_basic_layout(self.config)

    def test_json_report_exposes_plan_coverage_validation_and_free_volume(self) -> None:
        payload = json.loads(layout_to_json(self.config, self.layout))

        plan = payload["box_fill_plan"]
        self.assertEqual(plan["schema_version"], "box_fill_plan.v0")
        self.assertEqual(plan["box"]["id"], "demo-game-box")
        self.assertEqual(plan["coverage"][0]["status"], "covered")
        self.assertEqual(plan["free_volumes"][0]["total_free_volume_mm3"], 205325.0)
        self.assertEqual(plan["free_volumes"][0]["qualification"], "exact_aabb_cells_v0")
        self.assertEqual(plan["validation"]["status"], "valid")

    def test_markdown_report_exposes_manual_plan_without_claiming_solver(self) -> None:
        markdown = layout_to_markdown(self.config, self.layout)

        self.assertIn("## Box fill plan", markdown)
        self.assertIn("- Manual modules: 2", markdown)
        self.assertIn("### Asset coverage", markdown)
        self.assertIn("coin-tokens | 30 | 30 | 0 | 0 | covered", markdown)
        self.assertIn("exact_aabb_cells_v0", markdown)
        self.assertIn("### Free volumes by layer", markdown)
        self.assertIn("Occupancy ratio", markdown)

    def test_cad_ir_transports_plan_as_metadata_without_components(self) -> None:
        payload = build_blank_cad_scene(self.config, self.layout).to_dict()

        plan = payload["metadata"]["box_fill_plan"]
        self.assertEqual(plan["schema_version"], "box_fill_plan.v0")
        self.assertEqual(plan["modules"][0]["id"], "coin-tray")
        self.assertEqual(plan["reservations"][0]["printable"], False)
        self.assertEqual(payload["components"], [])


if __name__ == "__main__":
    unittest.main()
