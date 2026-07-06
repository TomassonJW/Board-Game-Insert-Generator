from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from context import ROOT

from board_game_insert_generator.cad_ir import build_blank_cad_scene
from board_game_insert_generator.config_loader import load_config
from board_game_insert_generator.layout import generate_basic_layout
from fusion_addin.BoardGameInsertGenerator.fusion_skeleton import (
    CAD_IR_PATH_OVERRIDE_FILENAME,
    DEFAULT_CAD_IR_INPUT_FILENAME,
    DOCUMENT_STATUS_READY,
    DOCUMENT_STATUS_ZERO_DOC,
    CAVITY_CUT_OPERATION_KIND,
    FINGER_NOTCH_CUT_OPERATION_KIND,
    FINGER_NOTCH_WALL_BACK,
    FINGER_NOTCH_WALL_FRONT,
    FINGER_NOTCH_WALL_LEFT,
    FINGER_NOTCH_WALL_RIGHT,
    FUSION_EXTENT_NEGATIVE,
    FUSION_EXTENT_POSITIVE,
    FUSION_MANUAL_VALIDATION_REQUIRED,
    FUSION_SKETCH_PLANE_XZ,
    FUSION_SKETCH_PLANE_YZ,
    GRID_PLACED_BLANK_OPERATION_KIND,
    PLAN_STATUS_PLANNED_ONLY,
    FusionSkeletonError,
    cad_ir_input_guidance,
    describe_document_state,
    generation_plan_from_cad_ir,
    load_cad_ir_json,
    mm_to_cm,
    planned_operations_from_cad_ir,
    resolve_cad_ir_input_path,
    validate_cad_ir_payload,
)


class _FakeDocument:
    def __init__(self, name: str) -> None:
        self.name = name


class _FakeApplication:
    def __init__(self, active_document) -> None:
        self.activeDocument = active_document


class FusionSkeletonTests(unittest.TestCase):
    def test_describes_zero_doc_when_application_is_unavailable(self) -> None:
        state = describe_document_state(None)

        self.assertEqual(state.status, DOCUMENT_STATUS_ZERO_DOC)
        self.assertIn("Fusion application is unavailable", state.message)
        self.assertIsNone(state.document_name)

    def test_describes_zero_doc_when_no_document_is_active(self) -> None:
        state = describe_document_state(_FakeApplication(active_document=None))

        self.assertEqual(state.status, DOCUMENT_STATUS_ZERO_DOC)
        self.assertIn("No active Fusion document", state.message)
        self.assertIsNone(state.document_name)

    def test_describes_ready_document_without_requiring_fusion_api(self) -> None:
        state = describe_document_state(_FakeApplication(_FakeDocument("BGIG test design")))

        self.assertEqual(state.status, DOCUMENT_STATUS_READY)
        self.assertEqual(state.document_name, "BGIG test design")
        self.assertIn("manual validation", state.message)

    def test_validates_minimal_cad_ir_contract(self) -> None:
        payload = _cad_ir_payload()

        validated = validate_cad_ir_payload(payload)

        self.assertIs(validated, payload)

    def test_rejects_unsupported_cad_ir_schema(self) -> None:
        payload = _cad_ir_payload()
        payload["schema_version"] = "cad_ir.future"

        with self.assertRaisesRegex(FusionSkeletonError, "Unsupported CAD IR"):
            validate_cad_ir_payload(payload)

    def test_rejects_non_millimeter_cad_ir_units(self) -> None:
        payload = _cad_ir_payload()
        payload["units"] = "inch"

        with self.assertRaisesRegex(FusionSkeletonError, "Unsupported CAD IR units"):
            validate_cad_ir_payload(payload)

    def test_rejects_payload_without_reference_box(self) -> None:
        payload = _cad_ir_payload()
        del payload["box_reference"]

        with self.assertRaisesRegex(FusionSkeletonError, "box_reference"):
            validate_cad_ir_payload(payload)

    def test_rejects_empty_components_list(self) -> None:
        payload = _cad_ir_payload()
        payload["components"] = []

        with self.assertRaisesRegex(FusionSkeletonError, "at least one component"):
            validate_cad_ir_payload(payload)

    def test_rejects_non_object_component_with_index(self) -> None:
        payload = _cad_ir_payload()
        payload["components"][0] = "bad component"

        with self.assertRaisesRegex(FusionSkeletonError, r"components\[0\]"):
            validate_cad_ir_payload(payload)

    def test_plans_operations_without_executing_geometry(self) -> None:
        payload = _cad_ir_payload()

        plans = planned_operations_from_cad_ir(payload)

        self.assertEqual(len(plans), 4)
        self.assertEqual(plans[0].component_id, "component:cards-main-01")
        self.assertEqual(plans[0].operation_kind, "create_rectangular_prism")
        self.assertEqual(plans[0].execution_status, PLAN_STATUS_PLANNED_ONLY)
        self.assertIn("no geometry is created", plans[0].reason)

    def test_loads_cad_ir_json_payload(self) -> None:
        temp_path = ROOT / "tmp_test_cad_ir_payload.json"
        temp_path.write_text(json.dumps(_cad_ir_payload()), encoding="utf-8")

        try:
            payload = load_cad_ir_json(temp_path)
        finally:
            temp_path.unlink()

        self.assertEqual(payload["schema_version"], "cad_ir.v0")
        self.assertEqual(len(payload["components"]), 4)

    def test_missing_cad_ir_json_path_has_actionable_error(self) -> None:
        missing_path = ROOT / "missing_cad_ir_payload.json"

        with self.assertRaisesRegex(FusionSkeletonError, "file not found"):
            load_cad_ir_json(missing_path)

    def test_resolves_default_cad_ir_input_path(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            addin_dir = Path(temp_dir)

            resolved_path = resolve_cad_ir_input_path(addin_dir)

            self.assertEqual(resolved_path, addin_dir / DEFAULT_CAD_IR_INPUT_FILENAME)

    def test_resolves_relative_cad_ir_override_path(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            addin_dir = Path(temp_dir)
            custom_path = addin_dir / "generated" / "simple_box_cad_ir.json"
            custom_path.parent.mkdir()
            custom_path.write_text(json.dumps(_cad_ir_payload()), encoding="utf-8")
            (addin_dir / CAD_IR_PATH_OVERRIDE_FILENAME).write_text(
                "# BGIG CAD IR input\ngenerated/simple_box_cad_ir.json\n",
                encoding="utf-8",
            )

            resolved_path = resolve_cad_ir_input_path(addin_dir)
            payload = load_cad_ir_json(resolved_path)

            self.assertEqual(resolved_path, custom_path.resolve())
            self.assertEqual(payload["schema_version"], "cad_ir.v0")

    def test_rejects_empty_cad_ir_override_path(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            addin_dir = Path(temp_dir)
            (addin_dir / CAD_IR_PATH_OVERRIDE_FILENAME).write_text(
                "# only comments\n\n",
                encoding="utf-8",
            )

            with self.assertRaisesRegex(FusionSkeletonError, "override file is empty"):
                resolve_cad_ir_input_path(addin_dir)

    def test_rejects_missing_configured_cad_ir_override_path(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            addin_dir = Path(temp_dir)
            (addin_dir / CAD_IR_PATH_OVERRIDE_FILENAME).write_text(
                "missing_scene.json\n",
                encoding="utf-8",
            )

            with self.assertRaisesRegex(
                FusionSkeletonError,
                "Configured CAD IR JSON file not found",
            ):
                resolve_cad_ir_input_path(addin_dir)

    def test_guidance_mentions_default_override_and_export_command(self) -> None:
        guidance = cad_ir_input_guidance(ROOT / "fusion_addin" / "BoardGameInsertGenerator")

        self.assertIn(DEFAULT_CAD_IR_INPUT_FILENAME, guidance)
        self.assertIn(CAD_IR_PATH_OVERRIDE_FILENAME, guidance)
        self.assertIn("export-cad-ir", guidance)

    def test_builds_generation_plan_from_engine_cad_ir(self) -> None:
        payload = _cad_ir_payload()

        plan = generation_plan_from_cad_ir(payload)

        self.assertEqual(plan.project_name, "Simple square box V0")
        self.assertEqual(plan.validation_status, FUSION_MANUAL_VALIDATION_REQUIRED)
        self.assertEqual(plan.reference_box.component_name, "Box reference - not printable")
        self.assertFalse(plan.reference_box.printable)
        self.assertEqual(plan.reference_box.operation_kind, "create_reference_outline")
        self.assertEqual(len(plan.blanks), 4)
        self.assertEqual(plan.blanks[0].component_name, "cards-main-01 - Main cards")
        self.assertEqual(plan.blanks[0].body_name, "cards-main-01 rectangular blank")
        self.assertEqual(plan.blanks[0].origin_mm.to_dict(), {"x": 0.8, "y": 0.8, "z": 0.0})
        self.assertEqual(plan.blanks[0].size_mm.to_dict(), {"x": 68.9, "y": 99.2, "z": 44.0})
        self.assertEqual(plan.blanks[0].validation_status, FUSION_MANUAL_VALIDATION_REQUIRED)

    def test_loads_addin_fixture_generation_plan(self) -> None:
        fixture_path = ROOT / "fusion_addin" / "BoardGameInsertGenerator" / "cad_ir_input.json"

        plan = generation_plan_from_cad_ir(load_cad_ir_json(fixture_path))

        self.assertEqual(plan.project_name, "BGIG Fusion smoke fixture")
        self.assertEqual(plan.created_object_count, 3)
        self.assertEqual([blank.body_name for blank in plan.blanks], [
            "cards-main-01 rectangular blank",
            "dice-01 rectangular blank",
        ])

    def test_rejects_generation_without_rectangular_prism_operation(self) -> None:
        payload = _cad_ir_payload()
        payload["components"][0]["body"]["operations"][0]["kind"] = "create_cavity"

        with self.assertRaisesRegex(FusionSkeletonError, "create_rectangular_prism"):
            generation_plan_from_cad_ir(payload)

    def test_converts_millimeters_to_fusion_centimeters(self) -> None:
        self.assertEqual(mm_to_cm(0.0), 0.0)
        self.assertEqual(mm_to_cm(1.0), 0.1)
        self.assertAlmostEqual(mm_to_cm(68.9), 6.89)


    def test_builds_cavity_cut_plan_from_simple_tray_cad_ir(self) -> None:
        payload = _cad_ir_payload_from_example("simple_tray.json")

        plan = generation_plan_from_cad_ir(payload)

        self.assertEqual(len(plan.blanks), 1)
        self.assertEqual(len(plan.cavity_cuts), 1)
        cut = plan.cavity_cuts[0]
        self.assertEqual(cut.operation_kind, CAVITY_CUT_OPERATION_KIND)
        self.assertEqual(cut.cavity_id, "token-pocket")
        self.assertEqual(cut.target_body_id, "token-tray-01-body")
        self.assertEqual(cut.cut_origin_mm.to_dict(), {"x": 4.8, "y": 4.8, "z": 23.0})
        self.assertEqual(cut.cut_size_mm.to_dict(), {"x": 62.0, "y": 52.0, "z": 20.0})
        self.assertEqual(cut.requested_local_origin_mm.to_dict(), {"x": 4.0, "y": 4.0, "z": 1.2})
        self.assertAlmostEqual(cut.retained_floor_mm, 3.0)
        self.assertEqual(cut.validation_status, FUSION_MANUAL_VALIDATION_REQUIRED)

    def test_builds_simple_finger_notch_cut_plan_from_cad_ir_feature(self) -> None:
        payload = _cad_ir_payload_from_example("simple_finger_notch_tray.json")

        plan = generation_plan_from_cad_ir(payload)

        self.assertEqual(plan.created_object_count, 4)
        self.assertEqual(len(plan.cavity_cuts), 1)
        self.assertEqual(plan.cavity_cuts[0].cavity_id, "token-pocket")
        self.assertEqual(len(plan.finger_notch_cuts), 1)
        cut = plan.finger_notch_cuts[0]
        self.assertEqual(cut.operation_kind, FINGER_NOTCH_CUT_OPERATION_KIND)
        self.assertEqual(cut.feature_id, "front-half-moon-notch")
        self.assertEqual(cut.source_feature_kind, "half_moon_notch")
        self.assertEqual(cut.placement, "front_center")
        self.assertEqual(cut.wall, FINGER_NOTCH_WALL_FRONT)
        self.assertEqual(cut.sketch_plane, FUSION_SKETCH_PLANE_XZ)
        self.assertAlmostEqual(cut.sketch_plane_offset_mm, 0.8)
        self.assertEqual(cut.extrude_direction, FUSION_EXTENT_POSITIVE)
        self.assertAlmostEqual(cut.cut_depth_mm, 4.0)
        self.assertEqual(cut.target_body_id, "finger-notch-tray-01-body")
        self.assertAlmostEqual(cut.cut_origin_mm.x, 26.8)
        self.assertAlmostEqual(cut.cut_origin_mm.y, 0.8)
        self.assertAlmostEqual(cut.cut_origin_mm.z, 13.0)
        self.assertEqual(cut.cut_size_mm.to_dict(), {"x": 18.0, "y": 4.0, "z": 10.0})
        self.assertTrue(cut.top_open)
        self.assertAlmostEqual(cut.notch_depth_from_top_mm, 10.0)
        self.assertAlmostEqual(cut.profile_bottom_z_mm, 13.0)
        self.assertAlmostEqual(cut.profile_top_z_mm, 24.0)
        self.assertAlmostEqual(cut.top_open_overshoot_mm, 1.0)
        _assert_vector_almost_equal(self, cut.profile_start_mm, {"x": 26.8, "y": 0.8, "z": 13.0})
        _assert_vector_almost_equal(self, cut.profile_end_mm, {"x": 44.8, "y": 0.8, "z": 24.0})
        self.assertEqual(cut.cavity_local_origin_mm.to_dict(), {"x": 4.0, "y": 4.0, "z": 1.2})
        self.assertEqual(cut.feature_position_mm.to_dict(), {"x": 22.0, "y": 0.0, "z": 8.0})
        self.assertEqual(cut.geometry_approximation, "rectangular_bounding_cut")


    def test_builds_grid_positioned_asset_blank_plan_from_executable_asset_plan(self) -> None:
        payload = _cad_ir_payload_from_example("simple_asset_executable_plan.json")

        plan = generation_plan_from_cad_ir(payload)

        self.assertEqual(len(plan.blanks), 1)
        self.assertEqual(len(plan.grid_positioned_blanks), 1)
        self.assertEqual(len(plan.rejected_grid_modules), 0)
        self.assertEqual(plan.created_object_count, 3)
        grid_blank = plan.grid_positioned_blanks[0]
        self.assertEqual(grid_blank.role, "generated_asset_grid_blank")
        self.assertEqual(grid_blank.operation_kind, GRID_PLACED_BLANK_OPERATION_KIND)
        self.assertEqual(grid_blank.component_name, "Grid placed Grouped candidate for tokens")
        self.assertEqual(grid_blank.origin_mm.to_dict(), {"x": 30.0, "y": 0.0, "z": 0.0})
        self.assertEqual(grid_blank.size_mm.to_dict(), {"x": 30.0, "y": 30.0, "z": 10.0})
        self.assertEqual(plan.to_dict()["grid_positioned_blanks"][0]["body_name"], grid_blank.body_name)


    def test_grid_positioned_asset_blank_supports_z_layer_origin(self) -> None:
        payload = _cad_ir_payload_from_example("simple_asset_executable_plan.json")
        placement = payload["metadata"]["executable_asset_plan"]["placements"][0]
        placement["origin_units"] = {"x": 1, "y": 0, "z": 1}
        placement["origin_mm"] = {"x": 30.0, "y": 0.0, "z": 10.0}

        plan = generation_plan_from_cad_ir(payload)

        grid_blank = plan.grid_positioned_blanks[0]
        self.assertEqual(grid_blank.origin_mm.to_dict(), {"x": 30.0, "y": 0.0, "z": 10.0})
        self.assertEqual(grid_blank.size_mm.to_dict(), {"x": 30.0, "y": 30.0, "z": 10.0})

    def test_transports_refused_grid_modules_without_creating_grid_blank(self) -> None:
        payload = _cad_ir_payload_from_example("simple_asset_grouping.json")

        plan = generation_plan_from_cad_ir(payload)

        self.assertEqual(len(plan.grid_positioned_blanks), 0)
        self.assertEqual(len(plan.rejected_grid_modules), 1)
        self.assertEqual(plan.rejected_grid_modules[0].code, "NO_VOLUMETRIC_GRID")
        self.assertIn("volumetric_grid", plan.rejected_grid_modules[0].constraint_ref)

    def test_rejects_grid_placement_collision_with_existing_blank(self) -> None:
        payload = _cad_ir_payload_from_example("simple_asset_executable_plan.json")
        placement = payload["metadata"]["executable_asset_plan"]["placements"][0]
        placement["origin_mm"] = {"x": 0.0, "y": 0.0, "z": 0.0}
        placement["origin_units"] = {"x": 0, "y": 0, "z": 0}

        with self.assertRaisesRegex(FusionSkeletonError, "collides"):
            generation_plan_from_cad_ir(payload)

    def test_rejects_grid_placement_outside_reference_box(self) -> None:
        payload = _cad_ir_payload_from_example("simple_asset_executable_plan.json")
        placement = payload["metadata"]["executable_asset_plan"]["placements"][0]
        placement["origin_mm"] = {"x": 120.0, "y": 0.0, "z": 0.0}
        placement["origin_units"] = {"x": 4, "y": 0, "z": 0}

        with self.assertRaisesRegex(FusionSkeletonError, "exceeds volumetric grid|exceeds reference box"):
            generation_plan_from_cad_ir(payload)

    def test_rounded_floor_feature_is_not_executed_as_fusion_cut(self) -> None:
        payload = _cad_ir_payload_from_example("simple_finger_notch_tray.json")

        plan = generation_plan_from_cad_ir(payload)

        self.assertEqual([cut.feature_id for cut in plan.finger_notch_cuts], ["front-half-moon-notch"])

    def test_finger_notch_cut_plan_supports_each_wall_orientation(self) -> None:
        cases = [
            (
                "front_center",
                {"x": 22.0, "y": 0.0, "z": 8.0},
                {"x": 18.0, "y": 4.0, "z": 10.0},
                FINGER_NOTCH_WALL_FRONT,
                FUSION_SKETCH_PLANE_XZ,
                FUSION_EXTENT_POSITIVE,
                {"x": 26.8, "y": 0.8, "z": 13.0},
                {"x": 44.8, "y": 0.8, "z": 24.0},
            ),
            (
                "back_center",
                {"x": 22.0, "y": 48.8, "z": 8.0},
                {"x": 18.0, "y": 3.2, "z": 10.0},
                FINGER_NOTCH_WALL_BACK,
                FUSION_SKETCH_PLANE_XZ,
                FUSION_EXTENT_NEGATIVE,
                {"x": 26.8, "y": 60.0, "z": 13.0},
                {"x": 44.8, "y": 60.0, "z": 24.0},
            ),
            (
                "left_side",
                {"x": 0.0, "y": 17.0, "z": 8.0},
                {"x": 4.0, "y": 18.0, "z": 10.0},
                FINGER_NOTCH_WALL_LEFT,
                FUSION_SKETCH_PLANE_YZ,
                FUSION_EXTENT_POSITIVE,
                {"x": 0.8, "y": 21.8, "z": 13.0},
                {"x": 0.8, "y": 39.8, "z": 24.0},
            ),
            (
                "right_side",
                {"x": 58.8, "y": 17.0, "z": 8.0},
                {"x": 3.2, "y": 18.0, "z": 10.0},
                FINGER_NOTCH_WALL_RIGHT,
                FUSION_SKETCH_PLANE_YZ,
                FUSION_EXTENT_NEGATIVE,
                {"x": 70.0, "y": 21.8, "z": 13.0},
                {"x": 70.0, "y": 39.8, "z": 24.0},
            ),
        ]
        for placement, position, size, wall, sketch_plane, direction, start, end in cases:
            with self.subTest(placement=placement):
                payload = _cad_ir_payload_from_example("simple_finger_notch_tray.json")
                operation = payload["components"][0]["body"]["operations"][2]
                operation["parameters"]["placement"] = placement
                operation["parameters"]["position_mm"] = dict(position)
                operation["parameters"]["size_mm"] = dict(size)

                plan = generation_plan_from_cad_ir(payload)

                self.assertEqual(len(plan.finger_notch_cuts), 1)
                cut = plan.finger_notch_cuts[0]
                self.assertEqual(cut.wall, wall)
                self.assertEqual(cut.sketch_plane, sketch_plane)
                self.assertEqual(cut.extrude_direction, direction)
                self.assertTrue(cut.top_open)
                self.assertAlmostEqual(cut.notch_depth_from_top_mm, size["z"])
                self.assertGreater(cut.profile_top_z_mm, cut.cut_origin_mm.z + cut.notch_depth_from_top_mm)
                self.assertAlmostEqual(cut.profile_bottom_z_mm, 13.0)
                self.assertAlmostEqual(cut.profile_top_z_mm, 24.0)
                _assert_vector_almost_equal(self, cut.profile_start_mm, start)
                _assert_vector_almost_equal(self, cut.profile_end_mm, end)

    def test_rejects_finger_notch_with_unknown_cavity(self) -> None:
        payload = _cad_ir_payload_from_example("simple_finger_notch_tray.json")
        operation = payload["components"][0]["body"]["operations"][2]
        operation["parameters"]["cavity_id"] = "missing-cavity"

        with self.assertRaisesRegex(FusionSkeletonError, "unknown cavity"):
            generation_plan_from_cad_ir(payload)

    def test_rejects_finger_notch_that_exceeds_front_wall(self) -> None:
        payload = _cad_ir_payload_from_example("simple_finger_notch_tray.json")
        operation = payload["components"][0]["body"]["operations"][2]
        operation["parameters"]["size_mm"]["y"] = 5.0

        with self.assertRaisesRegex(FusionSkeletonError, "front wall thickness"):
            generation_plan_from_cad_ir(payload)

    def test_rejects_finger_notch_that_starts_outside_cavity(self) -> None:
        payload = _cad_ir_payload_from_example("simple_finger_notch_tray.json")
        operation = payload["components"][0]["body"]["operations"][2]
        operation["parameters"]["position_mm"]["x"] = -1.0

        with self.assertRaisesRegex(FusionSkeletonError, "must be non-negative"):
            generation_plan_from_cad_ir(payload)

    def test_rejects_top_open_finger_notch_below_cavity_floor(self) -> None:
        payload = _cad_ir_payload_from_example("simple_finger_notch_tray.json")
        operation = payload["components"][0]["body"]["operations"][2]
        operation["parameters"]["size_mm"]["z"] = 22.0

        with self.assertRaisesRegex(FusionSkeletonError, "top-open depth"):
            generation_plan_from_cad_ir(payload)

    def test_rejects_cavity_cut_that_exceeds_printable_blank_xy(self) -> None:
        payload = _cad_ir_payload_from_example("simple_tray.json")
        operation = payload["components"][0]["body"]["operations"][1]
        operation["parameters"]["size_mm"]["x"] = 80.0

        with self.assertRaisesRegex(FusionSkeletonError, "exceeds printable blank width"):
            generation_plan_from_cad_ir(payload)

    def test_rejects_cavity_cut_that_removes_the_requested_floor(self) -> None:
        payload = _cad_ir_payload_from_example("simple_tray.json")
        operation = payload["components"][0]["body"]["operations"][1]
        operation["parameters"]["size_mm"]["z"] = 22.5

        with self.assertRaisesRegex(FusionSkeletonError, "below CAD IR local_origin.z"):
            generation_plan_from_cad_ir(payload)

    def test_addin_manifest_matches_current_fusion_contract(self) -> None:
        addin_dir = ROOT / "fusion_addin" / "BoardGameInsertGenerator"
        script_path = addin_dir / "BoardGameInsertGenerator.py"
        manifest_path = addin_dir / "BoardGameInsertGenerator.manifest"

        self.assertTrue(script_path.is_file())
        self.assertTrue(manifest_path.is_file())
        self.assertEqual(addin_dir.name, script_path.stem)
        self.assertEqual(addin_dir.name, manifest_path.stem)

        manifest = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
        self.assertEqual(manifest["autodeskProduct"], "Fusion")
        self.assertEqual(manifest["type"], "addin")
        self.assertEqual(manifest["supportedOS"], "windows|mac")
        self.assertFalse(manifest["runOnStartup"])
        self.assertTrue(manifest["editEnabled"])
        self.assertIsInstance(manifest["description"], dict)
        self.assertIn("", manifest["description"])

    def test_addin_entrypoint_uses_root_component_for_part_design_compatibility(self) -> None:
        entrypoint_path = ROOT / "fusion_addin" / "BoardGameInsertGenerator" / "BoardGameInsertGenerator.py"
        source = entrypoint_path.read_text(encoding="utf-8")

        self.assertNotIn("addNewComponent", source)
        self.assertIn("root_component.sketches.add", source)
        self.assertIn("root_component.features.extrudeFeatures.addSimple", source)
        self.assertIn("FeatureOperations.CutFeatureOperation", source)
        self.assertIn("participantBodies", source)
        self.assertIn("setOneSideExtent", source)
        self.assertIn("NegativeExtentDirection", source)
        self.assertIn("PositiveExtentDirection", source)
        self.assertIn("xZConstructionPlane", source)
        self.assertIn("yZConstructionPlane", source)
        self.assertIn("modelToSketchSpace", source)
        self.assertIn("finger_notch_features_planned", source)
        self.assertIn("finger_notch_cuts", source)
        self.assertIn("grid_positioned_blanks", source)
        self.assertIn("Grid-positioned module bodies", source)
        self.assertIn("_xy_plane_for_z", source)
        self.assertIn("Simple top-open finger notch cuts", source)
        self.assertIn("top-open rectangular wall cut", source)
        self.assertIn("compatible with Part Design documents", source)
        self.assertIn("resolve_cad_ir_input_path", source)
        self.assertIn("cad_ir_input_guidance", source)
        self.assertIn("Input CAD IR", source)


def _assert_vector_almost_equal(test_case: unittest.TestCase, vector, expected: dict[str, float]) -> None:
    test_case.assertAlmostEqual(vector.x, expected["x"])
    test_case.assertAlmostEqual(vector.y, expected["y"])
    test_case.assertAlmostEqual(vector.z, expected["z"])


def _cad_ir_payload() -> dict:
    return _cad_ir_payload_from_example("simple_box.json")


def _cad_ir_payload_from_example(filename: str) -> dict:
    config = load_config(ROOT / "examples" / filename)
    layout = generate_basic_layout(config)
    return build_blank_cad_scene(config, layout).to_dict()


if __name__ == "__main__":
    unittest.main()
