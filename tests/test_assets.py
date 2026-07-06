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

    def test_cad_ir_transports_assets_as_metadata_only(self) -> None:
        config = load_config(ROOT / "examples" / "simple_assets.json")
        layout = generate_basic_layout(config)

        payload = build_blank_cad_scene(config, layout).to_dict()

        self.assertEqual(payload["metadata"]["assets"][0]["id"], "main-board")
        operation_kinds = [
            operation["kind"]
            for component in payload["components"]
            for operation in component["body"]["operations"]
        ]
        self.assertEqual(operation_kinds, ["create_rectangular_prism", "create_rectangular_prism"])

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


def _load_payload(payload: dict):
    with tempfile.TemporaryDirectory() as temporary_directory:
        path = Path(temporary_directory) / "config.json"
        path.write_text(json.dumps(payload), encoding="utf-8")
        return load_config(path)


def _issue_keys(issues) -> set[tuple[str, str]]:
    return {(issue.field, issue.code) for issue in issues}


if __name__ == "__main__":
    unittest.main()