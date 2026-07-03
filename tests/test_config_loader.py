from __future__ import annotations

import unittest

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


if __name__ == "__main__":
    unittest.main()
