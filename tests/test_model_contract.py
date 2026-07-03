from __future__ import annotations

import unittest

from board_game_insert_generator.layout import generate_basic_layout
from board_game_insert_generator.models import (
    BoxSpec,
    Dimension3D,
    FunctionalType,
    GeometryDefaults,
    InsertConfig,
    LayoutSettings,
    ModuleRequest,
    ToleranceProfile,
)
from board_game_insert_generator.validation import validate_config


def _module(
    module_id: str = "cards",
    quantity: int = 1,
    height_mm: float = 35.0,
    min_dimensions: Dimension3D | None = None,
) -> ModuleRequest:
    return ModuleRequest(
        id=module_id,
        name="Cards",
        functional_type=FunctionalType.CARDS,
        min_dimensions=min_dimensions or Dimension3D(x=65.0, y=92.0, z=35.0),
        desired_height_mm=height_mm,
        priority=10,
        allow_rotation=True,
        quantity=quantity,
    )


def _config(
    box: BoxSpec | None = None,
    modules: tuple[ModuleRequest, ...] | None = None,
    tolerances: ToleranceProfile | None = None,
    layout: LayoutSettings | None = None,
) -> InsertConfig:
    return InsertConfig(
        project_name="Contract test",
        units="mm",
        box=box
        or BoxSpec(
            inner_dimensions=Dimension3D(x=120.0, y=180.0, z=60.0),
            usable_height_mm=45.0,
            lid_clearance_mm=5.0,
        ),
        tolerances=tolerances or ToleranceProfile(),
        defaults=GeometryDefaults(),
        layout=layout or LayoutSettings(),
        modules=modules or (_module(),),
    )


class ModelContractTests(unittest.TestCase):
    def test_valid_core_model_contract_has_no_validation_issues(self) -> None:
        issues = validate_config(_config())

        self.assertEqual(issues, [])

    def test_box_contract_reports_invalid_dimensions_and_usable_height(self) -> None:
        invalid_box = BoxSpec(
            inner_dimensions=Dimension3D(x=0.0, y=180.0, z=60.0),
            usable_height_mm=58.0,
            lid_clearance_mm=5.0,
        )

        issues = validate_config(_config(box=invalid_box))

        self.assertIn(("box.inner_dimensions_mm.x", "NOT_POSITIVE"), _issue_keys(issues))
        self.assertIn(("box.usable_height_mm", "USABLE_HEIGHT_TOO_TALL"), _issue_keys(issues))

    def test_module_contract_reports_duplicate_ids_and_invalid_quantities(self) -> None:
        modules = (_module("cards", quantity=1), _module("cards", quantity=0))

        issues = validate_config(_config(modules=modules))

        self.assertIn(("modules[1].id", "DUPLICATE_ID"), _issue_keys(issues))
        self.assertIn(("modules[1].quantity", "NOT_POSITIVE"), _issue_keys(issues))

    def test_tolerance_profile_contract_rejects_negative_values(self) -> None:
        tolerances = ToleranceProfile(module_gap_mm=-0.1)

        issues = validate_config(_config(tolerances=tolerances))

        self.assertIn(("tolerances.module_gap_mm", "NEGATIVE_VALUE"), _issue_keys(issues))

    def test_cell_and_printable_body_remain_distinct_contract_objects(self) -> None:
        result = generate_basic_layout(_config())

        self.assertEqual(len(result.cells), 1)
        self.assertEqual(len(result.printable_bodies), 1)

        cell = result.cells[0]
        body = result.printable_bodies[0]

        self.assertEqual(cell.instance_id, body.instance_id)
        self.assertLess(body.size.x, cell.size.x)
        self.assertLess(body.size.y, cell.size.y)
        self.assertEqual(body.primitive_volumes[0].size, body.size)


def _issue_keys(issues) -> set[tuple[str, str]]:
    return {(issue.field, issue.code) for issue in issues}


if __name__ == "__main__":
    unittest.main()
