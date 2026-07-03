from __future__ import annotations

from dataclasses import replace
import unittest

from context import ROOT

from board_game_insert_generator.config_loader import load_config
from board_game_insert_generator.layout import LayoutError, generate_basic_layout
from board_game_insert_generator.models import (
    BoxSpec,
    Dimension3D,
    FunctionalType,
    GeometryDefaults,
    IMPLEMENTED_LAYOUT_STRATEGIES,
    InsertConfig,
    LayoutSettings,
    ModuleRequest,
    RESERVED_LAYOUT_STRATEGIES,
    ToleranceProfile,
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

    def test_row_fill_sorts_by_priority_then_source_order(self) -> None:
        config = _config(
            modules=(
                _module("low", priority=1),
                _module("tie-a", priority=5),
                _module("high", priority=10),
                _module("tie-b", priority=5),
            )
        )

        result = generate_basic_layout(config)

        self.assertEqual(
            [cell.instance_id for cell in result.cells],
            ["high-01", "tie-a-01", "tie-b-01", "low-01"],
        )

    def test_row_fill_rotates_allowed_module_to_stay_on_current_row(self) -> None:
        config = _config(
            box_x=120.0,
            box_y=150.0,
            modules=(
                _module("fixed", x=80.0, y=40.0, priority=10, allow_rotation=False),
                _module("rotating", x=70.0, y=30.0, priority=9, allow_rotation=True),
            ),
        )

        result = generate_basic_layout(config)
        rotating = result.cells[1]

        self.assertEqual(rotating.instance_id, "rotating-01")
        self.assertTrue(rotating.rotated)
        self.assertEqual(rotating.origin.x, 80.0)
        self.assertEqual(rotating.origin.y, 0.0)
        self.assertEqual(rotating.size.x, 30.0)
        self.assertEqual(rotating.size.y, 70.0)

    def test_row_fill_starts_new_row_when_module_cannot_fit_remaining_width(self) -> None:
        config = _config(
            box_x=100.0,
            box_y=100.0,
            modules=(
                _module("first", x=70.0, y=20.0, priority=10, allow_rotation=False),
                _module("second", x=50.0, y=30.0, priority=9, allow_rotation=False),
            ),
        )

        result = generate_basic_layout(config)
        second = result.cells[1]

        self.assertFalse(second.rotated)
        self.assertEqual(second.origin.x, 0.0)
        self.assertEqual(second.origin.y, 20.0)

    def test_row_fill_reports_vertical_overflow_with_needed_height(self) -> None:
        config = _config(
            box_x=100.0,
            box_y=50.0,
            modules=(
                _module("first", x=100.0, y=30.0, priority=10, allow_rotation=False),
                _module("second", x=100.0, y=25.0, priority=9, allow_rotation=False),
            ),
        )

        with self.assertRaisesRegex(
            LayoutError,
            r"Module 'second'.*Needed Y up to 55\.00 mm, box has 50\.00 mm",
        ):
            generate_basic_layout(config)

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


def _config(
    box_x: float = 300.0,
    box_y: float = 200.0,
    modules: tuple[ModuleRequest, ...] = (),
) -> InsertConfig:
    return InsertConfig(
        project_name="Layout edge case",
        units="mm",
        box=BoxSpec(
            inner_dimensions=Dimension3D(x=box_x, y=box_y, z=60.0),
            usable_height_mm=45.0,
            lid_clearance_mm=5.0,
        ),
        tolerances=ToleranceProfile(),
        defaults=GeometryDefaults(),
        layout=LayoutSettings(),
        modules=modules,
    )


def _module(
    module_id: str,
    x: float = 20.0,
    y: float = 20.0,
    priority: int = 1,
    allow_rotation: bool = False,
) -> ModuleRequest:
    return ModuleRequest(
        id=module_id,
        name=module_id,
        functional_type=FunctionalType.OTHER,
        min_dimensions=Dimension3D(x=x, y=y, z=20.0),
        desired_height_mm=20.0,
        priority=priority,
        allow_rotation=allow_rotation,
    )


if __name__ == "__main__":
    unittest.main()
