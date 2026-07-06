from __future__ import annotations

import json
import unittest

from context import ROOT

from board_game_insert_generator.config_loader import load_config
from board_game_insert_generator.layout import generate_basic_layout
from board_game_insert_generator.report import layout_to_json, layout_to_markdown

class ReportTests(unittest.TestCase):
    def test_markdown_report_exposes_summary_and_tolerances(self) -> None:
        config = load_config(ROOT / "examples" / "simple_box.json")
        result = generate_basic_layout(config)

        report = layout_to_markdown(config, result)

        self.assertIn("## Summary", report)
        self.assertIn("- Layout strategy: `row_fill`", report)
        self.assertIn("- Requested modules: 3", report)
        self.assertIn("- Generated instances: 4", report)
        self.assertIn("## Layout comparison", report)
        self.assertIn("| `row_fill` | ok |", report)
        self.assertIn("| `grid` | ok |", report)
        self.assertIn("Simple score: higher means", report)
        self.assertIn("## Face classifications", report)
        self.assertIn("x_min: peripheral", report)
        self.assertIn("x_max: neighbor", report)
        self.assertIn("## Applied tolerances", report)
        self.assertIn("| cards-main-01 | x_min | peripheral | 0.80 mm |", report)
        self.assertIn("peripheral_clearance_mm + printer_compensation_mm", report)
        self.assertIn("neighbor_half_module_gap", report)
        self.assertIn("## Tolerance profile", report)
        self.assertIn("- Print profile: `default` (Default V0 values)", report)
        self.assertIn("Preset values are experimental starting points", report)
        self.assertIn("| Module gap | 0.60 mm |", report)

    def test_reports_expose_planned_cavities(self) -> None:
        config = load_config(ROOT / "examples" / "simple_tray.json")
        result = generate_basic_layout(config)

        markdown = layout_to_markdown(config, result)
        payload = json.loads(layout_to_json(config, result))

        self.assertIn("## Planned cavities", markdown)
        self.assertIn("| token-tray-01 | token-pocket | tokens |", markdown)
        self.assertIn("abstract_only", markdown)
        self.assertEqual(payload["summary"]["planned_cavity_count"], 1)
        self.assertEqual(payload["module_requests"][0]["cavities"][0]["id"], "token-pocket")
        body_cavity = payload["printable_bodies"][0]["planned_cavities"][0]
        self.assertEqual(body_cavity["functional_type"], "tokens")
        self.assertEqual(body_cavity["local_origin_mm"], {"x": 4.0, "y": 4.0, "z": 1.2})
        self.assertEqual(body_cavity["status"], "abstract_only")
        self.assertEqual(body_cavity["clearance_source"], "explicit")
    def test_reports_expose_abstract_cavity_features(self) -> None:
        config = load_config(ROOT / "examples" / "simple_finger_notch_tray.json")
        result = generate_basic_layout(config)

        markdown = layout_to_markdown(config, result)
        payload = json.loads(layout_to_json(config, result))

        self.assertIn("## Planned cavity features", markdown)
        self.assertIn("front-half-moon-notch | half_moon_notch | front_center | top_open_half_moon_notch", markdown)
        self.assertIn("rounded-floor-intent | rounded_floor | cavity_floor", markdown)
        self.assertIn("fusion=abstract_profile_with_validated_rectangular_fallback", markdown)
        self.assertEqual(payload["summary"]["planned_cavity_count"], 1)
        self.assertEqual(payload["summary"]["planned_feature_count"], 2)
        feature = payload["printable_bodies"][0]["planned_cavities"][0]["features"][0]
        self.assertEqual(feature["kind"], "half_moon_notch")
        self.assertEqual(feature["placement"], "front_center")
        self.assertEqual(feature["size_mm"], {"x": 18.0, "y": 4.0, "z": 10.0})
        self.assertEqual(feature["radius_mm"], 9.0)
        self.assertEqual(feature["status"], "abstract_only")
        self.assertEqual(feature["fusion_generation"], "not_implemented")
        self.assertEqual(feature["taxonomy"]["taxonomy"], "top_open_half_moon_notch")
        self.assertEqual(feature["taxonomy"]["fusion_fallback_taxonomy"], "top_open_rectangular_notch")
        self.assertFalse(feature["taxonomy"]["print_validated"])

    def test_json_report_exposes_diagnostic_fields(self) -> None:
        config = load_config(ROOT / "examples" / "simple_box.json")
        result = generate_basic_layout(config)

        report = json.loads(layout_to_json(config, result))

        self.assertEqual(report["layout"]["strategy"], "row_fill")
        self.assertEqual(report["print_profile"]["id"], "default")
        self.assertEqual(report["print_profile"]["label"], "Default V0 values")
        self.assertIn("not physical validation", report["print_profile"]["note"])
        self.assertEqual(report["summary"]["requested_module_count"], 3)
        self.assertEqual(report["summary"]["expanded_instance_count"], 4)
        self.assertEqual(report["summary"]["warning_count"], 2)
        self.assertEqual(
            [entry["strategy"] for entry in report["layout_comparison"]],
            ["row_fill", "grid"],
        )
        self.assertEqual(report["layout_comparison"][0]["status"], "ok")
        self.assertIn("occupation_percent", report["layout_comparison"][0])
        self.assertIn("score", report["layout_comparison"][0])
        first_body = report["printable_bodies"][0]
        self.assertEqual(first_body["face_classifications"][0]["face"], "x_min")
        self.assertEqual(first_body["face_classifications"][0]["role"], "peripheral")
        self.assertEqual(first_body["face_classifications"][1]["role"], "neighbor")
        self.assertEqual(
            first_body["face_classifications"][1]["neighbor_instance_id"],
            "cards-main-02",
        )
        self.assertEqual(first_body["applied_tolerances"][0]["face"], "x_min")
        self.assertEqual(first_body["applied_tolerances"][0]["role"], "peripheral")
        self.assertEqual(first_body["applied_tolerances"][0]["offset_mm"], 0.8)
        self.assertEqual(
            first_body["applied_tolerances"][0]["rule_id"],
            "peripheral_clearance",
        )
        self.assertTrue(first_body["applied_tolerances"][0]["receives_clearance"])
        self.assertEqual(first_body["applied_tolerances"][5]["rule_id"], "functional_vertical_lid_clearance")
        self.assertEqual(len(report["module_requests"]), 3)
        self.assertEqual(report["module_requests"][0]["id"], "cards-main")

if __name__ == "__main__":
    unittest.main()
