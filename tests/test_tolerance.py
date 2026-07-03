from __future__ import annotations

import unittest

from context import ROOT

from board_game_insert_generator.config_loader import load_config
from board_game_insert_generator.layout import generate_basic_layout
from board_game_insert_generator.models import (
    BoxSpec,
    Cell,
    Dimension3D,
    FaceClassification,
    FaceName,
    FaceRole,
    FunctionalType,
    GeometryDefaults,
    InsertConfig,
    LayoutSettings,
    Point3D,
    ToleranceProfile,
)
from board_game_insert_generator.tolerance import (
    classify_cell_faces,
    face_tolerance_applications_from_classifications,
)


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

    def test_face_role_names_cover_future_tolerance_cases(self) -> None:
        self.assertEqual(FaceRole.PERIPHERAL.value, "peripheral")
        self.assertEqual(FaceRole.NEIGHBOR.value, "neighbor")
        self.assertEqual(FaceRole.EXPOSED.value, "exposed")
        self.assertEqual(FaceRole.FUNCTIONAL.value, "functional")
        self.assertEqual(FaceRole.INTERNAL.value, "internal")
        self.assertEqual(FaceRole.WELDED.value, "welded")

    def test_face_tolerance_rules_cover_each_role(self) -> None:
        config = _config(tolerances=ToleranceProfile(printer_compensation_mm=0.2))
        classifications = (
            FaceClassification(FaceName.X_MIN, FaceRole.PERIPHERAL, "peripheral test"),
            FaceClassification(FaceName.X_MAX, FaceRole.NEIGHBOR, "neighbor test"),
            FaceClassification(FaceName.Y_MIN, FaceRole.EXPOSED, "exposed test"),
            FaceClassification(FaceName.Y_MAX, FaceRole.INTERNAL, "internal test"),
            FaceClassification(FaceName.Z_MIN, FaceRole.WELDED, "welded test"),
            FaceClassification(FaceName.Z_MAX, FaceRole.FUNCTIONAL, "functional test"),
        )

        applications = _apps_by_face(
            face_tolerance_applications_from_classifications(classifications, config)
        )

        self.assertAlmostEqual(applications[FaceName.X_MIN].offset_mm, 1.0)
        self.assertEqual(applications[FaceName.X_MIN].rule_id, "peripheral_clearance")
        self.assertTrue(applications[FaceName.X_MIN].receives_clearance)
        self.assertAlmostEqual(applications[FaceName.X_MAX].offset_mm, 0.5)
        self.assertEqual(applications[FaceName.X_MAX].rule_id, "neighbor_half_module_gap")
        self.assertTrue(applications[FaceName.X_MAX].receives_clearance)
        self.assertAlmostEqual(applications[FaceName.Y_MIN].offset_mm, 0.2)
        self.assertFalse(applications[FaceName.Y_MIN].receives_clearance)
        self.assertAlmostEqual(applications[FaceName.Y_MAX].offset_mm, 0.0)
        self.assertEqual(applications[FaceName.Y_MAX].rule_id, "internal_no_clearance")
        self.assertFalse(applications[FaceName.Y_MAX].receives_clearance)
        self.assertAlmostEqual(applications[FaceName.Z_MIN].offset_mm, 0.0)
        self.assertEqual(applications[FaceName.Z_MIN].rule_id, "welded_no_clearance")
        self.assertFalse(applications[FaceName.Z_MIN].receives_clearance)
        self.assertAlmostEqual(applications[FaceName.Z_MAX].offset_mm, 1.0)
        self.assertEqual(applications[FaceName.Z_MAX].rule_id, "functional_vertical_lid_clearance")
        self.assertTrue(applications[FaceName.Z_MAX].receives_clearance)

    def test_bottom_functional_face_receives_no_clearance(self) -> None:
        config = _config()
        classifications = (
            FaceClassification(FaceName.X_MIN, FaceRole.EXPOSED, "exposed test"),
            FaceClassification(FaceName.X_MAX, FaceRole.EXPOSED, "exposed test"),
            FaceClassification(FaceName.Y_MIN, FaceRole.EXPOSED, "exposed test"),
            FaceClassification(FaceName.Y_MAX, FaceRole.EXPOSED, "exposed test"),
            FaceClassification(FaceName.Z_MIN, FaceRole.FUNCTIONAL, "bottom functional test"),
            FaceClassification(FaceName.Z_MAX, FaceRole.FUNCTIONAL, "top functional test"),
        )

        applications = _apps_by_face(
            face_tolerance_applications_from_classifications(classifications, config)
        )

        self.assertAlmostEqual(applications[FaceName.Z_MIN].offset_mm, 0.0)
        self.assertEqual(applications[FaceName.Z_MIN].rule_id, "bottom_anchor_no_clearance")
        self.assertFalse(applications[FaceName.Z_MIN].receives_clearance)

    def test_simple_rectangular_cell_faces_are_classified(self) -> None:
        config = _config()
        cell = Cell(
            module_id="module",
            instance_id="module-01",
            label="Module",
            functional_type=FunctionalType.OTHER,
            origin=Point3D(x=0.0, y=0.0, z=0.0),
            size=Dimension3D(x=20.0, y=20.0, z=10.0),
            source_index=0,
        )

        classifications = _by_face(classify_cell_faces(cell, (cell,), config))

        self.assertEqual(classifications[FaceName.X_MIN].role, FaceRole.PERIPHERAL)
        self.assertEqual(classifications[FaceName.Y_MIN].role, FaceRole.PERIPHERAL)
        self.assertEqual(classifications[FaceName.X_MAX].role, FaceRole.EXPOSED)
        self.assertEqual(classifications[FaceName.Y_MAX].role, FaceRole.EXPOSED)
        self.assertEqual(classifications[FaceName.Z_MIN].role, FaceRole.FUNCTIONAL)
        self.assertEqual(classifications[FaceName.Z_MAX].role, FaceRole.FUNCTIONAL)

    def test_row_fill_layout_exposes_face_classifications(self) -> None:
        config = load_config(ROOT / "examples" / "simple_box.json")
        result = generate_basic_layout(config)

        first_body = result.printable_bodies[0]
        classifications = _by_face(first_body.face_classifications)

        self.assertEqual(classifications[FaceName.X_MIN].role, FaceRole.PERIPHERAL)
        self.assertEqual(classifications[FaceName.X_MAX].role, FaceRole.NEIGHBOR)
        self.assertEqual(classifications[FaceName.X_MAX].neighbor_instance_id, "cards-main-02")
        self.assertEqual(classifications[FaceName.Y_MIN].role, FaceRole.PERIPHERAL)
        self.assertEqual(classifications[FaceName.Y_MAX].role, FaceRole.EXPOSED)
        self.assertEqual(classifications[FaceName.Z_MAX].role, FaceRole.FUNCTIONAL)

    def test_grid_layout_exposes_face_classifications(self) -> None:
        config = load_config(ROOT / "examples" / "simple_grid.json")
        result = generate_basic_layout(config)

        first_body = result.printable_bodies[0]
        classifications = _by_face(first_body.face_classifications)

        self.assertEqual(classifications[FaceName.X_MIN].role, FaceRole.PERIPHERAL)
        self.assertEqual(classifications[FaceName.X_MAX].role, FaceRole.NEIGHBOR)
        self.assertEqual(classifications[FaceName.X_MAX].neighbor_instance_id, "small-cards-02")
        self.assertEqual(classifications[FaceName.Y_MIN].role, FaceRole.PERIPHERAL)
        self.assertEqual(classifications[FaceName.Y_MAX].role, FaceRole.EXPOSED)

    def test_simple_box_printable_dimensions_remain_unchanged(self) -> None:
        config = load_config(ROOT / "examples" / "simple_box.json")
        result = generate_basic_layout(config)

        self.assertEqual(
            _body_snapshot(result),
            [
                ("cards-main-01", (0.8, 0.8, 0.0), (68.9, 99.2, 44.0)),
                ("cards-main-02", (70.3, 0.8, 0.0), (69.4, 99.2, 44.0)),
                ("tokens-01", (140.3, 0.8, 0.0), (79.4, 79.2, 34.0)),
                ("dice-01", (220.3, 0.8, 0.0), (59.7, 59.2, 29.0)),
            ],
        )

    def test_simple_grid_printable_dimensions_remain_unchanged(self) -> None:
        config = load_config(ROOT / "examples" / "simple_grid.json")
        result = generate_basic_layout(config)

        self.assertEqual(
            _body_snapshot(result),
            [
                ("small-cards-01", (0.8, 0.8, 0.0), (53.9, 79.2, 29.0)),
                ("small-cards-02", (55.3, 0.8, 0.0), (54.4, 79.2, 29.0)),
                ("tokens-01", (110.3, 0.8, 0.0), (54.4, 79.2, 27.0)),
                ("tokens-02", (165.3, 0.8, 0.0), (54.7, 79.2, 27.0)),
            ],
        )


def _config(tolerances: ToleranceProfile | None = None) -> InsertConfig:
    return InsertConfig(
        project_name="Tolerance test",
        units="mm",
        box=BoxSpec(
            inner_dimensions=Dimension3D(x=100.0, y=80.0, z=40.0),
            usable_height_mm=30.0,
            lid_clearance_mm=5.0,
        ),
        tolerances=tolerances or ToleranceProfile(),
        defaults=GeometryDefaults(),
        layout=LayoutSettings(),
        modules=(),
    )


def _by_face(classifications):
    return {classification.face: classification for classification in classifications}


def _apps_by_face(applications):
    return {application.face: application for application in applications}


def _body_snapshot(result):
    return [
        (body.instance_id, _point_tuple(body.origin), _dimension_tuple(body.size))
        for body in result.printable_bodies
    ]


def _point_tuple(point: Point3D) -> tuple[float, float, float]:
    return (round(point.x, 4), round(point.y, 4), round(point.z, 4))


def _dimension_tuple(dimensions: Dimension3D) -> tuple[float, float, float]:
    return (round(dimensions.x, 4), round(dimensions.y, 4), round(dimensions.z, 4))


if __name__ == "__main__":
    unittest.main()
