from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from context import ROOT

from board_game_insert_generator.cad_ir import build_blank_cad_scene
from board_game_insert_generator.config_loader import ConfigError, load_config
from board_game_insert_generator.layout import generate_basic_layout
from board_game_insert_generator.report import layout_to_json, layout_to_markdown
from board_game_insert_generator.validation import validate_config


class AssetModelTests(unittest.TestCase):
    def test_loads_assets_without_deriving_modules(self) -> None:
        config = load_config(ROOT / "examples" / "simple_assets.json")

        self.assertEqual(len(config.assets), 2)
        self.assertEqual(config.assets[0].id, "main-board")
        self.assertEqual(config.assets[0].reservation_ref, "board-and-rules-reservation")
        self.assertEqual(config.assets[1].module_hint, "cards-stack")
        self.assertEqual(len(config.modules), 2)
        self.assertEqual(validate_config(config), [])

    def test_reports_assets_as_loaded_only(self) -> None:
        config = load_config(ROOT / "examples" / "simple_assets.json")
        layout = generate_basic_layout(config)

        markdown = layout_to_markdown(config, layout)
        payload = json.loads(layout_to_json(config, layout))

        self.assertIn("## Assets", markdown)
        self.assertIn("main-board | board | 1 single", markdown)
        self.assertEqual(payload["summary"]["asset_count"], 2)
        self.assertEqual(payload["assets"][0]["status"], "loaded_only")


    def test_reports_deterministic_variant_comparison(self) -> None:
        config = load_config(ROOT / "examples" / "simple_assets.json")
        layout = generate_basic_layout(config)

        markdown = layout_to_markdown(config, layout)
        payload = json.loads(layout_to_json(config, layout))

        self.assertIn("## Variant comparison", markdown)
        self.assertIn("layout:row_fill", markdown)
        self.assertIn("layout:grid", markdown)
        variants = payload["variant_comparison"]
        self.assertEqual([entry["variant_id"] for entry in variants], ["layout:row_fill", "layout:grid"])
        self.assertEqual(variants[0]["status"], "explain_only")
        self.assertIn("compactness", variants[0]["subscores"])
        self.assertTrue(any("assets are loaded as metadata only" in reason for reason in variants[0]["reasons"]))

    def test_rejected_variants_include_structured_actionable_reasons(self) -> None:
        config = _load_payload(_grid_rejection_payload())
        layout = generate_basic_layout(config)

        markdown = layout_to_markdown(config, layout)
        payload = json.loads(layout_to_json(config, layout))

        grid_variant = next(entry for entry in payload["variant_comparison"] if entry["variant_id"] == "layout:grid")
        self.assertEqual(grid_variant["status"], "rejected")
        self.assertEqual(grid_variant["rejection_reasons"][0]["code"], "DOES_NOT_FIT")
        self.assertEqual(grid_variant["rejection_reasons"][0]["category"], "fit")
        self.assertIn("box.inner_dimensions_mm", grid_variant["rejection_reasons"][0]["constraint_ref"])
        self.assertIn("Reduce module footprint", grid_variant["rejection_reasons"][0]["actionable"])
        self.assertIn("### Rejected variant details", markdown)
        self.assertIn("DOES_NOT_FIT", markdown)

    def test_reports_module_candidates_without_deriving_modules(self) -> None:
        config = load_config(ROOT / "examples" / "simple_assets.json")
        layout = generate_basic_layout(config)

        markdown = layout_to_markdown(config, layout)
        payload = json.loads(layout_to_json(config, layout))

        self.assertIn("## Module candidates from assets", markdown)
        self.assertEqual(payload["summary"]["module_candidate_count"], 2)
        self.assertEqual(payload["summary"]["candidate_only_module_count"], 1)
        self.assertEqual(len(config.modules), 2)
        board_candidate = payload["module_candidates"][0]
        card_candidate = payload["module_candidates"][1]
        self.assertEqual(board_candidate["status"], "reservation_only")
        self.assertIsNone(board_candidate["suggested_module"])
        self.assertEqual(card_candidate["status"], "candidate_only")
        self.assertEqual(card_candidate["suggested_module"]["id"], "candidate-module:card-deck")
        self.assertEqual(card_candidate["suggested_module"]["functional_type"], "sleeved_cards")
        self.assertIn("candidate-module:card-deck", markdown)
        self.assertIn("## Asset candidate variants", markdown)
        self.assertEqual(payload["asset_candidate_variants"][0]["variant_id"], "asset-candidates:row_fill")
        self.assertEqual(payload["asset_candidate_variants"][0]["status"], "recommended")
        self.assertTrue(payload["asset_candidate_variants"][0]["placements"][0]["rotated"])
        self.assertEqual(payload["recommended_asset_candidate_variant"]["variant_id"], "asset-candidates:row_fill")

    def test_cad_ir_transports_assets_and_candidates_as_metadata_only(self) -> None:
        config = load_config(ROOT / "examples" / "simple_assets.json")
        layout = generate_basic_layout(config)

        payload = build_blank_cad_scene(config, layout).to_dict()

        self.assertEqual(payload["metadata"]["assets"][0]["id"], "main-board")
        self.assertEqual(payload["metadata"]["module_candidates"][1]["candidate_id"], "asset-candidate:card-deck")
        self.assertEqual(payload["metadata"]["module_candidates"][1]["status"], "candidate_only")
        self.assertEqual(payload["metadata"]["asset_candidate_variants"][0]["status"], "recommended")
        self.assertEqual(payload["metadata"]["recommended_asset_candidate_variant"]["variant_id"], "asset-candidates:row_fill")
        operation_kinds = [
            operation["kind"]
            for component in payload["components"]
            for operation in component["body"]["operations"]
        ]
        self.assertEqual(operation_kinds, ["create_rectangular_prism", "create_rectangular_prism"])

    def test_groups_compatible_assets_into_report_only_candidate(self) -> None:
        config = load_config(ROOT / "examples" / "simple_asset_grouping.json")
        layout = generate_basic_layout(config)

        markdown = layout_to_markdown(config, layout)
        payload = json.loads(layout_to_json(config, layout))
        scene = build_blank_cad_scene(config, layout).to_dict()

        self.assertEqual(len(config.modules), 1)
        self.assertEqual(payload["summary"]["module_candidate_count"], 1)
        candidate = payload["module_candidates"][0]
        self.assertEqual(candidate["derivation"], "asset_group_dimension_padding")
        self.assertEqual(candidate["source_asset_ids"], ["coin-tokens", "status-tokens"])
        self.assertEqual(candidate["quantity"], {"count": 42, "grouping": "grouped_assets"})
        self.assertEqual(candidate["status"], "candidate_only")
        self.assertIn("Compatible assets share kind", candidate["reasons"][0])
        self.assertEqual(payload["asset_candidate_variants"][0]["status"], "recommended")
        self.assertEqual(scene["metadata"]["module_candidates"][0]["source_asset_ids"], ["coin-tokens", "status-tokens"])
        self.assertIn("asset-group-candidate", markdown)

    def test_reports_rejected_asset_candidate_variant_with_reasons(self) -> None:
        config = load_config(ROOT / "examples" / "simple_asset_rejected_variant.json")
        layout = generate_basic_layout(config)

        markdown = layout_to_markdown(config, layout)
        payload = json.loads(layout_to_json(config, layout))
        scene = build_blank_cad_scene(config, layout).to_dict()

        variant = payload["asset_candidate_variants"][0]
        self.assertEqual(variant["status"], "rejected")
        self.assertFalse(variant["recommended"])
        self.assertIn(variant["rejection_reasons"][0]["code"], {"DOES_NOT_FIT", "DIMENSIONS_INCOMPATIBLE"})
        self.assertIsNone(payload["recommended_asset_candidate_variant"])
        self.assertEqual(scene["metadata"]["asset_candidate_variants"][0]["status"], "rejected")
        self.assertIn("Recommended variant: none", markdown)


    def test_builds_executable_asset_plan_with_greedy_grid_placement(self) -> None:
        config = load_config(ROOT / "examples" / "simple_asset_executable_plan.json")
        layout = generate_basic_layout(config)

        markdown = layout_to_markdown(config, layout)
        payload = json.loads(layout_to_json(config, layout))
        scene = build_blank_cad_scene(config, layout).to_dict()

        self.assertEqual(len(config.modules), 1)
        self.assertEqual(validate_config(config), [])
        plan = payload["executable_asset_plan"]
        self.assertEqual(plan["status"], "placed")
        self.assertEqual(plan["summary"]["generated_module_count"], 1)
        self.assertEqual(plan["summary"]["placed_module_count"], 1)
        self.assertEqual(plan["summary"]["rejected_module_count"], 0)
        generated = plan["generated_modules"][0]
        self.assertEqual(generated["source_asset_ids"], ["coin-tokens", "status-tokens"])
        self.assertEqual(generated["dimensions_mm"], {"x": 25.6, "y": 25.6, "z": 9.8})
        self.assertEqual(generated["asset_fit_size_mm"], {"x": 23.2, "y": 23.2, "z": 8.6})
        self.assertEqual(generated["printable_body_size_mm"], {"x": 25.6, "y": 25.6, "z": 9.8})
        self.assertEqual(generated["clearance_applied"]["internal_asset_clearance_mm"], 0.6)
        placement = plan["placements"][0]
        self.assertEqual(placement["origin_units"], {"x": 1, "y": 0, "z": 0})
        self.assertEqual(placement["size_units"], {"x": 1, "y": 1, "z": 1})
        self.assertEqual(placement["origin_mm"], {"x": 30, "y": 0, "z": 0})
        self.assertEqual(placement["size_mm"], {"x": 25.6, "y": 25.6, "z": 9.8})
        self.assertEqual(placement["theoretical_grid_extent_mm"], {"x": 30, "y": 30, "z": 10})
        self.assertEqual(placement["asset_fit_size_mm"], {"x": 23.2, "y": 23.2, "z": 8.6})
        self.assertEqual(placement["printable_body_size_mm"], {"x": 25.6, "y": 25.6, "z": 9.8})
        self.assertIn("## Executable asset module plan", markdown)
        self.assertIn("theoretical grid extent", markdown)
        self.assertIn("greedy_z_y_x_first_free_span", markdown)
        self.assertEqual(scene["metadata"]["executable_asset_plan"]["status"], "placed")
        self.assertEqual(scene["metadata"]["executable_asset_plan"]["placements"][0]["origin_units"], {"x": 1, "y": 0, "z": 0})

    def test_builds_multilayer_executable_asset_plan(self) -> None:
        config = load_config(ROOT / "examples" / "simple_multilayer_grid_scene.json")
        layout = generate_basic_layout(config)

        markdown = layout_to_markdown(config, layout)
        payload = json.loads(layout_to_json(config, layout))
        scene = build_blank_cad_scene(config, layout).to_dict()

        self.assertEqual(validate_config(config), [])
        plan = payload["executable_asset_plan"]
        self.assertEqual(plan["status"], "placed")
        self.assertEqual(plan["summary"]["generated_module_count"], 2)
        self.assertEqual(plan["summary"]["placed_module_count"], 2)
        self.assertEqual(plan["summary"]["multi_layer_module_count"], 1)
        self.assertEqual(plan["summary"]["z_placed_module_count"], 1)
        self.assertEqual(plan["summary"]["height_variant_count"], 2)
        self.assertEqual(
            plan["placements"][0]["origin_units"],
            {"x": 1, "y": 0, "z": 0},
        )
        self.assertEqual(plan["placements"][0]["size_units"], {"x": 3, "y": 3, "z": 1})
        self.assertEqual(plan["placements"][0]["size_mm"], {"x": 61.6, "y": 61.6, "z": 7.8})
        self.assertEqual(plan["placements"][0]["theoretical_grid_extent_mm"], {"x": 90, "y": 90, "z": 10})
        self.assertEqual(plan["placements"][0]["asset_fit_size_mm"], {"x": 59.2, "y": 59.2, "z": 6.6})
        self.assertEqual(
            plan["placements"][1]["origin_units"],
            {"x": 0, "y": 0, "z": 1},
        )
        self.assertEqual(plan["placements"][1]["size_units"], {"x": 2, "y": 2, "z": 2})
        self.assertEqual(plan["placements"][1]["origin_mm"], {"x": 0, "y": 0, "z": 10})
        self.assertEqual(plan["placements"][1]["size_mm"], {"x": 37.6, "y": 37.6, "z": 17.8})
        self.assertEqual(plan["placements"][1]["theoretical_grid_extent_mm"], {"x": 60, "y": 60, "z": 20})
        self.assertEqual(plan["placements"][1]["printable_body_size_mm"], {"x": 37.6, "y": 37.6, "z": 17.8})
        self.assertIn("Multi-layer generated modules: 1", markdown)
        self.assertIn("Generated modules with Z placement: 1", markdown)
        self.assertEqual(
            scene["metadata"]["executable_asset_plan"]["summary"]["multi_layer_module_count"],
            1,
        )
        self.assertEqual(
            scene["metadata"]["executable_asset_plan"]["placements"][1]["origin_units"],
            {"x": 0, "y": 0, "z": 1},
        )

    def test_rejects_unknown_asset_field(self) -> None:
        payload = _asset_payload()
        payload["assets"][0]["solver_hint"] = "not-yet"

        with self.assertRaisesRegex(ConfigError, "Unknown field"):
            _load_payload(payload)

    def test_validation_reports_unknown_reservation_ref(self) -> None:
        payload = _asset_payload()
        payload["assets"][0]["reservation_ref"] = "missing-zone"
        config = _load_payload(payload)

        keys = _issue_keys(validate_config(config))

        self.assertIn(("assets[0].reservation_ref", "ASSET_UNKNOWN_RESERVATION"), keys)

    def test_validation_reports_unknown_module_hint(self) -> None:
        payload = _asset_payload()
        payload["assets"][1]["module_hint"] = "missing-module"
        config = _load_payload(payload)

        keys = _issue_keys(validate_config(config))

        self.assertIn(("assets[1].module_hint", "ASSET_UNKNOWN_MODULE_HINT"), keys)

    def test_unknown_z_allows_zero_asset_z(self) -> None:
        payload = _asset_payload()
        payload["assets"][0]["dimensions_mm"]["z"] = 0
        payload["assets"][0]["dimension_confidence"] = "unknown_z"
        config = _load_payload(payload)

        self.assertNotIn(("assets[0].dimensions_mm.z", "NOT_POSITIVE"), _issue_keys(validate_config(config)))


def _asset_payload() -> dict:
    return json.loads((ROOT / "examples" / "simple_assets.json").read_text(encoding="utf-8"))


def _grid_rejection_payload() -> dict:
    payload = json.loads((ROOT / "examples" / "simple_box.json").read_text(encoding="utf-8"))
    payload["project_name"] = "Variant rejection fixture"
    payload["box"]["inner_dimensions_mm"] = {"x": 100, "y": 80, "z": 50}
    payload["box"]["usable_height_mm"] = 40
    payload["box"]["lid_clearance_mm"] = 10
    payload["modules"] = [
        _fixture_module("wide-a", 60, 30, 100),
        _fixture_module("narrow-a", 40, 30, 90),
        _fixture_module("wide-b", 60, 30, 80),
        _fixture_module("narrow-b", 40, 30, 70),
    ]
    return payload


def _fixture_module(module_id: str, x: float, y: float, priority: int) -> dict:
    return {
        "id": module_id,
        "name": module_id,
        "functional_type": "tokens",
        "min_dimensions_mm": {"x": x, "y": y},
        "height_mm": 20,
        "priority": priority,
        "allow_rotation": False,
        "quantity": 1,
    }


def _load_payload(payload: dict):
    with tempfile.TemporaryDirectory() as temporary_directory:
        path = Path(temporary_directory) / "config.json"
        path.write_text(json.dumps(payload), encoding="utf-8")
        return load_config(path)


def _issue_keys(issues) -> set[tuple[str, str]]:
    return {(issue.field, issue.code) for issue in issues}


if __name__ == "__main__":
    unittest.main()