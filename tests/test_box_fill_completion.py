from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from context import ROOT

from board_game_insert_generator.box_fill import (
    analyze_box_fill_plan,
    derive_box_fill_plan_from_executable_asset_plan,
)
from board_game_insert_generator.cli import main
from board_game_insert_generator.config_loader import load_config
from board_game_insert_generator.validation import validate_config


class BoxFillPlanCompletionTests(unittest.TestCase):
    def test_valid_fixture_has_exact_free_cells_and_volume_conservation(self) -> None:
        config = load_config(ROOT / "examples" / "box_fill_valid_v0.json")
        assert config.box_fill_plan is not None

        analysis = analyze_box_fill_plan(config.box_fill_plan)
        free = analysis.free_volume

        self.assertEqual(len(config.box_fill_plan.modules), 3)
        self.assertTrue(analysis.valid)
        self.assertEqual(free.qualification, "exact_aabb_cells_v0")
        self.assertGreater(len(free.regions), 0)
        self.assertAlmostEqual(
            free.total_box_volume_mm3,
            free.occupied_module_volume_mm3 + free.occupied_reservation_volume_mm3 + free.total_free_volume_mm3,
        )
        self.assertEqual(analysis.metrics["coverage_ratio"], 1.0)

    def test_invalid_fixtures_expose_actionable_codes(self) -> None:
        expected = {
            "box_fill_collision_v0.json": "BOX_FILL_MODULE_COLLISION",
            "box_fill_outside_v0.json": "BOX_FILL_VOLUME_OUTSIDE_BOX",
            "box_fill_reservation_collision_v0.json": "BOX_FILL_MODULE_RESERVATION_COLLISION",
            "box_fill_partial_coverage_v0.json": "BOX_FILL_ASSET_UNCOVERED",
            "box_fill_overallocation_v0.json": "BOX_FILL_ALLOCATION_OVER_CAPACITY",
        }
        for filename, code in expected.items():
            with self.subTest(filename=filename):
                config = load_config(ROOT / "examples" / filename)
                issues = validate_config(config)
                self.assertIn(code, {issue.code for issue in issues})
                assert config.box_fill_plan is not None
                diagnostic = analyze_box_fill_plan(config.box_fill_plan).to_dict()["validation"]["issues"][0]
                self.assertIn("severity", diagnostic)
                self.assertIn("corrective_action", diagnostic)
                self.assertIn("constraint_ref", diagnostic)

    def test_bridge_preserves_source_and_does_not_invent_reservations(self) -> None:
        config = load_config(ROOT / "examples" / "box_fill_manual_v0.json")
        derived = derive_box_fill_plan_from_executable_asset_plan(
            config,
            {
                "plan_id": "asset-module-plan:test",
                "generated_modules": [{"module_id": "derived-token-tray", "source_asset_ids": ["coin-tokens"]}],
                "placements": [{
                    "module_id": "derived-token-tray",
                    "candidate_id": "candidate:test",
                    "placement_source": "grid_placement",
                    "origin_mm": {"x": 0.0, "y": 0.0, "z": 0.0},
                    "size_mm": {"x": 40.0, "y": 30.0, "z": 12.0},
                }],
            },
        )

        self.assertEqual(derived.metadata["source"], "derived_from_executable_asset_plan")
        self.assertEqual(derived.reservations, ())
        self.assertEqual(derived.modules[0].source, "derived_from_executable_asset_plan")
        self.assertEqual(derived.allocations[0].asset_id, "coin-tokens")
        self.assertIn("bridge_warnings", derived.metadata)

    def test_cli_box_fill_commands_have_stable_exit_codes(self) -> None:
        valid = ROOT / "examples" / "box_fill_valid_v0.json"
        invalid = ROOT / "examples" / "box_fill_collision_v0.json"
        self.assertEqual(main(["validate-box-fill", str(valid)]), 0)
        self.assertEqual(main(["validate-box-fill", str(invalid)]), 2)
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "box_fill.json"
            self.assertEqual(main(["export-box-fill-plan", str(valid), "--output", str(output)]), 0)
            payload = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(payload["schema_version"], "box_fill_plan.v0")
            self.assertEqual(payload["free_volumes"][0]["qualification"], "exact_aabb_cells_v0")


if __name__ == "__main__":
    unittest.main()
