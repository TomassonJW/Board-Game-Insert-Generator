from __future__ import annotations

import unittest

from context import ROOT

from board_game_insert_generator.config_loader import load_config
from board_game_insert_generator.layout import generate_basic_layout
from board_game_insert_generator.report import layout_to_markdown


class LayoutBasicTests(unittest.TestCase):
    def test_simple_box_generates_cells_and_bodies(self) -> None:
        config = load_config(ROOT / "examples" / "simple_box.json")
        result = generate_basic_layout(config)

        self.assertEqual(len(result.cells), 4)
        self.assertEqual(len(result.printable_bodies), 4)
        self.assertEqual(result.cells[0].origin.x, 0.0)
        self.assertEqual(result.cells[1].origin.x, 70.0)

    def test_cards_and_tokens_example_fits(self) -> None:
        config = load_config(ROOT / "examples" / "cards_and_tokens.json")
        result = generate_basic_layout(config)

        self.assertEqual(len(result.cells), 6)
        self.assertLessEqual(
            max(cell.origin.y + cell.size.y for cell in result.cells),
            config.box.inner_dimensions.y,
        )

    def test_markdown_report_mentions_theoretical_and_printable_sizes(self) -> None:
        config = load_config(ROOT / "examples" / "simple_box.json")
        result = generate_basic_layout(config)

        report = layout_to_markdown(config, result)

        self.assertIn("Cell size is the theoretical layout reservation", report)
        self.assertIn("cards-main-01", report)


if __name__ == "__main__":
    unittest.main()
