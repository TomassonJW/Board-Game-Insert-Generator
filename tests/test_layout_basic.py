from __future__ import annotations

from dataclasses import replace
import unittest

from context import ROOT

from board_game_insert_generator.config_loader import load_config
from board_game_insert_generator.layout import generate_basic_layout
from board_game_insert_generator.models import (
    IMPLEMENTED_LAYOUT_STRATEGIES,
    RESERVED_LAYOUT_STRATEGIES,
    LayoutSettings,
)
from board_game_insert_generator.report import layout_to_markdown
from board_game_insert_generator.validation import validate_config


class LayoutBasicTests(unittest.TestCase):
    def test_simple_box_generates_cells_and_bodies(self) -> None:
        config = load_config(ROOT / "examples" / "simple_box.json")
        result = generate_basic_layout(config)

        self.assertEqual(len(result.cells), 4)
        self.assertEqual(len(result.printable_bodies), 4)
        self.assertEqual(result.cells[0].origin.x, 0.0)
        self.assertEqual(result.cells[1].origin.x, 70.0)

    def test_layout_strategy_contract_names_current_and_reserved_strategies(self) -> None:
        self.assertEqual(IMPLEMENTED_LAYOUT_STRATEGIES, ("row_fill",))
        self.assertEqual(RESERVED_LAYOUT_STRATEGIES, ("grid", "columns"))

    def test_row_fill_keeps_priority_order_and_source_order(self) -> None:
        config = load_config(ROOT / "examples" / "simple_box.json")
        result = generate_basic_layout(config)

        self.assertEqual(
            [cell.instance_id for cell in result.cells],
            ["cards-main-01", "cards-main-02", "tokens-01", "dice-01"],
        )
        self.assertEqual([cell.source_index for cell in result.cells], [0, 0, 1, 2])

    def test_reserved_layout_strategy_is_not_executable_yet(self) -> None:
        config = load_config(ROOT / "examples" / "simple_box.json")
        grid_config = replace(config, layout=LayoutSettings(strategy="grid"))

        issues = validate_config(grid_config)

        self.assertIn(("layout.strategy", "UNSUPPORTED_LAYOUT_STRATEGY"), _issue_keys(issues))
        self.assertIn("reserved for a later layout mission", issues[0].message)

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


def _issue_keys(issues) -> set[tuple[str, str]]:
    return {(issue.field, issue.code) for issue in issues}


if __name__ == "__main__":
    unittest.main()
