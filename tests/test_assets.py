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
        self.assertEqual(candidate["derivation"], "count_aware_stacked_asset_piles")
        self.assertEqual(candidate["source_asset_ids"], ["coin-tokens", "status-tokens"])
        self.assertEqual(candidate["quantity"], {"count": 42, "grouping": "grouped_assets"})
        self.assertEqual(candidate["status"], "candidate_only")
        self.assertTrue(candidate["suggested_module"]["storage_sizing"]["count_aware_applied"])
        self.assertEqual(candidate["suggested_module"]["storage_sizing"]["total_count_read"], 42)
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


    def test_count_aware_fixture_rejects_when_manual_blocker_prevents_capacity_span(self) -> None:
        config = load_config(ROOT / "examples" / "simple_asset_executable_plan.json")
        layout = generate_basic_layout(config)

        markdown = layout_to_markdown(config, layout)
        payload = json.loads(layout_to_json(config, layout))
        scene = build_blank_cad_scene(config, layout).to_dict()

        self.assertEqual(len(config.modules), 1)
        self.assertEqual(validate_config(config), [])
        plan = payload["executable_asset_plan"]
        self.assertEqual(plan["status"], "rejected")
        self.assertEqual(plan["summary"]["generated_module_count"], 1)
        self.assertEqual(plan["summary"]["placed_module_count"], 0)
        self.assertEqual(plan["summary"]["rejected_module_count"], 1)
        generated = plan["generated_modules"][0]
        self.assertEqual(generated["source_asset_ids"], ["coin-tokens", "status-tokens"])
        self.assertEqual(generated["dimensions_mm"], {"x": 113.6, "y": 90.0, "z": 19.8})
        self.assertEqual(generated["asset_fit_size_mm"], {"x": 111.2, "y": 87.6, "z": 18.6})
        self.assertEqual(generated["storage_sizing"]["count_aware_storage_sizing"], "yes")
        self.assertEqual(generated["storage_sizing"]["asset_diagnostics"][0]["pile_count"], 12)
        self.assertEqual(generated["clearance_applied"]["internal_asset_clearance_mm"], 0.6)
        cavity = generated["asset_fit_cavity"]
        self.assertEqual(cavity["status"], "planned")
        self.assertEqual(cavity["policy"], "per_source_asset_rectangular_compartments_v0")
        self.assertEqual(cavity["operation_kind"], "subtract_rectangular_cavity")
        self.assertEqual(cavity["layout_strategy"], "deterministic_single_column_by_source_asset_v0")
        self.assertEqual(cavity["compartment_count"], 2)
        self.assertEqual([item["asset_id"] for item in cavity["compartments"]], ["coin-tokens", "status-tokens"])
        self.assertEqual(cavity["compartments"][0]["local_origin_mm"], {"x": 1.2, "y": 1.2, "z": 1.2})
        self.assertEqual(cavity["compartments"][0]["size_mm"], {"x": 111.2, "y": 67.2, "z": 18.6})
        self.assertEqual(cavity["compartments"][1]["local_origin_mm"], {"x": 1.2, "y": 69.6, "z": 1.2})
        self.assertEqual(cavity["compartments"][1]["size_mm"], {"x": 109.2, "y": 19.2, "z": 18.6})
        self.assertEqual(cavity["compartments"][1]["internal_wall_thickness_mm"], 1.2)
        rejection = plan["rejected_modules"][0]
        self.assertEqual(rejection["code"], "DOES_NOT_FIT")
        self.assertIn("no free non-reserved span", rejection["message"])
        self.assertIn("## Executable asset module plan", markdown)
        self.assertIn("Rejected generated modules", markdown)
        self.assertEqual(scene["metadata"]["executable_asset_plan"]["status"], "rejected")

    def test_count_aware_single_item_keeps_one_small_stack(self) -> None:
        payload = _count_aware_tokens_payload(count=1)
        plan = _layout_payload(payload)["executable_asset_plan"]

        generated = plan["generated_modules"][0]
        sizing = generated["storage_sizing"]
        self.assertEqual(plan["status"], "placed")
        self.assertEqual(generated["dimensions_mm"], {"x": 13.6, "y": 13.6, "z": 3.8})
        self.assertEqual(generated["asset_fit_cavity"]["status"], "planned")
        self.assertEqual(generated["asset_fit_cavity"]["policy"], "per_source_asset_rectangular_compartments_v0")
        self.assertEqual(generated["asset_fit_cavity"]["compartment_count"], 1)
        self.assertEqual(generated["asset_fit_cavity"]["compartments"][0]["size_mm"], generated["asset_fit_size_mm"])
        self.assertEqual(generated["asset_fit_cavity"]["compartments"][0]["retained_floor_mm"], 1.2)
        self.assertEqual(sizing["asset_diagnostics"][0]["capacity_per_stack"], 14)
        self.assertEqual(sizing["asset_diagnostics"][0]["pile_count"], 1)
        self.assertEqual(sizing["asset_diagnostics"][0]["items_per_pile"], 1)

    def test_count_aware_count_can_increase_stack_height_before_xy_piles(self) -> None:
        low = _layout_payload(_count_aware_tokens_payload(count=1))["executable_asset_plan"]["generated_modules"][0]
        high = _layout_payload(_count_aware_tokens_payload(count=10))["executable_asset_plan"]["generated_modules"][0]

        self.assertEqual(low["dimensions_mm"]["x"], high["dimensions_mm"]["x"])
        self.assertEqual(low["dimensions_mm"]["y"], high["dimensions_mm"]["y"])
        self.assertGreater(high["dimensions_mm"]["z"], low["dimensions_mm"]["z"])
        self.assertGreater(
            high["asset_fit_cavity"]["compartments"][0]["size_mm"]["z"],
            low["asset_fit_cavity"]["compartments"][0]["size_mm"]["z"],
        )
        self.assertEqual(high["storage_sizing"]["asset_diagnostics"][0]["pile_count"], 1)
        self.assertEqual(high["storage_sizing"]["asset_diagnostics"][0]["items_per_pile"], 10)

    def test_count_aware_high_count_requires_multiple_xy_piles(self) -> None:
        generated = _layout_payload(_count_aware_tokens_payload(count=30))["executable_asset_plan"]["generated_modules"][0]
        diagnostic = generated["storage_sizing"]["asset_diagnostics"][0]

        self.assertEqual(diagnostic["pile_count"], 3)
        self.assertEqual(diagnostic["items_per_pile"], 10)
        self.assertEqual(generated["dimensions_mm"], {"x": 33.6, "y": 13.6, "z": 21.8})
        self.assertEqual(generated["asset_fit_cavity"]["compartments"][0]["size_mm"], {"x": 31.2, "y": 11.2, "z": 20.6})

    def test_asset_compartments_plan_front_access_notches_for_smoke_case(self) -> None:
        payload = _count_aware_tokens_payload(count=40)
        payload["project_name"] = "P13 M005 access notch smoke fixture"
        payload["box"]["inner_dimensions_mm"] = {"x": 130, "y": 50, "z": 60}
        payload["box"]["usable_height_mm"] = 60
        payload["volumetric_grid"] = {
            "unit_mm": {"x": 32.5, "y": 12.5, "z": 20},
            "size_units": {"x": 4, "y": 4, "z": 3},
        }
        payload["assets"] = [
            {
                "id": "coin-tokens",
                "name": "Coin tokens",
                "kind": "tokens",
                "quantity": {"count": 40, "grouping": "set"},
                "dimensions_mm": {"x": 18, "y": 16, "z": 2},
                "dimension_confidence": "exact",
                "containment_intent": "store",
            },
            {
                "id": "status-tokens",
                "name": "Status tokens",
                "kind": "tokens",
                "quantity": {"count": 23, "grouping": "set"},
                "dimensions_mm": {"x": 10, "y": 35, "z": 2},
                "dimension_confidence": "exact",
                "containment_intent": "store",
            },
        ]
        generated = _layout_payload(payload)["executable_asset_plan"]["generated_modules"][0]
        cavity = generated["asset_fit_cavity"]

        self.assertEqual(cavity["asset_access_policy"], "per_compartment_top_open_rectangular_notch_v0")
        self.assertTrue(cavity["asset_access_features_generated"])
        self.assertEqual(cavity["asset_access_notches_planned"], 2)
        self.assertEqual(cavity["asset_access_notches_refused"], 0)
        notches = [compartment["asset_access_notch"] for compartment in cavity["compartments"]]
        self.assertEqual([notch["asset_id"] for notch in notches], ["coin-tokens", "status-tokens"])
        self.assertEqual([notch["compartment_id"] for notch in notches], ["asset-compartment:coin-tokens", "asset-compartment:status-tokens"])
        self.assertEqual([notch["status"] for notch in notches], ["planned", "planned"])
        self.assertEqual([notch["target_wall"] for notch in notches], ["front", "front"])
        self.assertEqual(notches[0]["width_mm"], 18.0)
        self.assertEqual(notches[0]["depth_from_top_mm"], 10.0)
        self.assertEqual(notches[0]["size_mm"], {"x": 18.0, "y": 1.2, "z": 10.0})
        self.assertEqual(notches[1]["width_mm"], 8.8)
        self.assertEqual(notches[1]["depth_from_top_mm"], 10.0)
        self.assertLess(notches[0]["depth_from_top_mm"], cavity["compartments"][0]["size_mm"]["z"])
        self.assertLess(notches[1]["depth_from_top_mm"], cavity["compartments"][1]["size_mm"]["z"])

    def test_asset_access_notch_refuses_too_narrow_compartment(self) -> None:
        payload = _count_aware_tokens_payload(count=1)
        payload["assets"][0]["dimensions_mm"] = {"x": 3, "y": 10, "z": 2}
        generated = _layout_payload(payload)["executable_asset_plan"]["generated_modules"][0]
        cavity = generated["asset_fit_cavity"]
        notch = cavity["compartments"][0]["asset_access_notch"]

        self.assertEqual(cavity["asset_access_notches_planned"], 0)
        self.assertEqual(cavity["asset_access_notches_refused"], 1)
        self.assertEqual(notch["status"], "refused")
        self.assertFalse(notch["notch_generated"])
        self.assertIn("too narrow", notch["reason"])
        self.assertEqual(notch["asset_id"], "coin-tokens")
        self.assertEqual(notch["compartment_id"], "asset-compartment:coin-tokens")
    def test_asset_fit_cavity_refuses_card_stack_v0(self) -> None:
        payload = _count_aware_tokens_payload(count=60)
        payload["assets"][0]["kind"] = "cards"
        payload["assets"][0]["dimensions_mm"] = {"x": 63, "y": 88, "z": 20}
        payload["box"]["inner_dimensions_mm"] = {"x": 140, "y": 95, "z": 30}
        payload["box"]["usable_height_mm"] = 30
        payload["volumetric_grid"] = {"unit_mm": {"x": 70, "y": 95, "z": 30}, "size_units": {"x": 2, "y": 1, "z": 1}}
        generated = _layout_payload(payload)["executable_asset_plan"]["generated_modules"][0]

        cavity = generated["asset_fit_cavity"]
        self.assertEqual(cavity["status"], "refused")
        self.assertEqual(cavity["code"], "UNSUPPORTED_ASSET_CAVITY_TYPE")
        self.assertIn("supports tokens/dice/meeples/generic", cavity["reason"])

    def test_count_aware_too_many_items_rejects_instead_of_claiming_capacity(self) -> None:
        payload = _count_aware_tokens_payload(count=1000)
        plan_payload = _layout_payload(payload)

        self.assertEqual(plan_payload["asset_candidate_variants"][0]["status"], "rejected")
        self.assertEqual(plan_payload["executable_asset_plan"]["status"], "rejected")
        self.assertIn("DIMENSIONS_INCOMPATIBLE", plan_payload["executable_asset_plan"]["rejected_modules"][0]["code"])
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


def _layout_payload(payload: dict) -> dict:
    config = _load_payload(payload)
    layout = generate_basic_layout(config)
    return json.loads(layout_to_json(config, layout))


def _count_aware_tokens_payload(*, count: int) -> dict:
    return {
        "project_name": "Count-aware token fixture",
        "units": "mm",
        "box": {
            "inner_dimensions_mm": {"x": 100, "y": 80, "z": 30},
            "usable_height_mm": 30,
            "lid_clearance_mm": 0,
        },
        "print_profile": "default",
        "defaults": {
            "wall_thickness_mm": 1.2,
            "floor_thickness_mm": 1.2,
            "corner_radius_mm": 1.5,
        },
        "layout": {"strategy": "row_fill"},
        "assets": [
            {
                "id": "coin-tokens",
                "name": "Coin tokens",
                "kind": "tokens",
                "quantity": {"count": count, "grouping": "set"},
                "dimensions_mm": {"x": 10, "y": 10, "z": 2},
                "dimension_confidence": "exact",
                "containment_intent": "store",
            }
        ],
        "volumetric_grid": {
            "unit_mm": {"x": 20, "y": 20, "z": 10},
            "size_units": {"x": 5, "y": 4, "z": 3},
        },
        "modules": [],
    }
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