from __future__ import annotations

import unittest

from context import ROOT

from board_game_insert_generator.config_loader import load_config
from board_game_insert_generator.layout import generate_basic_layout


class ToleranceTests(unittest.TestCase):
    def test_peripheral_and_neighbor_offsets_are_distinct(self) -> None:
        config = load_config(ROOT / "examples" / "simple_box.json")
        result = generate_basic_layout(config)

        first_body = result.printable_bodies[0]

        self.assertAlmostEqual(
            first_body.offsets.x_min,
            config.tolerances.peripheral_clearance_mm,
        )
        self.assertAlmostEqual(
            first_body.offsets.x_max,
            config.tolerances.module_gap_mm / 2.0,
        )
        self.assertLess(first_body.size.x, result.cells[0].size.x)

    def test_vertical_lid_clearance_reduces_printable_height(self) -> None:
        config = load_config(ROOT / "examples" / "simple_box.json")
        result = generate_basic_layout(config)

        first_cell = result.cells[0]
        first_body = result.printable_bodies[0]

        self.assertAlmostEqual(
            first_body.size.z,
            first_cell.size.z - config.tolerances.vertical_lid_clearance_mm,
        )


if __name__ == "__main__":
    unittest.main()
