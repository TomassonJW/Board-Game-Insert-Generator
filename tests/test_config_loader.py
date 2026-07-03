from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from context import ROOT

from board_game_insert_generator.config_loader import ConfigError, load_config
from board_game_insert_generator.models import FunctionalType


class ConfigLoaderTests(unittest.TestCase):
    def test_load_simple_config(self) -> None:
        config = load_config(ROOT / "examples" / "simple_box.json")

        self.assertEqual(config.units, "mm")
        self.assertEqual(config.project_name, "Simple square box V0")
        self.assertEqual(len(config.modules), 3)
        self.assertEqual(config.modules[0].functional_type, FunctionalType.SLEEVED_CARDS)
        self.assertEqual(config.modules[0].quantity, 2)

    def test_rejects_missing_file(self) -> None:
        with self.assertRaises(ConfigError):
            load_config(ROOT / "examples" / "missing.json")

    def test_rejects_unknown_top_level_field(self) -> None:
        payload = _simple_payload()
        payload["unexpected"] = True

        with self.assertRaisesRegex(ConfigError, r"Unknown field\(s\) in 'root': unexpected"):
            _load_payload(payload)

    def test_rejects_unknown_module_field(self) -> None:
        payload = _simple_payload()
        payload["modules"][0]["surprise"] = "unsupported"

        with self.assertRaisesRegex(
            ConfigError,
            r"Unknown field\(s\) in 'modules\[0\]': surprise",
        ):
            _load_payload(payload)

    def test_rejects_invalid_tolerance_type(self) -> None:
        payload = _simple_payload()
        payload["tolerances"]["module_gap_mm"] = "wide"

        with self.assertRaisesRegex(
            ConfigError,
            "Field 'tolerances.module_gap_mm' must be a number.",
        ):
            _load_payload(payload)

    def test_rejects_non_integer_quantity(self) -> None:
        payload = _simple_payload()
        payload["modules"][0]["quantity"] = 1.5

        with self.assertRaisesRegex(
            ConfigError,
            r"Field 'modules\[0\].quantity' must be an integer.",
        ):
            _load_payload(payload)

    def test_rejects_non_boolean_rotation_flag(self) -> None:
        payload = _simple_payload()
        payload["modules"][0]["allow_rotation"] = "yes"

        with self.assertRaisesRegex(
            ConfigError,
            r"Field 'modules\[0\].allow_rotation' must be a boolean.",
        ):
            _load_payload(payload)

    def test_missing_module_id_and_name_keep_stable_defaults(self) -> None:
        payload = _simple_payload()
        payload["modules"][0].pop("id")
        payload["modules"][0].pop("name")

        config = _load_payload(payload)

        self.assertEqual(config.modules[0].id, "module-1")
        self.assertEqual(config.modules[0].name, "Module 1")


def _simple_payload() -> dict:
    return json.loads((ROOT / "examples" / "simple_box.json").read_text(encoding="utf-8"))


def _load_payload(payload: dict):
    with tempfile.TemporaryDirectory() as temporary_directory:
        path = Path(temporary_directory) / "config.json"
        path.write_text(json.dumps(payload), encoding="utf-8")
        return load_config(path)


if __name__ == "__main__":
    unittest.main()
