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
    ASSEMBLY_DOCUMENT_REQUIRED_STATUS,
    BGIG_ACTION_GUIDANCE,
    BGIG_CLEAR_SCOPE,
    BGIG_EXISTING_SCENE_MESSAGE,
    BGIG_GENERATE_EXISTING_SCENE_POLICY,
    BGIG_PARAMETRIC_FIELDS_STATUS,
    BGIG_QUICK_PARAMETRIC_BOX_STATUS,
    BGIG_SCENE_ROOT_COMPONENT_NAME,
    BGIG_SCENE_ROOT_ROLE,
    BGIG_SCENE_OWNERSHIP_POLICY,
    BGIG_COMPONENT_CREATION_POLICY,
    BGIG_SOURCE_HELPER_POLICY,
    BGIG_UI_SETTINGS_FILENAME,
    BGIG_VISIBLE_OCCURRENCE_POLICY,
    BGIG_COMMAND_NAME,
    BGIG_TOOLBAR_LOCATION,
    BGIG_TOOLBAR_PANEL_IDS,
    BGIG_TOOLBAR_WORKSPACE_ID,
    BGIG_UI_REOPEN_POLICY,
    CAD_IR_PATH_OVERRIDE_FILENAME,
    DEFAULT_CAD_IR_INPUT_FILENAME,
    COMPACT_OCCURRENCE_ROLE,
    EXPLODED_OCCURRENCE_ROLE,
    EXPLODED_VIEW_MODE_FILENAME,
    DOCUMENT_STATUS_READY,
    DOCUMENT_STATUS_ZERO_DOC,
    CAVITY_CUT_OPERATION_KIND,
    FINGER_NOTCH_CUT_OPERATION_KIND,
    FINGER_NOTCH_WALL_BACK,
    FINGER_NOTCH_WALL_FRONT,
    FINGER_NOTCH_WALL_LEFT,
    FINGER_NOTCH_WALL_RIGHT,
    FUSION_COMMAND_ACTION_CLEAR,
    FUSION_COMMAND_ACTION_GENERATE,
    FUSION_COMMAND_ACTION_REGENERATE,
    FUSION_INPUT_MODE_CAD_IR_FILE,
    FUSION_INPUT_MODE_CONFIG_FILE,
    FUSION_INPUT_MODE_QUICK_PARAMETRIC_BOX,
    FUSION_GENERATION_MODE_COMPACT_AND_EXPLODED,
    FUSION_GENERATION_MODE_COMPACT_ONLY,
    FUSION_EXTENT_NEGATIVE,
    FUSION_EXTENT_POSITIVE,
    FUSION_MANUAL_VALIDATION_REQUIRED,
    FUSION_SKETCH_PLANE_XZ,
    FUSION_SKETCH_PLANE_YZ,
    GRID_PLACED_BLANK_OPERATION_KIND,
    LINKED_OCCURRENCE_OPERATION_KIND,
    OCCURRENCE_NAME_POLICY_COMPONENT_SOURCE,
    P12_PARAMETRIC_FIELD_DEFAULTS,
    PLAN_STATUS_PLANNED_ONLY,
    FusionSkeletonError,
    apply_parametric_overrides_to_config_payload,
    assembly_document_required_message,
    build_fusion_command_request,
    cad_ir_input_guidance,
    default_fusion_command_values,
    default_fusion_ui_settings,
    detect_bgig_project_root,
    describe_document_state,
    fusion_command_summary,
    fusion_ui_settings_path,
    fusion_ui_launch_plan,
    generation_plan_from_cad_ir,
    is_part_design_component_limit_error,
    load_cad_ir_json,
    load_fusion_ui_settings,
    mm_to_cm,
    parse_parametric_overrides,
    planned_operations_from_cad_ir,
    resolve_cad_ir_input_path,
    resolve_generation_mode,
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

    def test_detects_part_design_single_component_limit_error(self) -> None:
        error = RuntimeError(
            "3 : Failed to create component: Part Design documents can only contain "
            "one component, please add this Part to an Assembly to add multiple components."
        )

        self.assertTrue(is_part_design_component_limit_error(error))
        self.assertFalse(is_part_design_component_limit_error(RuntimeError("different Fusion error")))

    def test_assembly_document_required_message_is_actionable(self) -> None:
        message = assembly_document_required_message(
            "Part Design documents can only contain one component"
        )

        self.assertIn(ASSEMBLY_DOCUMENT_REQUIRED_STATUS.replace("_", " "), message)
        self.assertIn("one Fusion Component per physical BGIG module", message)
        self.assertIn("Part Design", message)
        self.assertIn("Assembly-compatible", message)
        self.assertIn("add this Part to an Assembly", message)
        self.assertIn("did not fall back to independent exploded body copies", message)

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

    def test_describes_reopenable_toolbar_launch_plan(self) -> None:
        plan = fusion_ui_launch_plan()
        payload = plan.to_dict()

        self.assertEqual(plan.command_name, BGIG_COMMAND_NAME)
        self.assertEqual(plan.toolbar_workspace_id, BGIG_TOOLBAR_WORKSPACE_ID)
        self.assertEqual(plan.toolbar_location, BGIG_TOOLBAR_LOCATION)
        self.assertEqual(plan.reopen_policy, BGIG_UI_REOPEN_POLICY)
        self.assertTrue(plan.opens_dialog_on_run)
        self.assertTrue(plan.legacy_files_are_defaults_only)
        self.assertTrue(plan.config_input_supported)
        self.assertEqual(plan.clear_scope, BGIG_CLEAR_SCOPE)
        self.assertIn(FUSION_COMMAND_ACTION_GENERATE, plan.command_actions)
        self.assertIn(FUSION_COMMAND_ACTION_REGENERATE, plan.command_actions)
        self.assertIn(FUSION_COMMAND_ACTION_CLEAR, plan.command_actions)
        self.assertIn("box_inner_x_mm", plan.parametric_fields)
        self.assertIn("grid_units_z", plan.parametric_fields)
        self.assertIn("SolidScriptsAddinsPanel", BGIG_TOOLBAR_PANEL_IDS)
        self.assertIn("Utilities", payload["toolbar_location"])
        self.assertEqual(payload["toolbar_panel_ids"], list(BGIG_TOOLBAR_PANEL_IDS))
        self.assertEqual(payload["clear_scope"], BGIG_CLEAR_SCOPE)

    def test_builds_fusion_command_request_from_ui_values(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            addin_dir = Path(temp_dir)
            cad_ir_path = addin_dir / "scene.json"
            cad_ir_path.write_text(json.dumps(_cad_ir_payload()), encoding="utf-8")

            request = build_fusion_command_request(
                "scene.json",
                FUSION_GENERATION_MODE_COMPACT_ONLY,
                addin_dir,
            )

        self.assertEqual(request.cad_ir_path.name, "scene.json")
        self.assertEqual(request.generation_mode, FUSION_GENERATION_MODE_COMPACT_ONLY)
        self.assertEqual(request.action, FUSION_COMMAND_ACTION_GENERATE)
        self.assertEqual(request.source_kind, "cad_ir")
        self.assertIn("Generation mode: compact_only", fusion_command_summary(request))

    def test_builds_config_source_request_with_project_root_detection(self) -> None:
        config_path = ROOT / "examples" / "simple_asset_product_scene.json"

        request = build_fusion_command_request(
            "",
            FUSION_GENERATION_MODE_COMPACT_AND_EXPLODED,
            ROOT / "fusion_addin" / "BoardGameInsertGenerator",
            config_json_path_text=str(config_path),
            parameter_values={"box_inner_x_mm": "121.5", "grid_units_z": "2"},
        )

        self.assertIsNone(request.cad_ir_path)
        self.assertEqual(request.config_json_path, config_path.resolve())
        self.assertEqual(request.project_root, ROOT)
        self.assertEqual(request.source_kind, "config")
        self.assertEqual(request.parameter_overrides["box_inner_x_mm"], 121.5)
        self.assertEqual(request.parameter_overrides["grid_units_z"], 2)
        self.assertIn("Source: BGIG config JSON", fusion_command_summary(request))

    def test_builds_clear_request_without_requiring_input_file(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            request = build_fusion_command_request(
                "",
                FUSION_GENERATION_MODE_COMPACT_ONLY,
                Path(temp_dir),
                action=FUSION_COMMAND_ACTION_CLEAR,
            )

        self.assertIsNone(request.cad_ir_path)
        self.assertEqual(request.action, FUSION_COMMAND_ACTION_CLEAR)
        self.assertEqual(request.source_kind, "clear_only")
        summary = fusion_command_summary(request)
        self.assertIn("Clear tagged BGIG scene objects", summary)
        self.assertIn(BGIG_GENERATE_EXISTING_SCENE_POLICY, summary)
        self.assertIn(BGIG_ACTION_GUIDANCE, summary)

    def test_parses_and_applies_p12_parametric_config_overrides(self) -> None:
        payload = json.loads((ROOT / "examples" / "simple_asset_product_scene.json").read_text(encoding="utf-8"))
        overrides = parse_parametric_overrides(
            {
                **P12_PARAMETRIC_FIELD_DEFAULTS,
                "box_inner_x_mm": "122.5",
                "box_inner_y_mm": "91,5",
                "grid_units_x": "5",
                "wall_thickness_mm": "1.4",
                "floor_thickness_mm": "1.6",
                "peripheral_clearance_mm": "0.9",
                "module_gap_mm": "0.7",
                "print_profile": "fine_detail",
            }
        )

        updated = apply_parametric_overrides_to_config_payload(payload, overrides)

        self.assertEqual(updated["box"]["inner_dimensions_mm"]["x"], 122.5)
        self.assertEqual(updated["box"]["inner_dimensions_mm"]["y"], 91.5)
        self.assertEqual(updated["volumetric_grid"]["size_units"]["x"], 5)
        self.assertEqual(updated["defaults"]["wall_thickness_mm"], 1.4)
        self.assertEqual(updated["defaults"]["floor_thickness_mm"], 1.6)
        self.assertEqual(updated["tolerances"]["peripheral_clearance_mm"], 0.9)
        self.assertEqual(updated["tolerances"]["module_gap_mm"], 0.7)
        self.assertEqual(updated["print_profile"], "fine_detail")
        self.assertNotEqual(payload["box"]["inner_dimensions_mm"]["x"], 122.5)

    def test_rejects_grid_override_without_volumetric_grid(self) -> None:
        payload = json.loads((ROOT / "examples" / "simple_tray.json").read_text(encoding="utf-8"))

        with self.assertRaisesRegex(FusionSkeletonError, "volumetric_grid"):
            apply_parametric_overrides_to_config_payload(payload, {"grid_units_x": 4})
    def test_rejects_parametric_overrides_in_cad_ir_mode(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            addin_dir = Path(temp_dir)
            cad_ir_path = addin_dir / "scene.json"
            cad_ir_path.write_text(json.dumps(_cad_ir_payload()), encoding="utf-8")

            with self.assertRaisesRegex(FusionSkeletonError, "config_file mode"):
                build_fusion_command_request(
                    "scene.json",
                    FUSION_GENERATION_MODE_COMPACT_ONLY,
                    addin_dir,
                    parameter_values={"box_inner_x_mm": "120"},
                    input_mode=FUSION_INPUT_MODE_CAD_IR_FILE,
                )

    def test_rejects_quick_parametric_box_until_real_builder_exists(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            with self.assertRaisesRegex(FusionSkeletonError, "quick_parametric_box"):
                build_fusion_command_request(
                    "",
                    FUSION_GENERATION_MODE_COMPACT_AND_EXPLODED,
                    Path(temp_dir),
                    parameter_values={"box_inner_x_mm": "120"},
                    input_mode=FUSION_INPUT_MODE_QUICK_PARAMETRIC_BOX,
                )

    def test_default_ui_settings_reads_local_settings_file(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            addin_dir = Path(temp_dir)
            settings_path = addin_dir / BGIG_UI_SETTINGS_FILENAME
            settings_path.write_text(
                json.dumps(
                    {
                        "config_json_path": str(ROOT / "examples" / "simple_tray.json"),
                        "project_root": str(ROOT),
                    }
                ),
                encoding="utf-8",
            )

            settings = default_fusion_ui_settings(addin_dir)

        self.assertEqual(settings["input_mode"], FUSION_INPUT_MODE_CONFIG_FILE)
        self.assertEqual(Path(settings["config_json_path"]), (ROOT / "examples" / "simple_tray.json").resolve())
        self.assertEqual(Path(settings["project_root"]), ROOT)
        self.assertEqual(Path(settings["settings_path"]).name, BGIG_UI_SETTINGS_FILENAME)

    def test_detects_bgig_project_root_from_config_path(self) -> None:
        detected = detect_bgig_project_root(
            ROOT / "examples" / "simple_asset_product_scene.json",
            ROOT / "fusion_addin" / "BoardGameInsertGenerator",
        )

        self.assertEqual(detected, ROOT)
    def test_rejects_fusion_command_request_without_existing_cad_ir(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            with self.assertRaisesRegex(FusionSkeletonError, "CAD IR JSON file not found"):
                build_fusion_command_request(
                    "missing.json",
                    FUSION_GENERATION_MODE_COMPACT_ONLY,
                    Path(temp_dir),
                )

    def test_default_fusion_command_values_prefill_product_config_when_root_is_detected(self) -> None:
        request = default_fusion_command_values(ROOT / "fusion_addin" / "BoardGameInsertGenerator")

        self.assertEqual(request.input_mode, FUSION_INPUT_MODE_CONFIG_FILE)
        self.assertEqual(request.source_kind, "config")
        self.assertEqual(request.config_json_path, (ROOT / "examples" / "simple_asset_product_scene.json").resolve())
        self.assertEqual(request.project_root, ROOT)
        self.assertEqual(request.generation_mode, FUSION_GENERATION_MODE_COMPACT_AND_EXPLODED)

    def test_builds_explicit_cad_ir_file_mode_request(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            addin_dir = Path(temp_dir)
            cad_ir_path = addin_dir / DEFAULT_CAD_IR_INPUT_FILENAME
            cad_ir_path.write_text(json.dumps(_cad_ir_payload()), encoding="utf-8")

            request = build_fusion_command_request(
                str(cad_ir_path),
                FUSION_GENERATION_MODE_COMPACT_AND_EXPLODED,
                addin_dir,
                input_mode=FUSION_INPUT_MODE_CAD_IR_FILE,
            )

        self.assertEqual(request.input_mode, FUSION_INPUT_MODE_CAD_IR_FILE)
        self.assertEqual(request.cad_ir_path.name, DEFAULT_CAD_IR_INPUT_FILENAME)
        self.assertEqual(request.generation_mode, FUSION_GENERATION_MODE_COMPACT_AND_EXPLODED)

    def test_resolves_default_generation_mode_to_compact_and_exploded(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            self.assertEqual(
                resolve_generation_mode(Path(temp_dir)),
                FUSION_GENERATION_MODE_COMPACT_AND_EXPLODED,
            )

    def test_resolves_compact_only_generation_mode_override(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            addin_dir = Path(temp_dir)
            (addin_dir / EXPLODED_VIEW_MODE_FILENAME).write_text("compact_only\n", encoding="utf-8")

            self.assertEqual(
                resolve_generation_mode(addin_dir),
                FUSION_GENERATION_MODE_COMPACT_ONLY,
            )

    def test_rejects_unknown_generation_mode_override(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            addin_dir = Path(temp_dir)
            (addin_dir / EXPLODED_VIEW_MODE_FILENAME).write_text("explode_everything\n", encoding="utf-8")

            with self.assertRaisesRegex(FusionSkeletonError, "Unsupported Fusion generation mode"):
                resolve_generation_mode(addin_dir)

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
        self.assertEqual(plan.created_object_count, 5)
        self.assertEqual([blank.body_name for blank in plan.blanks], [
            "cards-main-01 rectangular blank",
            "dice-01 rectangular blank",
        ])
        self.assertEqual([occurrence.occurrence_name for occurrence in plan.exploded_occurrences], [
            "cards-main-01 rectangular blank exploded occurrence",
            "dice-01 rectangular blank exploded occurrence",
        ])
        self.assertTrue(plan.linked_exploded_occurrences)

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

        self.assertEqual(plan.created_object_count, 5)
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
        self.assertEqual(plan.created_object_count, 5)
        grid_blank = plan.grid_positioned_blanks[0]
        self.assertEqual(grid_blank.role, "generated_asset_grid_blank")
        self.assertEqual(grid_blank.operation_kind, GRID_PLACED_BLANK_OPERATION_KIND)
        self.assertEqual(grid_blank.component_name, "Grid placed Grouped candidate for tokens")
        self.assertEqual(grid_blank.origin_mm.to_dict(), {"x": 30.0, "y": 0.0, "z": 0.0})
        self.assertEqual(grid_blank.size_mm.to_dict(), {"x": 25.6, "y": 25.6, "z": 9.8})
        self.assertEqual(grid_blank.printable_body_size_mm.to_dict(), {"x": 25.6, "y": 25.6, "z": 9.8})
        self.assertEqual(grid_blank.body_size_source, "printable_body_size_mm")
        self.assertNotEqual(grid_blank.size_mm.to_dict(), grid_blank.theoretical_grid_extent_mm.to_dict())
        self.assertEqual(grid_blank.asset_fit_size_mm.to_dict(), {"x": 23.2, "y": 23.2, "z": 8.6})
        self.assertEqual(grid_blank.theoretical_grid_extent_mm.to_dict(), {"x": 30.0, "y": 30.0, "z": 10.0})
        self.assertEqual(plan.to_dict()["grid_positioned_blanks"][0]["body_name"], grid_blank.body_name)
        self.assertEqual(plan.to_dict()["grid_positioned_blanks"][0]["body_size_source"], "printable_body_size_mm")
        self.assertEqual(plan.to_dict()["grid_positioned_blanks"][0]["module_source"], "asset_candidate")
        self.assertEqual(
            plan.to_dict()["grid_positioned_blanks"][0]["theoretical_grid_extent_mm"],
            {"x": 30.0, "y": 30.0, "z": 10.0},
        )


    def test_product_asset_scene_generates_single_sourced_grid_module(self) -> None:
        payload = _cad_ir_payload_from_example("simple_asset_product_scene.json")

        plan = generation_plan_from_cad_ir(payload)

        self.assertEqual(len(plan.blanks), 0)
        self.assertEqual(len(plan.grid_positioned_blanks), 1)
        self.assertEqual(plan.module_component_count, 1)
        self.assertEqual(len(plan.compact_occurrences), 1)
        self.assertEqual(len(plan.exploded_occurrences), 1)
        grid_blank = plan.grid_positioned_blanks[0]
        self.assertEqual(grid_blank.module_source, "asset_candidate")
        self.assertEqual(grid_blank.placement_source, "grid_placement")
        self.assertEqual(grid_blank.source_asset_ids, ("coin-tokens", "status-tokens"))
        self.assertEqual(grid_blank.candidate_id, "asset-group-candidate:tokens:store:exact")
        self.assertEqual(grid_blank.origin_mm.to_dict(), {"x": 0.0, "y": 0.0, "z": 0.0})
        self.assertEqual(grid_blank.size_mm.to_dict(), {"x": 25.6, "y": 25.6, "z": 9.8})
        self.assertEqual(grid_blank.theoretical_grid_extent_mm.to_dict(), {"x": 30.0, "y": 30.0, "z": 10.0})
        self.assertEqual(grid_blank.body_size_source, "printable_body_size_mm")
        self.assertEqual(grid_blank.clearance_applied["peripheral_clearance_mm"], 0.0)
        self.assertEqual(grid_blank.clearance_applied["inter_module_gap_mm"], 0.0)
        plan_dict = plan.to_dict()
        self.assertEqual(plan_dict["blanks"], [])
        self.assertEqual(plan_dict["grid_positioned_blanks"][0]["module_source"], "asset_candidate")
        self.assertEqual(plan_dict["grid_positioned_blanks"][0]["placement_source"], "grid_placement")
        self.assertEqual(plan_dict["grid_positioned_blanks"][0]["source_asset_ids"], ["coin-tokens", "status-tokens"])

    def test_rejects_modern_grid_placement_without_printable_body_size(self) -> None:
        payload = _cad_ir_payload_from_example("simple_asset_executable_plan.json")
        placement = payload["metadata"]["executable_asset_plan"]["placements"][0]
        generated_module = payload["metadata"]["executable_asset_plan"]["generated_modules"][0]
        placement.pop("printable_body_size_mm")
        generated_module.pop("printable_body_size_mm")

        with self.assertRaisesRegex(FusionSkeletonError, "does not provide printable_body_size_mm"):
            generation_plan_from_cad_ir(payload)


    def test_grid_positioned_asset_blank_supports_z_layer_origin(self) -> None:
        payload = _cad_ir_payload_from_example("simple_asset_executable_plan.json")
        placement = payload["metadata"]["executable_asset_plan"]["placements"][0]
        placement["origin_units"] = {"x": 1, "y": 0, "z": 1}
        placement["origin_mm"] = {"x": 30.0, "y": 0.0, "z": 10.0}
        placement["theoretical_grid_origin_mm"] = {"x": 30.0, "y": 0.0, "z": 10.0}
        placement["printable_body_origin_mm"] = {"x": 30.0, "y": 0.0, "z": 10.0}

        plan = generation_plan_from_cad_ir(payload)

        grid_blank = plan.grid_positioned_blanks[0]
        self.assertEqual(grid_blank.origin_mm.to_dict(), {"x": 30.0, "y": 0.0, "z": 10.0})
        self.assertEqual(grid_blank.size_mm.to_dict(), {"x": 25.6, "y": 25.6, "z": 9.8})
        self.assertEqual(grid_blank.printable_body_size_mm.to_dict(), {"x": 25.6, "y": 25.6, "z": 9.8})
        self.assertEqual(grid_blank.body_size_source, "printable_body_size_mm")
        self.assertNotEqual(grid_blank.size_mm.to_dict(), grid_blank.theoretical_grid_extent_mm.to_dict())

    def test_builds_multilayer_grid_scene_with_linked_occurrences(self) -> None:
        payload = _cad_ir_payload_from_example("simple_multilayer_grid_scene.json")

        plan = generation_plan_from_cad_ir(payload)

        self.assertEqual(len(plan.blanks), 1)
        self.assertEqual(len(plan.grid_positioned_blanks), 2)
        self.assertEqual(plan.module_component_count, 3)
        self.assertEqual(plan.multi_layer_grid_module_count, 1)
        self.assertEqual(plan.grid_modules_with_z_placement_count, 1)
        self.assertEqual(plan.grid_module_height_variant_count, 2)
        self.assertEqual(len(plan.compact_occurrences), 3)
        self.assertEqual(len(plan.exploded_occurrences), 3)
        self.assertTrue(plan.linked_exploded_occurrences)

        low_blank = plan.grid_positioned_blanks[0]
        high_blank = plan.grid_positioned_blanks[1]
        self.assertEqual(low_blank.grid_origin_units, (1, 0, 0))
        self.assertEqual(low_blank.grid_size_units, (3, 3, 1))
        self.assertEqual(low_blank.origin_mm.to_dict(), {"x": 30.0, "y": 0.0, "z": 0.0})
        self.assertEqual(low_blank.size_mm.to_dict(), {"x": 61.6, "y": 61.6, "z": 7.8})
        self.assertEqual(low_blank.printable_body_size_mm.to_dict(), {"x": 61.6, "y": 61.6, "z": 7.8})
        self.assertEqual(low_blank.body_size_source, "printable_body_size_mm")
        self.assertEqual(low_blank.theoretical_grid_extent_mm.to_dict(), {"x": 90.0, "y": 90.0, "z": 10.0})
        self.assertEqual(high_blank.grid_origin_units, (0, 0, 1))
        self.assertEqual(high_blank.grid_size_units, (2, 2, 2))
        self.assertEqual(high_blank.origin_mm.to_dict(), {"x": 0.0, "y": 0.0, "z": 10.0})
        self.assertEqual(high_blank.size_mm.to_dict(), {"x": 37.6, "y": 37.6, "z": 17.8})
        self.assertEqual(high_blank.printable_body_size_mm.to_dict(), {"x": 37.6, "y": 37.6, "z": 17.8})
        self.assertEqual(high_blank.body_size_source, "printable_body_size_mm")
        self.assertEqual(high_blank.theoretical_grid_extent_mm.to_dict(), {"x": 60.0, "y": 60.0, "z": 20.0})

        high_compact = [
            occurrence
            for occurrence in plan.compact_occurrences
            if occurrence.component_id == high_blank.cad_id
        ][0]
        high_exploded = [
            occurrence
            for occurrence in plan.exploded_occurrences
            if occurrence.component_id == high_blank.cad_id
        ][0]
        self.assertEqual(high_compact.origin_mm.to_dict(), {"x": 0.0, "y": 0.0, "z": 10.0})
        self.assertEqual(high_exploded.view_role, EXPLODED_OCCURRENCE_ROLE)
        self.assertTrue(high_exploded.linked_component)

        plan_dict = plan.to_dict()
        self.assertEqual(plan_dict["multi_layer_grid_modules"], 1)
        self.assertEqual(plan_dict["grid_modules_with_z_placement"], 1)
        self.assertEqual(plan_dict["grid_module_height_variants"], 2)
        self.assertEqual(
            plan_dict["grid_positioned_blanks"][1]["grid_size_units"],
            {"x": 2, "y": 2, "z": 2},
        )

    def test_builds_basic_exploded_view_from_linked_compact_and_grid_occurrences(self) -> None:
        payload = _cad_ir_payload_from_example("simple_asset_executable_plan.json")

        plan = generation_plan_from_cad_ir(payload)

        self.assertEqual(plan.generation_mode, FUSION_GENERATION_MODE_COMPACT_AND_EXPLODED)
        self.assertTrue(plan.requires_assembly_document)
        self.assertTrue(plan.to_dict()["requires_assembly_document"])
        self.assertEqual(plan.module_component_count, 2)
        self.assertEqual(len(plan.compact_occurrences), 2)
        self.assertEqual(len(plan.exploded_occurrences), 2)
        self.assertTrue(plan.linked_exploded_occurrences)

        compact_occurrence = plan.compact_occurrences[0]
        compact_exploded = plan.exploded_occurrences[0]
        grid_exploded = plan.exploded_occurrences[1]

        self.assertEqual(compact_occurrence.view_role, COMPACT_OCCURRENCE_ROLE)
        self.assertEqual(compact_occurrence.component_id, "manual-reference-bin-01-body")
        self.assertEqual(compact_occurrence.origin_mm.to_dict(), {"x": 0.8, "y": 0.8, "z": 0.0})
        self.assertEqual(compact_exploded.view_role, EXPLODED_OCCURRENCE_ROLE)
        self.assertEqual(compact_exploded.operation_kind, LINKED_OCCURRENCE_OPERATION_KIND)
        self.assertTrue(compact_exploded.linked_component)
        self.assertEqual(compact_exploded.component_id, compact_occurrence.component_id)
        self.assertEqual(compact_exploded.source_body_id, "manual-reference-bin-01-body")
        self.assertEqual(compact_exploded.occurrence_name, "manual-reference-bin-01 rectangular blank exploded occurrence")
        self.assertEqual(compact_exploded.origin_mm.to_dict(), {"x": 140.0, "y": 0.0, "z": 0.0})
        self.assertEqual(
            grid_exploded.occurrence_name,
            "generated - asset-group-candidate - tokens - store - exact grid positioned rectangular blank exploded occurrence",
        )
        self.assertAlmostEqual(grid_exploded.origin_mm.x, 179.2)
        self.assertEqual(grid_exploded.origin_mm.y, 0.0)
        self.assertEqual(grid_exploded.origin_mm.z, 0.0)
        plan_dict = plan.to_dict()
        exploded_occurrence_dict = plan_dict["exploded_occurrences"][0]
        self.assertEqual(plan_dict["exploded_occurrences"][1]["operation_kind"], LINKED_OCCURRENCE_OPERATION_KIND)
        self.assertEqual(exploded_occurrence_dict["planned_occurrence_label"], compact_exploded.occurrence_name)
        self.assertEqual(
            exploded_occurrence_dict["occurrence_name_policy"],
            OCCURRENCE_NAME_POLICY_COMPONENT_SOURCE,
    P12_PARAMETRIC_FIELD_DEFAULTS,
        )
        self.assertFalse(exploded_occurrence_dict["direct_occurrence_rename"])
        self.assertTrue(plan_dict["linked_exploded_occurrences"])

    def test_compact_only_generation_mode_disables_exploded_view(self) -> None:
        payload = _cad_ir_payload_from_example("simple_asset_executable_plan.json")

        plan = generation_plan_from_cad_ir(
            payload,
            generation_mode=FUSION_GENERATION_MODE_COMPACT_ONLY,
        )

        self.assertEqual(len(plan.blanks), 1)
        self.assertEqual(len(plan.grid_positioned_blanks), 1)
        self.assertEqual(len(plan.exploded_occurrences), 0)
        self.assertEqual(plan.created_object_count, 3)

    def test_rejects_unknown_generation_mode_for_generation_plan(self) -> None:
        payload = _cad_ir_payload_from_example("simple_asset_executable_plan.json")

        with self.assertRaisesRegex(FusionSkeletonError, "Unsupported Fusion generation mode"):
            generation_plan_from_cad_ir(payload, generation_mode="explode_everything")

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
        placement["theoretical_grid_origin_mm"] = {"x": 0.0, "y": 0.0, "z": 0.0}
        placement["printable_body_origin_mm"] = {"x": 0.0, "y": 0.0, "z": 0.0}
        placement["origin_units"] = {"x": 0, "y": 0, "z": 0}

        with self.assertRaisesRegex(FusionSkeletonError, "collides"):
            generation_plan_from_cad_ir(payload)

    def test_rejects_grid_placement_outside_reference_box(self) -> None:
        payload = _cad_ir_payload_from_example("simple_asset_executable_plan.json")
        placement = payload["metadata"]["executable_asset_plan"]["placements"][0]
        placement["origin_mm"] = {"x": 120.0, "y": 0.0, "z": 0.0}
        placement["theoretical_grid_origin_mm"] = {"x": 120.0, "y": 0.0, "z": 0.0}
        placement["printable_body_origin_mm"] = {"x": 120.0, "y": 0.0, "z": 0.0}
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

    def test_addin_entrypoint_uses_linked_component_occurrences(self) -> None:
        entrypoint_path = ROOT / "fusion_addin" / "BoardGameInsertGenerator" / "BoardGameInsertGenerator.py"
        source = entrypoint_path.read_text(encoding="utf-8")

        self.assertIn("addNewComponent", source)
        self.assertIn("addExistingComponent", source)
        self.assertIn("transform2", source)
        self.assertNotIn("occurrence.name =", source)
        self.assertNotIn(".name = occurrence_plan.occurrence_name", source)
        self.assertIn("Module components created", source)
        self.assertIn("Physical module count", source)
        self.assertIn("Source components created", source)
        self.assertIn("Source/helper occurrences created", source)
        self.assertIn("Visible BGIG source/helper occurrences", source)
        self.assertIn("Compact occurrences created", source)
        self.assertIn("Exploded occurrences created", source)
        self.assertIn("Visible BGIG occurrences expected", source)
        self.assertIn("Visible BGIG occurrences actual", source)
        self.assertIn("Legacy bodies created", source)
        self.assertIn("Linked exploded occurrences", source)
        self.assertIn("Occurrence direct rename attempted: no", source)
        self.assertIn("Occurrence Browser names", source)
        self.assertIn("FusionAssemblyDocumentRequiredError", source)
        self.assertIn("Assembly-compatible Fusion document", source)
        self.assertIn("assembly document required", source)
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
        self.assertIn("compact_occurrences", source)
        self.assertIn("exploded_occurrences", source)
        self.assertIn("generated CAD IR scene from command UI", source)
        self.assertIn("commandCreated", source)
        self.assertIn("addStringValueInput", source)
        self.assertIn("addDropDownCommandInput", source)
        self.assertIn("build_fusion_command_request", source)
        self.assertIn("CAD IR JSON path", source)
        self.assertIn("resolve_generation_mode", source)
        self.assertIn("_xy_plane_for_z", source)
        self.assertIn("Simple top-open finger notch cuts", source)
        self.assertIn("Simple top-open finger notch cuts", source)
        self.assertIn("one Fusion component per physical BGIG module", source)
        self.assertIn("resolve_cad_ir_input_path", source)
        self.assertIn("cad_ir_input_guidance", source)
        self.assertIn("Input CAD IR", source)
        self.assertIn('BGIG_COMMAND_ID = "board_game_insert_generator_generate_scene"', source)
        self.assertNotIn('BGIG_COMMAND_ID = "board_game_insert_generator.generate_scene"', source)
        self.assertIn("BGIG_LEGACY_COMMAND_ID", source)
        self.assertIn("BGIG_TOOLBAR_WORKSPACE_ID", source)
        self.assertIn("BGIG_TOOLBAR_PANEL_IDS", source)
        self.assertIn("_add_toolbar_button", source)
        self.assertIn("controls.addCommand", source)
        self.assertIn("command.okButtonText", source)
        self.assertIn("_delete_command_control", source)
        self.assertIn("_delete_command_definition", source)
        self.assertIn("command_definition.execute()", source)
        self.assertLess(source.index("adsk.autoTerminate(False)"), source.index("command_definition.execute()"))
        self.assertIn("Module source mapping", source)
        self.assertIn("module_source", source)
        self.assertIn("placement_source", source)
        self.assertIn("Body sizing report", source)
        self.assertIn("body.boundingBox", source)
        self.assertIn("actual_fusion_body_bbox_mm", source)
        self.assertIn("printable body planned", source)
        self.assertIn("size match", source)
        self.assertIn("printable_body_size_mm", source)
        self.assertIn("UI reopen policy", source)
        self.assertIn("BGIG_UI_REOPEN_POLICY", source)
        self.assertIn("BGIG config JSON path", source)
        self.assertIn("BGIG project root", source)
        self.assertIn("Action", source)
        self.assertIn("FUSION_COMMAND_ACTION_REGENERATE", source)
        self.assertIn("FUSION_COMMAND_ACTION_CLEAR", source)
        self.assertIn("P12_PARAMETRIC_FIELD_LABELS", source)
        self.assertIn("apply_parametric_overrides_to_config_payload", source)
        self.assertIn("BGIG_GENERATED_CONFIG_FILENAME", source)
        self.assertIn("BGIG_GENERATED_CAD_IR_FILENAME", source)
        self.assertIn("_clear_bgig_scene", source)
        self.assertIn("findAttributes", source)
        self.assertIn("_find_bgig_attributes", source)
        self.assertIn("_tag_bgig_entity", source)
        self.assertIn("BGIG_CLEAR_SCOPE", source)
        self.assertIn("Print validation: false", source)
        self.assertIn("Input mode", source)
        self.assertIn("SUPPORTED_FUSION_INPUT_MODES", source)
        self.assertIn("default_fusion_ui_settings", source)
        self.assertIn("fusion_ui_settings_path", source)
        self.assertIn("BGIG Generated Scene", source)
        self.assertIn("BGIG_SCENE_ROOT_ROLE", source)
        self.assertIn("BGIG_COMPONENT_CREATION_POLICY", source)
        self.assertIn("BGIG_SOURCE_HELPER_POLICY", source)
        self.assertIn("BGIG_SCENE_OWNERSHIP_POLICY", source)
        self.assertIn("BGIG_VISIBLE_OCCURRENCE_POLICY", source)
        self.assertIn("_create_module_component_occurrence", source)
        self.assertIn("def _create_module_component_occurrence", source)
        self.assertNotIn("_create_module_source_component", source)
        self.assertNotIn("_hide_source_helper_occurrence", source)
        self.assertNotIn("occurrence.isLightBulbOn = False", source)
        self.assertIn("_count_visible_bgig_occurrences_by_role", source)
        self.assertIn("COMPACT_OCCURRENCE_ROLE", source)
        self.assertIn("EXPLODED_OCCURRENCE_ROLE", source)
        self.assertIn("scene_roots_created", source)
        self.assertIn("non_bgig_objects_preserved", source)
        self.assertIn("quick_parametric_box", source)
        self.assertIn("Config-file overrides only", source)
        self.assertIn("_count_bgig_scene_roots", source)
        self.assertIn("_bgig_scene_root_occurrences", source)
        self.assertIn("_count_bgig_tagged_objects", source)
        self.assertIn("scene_roots_deleted", source)
        self.assertIn("legacy_bgig_objects_deleted", source)
        self.assertIn("bgig_objects_remaining", source)
        self.assertIn("deleteMe()", source)
        self.assertIn("BGIG_ATTRIBUTE_ROLE_KEY", source)
        self.assertIn("BGIG_LEGACY_ATTRIBUTE_GROUPS", source)
        self.assertIn("_generate_existing_scene_blocked_message", source)
        self.assertIn("BGIG scene roots before", source)
        self.assertIn("BGIG scene roots after", source)
        self.assertIn("scene_roots_before", source)
        self.assertIn("scene_roots_after", source)
        self.assertIn("BGIG_EXISTING_SCENE_MESSAGE", source)
        self.assertIn("BGIG_GENERATE_EXISTING_SCENE_POLICY", source)
        skeleton_source = (ROOT / "fusion_addin" / "BoardGameInsertGenerator" / "fusion_skeleton.py").read_text(encoding="utf-8")
        self.assertIn(BGIG_EXISTING_SCENE_MESSAGE, skeleton_source)
        self.assertIn(BGIG_GENERATE_EXISTING_SCENE_POLICY, skeleton_source)
        self.assertIn(BGIG_COMPONENT_CREATION_POLICY, skeleton_source)
        self.assertIn(BGIG_SOURCE_HELPER_POLICY, skeleton_source)
        self.assertIn(BGIG_SCENE_OWNERSHIP_POLICY, skeleton_source)
        self.assertIn(BGIG_VISIBLE_OCCURRENCE_POLICY, skeleton_source)
        execute_block = source[
            source.index("def _execute_generation_request") : source.index("def _generate_cad_ir_from_config_request")
        ]
        self.assertIn("scene_roots_before = _count_bgig_scene_roots(design)", execute_block)
        self.assertIn("request.action == FUSION_COMMAND_ACTION_GENERATE and bgig_objects_before > 0", execute_block)
        self.assertLess(
            execute_block.index("request.action == FUSION_COMMAND_ACTION_GENERATE and bgig_objects_before > 0"),
            execute_block.index("cad_ir_path = request.cad_ir_path"),
        )
        self.assertLess(
            execute_block.index("generation_plan = generation_plan_from_cad_ir"),
            execute_block.index("if request.action == FUSION_COMMAND_ACTION_REGENERATE:"),
        )
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
