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
        self.assertEqual(config.print_profile, "default")
        self.assertEqual(len(config.modules), 3)
        self.assertEqual(config.modules[0].functional_type, FunctionalType.SLEEVED_CARDS)
        self.assertEqual(config.modules[0].quantity, 2)

    def test_loads_module_cavities(self) -> None:
        config = load_config(ROOT / "examples" / "simple_tray.json")

        self.assertEqual(len(config.modules), 1)
        cavity = config.modules[0].cavities[0]
        self.assertEqual(cavity.id, "token-pocket")
        self.assertEqual(cavity.functional_type, FunctionalType.TOKENS)
        self.assertEqual(cavity.origin.x, 4.0)
        self.assertEqual(cavity.origin.z, 1.2)
        self.assertEqual(cavity.size.x, 62.0)
        self.assertEqual(cavity.clearance_mm, 0.6)


    def test_card_cavities_default_clearance_from_profile(self) -> None:
        config = load_config(ROOT / "examples" / "simple_card_tray.json")

        standard_cavity = config.modules[0].cavities[0]
        sleeved_cavity = config.modules[1].cavities[0]

        self.assertEqual(standard_cavity.functional_type, FunctionalType.CARDS)
        self.assertEqual(standard_cavity.clearance_mm, 0.45)
        self.assertEqual(standard_cavity.clearance_source, "tolerances.card_clearance_mm")
        self.assertEqual(sleeved_cavity.functional_type, FunctionalType.SLEEVED_CARDS)
        self.assertEqual(sleeved_cavity.clearance_mm, 0.95)
        self.assertEqual(sleeved_cavity.clearance_source, "tolerances.sleeved_card_clearance_mm")

    def test_rejects_missing_generic_cavity_clearance(self) -> None:
        payload = _simple_payload()
        payload["modules"][0]["functional_type"] = "tokens"
        payload["modules"][0]["cavities"] = [
            {
                "id": "missing-clearance",
                "functional_type": "tokens",
                "origin_mm": {"x": 2, "y": 2, "z": 1.2},
                "size_mm": {"x": 10, "y": 10, "z": 5},
            }
        ]

        with self.assertRaisesRegex(
            ConfigError,
            r"Missing required field 'modules\[0\]\.cavities\[0\]\.clearance_mm'",
        ):
            _load_payload(payload)

    def test_rejects_unknown_cavity_field(self) -> None:
        payload = _simple_payload()
        payload["modules"][0]["cavities"] = [
            {
                "id": "bad-pocket",
                "origin_mm": {"x": 2, "y": 2, "z": 1.2},
                "size_mm": {"x": 10, "y": 10, "z": 5},
                "clearance_mm": 0.5,
                "surprise": True,
            }
        ]

        with self.assertRaisesRegex(
            ConfigError,
            r"Unknown field\(s\) in 'modules\[0\]\.cavities\[0\]': surprise",
        ):
            _load_payload(payload)

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

    def test_rejects_unknown_print_profile(self) -> None:
        payload = _simple_payload()
        payload["print_profile"] = "magic_filament"

        with self.assertRaisesRegex(ConfigError, "Unsupported print_profile 'magic_filament'"):
            _load_payload(payload)

    def test_resolves_print_profile_then_tolerance_overrides(self) -> None:
        payload = _simple_payload()
        payload["print_profile"] = "petg_standard"
        payload["tolerances"] = {"module_gap_mm": 0.42}

        config = _load_payload(payload)

        self.assertEqual(config.print_profile, "petg_standard")
        self.assertAlmostEqual(config.tolerances.peripheral_clearance_mm, 1.0)
        self.assertAlmostEqual(config.tolerances.printer_compensation_mm, 0.05)
        self.assertAlmostEqual(config.tolerances.module_gap_mm, 0.42)

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
