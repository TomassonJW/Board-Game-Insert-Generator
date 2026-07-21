from __future__ import annotations

import ast
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from context import ROOT

from board_game_insert_generator.cad_ir import build_blank_cad_scene
from board_game_insert_generator.config_loader import load_config
from board_game_insert_generator.layout import generate_basic_layout
from board_game_insert_generator.report import layout_to_json
from fusion_addin.BoardGameInsertGenerator import BoardGameInsertGenerator as fusion_entrypoint
from fusion_addin.BoardGameInsertGenerator.fusion_skeleton import (
    ASSEMBLY_DOCUMENT_REQUIRED_STATUS,
    ASSET_FIT_CAVITY_POLICY,
    ASSET_COMPARTMENT_CAVITY_POLICY,
    ASSET_ACCESS_POLICY,
    BGIG_ACTION_GUIDANCE,
    BGIG_CLEAR_SCOPE,
    BGIG_EXISTING_SCENE_MESSAGE,
    BGIG_GENERATE_EXISTING_SCENE_POLICY,
    BGIG_PARAMETRIC_FIELDS_STATUS,
    BGIG_QUICK_PARAMETRIC_BOX_STATUS,
    BGIG_QUICK_ASSET_BOX_DEFAULT_ASSETS,
    BGIG_QUICK_ASSET_BOX_FIELD,
    BGIG_QUICK_ASSET_BOX_MAX_STACK_HEIGHT_FIELD,
    BGIG_QUICK_ASSET_BOX_TARGET_ASPECT_RATIO_FIELD,
    BGIG_QUICK_ASSET_BOX_MAX_MODULE_LENGTH_FIELD,
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
    FUSION_COMMAND_ACTION_INSPECT,
    FUSION_COMMAND_ACTION_EXPORT_PRINTABLES,
    FUSION_COMMAND_ACTION_REGENERATE,
    FUSION_INPUT_MODE_CAD_IR_FILE,
    FUSION_INPUT_MODE_CONFIG_FILE,
    FUSION_INPUT_MODE_QUICK_PARAMETRIC_BOX,
    FUSION_INPUT_MODE_QUICK_ASSET_BOX,
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
    build_quick_parametric_box_cad_ir_payload,
    build_quick_asset_box_config_payload,
    cad_ir_input_guidance,
    default_fusion_command_values,
    default_fusion_ui_settings,
    detect_bgig_project_root,
    describe_document_state,
    fusion_command_summary,
    fusion_ui_settings_summary,
    fusion_ui_settings_path,
    fusion_ui_launch_plan,
    generation_plan_from_cad_ir,
    is_part_design_component_limit_error,
    load_cad_ir_json,
    load_fusion_ui_settings,
    parametric_values_from_ui_settings,
    mm_to_cm,
    parse_parametric_overrides,
    parse_quick_asset_box_assets_text,
    planned_operations_from_cad_ir,
    printable_export_filename,
    printable_export_result_summary,
    quick_parametric_box_summary,
    quick_asset_box_metadata,
    quick_asset_box_summary,
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


class _FakeAttribute:
    def __init__(self, group: str, name: str, value: str, parent) -> None:
        self.group = group
        self.name = name
        self.value = value
        self.parent = parent


class _FakeAttributeCollection:
    def __init__(self, owner) -> None:
        self.owner = owner
        self._attributes: list[_FakeAttribute] = []

    def add(self, group: str, name: str, value: str):
        existing = self.itemByName(group, name)
        if existing is not None:
            existing.value = value
            return existing
        attribute = _FakeAttribute(group, name, value, self.owner)
        self._attributes.append(attribute)
        return attribute

    def itemByName(self, group: str, name: str):
        for attribute in self._attributes:
            if attribute.group == group and attribute.name == name:
                return attribute
        return None


class _FakeFusionEntity:
    def __init__(self, name: str, token: str) -> None:
        self.name = name
        self.entityToken = token
        self.attributes = _FakeAttributeCollection(self)
        self.isVisible = True
        self.isLightBulbOn = True


class _FakeOccurrence(_FakeFusionEntity):
    def __init__(self, name: str, token: str, component=None) -> None:
        super().__init__(name, token)
        self.component = component
        self.deleted = False

    def deleteMe(self):
        self.deleted = True
        return True


class _FakeComponent(_FakeFusionEntity):
    def __init__(self, name: str, token: str) -> None:
        super().__init__(name, token)
        self.occurrences = _FakeCollection([])
        self.bRepBodies = _FakeCollection([])
        self.sketches = _FakeCollection([])
        self.features = _FakeFeatures([])


class _FakeBody(_FakeFusionEntity):
    pass


class _FakeSketch(_FakeFusionEntity):
    pass


class _FakeExtrudeFeature(_FakeFusionEntity):
    pass


class _FakeFeatures:
    def __init__(self, extrudes: list[object]) -> None:
        self.extrudeFeatures = _FakeCollection(extrudes)


class _FakeCollection:
    def __init__(self, items: list[object]) -> None:
        self._items = items
        self.count = len(items)

    def item(self, index: int):
        return self._items[index]

    def __iter__(self):
        return iter(self._items)


class _FakeDesignForRegistry:
    def __init__(self, root_component: _FakeComponent, entities: list[_FakeFusionEntity]) -> None:
        self.rootComponent = root_component
        self.entities = entities

    def findAttributes(self, group: str, name: str):
        found = []
        for entity in self.entities:
            for attribute in entity.attributes._attributes:
                if attribute.group == group and (name == "" or attribute.name == name):
                    found.append(attribute)
        return _FakeCollection(found)


class _FakeStlExportOptions:
    def __init__(self, geometry, filename: str) -> None:
        self.geometry = geometry
        self.filename = filename
        self.sendToPrintUtility = True
        self.isBinaryFormat = False


class _FakeExportManager:
    def __init__(self) -> None:
        self.created_options: list[_FakeStlExportOptions] = []
        self.executed_options: list[_FakeStlExportOptions] = []

    def createSTLExportOptions(self, geometry, filename: str):
        options = _FakeStlExportOptions(geometry, filename)
        self.created_options.append(options)
        return options

    def execute(self, options) -> bool:
        self.executed_options.append(options)
        return True


class FusionSkeletonTests(unittest.TestCase):
    def test_palette_contract_is_local_french_and_uses_the_fusion_bridge(self) -> None:
        addin_dir = ROOT / "fusion_addin" / "BoardGameInsertGenerator"
        source = (addin_dir / "BoardGameInsertGenerator.py").read_text(encoding="utf-8")
        markup = (addin_dir / "palette.html").read_text(encoding="utf-8")

        self.assertIn("_register_command_and_show_palette", source)
        self.assertIn("palettes.add", source)
        self.assertIn("incomingFromHTML", source)
        self.assertIn("sendInfoToHTML", source)
        self.assertIn("Atelier de rangement", markup)
        for label in ("Boîte et plateaux", "Conteneurs et éléments", "Réglages", "Aperçu"):
            self.assertIn(label, markup)
        self.assertIn("Recalculer maintenant", markup)
        self.assertNotIn('data-bridge="validate_project"', markup)
        self.assertIn("Enregistrer", markup)
        self.assertNotIn("Reglages experts", markup)
        self.assertIn("bgig.palette.request.v1", markup)
        self.assertIn("adsk.fusionSendData", markup)
        self.assertIn("fusionJavaScriptHandler", markup)
        self.assertNotIn("localhost", markup)

    def test_palette_state_keeps_the_print_status_honest(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            cad_ir_path = Path(temp_dir) / "selection.cad-ir.json"
            cad_ir_path.write_text("{}", encoding="utf-8")
            request = SimpleNamespace(cad_ir_path=cad_ir_path)
            inspection = {
                "bgig_scene_roots_total": 1,
                "bodies_tagged": 3,
                "bgig_name_like_untagged_entities": 0,
            }
            with patch.object(fusion_entrypoint, "_safe_default_command_request", return_value=request), patch.object(
                fusion_entrypoint, "_active_design", return_value=object()
            ), patch.object(fusion_entrypoint, "BgigFusionRegistry") as registry:
                registry.return_value.inspect.return_value = inspection
                state = fusion_entrypoint._palette_state(Path(temp_dir), notice="Scene actualisee.")

        self.assertEqual(state["source_status"], "Design recu")
        self.assertEqual(state["scene_status"], "Bacs visibles dans Fusion")
        self.assertTrue(state["scene_present"])
        self.assertIsNone(state["scene_artifact_identity"])
        self.assertIn("3 corps", state["scene_detail"])
        self.assertIn("impression non validee", state["manufacturing_status"])
        self.assertEqual(state["notice"], "Scene actualisee.")

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
        self.assertIn(FUSION_COMMAND_ACTION_INSPECT, plan.command_actions)
        self.assertIn(FUSION_COMMAND_ACTION_EXPORT_PRINTABLES, plan.command_actions)
        self.assertIn("box_inner_x_mm", plan.parametric_fields)
        self.assertIn("grid_units_z", plan.parametric_fields)
        self.assertIn("SolidScriptsAddinsPanel", BGIG_TOOLBAR_PANEL_IDS)
        self.assertIn("Utilities", payload["toolbar_location"])
        self.assertEqual(payload["toolbar_panel_ids"], list(BGIG_TOOLBAR_PANEL_IDS))
        self.assertEqual(payload["clear_scope"], BGIG_CLEAR_SCOPE)

    def test_builds_export_printables_request_without_source_file(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            request = build_fusion_command_request(
                "",
                FUSION_GENERATION_MODE_COMPACT_ONLY,
                Path(temp_dir),
                action=FUSION_COMMAND_ACTION_EXPORT_PRINTABLES,
                input_mode=FUSION_INPUT_MODE_CAD_IR_FILE,
            )

        self.assertEqual(request.action, FUSION_COMMAND_ACTION_EXPORT_PRINTABLES)
        self.assertEqual(request.source_kind, "export_printables_only")
        self.assertIsNone(request.cad_ir_path)

    def test_printable_export_filename_and_summary_are_deterministic(self) -> None:
        filename = printable_export_filename(3, "generated:asset-group/tokens", "module_body")

        self.assertEqual(filename, "03-generated-asset-group-tokens-module-body.stl")
        summary = printable_export_result_summary(
            {
                "export_directory": "C:/tmp/bgig-export",
                "printable_modules_detected": 1,
                "printable_modules_exported": 1,
                "printable_modules_refused": 0,
                "exported_files": ["C:/tmp/bgig-export/01-module-module-body.stl"],
                "refused_modules": [],
                "status": "exported",
            }
        )

        self.assertIn("Action: export_printables", summary)
        self.assertIn("printable_modules_exported: 1", summary)
        self.assertIn("print_validated: false", summary)

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

    def test_builds_inspect_request_without_requiring_input_file(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            request = build_fusion_command_request(
                "",
                FUSION_GENERATION_MODE_COMPACT_ONLY,
                Path(temp_dir),
                action=FUSION_COMMAND_ACTION_INSPECT,
            )

        self.assertIsNone(request.cad_ir_path)
        self.assertEqual(request.action, FUSION_COMMAND_ACTION_INSPECT)
        self.assertEqual(request.source_kind, "inspect_only")
        self.assertIn("inspect_bgig_scene", fusion_command_summary(request))

    def test_fusion_reporting_messages_tolerate_partial_dictionaries(self) -> None:
        clear_message = fusion_entrypoint._clear_result_message({})
        self.assertIn("BGIG objects remaining after clear: 0", clear_message)
        self.assertIn("Non-BGIG objects preserved: yes", clear_message)

        stable = fusion_entrypoint._stable_generation_result({"scene_roots_created": 1})
        self.assertEqual(stable["non_bgig_objects_preserved"], "yes")
        self.assertEqual(stable["registry_validation_status"], "not_run")

    def test_inspection_message_is_read_only_and_copiable(self) -> None:
        message = fusion_entrypoint._inspection_result_message(
            {
                "root_occurrences_count": 0,
                "components_count": 1,
                "bodies_count": 1,
                "sketches_count": 0,
                "bgig_scene_roots_total": 0,
                "tagged_bgig_entities": 0,
                "bgig_name_like_untagged_entities": 1,
                "name_like_untagged_lines": ["- type=Body; name=BGIG orphan body"],
                "inconsistency_lines": ["- BGIG-looking visible/name-like entity without bgig attribute"],
            }
        )

        self.assertIn("Action: inspect_bgig_scene", message)
        self.assertIn("Read-only: yes", message)
        self.assertIn("Tagged BGIG unique entities sample", message)
        self.assertIn("BGIG-looking untagged entities", message)
        self.assertIn("BGIG-looking visible/name-like entity without bgig attribute", message)

    def test_bgig_registry_inspection_deduplicates_entities_and_scene_roots(self) -> None:
        root_component = _FakeComponent("Root", "component-root")
        scene_component = _FakeComponent("BGIG Generated Scene", "component-scene")
        scene_occurrence = _FakeOccurrence("BGIG Generated Scene:1", "occurrence-scene", scene_component)
        module_component = _FakeComponent("Grid placed tokens", "component-module")
        module_occurrence = _FakeOccurrence("Grid placed tokens:1", "occurrence-module", module_component)
        module_body = _FakeBody("BGIG token module body", "body-module")
        module_sketch = _FakeSketch("BGIG token module footprint", "sketch-module")
        module_feature = _FakeExtrudeFeature("BGIG token module extrusion", "feature-module")
        root_component.occurrences = _FakeCollection([scene_occurrence])
        scene_component.occurrences = _FakeCollection([module_occurrence])
        module_component.bRepBodies = _FakeCollection([module_body])
        module_component.sketches = _FakeCollection([module_sketch])
        module_component.features = _FakeFeatures([module_feature])

        tagged = [
            (scene_occurrence, "scene_root", None),
            (scene_component, "scene_root_component", None),
            (module_component, "module_component", "module-tokens"),
            (module_occurrence, "compact_occurrence", "module-tokens"),
            (module_body, "module_body", "module-tokens"),
            (module_sketch, "module_sketch", "module-tokens"),
            (module_feature, "module_extrude", "module-tokens"),
        ]
        for entity, role, module_id in tagged:
            fusion_entrypoint._tag_bgig_entity_direct(entity, role, scene_id="scene-001", module_id=module_id)
            entity.attributes.add("bgig", "extra_test_attribute", "duplicate-proof")

        design = _FakeDesignForRegistry(
            root_component,
            [root_component, scene_occurrence, scene_component, module_component, module_occurrence, module_body, module_sketch, module_feature],
        )
        registry = fusion_entrypoint.BgigFusionRegistry(design)

        inspection = registry.inspect()
        message = fusion_entrypoint._inspection_result_message(inspection)

        self.assertEqual(inspection["root_occurrences_count"], 1)
        self.assertEqual(inspection["scene_roots_by_name"], 1)
        self.assertEqual(inspection["scene_roots_by_attribute"], 1)
        self.assertEqual(inspection["bgig_scene_roots_total"], 1)
        self.assertEqual(inspection["bgig_scene_root_occurrences"], 1)
        self.assertEqual(inspection["tagged_bgig_unique_entities"], 7)
        self.assertGreater(inspection["tagged_bgig_attributes_found"], inspection["tagged_bgig_unique_entities"])
        self.assertEqual(inspection["bgig_name_like_untagged_entities"], 0)
        self.assertEqual(inspection["occurrences_tagged"], 2)
        self.assertEqual(inspection["components_tagged"], 2)
        self.assertEqual(inspection["bodies_tagged"], 1)
        self.assertEqual(inspection["sketches_tagged"], 1)
        self.assertEqual(inspection["features_tagged"], 1)
        self.assertIn("- none", inspection["inconsistency_lines"])
        self.assertIn("BGIG scene roots total: 1", message)
        self.assertIn("Tagged BGIG unique entities: 7", message)
        self.assertIn("BGIG-looking untagged entities: 0", message)
        self.assertIn("Inconsistencies:\n- none", message)

    def test_registry_reports_the_exact_scene_artifact_identity(self) -> None:
        root_component = _FakeComponent("Root", "component-root")
        scene_component = _FakeComponent("BGIG Generated Scene", "component-scene")
        scene_occurrence = _FakeOccurrence(
            "BGIG Generated Scene:1", "occurrence-scene", scene_component
        )
        root_component.occurrences = _FakeCollection([scene_occurrence])
        identity = {
            "schema_version": "bgig.scene_artifact_identity.v1",
            "artifact_kind": "minimal_layout",
            "artifact_digest": "a" * 64,
            "partition_plan_digest": "b" * 64,
            "cad_ir_digest": "c" * 64,
            "source_revision": 7,
        }
        fusion_entrypoint._tag_bgig_entity_direct(
            scene_occurrence,
            "scene_root",
            scene_id="scene-identity",
            artifact_identity=identity,
        )
        fusion_entrypoint._tag_bgig_entity_direct(
            scene_component,
            "scene_root_component",
            scene_id="scene-identity",
            artifact_identity=identity,
        )
        design = _FakeDesignForRegistry(
            root_component,
            [root_component, scene_occurrence, scene_component],
        )

        inspection = fusion_entrypoint.BgigFusionRegistry(design).inspect()

        self.assertEqual(
            inspection["scene_artifact_identity"],
            {**identity, "source_revision": "7"},
        )

    def test_fixture_15_registry_clear_preserves_untagged_user_objects(self) -> None:
        root_component = _FakeComponent("Root", "component-root")
        scene_component = _FakeComponent("BGIG Generated Scene", "component-scene")
        scene_occurrence = _FakeOccurrence(
            "BGIG Generated Scene:1", "occurrence-scene", scene_component
        )
        user_component = _FakeComponent("Thomas custom part", "component-user")
        user_occurrence = _FakeOccurrence(
            "Thomas custom part:1", "occurrence-user", user_component
        )
        root_component.occurrences = _FakeCollection(
            [scene_occurrence, user_occurrence]
        )
        fusion_entrypoint._tag_bgig_entity_direct(
            scene_occurrence,
            "scene_root",
            scene_id="scene-owned",
        )
        fusion_entrypoint._tag_bgig_entity_direct(
            scene_component,
            "scene_root_component",
            scene_id="scene-owned",
        )
        design = _FakeDesignForRegistry(
            root_component,
            [
                root_component,
                scene_occurrence,
                scene_component,
                user_occurrence,
                user_component,
            ],
        )

        result = fusion_entrypoint.BgigFusionRegistry(design).clear()

        self.assertTrue(scene_occurrence.deleted)
        self.assertFalse(user_occurrence.deleted)
        self.assertEqual(result["non_bgig_objects_preserved"], "yes")
        self.assertEqual(result["scene_roots_found"], 1)

    def test_export_printables_exports_only_tagged_module_bodies(self) -> None:
        root_component = _FakeComponent("Root", "component-root")
        scene_component = _FakeComponent("BGIG Generated Scene", "component-scene")
        scene_occurrence = _FakeOccurrence("BGIG Generated Scene:1", "occurrence-scene", scene_component)
        module_component = _FakeComponent("Grid placed tokens", "component-module")
        module_occurrence = _FakeOccurrence("Grid placed tokens:1", "occurrence-module", module_component)
        module_body = _FakeBody("BGIG token module body", "body-module")
        module_sketch = _FakeSketch("asset-fit debug outline", "sketch-module")
        root_component.occurrences = _FakeCollection([scene_occurrence])
        scene_component.occurrences = _FakeCollection([module_occurrence])
        module_component.bRepBodies = _FakeCollection([module_body])
        module_component.sketches = _FakeCollection([module_sketch])

        for entity, role, module_id in [
            (scene_occurrence, "scene_root", None),
            (scene_component, "scene_root_component", None),
            (module_component, "module_component", "module-tokens"),
            (module_occurrence, "compact_occurrence", "module-tokens"),
            (module_body, "module_body", "module-tokens"),
            (module_sketch, "module_sketch", "module-tokens"),
        ]:
            fusion_entrypoint._tag_bgig_entity_direct(entity, role, scene_id="scene-001", module_id=module_id)

        design = _FakeDesignForRegistry(
            root_component,
            [root_component, scene_occurrence, scene_component, module_component, module_occurrence, module_body, module_sketch],
        )
        design.exportManager = _FakeExportManager()
        registry = fusion_entrypoint.BgigFusionRegistry(design)
        original_export_dir = fusion_entrypoint._default_printable_export_dir
        temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(temp_dir.cleanup)
        fusion_entrypoint._default_printable_export_dir = lambda _addin, _registry, _targets: Path(temp_dir.name) / "exports"
        try:
            result = fusion_entrypoint._export_printables_from_scene(
                design,
                registry,
                Path(temp_dir.name),
                registry.inspect(),
            )
        finally:
            fusion_entrypoint._default_printable_export_dir = original_export_dir

        self.assertEqual(result["status"], "exported")
        self.assertEqual(result["printable_modules_detected"], 1)
        self.assertEqual(result["printable_modules_exported"], 1)
        self.assertTrue(Path(result["manifest_json"]).is_file())
        self.assertTrue(Path(result["manifest_markdown"]).is_file())
        manifest = json.loads(Path(result["manifest_json"]).read_text(encoding="utf-8"))
        self.assertEqual(manifest["schema_version"], "bgig.export_manifest.v0")
        self.assertFalse(manifest["print_validated"])
        self.assertEqual(manifest["summary"]["printable_modules_exported"], 1)
        self.assertIn("print validation", Path(result["manifest_markdown"]).read_text(encoding="utf-8").lower())
        self.assertEqual(len(design.exportManager.executed_options), 1)
        self.assertIs(design.exportManager.executed_options[0].geometry, module_body)
        self.assertTrue(design.exportManager.executed_options[0].filename.endswith("01-module-tokens-module-body.stl"))
        refused_roles = {item["role"] for item in result["refused_modules"]}
        self.assertIn("scene_root", refused_roles)
        self.assertIn("compact_occurrence", refused_roles)
        self.assertIn("module_sketch", refused_roles)

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
                "inter_module_clearance_mm": "0.7",
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
    def test_ignores_parametric_overrides_in_cad_ir_mode(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            addin_dir = Path(temp_dir)
            cad_ir_path = addin_dir / "scene.json"
            cad_ir_path.write_text(json.dumps(_cad_ir_payload()), encoding="utf-8")

            request = build_fusion_command_request(
                "scene.json",
                FUSION_GENERATION_MODE_COMPACT_ONLY,
                addin_dir,
                parameter_values={"box_inner_x_mm": "120"},
                input_mode=FUSION_INPUT_MODE_CAD_IR_FILE,
            )

        self.assertEqual(request.input_mode, FUSION_INPUT_MODE_CAD_IR_FILE)
        self.assertEqual(request.source_kind, "cad_ir")
        self.assertEqual(request.parameter_overrides, {})
        self.assertEqual(request.parameter_values["box_inner_x_mm"], "120")

    def test_builds_quick_parametric_box_request_and_cad_ir_payload(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            overrides = {
                **P12_PARAMETRIC_FIELD_DEFAULTS,
                "box_inner_x_mm": "120",
                "box_inner_y_mm": "80",
                "box_inner_z_mm": "30",
                "grid_units_x": "4",
                "grid_units_y": "4",
                "grid_units_z": "3",
                "wall_thickness_mm": "1.2",
                "floor_thickness_mm": "1.2",
                "peripheral_clearance_mm": "0.4",
                "inter_module_clearance_mm": "0.3",
                "print_profile": "draft",
            }
            request = build_fusion_command_request(
                "",
                FUSION_GENERATION_MODE_COMPACT_ONLY,
                Path(temp_dir),
                parameter_values=overrides,
                input_mode=FUSION_INPUT_MODE_QUICK_PARAMETRIC_BOX,
            )

        self.assertEqual(request.source_kind, "quick_parametric_box")
        self.assertEqual(request.generation_mode, FUSION_GENERATION_MODE_COMPACT_ONLY)
        self.assertEqual(request.parameter_overrides["inter_module_clearance_mm"], 0.3)
        self.assertIn("Source: Quick parametric box UI fields", fusion_command_summary(request))

        payload = build_quick_parametric_box_cad_ir_payload(request.parameter_overrides)
        validated = validate_cad_ir_payload(payload)
        quick = validated["metadata"]["quick_parametric_box"]
        self.assertEqual(quick["box_inner_mm"], {"x": 120.0, "y": 80.0, "z": 30.0})
        self.assertEqual(quick["grid_units"], {"x": 4, "y": 4, "z": 3})
        self.assertEqual(quick["grid_unit_mm"], {"x": 30.0, "y": 20.0, "z": 10.0})
        self.assertEqual(quick["printable_body_size_mm"], {"x": 28.9, "y": 18.9, "z": 8.8})
        body = validated["components"][0]["body"]
        self.assertEqual(body["printable_origin_mm"], {"x": 0.4, "y": 0.4, "z": 0.0})
        self.assertEqual(body["printable_size_mm"], {"x": 28.9, "y": 18.9, "z": 8.8})
        plan = generation_plan_from_cad_ir(validated, FUSION_GENERATION_MODE_COMPACT_ONLY)
        self.assertEqual(len(plan.blanks), 1)
        self.assertEqual(len(plan.compact_occurrences), 1)
        self.assertEqual(len(plan.exploded_occurrences), 0)
        self.assertIn("temporary_cad_ir_created: yes", quick_parametric_box_summary(validated))


    def test_parses_quick_asset_box_text_with_partial_rejections(self) -> None:
        report = parse_quick_asset_box_assets_text(
            "coin-tokens,tokens,30,20,20,2,loose; bad-entry; cards,cards,60,63,88,25,exact"
        )

        self.assertEqual(len(report["accepted_assets"]), 2)
        self.assertEqual(report["accepted_assets"][0]["kind"], "tokens")
        self.assertEqual(report["accepted_assets"][0]["dimension_confidence"], "approximate")
        self.assertEqual(report["accepted_assets"][1]["kind"], "cards")
        self.assertEqual(report["accepted_assets"][1]["dimension_confidence"], "exact")
        self.assertEqual(len(report["rejected_assets"]), 1)
        self.assertIn("expected 7 comma-separated fields", report["rejected_assets"][0]["reason"])

    def test_builds_quick_asset_box_request_config_and_cad_ir_payload(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            overrides = {
                **P12_PARAMETRIC_FIELD_DEFAULTS,
                "box_inner_x_mm": "120",
                "box_inner_y_mm": "80",
                "box_inner_z_mm": "30",
                "grid_units_x": "4",
                "grid_units_y": "4",
                "grid_units_z": "3",
                "wall_thickness_mm": "1.2",
                "floor_thickness_mm": "1.2",
                "peripheral_clearance_mm": "0.4",
                "inter_module_clearance_mm": "0.3",
                "print_profile": "draft",
            }
            assets_text = "coin-tokens,tokens,30,20,20,2,loose; status-tokens,tokens,20,18,18,2,loose"
            request = build_fusion_command_request(
                "",
                FUSION_GENERATION_MODE_COMPACT_ONLY,
                Path(temp_dir),
                project_root_text=str(ROOT),
                parameter_values=overrides,
                input_mode=FUSION_INPUT_MODE_QUICK_ASSET_BOX,
                quick_asset_box_assets_text=assets_text,
            )
            config_payload = build_quick_asset_box_config_payload(request.parameter_overrides, request.quick_asset_box_assets_text)
            config_path = Path(temp_dir) / "quick_asset_box_config.json"
            config_path.write_text(json.dumps(config_payload), encoding="utf-8")
            config = load_config(config_path)
            layout = generate_basic_layout(config)
            scene = build_blank_cad_scene(config, layout).to_dict()
            scene["metadata"]["quick_asset_box"] = quick_asset_box_metadata(
                config_payload,
                request.quick_asset_box_assets_text,
                scene,
            )

        self.assertEqual(request.source_kind, "quick_asset_box")
        self.assertEqual(request.project_root, ROOT)
        self.assertEqual(config_payload["project_name"], "Quick asset box")
        self.assertEqual(len(config_payload["assets"]), 2)
        self.assertEqual(config_payload["volumetric_grid"]["unit_mm"], {"x": 30.0, "y": 20.0, "z": 10.0})
        quick_metadata = scene["metadata"]["quick_asset_box"]
        self.assertEqual(quick_metadata["grid_semantics"], "placement_reservation_lattice_v0")
        self.assertEqual(quick_metadata["body_snap_to_grid"], "no")
        self.assertEqual(quick_metadata["grid_span_is_reserved_space"], "yes")
        self.assertEqual(quick_metadata["body_size_may_be_smaller_than_grid_span"], "yes")
        self.assertEqual(quick_metadata["accepted_asset_count"], 2)
        self.assertEqual(quick_metadata["module_candidate_count"], 1)
        self.assertEqual(quick_metadata["placed_module_count"], 1)
        self.assertFalse(quick_metadata["asset_items_visualized"])
        self.assertTrue(quick_metadata["asset_cavities_generated"])
        self.assertEqual(quick_metadata["asset_cavity_policy"], ASSET_COMPARTMENT_CAVITY_POLICY)
        self.assertEqual(quick_metadata["asset_fit_cavities_planned"], 2)
        self.assertEqual(quick_metadata["asset_fit_cavities_refused"], 0)
        self.assertTrue(quick_metadata["asset_compartments_generated"])
        self.assertEqual(quick_metadata["asset_compartment_cavities_planned"], 2)
        self.assertEqual(quick_metadata["asset_compartment_cavities_refused"], 0)
        self.assertTrue(quick_metadata["asset_compartment_debug_outlines"])
        self.assertTrue(quick_metadata["asset_access_features_generated"])
        self.assertEqual(quick_metadata["asset_access_policy"], ASSET_ACCESS_POLICY)
        self.assertEqual(quick_metadata["asset_access_notches_planned"], 2)
        self.assertEqual(quick_metadata["asset_access_notches_generated"], 2)
        self.assertEqual(quick_metadata["asset_access_notches_refused"], 0)
        self.assertEqual(len(quick_metadata["asset_access_diagnostics"]), 2)
        self.assertEqual(quick_metadata["asset_access_diagnostics"][0]["asset_id"], "coin-tokens")
        self.assertEqual(quick_metadata["asset_access_diagnostics"][0]["target_wall"], "front")
        self.assertEqual(quick_metadata["asset_access_diagnostics"][0]["depth_from_top_mm"], 10.0)
        self.assertEqual(quick_metadata["asset_access_diagnostics"][0]["tray_packing_policy"], "flat_tray_2d_v0")
        self.assertEqual(quick_metadata["asset_access_diagnostics"][0]["pile_grid_columns"], 3)
        self.assertEqual(quick_metadata["asset_access_diagnostics"][0]["pile_grid_rows"], 2)
        self.assertEqual(quick_metadata["printability_checked"], "yes")
        self.assertEqual(quick_metadata["printability_validated_by_print"], "no")
        self.assertEqual(len(quick_metadata["printability_report_v0"]), 1)
        printability = quick_metadata["printability_report_v0"][0]
        self.assertEqual(printability["policy"], "printability_report_v0")
        self.assertEqual(printability["printability_status"], "warning")
        self.assertTrue(printability["printability_export_allowed"])
        self.assertEqual(printability["min_external_wall_mm"], 1.2)
        self.assertEqual(printability["min_internal_wall_mm"], 1.2)
        self.assertEqual(printability["min_retained_floor_mm"], 1.2)
        self.assertTrue(any("no physical print validation" in warning for warning in printability["warnings"]))
        self.assertEqual(quick_metadata["count_aware_storage_sizing"], "yes")
        self.assertEqual(quick_metadata["storage_sizing_scope"], "count_aware_tray_storage_rectangular_piles_v0")
        self.assertTrue(quick_metadata["asset_debug_visualization"])
        self.assertEqual(quick_metadata["asset_debug_visualization_scope"], "asset_fit_envelope_sketch_only_non_printable")
        self.assertIsNone(quick_metadata["max_stack_height_mm"])
        self.assertEqual(len(quick_metadata["asset_sizing_diagnostics"]), 2)
        self.assertTrue(quick_metadata["asset_sizing_diagnostics"][0]["count_used_for_sizing"])
        self.assertEqual(quick_metadata["asset_sizing_diagnostics"][0]["capacity_per_stack"], 5)
        self.assertEqual(quick_metadata["asset_sizing_diagnostics"][0]["pile_count"], 6)
        self.assertEqual(quick_metadata["asset_sizing_diagnostics"][0]["storage_orientation"], "flat_tray")
        self.assertEqual(quick_metadata["asset_sizing_diagnostics"][0]["stack_height_policy"], "flat_tray_max_stack_height_v0")
        self.assertEqual(quick_metadata["asset_sizing_diagnostics"][0]["max_stack_height_mm"], 12.0)
        self.assertEqual(quick_metadata["asset_sizing_diagnostics"][0]["stack_height_used_mm"], 10.0)
        self.assertEqual(quick_metadata["asset_sizing_diagnostics"][0]["xy_expansion_used"], "yes")
        self.assertEqual(quick_metadata["asset_sizing_diagnostics"][0]["z_expansion_used"], "yes")
        self.assertEqual(quick_metadata["asset_sizing_diagnostics"][0]["tray_packing_policy"], "flat_tray_2d_v0")
        self.assertEqual(quick_metadata["asset_sizing_diagnostics"][0]["pile_grid_columns"], 3)
        self.assertEqual(quick_metadata["asset_sizing_diagnostics"][0]["pile_grid_rows"], 2)
        self.assertEqual(quick_metadata["asset_sizing_diagnostics"][0]["linear_layout_avoided"], "yes")
        self.assertEqual(quick_metadata["asset_sizing_diagnostics"][1]["pile_count"], 4)
        self.assertEqual(len(quick_metadata["module_candidate_sizing_diagnostics"]), 1)
        module_diagnostic = quick_metadata["module_candidate_sizing_diagnostics"][0]
        self.assertTrue(module_diagnostic["count_used_for_sizing"])
        self.assertEqual(module_diagnostic["count_aware_storage_sizing"], "yes")
        self.assertEqual(module_diagnostic["policy"], "stacked_rectangular_piles_v0")
        self.assertEqual(module_diagnostic["sizing_scope"], "count_aware_tray_storage_rectangular_piles_v0")
        self.assertEqual(module_diagnostic["storage_orientation"], "flat_tray")
        self.assertEqual(module_diagnostic["stack_height_policy"], "flat_tray_max_stack_height_v0")
        self.assertEqual(module_diagnostic["max_stack_height_mm"], 12.0)
        self.assertEqual(module_diagnostic["stack_height_used_mm"], 10.0)
        self.assertEqual(module_diagnostic["xy_expansion_used"], "yes")
        self.assertEqual(module_diagnostic["z_expansion_used"], "yes")
        self.assertEqual(module_diagnostic["tray_packing_policy"], "flat_tray_2d_v0")
        self.assertEqual(module_diagnostic["pile_grid_columns"], 5)
        self.assertEqual(module_diagnostic["pile_grid_rows"], 2)
        self.assertEqual(module_diagnostic["linear_layout_avoided"], "yes")
        self.assertEqual(module_diagnostic["declared_capacity_count"], 50)
        self.assertEqual(module_diagnostic["module_size_mm"], {"x": 102.8, "y": 44.0, "z": 12.0})
        self.assertEqual(module_diagnostic["asset_fit_size_mm"], {"x": 100.4, "y": 41.6, "z": 10.8})
        self.assertEqual(len(quick_metadata["asset_cavity_diagnostics"]), 2)
        cavity_diagnostic = quick_metadata["asset_cavity_diagnostics"][0]
        self.assertEqual(cavity_diagnostic["status"], "planned")
        self.assertEqual(cavity_diagnostic["policy"], ASSET_COMPARTMENT_CAVITY_POLICY)
        self.assertEqual(cavity_diagnostic["asset_id"], "coin-tokens")
        self.assertEqual(cavity_diagnostic["size_mm"], {"x": 61.6, "y": 41.6, "z": 10.8})
        self.assertEqual(cavity_diagnostic["retained_floor_mm"], 1.2)
        self.assertEqual(cavity_diagnostic["expected_walls_mm"], {"x_min": 1.2, "x_max": 40.0, "y_min": 1.2, "y_max": 1.2})
        self.assertEqual(cavity_diagnostic["tray_packing_policy"], "flat_tray_2d_v0")
        self.assertEqual(cavity_diagnostic["pile_grid_columns"], 3)
        self.assertEqual(cavity_diagnostic["pile_grid_rows"], 2)
        self.assertEqual(cavity_diagnostic["linear_layout_avoided"], "yes")
        plan = generation_plan_from_cad_ir(validate_cad_ir_payload(scene), FUSION_GENERATION_MODE_COMPACT_ONLY)
        self.assertEqual(len(plan.grid_positioned_blanks), 1)
        self.assertEqual(len(plan.cavity_cuts), 2)
        self.assertEqual(len(plan.finger_notch_cuts), 2)
        access_cut = plan.finger_notch_cuts[0]
        self.assertEqual(access_cut.source_feature_kind, "asset_access_notch")
        self.assertEqual(access_cut.wall, FINGER_NOTCH_WALL_FRONT)
        self.assertEqual(access_cut.notch_depth_from_top_mm, 10.0)
        self.assertGreater(access_cut.profile_bottom_z_mm, access_cut.cavity_local_origin_mm.z)
        cut = plan.cavity_cuts[0]
        self.assertEqual(cut.cavity_source, "asset_compartment_cavity")
        self.assertEqual(cut.policy, ASSET_COMPARTMENT_CAVITY_POLICY)
        self.assertEqual(cut.cut_size_mm.to_dict(), {"x": 61.6, "y": 41.6, "z": 10.8})
        self.assertEqual(cut.requested_local_origin_mm.to_dict(), {"x": 1.2, "y": 1.2, "z": 1.2})
        self.assertAlmostEqual(cut.retained_floor_mm, 1.2)
        summary = quick_asset_box_summary(scene)
        self.assertIn("Quick asset box inputs", summary)
        self.assertIn("assets_read: 2", summary)
        self.assertIn("asset_items_visualized: no", summary)
        self.assertIn("asset_cavities_generated: yes", summary)
        self.assertIn("asset_cavity_policy: per_source_asset_rectangular_compartments_v0", summary)
        self.assertIn("asset_fit_cavities_planned: 2", summary)
        self.assertIn("asset_compartments_generated: yes", summary)
        self.assertIn("asset_compartment_cavities_planned: 2", summary)
        self.assertIn("asset_compartment_debug_outlines: yes", summary)
        self.assertIn("asset_access_features_generated: yes", summary)
        self.assertIn("asset_access_policy: per_compartment_top_open_rectangular_notch_v0", summary)
        self.assertIn("asset_access_notches_planned: 2", summary)
        self.assertIn("asset_access_notches_generated: 2", summary)
        self.assertIn("asset_access_notches_refused: 0", summary)
        self.assertIn("asset_access_notch: asset coin-tokens", summary)
        self.assertIn("target_wall front", summary)
        self.assertIn("count_aware_storage_sizing: yes", summary)
        self.assertIn("grid_semantics: placement_reservation_lattice_v0", summary)
        self.assertIn("body_snap_to_grid: no", summary)
        self.assertIn("grid_span_is_reserved_space: yes", summary)
        self.assertIn("body_size_may_be_smaller_than_grid_span: yes", summary)
        self.assertIn("asset_debug_visualization: yes", summary)
        self.assertIn("max_stack_height_mm: default", summary)
        self.assertIn("storage_orientation flat_tray", summary)
        self.assertIn("stack_height_policy flat_tray_max_stack_height_v0", summary)
        self.assertIn("max_stack_height_mm 12.0", summary)
        self.assertIn("stack_height_used_mm 10.0", summary)
        self.assertIn("xy_expansion_used yes", summary)
        self.assertIn("z_expansion_used yes", summary)
        self.assertIn("printability_checked: yes", summary)
        self.assertIn("printability_validated_by_print: no", summary)
        self.assertIn("printability_status: warning", summary)
        self.assertIn("printability_export_allowed: yes", summary)
        self.assertIn("printability_report_v0:", summary)
        self.assertIn("status warning", summary)
        self.assertIn("export_allowed yes", summary)
        self.assertIn("validated_by_print no", summary)
        self.assertIn("printability_warning: Heuristic printability report only", summary)
        self.assertIn("capacity_per_stack 5", summary)
        self.assertIn("pile_count 6", summary)
        self.assertIn("module_size 102.8 x 44.0 x 12.0 mm", summary)
        self.assertIn("asset_cavity: generated:asset-group-candidate:tokens:store:approximate", summary)
        self.assertIn("asset coin-tokens", summary)
        self.assertIn("retained_floor 1.2 mm", summary)
        self.assertIn("individual item and pile cavities remain not generated", summary)
        self.assertIn("module_candidates_generated: 1", summary)
        self.assertIn("placed_asset_modules: 1", summary)


    def test_quick_asset_box_max_stack_height_override_is_persisted_and_reported(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            overrides = {
                **P12_PARAMETRIC_FIELD_DEFAULTS,
                "box_inner_x_mm": "120",
                "box_inner_y_mm": "80",
                "box_inner_z_mm": "30",
                "grid_units_x": "4",
                "grid_units_y": "4",
                "grid_units_z": "3",
                "wall_thickness_mm": "1.2",
                "floor_thickness_mm": "1.2",
                "peripheral_clearance_mm": "0.4",
                "inter_module_clearance_mm": "0.3",
                "print_profile": "draft",
            }
            assets_text = "coin-tokens,tokens,30,20,20,2,loose; status-tokens,tokens,20,18,18,2,loose"
            request = build_fusion_command_request(
                "",
                FUSION_GENERATION_MODE_COMPACT_ONLY,
                Path(temp_dir),
                project_root_text=str(ROOT),
                parameter_values=overrides,
                input_mode=FUSION_INPUT_MODE_QUICK_ASSET_BOX,
                quick_asset_box_assets_text=assets_text,
                quick_asset_box_max_stack_height_mm="6",
                quick_asset_box_target_aspect_ratio="1.0",
                quick_asset_box_max_module_length_mm="40",
            )
            config_payload = build_quick_asset_box_config_payload(
                request.parameter_overrides,
                request.quick_asset_box_assets_text,
                request.quick_asset_box_max_stack_height_mm,
            )
            config_path = Path(temp_dir) / "quick_asset_box_config.json"
            config_path.write_text(json.dumps(config_payload), encoding="utf-8")
            config = load_config(config_path)
            layout = generate_basic_layout(config)
            scene = build_blank_cad_scene(config, layout).to_dict()
            scene["metadata"]["quick_asset_box"] = quick_asset_box_metadata(
                config_payload,
                request.quick_asset_box_assets_text,
                scene,
            )

        self.assertEqual(request.quick_asset_box_max_stack_height_mm, "6")
        self.assertEqual(config_payload["assets"][0]["max_stack_height_mm"], 6.0)
        self.assertEqual(config_payload["assets"][1]["max_stack_height_mm"], 6.0)
        quick_metadata = scene["metadata"]["quick_asset_box"]
        self.assertEqual(quick_metadata["max_stack_height_mm"], 6.0)
        asset_diagnostic = quick_metadata["asset_sizing_diagnostics"][0]
        self.assertEqual(asset_diagnostic["capacity_per_stack"], 2)
        self.assertEqual(asset_diagnostic["pile_count"], 15)
        self.assertEqual(asset_diagnostic["max_stack_height_mm"], 6.0)
        self.assertEqual(asset_diagnostic["stack_height_used_mm"], 4.0)
        self.assertEqual(asset_diagnostic["xy_expansion_used"], "yes")
        self.assertEqual(asset_diagnostic["z_expansion_used"], "yes")
        module_diagnostic = quick_metadata["module_candidate_sizing_diagnostics"][0]
        self.assertEqual(module_diagnostic["module_size_mm"], {"x": 104.0, "y": 102.0, "z": 6.0})
        self.assertEqual(module_diagnostic["asset_fit_size_mm"], {"x": 101.6, "y": 99.6, "z": 4.8})
        self.assertEqual(module_diagnostic["max_stack_height_mm"], 6.0)
        self.assertEqual(module_diagnostic["stack_height_used_mm"], 4.0)
        summary = quick_asset_box_summary(scene)
        self.assertIn("max_stack_height_mm: 6.0", summary)
        self.assertIn("capacity_per_stack 2", summary)
        self.assertIn("pile_count 15", summary)
        self.assertIn("module_size 104.0 x 102.0 x 6.0 mm", summary)
        self.assertIn("stack_height_used_mm 4.0", summary)

    def test_quick_asset_box_tray_packing_overrides_are_persisted_and_reported(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            overrides = {
                **P12_PARAMETRIC_FIELD_DEFAULTS,
                "box_inner_x_mm": "120",
                "box_inner_y_mm": "80",
                "box_inner_z_mm": "30",
                "grid_units_x": "4",
                "grid_units_y": "4",
                "grid_units_z": "3",
                "wall_thickness_mm": "1.2",
                "floor_thickness_mm": "1.2",
                "peripheral_clearance_mm": "0.4",
                "inter_module_clearance_mm": "0.3",
                "print_profile": "draft",
            }
            assets_text = "coin-tokens,tokens,30,20,20,2,loose"
            request = build_fusion_command_request(
                "",
                FUSION_GENERATION_MODE_COMPACT_ONLY,
                Path(temp_dir),
                project_root_text=str(ROOT),
                parameter_values=overrides,
                input_mode=FUSION_INPUT_MODE_QUICK_ASSET_BOX,
                quick_asset_box_assets_text=assets_text,
                quick_asset_box_max_stack_height_mm="6",
                quick_asset_box_target_aspect_ratio="1.0",
                quick_asset_box_max_module_length_mm="40",
            )
            config_payload = build_quick_asset_box_config_payload(
                request.parameter_overrides,
                request.quick_asset_box_assets_text,
                request.quick_asset_box_max_stack_height_mm,
                request.quick_asset_box_target_aspect_ratio,
                request.quick_asset_box_max_module_length_mm,
            )
            config_path = Path(temp_dir) / "quick_asset_box_config.json"
            config_path.write_text(json.dumps(config_payload), encoding="utf-8")
            config = load_config(config_path)
            layout = generate_basic_layout(config)
            scene = build_blank_cad_scene(config, layout).to_dict()
            scene["metadata"]["quick_asset_box"] = quick_asset_box_metadata(
                config_payload,
                request.quick_asset_box_assets_text,
                scene,
            )

        self.assertEqual(request.quick_asset_box_target_aspect_ratio, "1.0")
        self.assertEqual(request.quick_asset_box_max_module_length_mm, "40")
        self.assertEqual(config_payload["assets"][0]["target_aspect_ratio"], 1.0)
        self.assertEqual(config_payload["assets"][0]["max_module_length_mm"], 40.0)
        quick_metadata = scene["metadata"]["quick_asset_box"]
        self.assertEqual(quick_metadata["target_aspect_ratio"], 1.0)
        self.assertEqual(quick_metadata["max_module_length_mm"], 40.0)
        module_diagnostic = quick_metadata["module_candidate_sizing_diagnostics"][0]
        self.assertEqual(module_diagnostic["target_aspect_ratio"], 1.0)
        self.assertEqual(module_diagnostic["max_module_length_mm"], 40.0)
        summary = quick_asset_box_summary(scene)
        self.assertIn("target_aspect_ratio: 1.0", summary)
        self.assertIn("max_module_length_mm: 40.0", summary)
        self.assertIn("tray_packing_policy flat_tray_2d_v0", summary)
        self.assertIn("pile_grid_columns", summary)
        self.assertIn("pile_grid_rows", summary)
        self.assertIn("linear_layout_avoided", summary)

    def test_quick_asset_box_rejects_when_no_valid_assets_remain(self) -> None:
        with self.assertRaisesRegex(FusionSkeletonError, "at least one valid asset"):
            build_quick_asset_box_config_payload(
                {
                    "box_inner_x_mm": 120,
                    "box_inner_y_mm": 80,
                    "box_inner_z_mm": 30,
                    "grid_units_x": 4,
                    "grid_units_y": 4,
                    "grid_units_z": 3,
                    "wall_thickness_mm": 1.2,
                    "floor_thickness_mm": 1.2,
                    "peripheral_clearance_mm": 0.4,
                    "inter_module_clearance_mm": 0.3,
                },
                "bad-entry",
            )
    def test_quick_parametric_box_rejects_missing_required_fields(self) -> None:
        with self.assertRaisesRegex(FusionSkeletonError, "requires these filled fields"):
            build_quick_parametric_box_cad_ir_payload({"box_inner_x_mm": 120})

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

    def test_default_ui_settings_reads_utf8_bom_settings_file(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            addin_dir = Path(temp_dir)
            values = {
                "action": FUSION_COMMAND_ACTION_GENERATE,
                "input_mode": FUSION_INPUT_MODE_QUICK_PARAMETRIC_BOX,
                "generation_mode": FUSION_GENERATION_MODE_COMPACT_ONLY,
                "project_root": str(ROOT),
                "box_inner_x_mm": "120",
                "box_inner_y_mm": "80",
                "box_inner_z_mm": "30",
                "grid_units_x": "4",
                "grid_units_y": "4",
                "grid_units_z": "3",
                "wall_thickness_mm": "1.2",
                "floor_thickness_mm": "1.2",
                "peripheral_clearance_mm": "0.4",
                "inter_module_clearance_mm": "0.3",
                "print_profile": "draft",
            }
            (addin_dir / BGIG_UI_SETTINGS_FILENAME).write_text(json.dumps(values), encoding="utf-8-sig")

            raw_settings = load_fusion_ui_settings(addin_dir)
            settings = default_fusion_ui_settings(addin_dir)
            request = default_fusion_command_values(addin_dir)
            summary = fusion_ui_settings_summary(settings)

        self.assertEqual(raw_settings["input_mode"], FUSION_INPUT_MODE_QUICK_PARAMETRIC_BOX)
        self.assertEqual(settings["settings_loaded"], "yes")
        self.assertEqual(settings["loaded_input_mode"], FUSION_INPUT_MODE_QUICK_PARAMETRIC_BOX)
        self.assertEqual(settings["loaded_action"], FUSION_COMMAND_ACTION_GENERATE)
        self.assertEqual(settings["loaded_generation_mode"], FUSION_GENERATION_MODE_COMPACT_ONLY)
        self.assertEqual(settings["box_inner_x_mm"], "120")
        self.assertEqual(request.input_mode, FUSION_INPUT_MODE_QUICK_PARAMETRIC_BOX)
        self.assertEqual(request.generation_mode, FUSION_GENERATION_MODE_COMPACT_ONLY)
        self.assertEqual(request.parameter_values["print_profile"], "draft")
        self.assertIn("UI settings loaded: yes", summary)
        self.assertIn("Loaded input mode: quick_parametric_box", summary)
        self.assertIn("box 120 x 80 x 30", summary)

    def test_default_ui_settings_rehydrates_quick_parametric_box_fields(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            addin_dir = Path(temp_dir)
            cad_ir_path = addin_dir / DEFAULT_CAD_IR_INPUT_FILENAME
            cad_ir_path.write_text(json.dumps(_cad_ir_payload()), encoding="utf-8")
            values = {
                "action": FUSION_COMMAND_ACTION_REGENERATE,
                "input_mode": FUSION_INPUT_MODE_QUICK_PARAMETRIC_BOX,
                "generation_mode": FUSION_GENERATION_MODE_COMPACT_ONLY,
                "cad_ir_path": str(cad_ir_path),
                "config_json_path": str(ROOT / "examples" / "simple_asset_product_scene.json"),
                "project_root": str(ROOT),
                "box_inner_x_mm": "160",
                "box_inner_y_mm": "80",
                "box_inner_z_mm": "30",
                "grid_units_x": "4",
                "grid_units_y": "4",
                "grid_units_z": "3",
                "wall_thickness_mm": "1.2",
                "floor_thickness_mm": "1.2",
                "peripheral_clearance_mm": "0.4",
                "inter_module_clearance_mm": "0.3",
                "print_profile": "draft",
            }
            (addin_dir / BGIG_UI_SETTINGS_FILENAME).write_text(json.dumps(values), encoding="utf-8")

            settings = default_fusion_ui_settings(addin_dir)
            request = default_fusion_command_values(addin_dir)

        self.assertEqual(settings["input_mode"], FUSION_INPUT_MODE_QUICK_PARAMETRIC_BOX)
        self.assertEqual(settings["action"], FUSION_COMMAND_ACTION_REGENERATE)
        self.assertEqual(settings["box_inner_x_mm"], "160")
        self.assertEqual(settings["print_profile"], "draft")
        self.assertEqual(request.input_mode, FUSION_INPUT_MODE_QUICK_PARAMETRIC_BOX)
        self.assertEqual(request.action, FUSION_COMMAND_ACTION_REGENERATE)
        self.assertEqual(request.generation_mode, FUSION_GENERATION_MODE_COMPACT_ONLY)
        self.assertEqual(request.parameter_values["box_inner_x_mm"], "160")
        self.assertEqual(request.parameter_overrides["box_inner_x_mm"], 160.0)
        self.assertEqual(request.parameter_overrides["print_profile"], "draft")

    def test_save_command_settings_preserves_paths_and_all_ui_fields(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            addin_dir = Path(temp_dir)
            cad_ir_path = addin_dir / "last-user-cad-ir.json"
            cad_ir_path.write_text(json.dumps(_cad_ir_payload()), encoding="utf-8")
            config_path = ROOT / "examples" / "simple_asset_product_scene.json"
            (addin_dir / BGIG_UI_SETTINGS_FILENAME).write_text(
                json.dumps(
                    {
                        "cad_ir_path": str(cad_ir_path),
                        "config_json_path": str(config_path),
                        "project_root": str(ROOT),
                    }
                ),
                encoding="utf-8",
            )
            values = {
                "box_inner_x_mm": "160",
                "box_inner_y_mm": "80",
                "box_inner_z_mm": "30",
                "grid_units_x": "4",
                "grid_units_y": "4",
                "grid_units_z": "3",
                "wall_thickness_mm": "1.2",
                "floor_thickness_mm": "1.2",
                "peripheral_clearance_mm": "0.4",
                "inter_module_clearance_mm": "0.3",
                "print_profile": "draft",
            }
            request = build_fusion_command_request(
                "",
                FUSION_GENERATION_MODE_COMPACT_ONLY,
                addin_dir,
                action=FUSION_COMMAND_ACTION_REGENERATE,
                parameter_values=values,
                input_mode=FUSION_INPUT_MODE_QUICK_PARAMETRIC_BOX,
            )
            generated_cad_ir = addin_dir / "bgig_ui_generated_cad_ir.json"

            saved_ok = fusion_entrypoint._save_command_settings(addin_dir, request, generated_cad_ir)
            saved = load_fusion_ui_settings(addin_dir)

        self.assertTrue(saved_ok)
        self.assertEqual(saved["action"], FUSION_COMMAND_ACTION_REGENERATE)
        self.assertEqual(saved["input_mode"], FUSION_INPUT_MODE_QUICK_PARAMETRIC_BOX)
        self.assertEqual(saved["generation_mode"], FUSION_GENERATION_MODE_COMPACT_ONLY)
        self.assertEqual(Path(saved["cad_ir_path"]), cad_ir_path)
        self.assertEqual(Path(saved["generated_cad_ir_path"]), generated_cad_ir)
        self.assertEqual(Path(saved["config_json_path"]), config_path)
        self.assertEqual(Path(saved["project_root"]), ROOT)
        self.assertEqual(parametric_values_from_ui_settings(saved), values)


    def test_default_ui_settings_rehydrates_quick_asset_box_fields(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            addin_dir = Path(temp_dir)
            assets_text = "coin-tokens,tokens,30,20,20,2,loose; status-tokens,tokens,20,18,18,2,loose"
            values = {
                "action": FUSION_COMMAND_ACTION_REGENERATE,
                "input_mode": FUSION_INPUT_MODE_QUICK_ASSET_BOX,
                "generation_mode": FUSION_GENERATION_MODE_COMPACT_ONLY,
                "project_root": str(ROOT),
                BGIG_QUICK_ASSET_BOX_FIELD: assets_text,
                BGIG_QUICK_ASSET_BOX_MAX_STACK_HEIGHT_FIELD: "6",
                BGIG_QUICK_ASSET_BOX_TARGET_ASPECT_RATIO_FIELD: "1.0",
                BGIG_QUICK_ASSET_BOX_MAX_MODULE_LENGTH_FIELD: "40",
                "box_inner_x_mm": "120",
                "box_inner_y_mm": "80",
                "box_inner_z_mm": "30",
                "grid_units_x": "4",
                "grid_units_y": "4",
                "grid_units_z": "3",
                "wall_thickness_mm": "1.2",
                "floor_thickness_mm": "1.2",
                "peripheral_clearance_mm": "0.4",
                "inter_module_clearance_mm": "0.3",
                "print_profile": "draft",
            }
            (addin_dir / BGIG_UI_SETTINGS_FILENAME).write_text(json.dumps(values), encoding="utf-8")

            settings = default_fusion_ui_settings(addin_dir)
            request = default_fusion_command_values(addin_dir)
            summary = fusion_ui_settings_summary(settings)

        self.assertEqual(settings["input_mode"], FUSION_INPUT_MODE_QUICK_ASSET_BOX)
        self.assertEqual(settings[BGIG_QUICK_ASSET_BOX_FIELD], assets_text)
        self.assertEqual(settings[BGIG_QUICK_ASSET_BOX_MAX_STACK_HEIGHT_FIELD], "6")
        self.assertEqual(settings[BGIG_QUICK_ASSET_BOX_TARGET_ASPECT_RATIO_FIELD], "1.0")
        self.assertEqual(settings[BGIG_QUICK_ASSET_BOX_MAX_MODULE_LENGTH_FIELD], "40")
        self.assertEqual(request.source_kind, "quick_asset_box")
        self.assertEqual(request.quick_asset_box_assets_text, assets_text)
        self.assertEqual(request.quick_asset_box_max_stack_height_mm, "6")
        self.assertEqual(request.quick_asset_box_target_aspect_ratio, "1.0")
        self.assertEqual(request.quick_asset_box_max_module_length_mm, "40")
        self.assertIn("Loaded quick asset max stack height mm: 6", summary)
        self.assertIn("Loaded quick asset target aspect ratio: 1.0", summary)
        self.assertIn("Loaded quick asset max module length mm: 40", summary)
        self.assertIn("Loaded quick asset text", summary)
        self.assertIn("coin-tokens", summary)

    def test_save_command_settings_preserves_quick_asset_text(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            addin_dir = Path(temp_dir)
            values = {
                "box_inner_x_mm": "120",
                "box_inner_y_mm": "80",
                "box_inner_z_mm": "30",
                "grid_units_x": "4",
                "grid_units_y": "4",
                "grid_units_z": "3",
                "wall_thickness_mm": "1.2",
                "floor_thickness_mm": "1.2",
                "peripheral_clearance_mm": "0.4",
                "inter_module_clearance_mm": "0.3",
                "print_profile": "draft",
            }
            assets_text = "coin-tokens,tokens,30,20,20,2,loose"
            request = build_fusion_command_request(
                "",
                FUSION_GENERATION_MODE_COMPACT_ONLY,
                addin_dir,
                project_root_text=str(ROOT),
                parameter_values=values,
                input_mode=FUSION_INPUT_MODE_QUICK_ASSET_BOX,
                quick_asset_box_assets_text=assets_text,
                quick_asset_box_max_stack_height_mm="6",
                quick_asset_box_target_aspect_ratio="1.0",
                quick_asset_box_max_module_length_mm="40",
            )
            generated_cad_ir = addin_dir / "bgig_ui_generated_cad_ir.json"

            saved_ok = fusion_entrypoint._save_command_settings(addin_dir, request, generated_cad_ir)
            saved = load_fusion_ui_settings(addin_dir)

        self.assertTrue(saved_ok)
        self.assertEqual(saved["input_mode"], FUSION_INPUT_MODE_QUICK_ASSET_BOX)
        self.assertEqual(saved[BGIG_QUICK_ASSET_BOX_FIELD], assets_text)
        self.assertEqual(saved[BGIG_QUICK_ASSET_BOX_MAX_STACK_HEIGHT_FIELD], "6")
        self.assertEqual(saved[BGIG_QUICK_ASSET_BOX_TARGET_ASPECT_RATIO_FIELD], "1.0")
        self.assertEqual(saved[BGIG_QUICK_ASSET_BOX_MAX_MODULE_LENGTH_FIELD], "40")

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

    def test_staged_cad_identity_covers_the_exact_geometry(self) -> None:
        payload = _cad_ir_payload()
        identity = {
            "schema_version": "bgig.scene_artifact_identity.v1",
            "artifact_kind": "minimal_layout",
            "artifact_digest": "a" * 64,
            "partition_plan_digest": "b" * 64,
            "source_revision": 3,
        }
        payload.setdefault("metadata", {})["artifact_identity"] = identity
        cad_ir_digest = hashlib.sha256(
            json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest()
        payload["metadata"]["artifact_identity"] = {
            **identity,
            "cad_ir_digest": cad_ir_digest,
        }

        plan = generation_plan_from_cad_ir(payload)

        self.assertEqual(plan.artifact_identity, payload["metadata"]["artifact_identity"])
        payload["components"][0]["body"]["printable_size_mm"]["x"] += 1
        with self.assertRaisesRegex(FusionSkeletonError, "cad_ir_digest"):
            generation_plan_from_cad_ir(payload)
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
        payload = _cad_ir_payload_from_example("simple_asset_product_scene.json")

        plan = generation_plan_from_cad_ir(payload)

        self.assertEqual(len(plan.blanks), 0)
        self.assertEqual(len(plan.grid_positioned_blanks), 1)
        self.assertEqual(len(plan.rejected_grid_modules), 0)
        self.assertEqual(plan.created_object_count, 6)
        self.assertEqual(len(plan.cavity_cuts), 2)
        self.assertEqual(len(plan.finger_notch_cuts), 1)
        self.assertEqual(plan.finger_notch_cuts[0].source_feature_kind, "asset_access_notch")
        cut = plan.cavity_cuts[0]
        self.assertEqual(cut.cavity_source, "asset_compartment_cavity")
        self.assertEqual(cut.policy, ASSET_COMPARTMENT_CAVITY_POLICY)
        self.assertEqual(cut.cavity_id, "asset-compartment:coin-tokens")
        self.assertEqual(cut.cut_size_mm.to_dict(), {"x": 111.2, "y": 67.2, "z": 18.6})
        self.assertEqual(cut.requested_local_origin_mm.to_dict(), {"x": 1.2, "y": 1.2, "z": 1.2})
        self.assertAlmostEqual(cut.retained_floor_mm, 1.2)
        grid_blank = plan.grid_positioned_blanks[0]
        self.assertEqual(grid_blank.role, "generated_asset_grid_blank")
        self.assertEqual(grid_blank.grid_semantics, "placement_reservation_lattice_v0")
        self.assertEqual(grid_blank.body_snap_to_grid, "no")
        self.assertEqual(grid_blank.grid_span_is_reserved_space, "yes")
        self.assertEqual(grid_blank.body_size_may_be_smaller_than_grid_span, "yes")
        self.assertEqual(grid_blank.operation_kind, GRID_PLACED_BLANK_OPERATION_KIND)
        self.assertEqual(grid_blank.component_name, "Grid placed Grouped candidate for tokens")
        self.assertEqual(grid_blank.origin_mm.to_dict(), {"x": 0.0, "y": 0.0, "z": 0.0})
        self.assertEqual(grid_blank.size_mm.to_dict(), {"x": 113.6, "y": 90.0, "z": 19.8})
        self.assertEqual(grid_blank.printable_body_size_mm.to_dict(), {"x": 113.6, "y": 90.0, "z": 19.8})
        self.assertEqual(grid_blank.body_size_source, "printable_body_size_mm")
        self.assertNotEqual(grid_blank.size_mm.to_dict(), grid_blank.theoretical_grid_extent_mm.to_dict())
        self.assertEqual(grid_blank.asset_fit_size_mm.to_dict(), {"x": 111.2, "y": 87.6, "z": 18.6})
        self.assertEqual(grid_blank.theoretical_grid_extent_mm.to_dict(), {"x": 120.0, "y": 90.0, "z": 20.0})
        self.assertEqual(plan.to_dict()["grid_positioned_blanks"][0]["body_name"], grid_blank.body_name)
        self.assertEqual(plan.to_dict()["grid_positioned_blanks"][0]["body_size_source"], "printable_body_size_mm")
        self.assertEqual(plan.to_dict()["grid_positioned_blanks"][0]["grid_semantics"], "placement_reservation_lattice_v0")
        self.assertEqual(plan.to_dict()["grid_positioned_blanks"][0]["body_snap_to_grid"], "no")
        self.assertEqual(plan.to_dict()["grid_positioned_blanks"][0]["module_source"], "asset_candidate")
        self.assertEqual(plan.to_dict()["grid_positioned_blanks"][0]["asset_fit_cavity"]["policy"], ASSET_COMPARTMENT_CAVITY_POLICY)
        self.assertEqual(plan.to_dict()["cavity_cuts"][0]["cavity_source"], "asset_compartment_cavity")
        self.assertEqual(
            plan.to_dict()["grid_positioned_blanks"][0]["theoretical_grid_extent_mm"],
            {"x": 120.0, "y": 90.0, "z": 20.0},
        )


    def test_product_asset_scene_generates_single_sourced_grid_module(self) -> None:
        payload = _cad_ir_payload_from_example("simple_asset_product_scene.json")

        plan = generation_plan_from_cad_ir(payload)

        self.assertEqual(len(plan.blanks), 0)
        self.assertEqual(len(plan.grid_positioned_blanks), 1)
        self.assertEqual(plan.module_component_count, 1)
        self.assertEqual(len(plan.compact_occurrences), 1)
        self.assertEqual(len(plan.exploded_occurrences), 1)
        self.assertEqual(len(plan.cavity_cuts), 2)
        grid_blank = plan.grid_positioned_blanks[0]
        self.assertEqual(grid_blank.module_source, "asset_candidate")
        self.assertEqual(grid_blank.placement_source, "grid_placement")
        self.assertEqual(grid_blank.source_asset_ids, ("coin-tokens", "status-tokens"))
        self.assertEqual(grid_blank.candidate_id, "asset-group-candidate:tokens:store:exact")
        self.assertEqual(grid_blank.origin_mm.to_dict(), {"x": 0.0, "y": 0.0, "z": 0.0})
        self.assertEqual(grid_blank.size_mm.to_dict(), {"x": 113.6, "y": 90.0, "z": 19.8})
        self.assertEqual(grid_blank.theoretical_grid_extent_mm.to_dict(), {"x": 120.0, "y": 90.0, "z": 20.0})
        self.assertEqual(grid_blank.body_size_source, "printable_body_size_mm")
        self.assertEqual(grid_blank.clearance_applied["peripheral_clearance_mm"], 0.0)
        self.assertEqual(grid_blank.clearance_applied["inter_module_gap_mm"], 0.0)
        plan_dict = plan.to_dict()
        self.assertEqual(plan_dict["blanks"], [])
        self.assertEqual(plan_dict["grid_positioned_blanks"][0]["module_source"], "asset_candidate")
        self.assertEqual(plan_dict["grid_positioned_blanks"][0]["placement_source"], "grid_placement")
        self.assertEqual(plan_dict["grid_positioned_blanks"][0]["source_asset_ids"], ["coin-tokens", "status-tokens"])

    def test_rejects_modern_grid_placement_without_printable_body_size(self) -> None:
        payload = _cad_ir_payload_from_example("simple_asset_product_scene.json")
        placement = payload["metadata"]["executable_asset_plan"]["placements"][0]
        generated_module = payload["metadata"]["executable_asset_plan"]["generated_modules"][0]
        placement.pop("printable_body_size_mm")
        generated_module.pop("printable_body_size_mm")

        with self.assertRaisesRegex(FusionSkeletonError, "does not provide printable_body_size_mm"):
            generation_plan_from_cad_ir(payload)


    def test_grid_positioned_asset_blank_supports_z_layer_origin(self) -> None:
        payload = _cad_ir_payload_from_example("simple_asset_product_scene.json")
        placement = payload["metadata"]["executable_asset_plan"]["placements"][0]
        placement["origin_units"] = {"x": 0, "y": 0, "z": 1}
        placement["origin_mm"] = {"x": 0.0, "y": 0.0, "z": 10.0}
        placement["theoretical_grid_origin_mm"] = {"x": 0.0, "y": 0.0, "z": 10.0}
        placement["printable_body_origin_mm"] = {"x": 0.0, "y": 0.0, "z": 10.0}

        plan = generation_plan_from_cad_ir(payload)

        grid_blank = plan.grid_positioned_blanks[0]
        self.assertEqual(grid_blank.origin_mm.to_dict(), {"x": 0.0, "y": 0.0, "z": 10.0})
        self.assertEqual(grid_blank.size_mm.to_dict(), {"x": 113.6, "y": 90.0, "z": 19.8})
        self.assertEqual(grid_blank.printable_body_size_mm.to_dict(), {"x": 113.6, "y": 90.0, "z": 19.8})
        self.assertEqual(grid_blank.body_size_source, "printable_body_size_mm")
        self.assertNotEqual(grid_blank.size_mm.to_dict(), grid_blank.theoretical_grid_extent_mm.to_dict())

    def test_transports_count_aware_multilayer_grid_rejection(self) -> None:
        payload = _cad_ir_payload_from_example("simple_multilayer_grid_scene.json")

        plan = generation_plan_from_cad_ir(payload)

        self.assertEqual(len(plan.blanks), 1)
        self.assertEqual(len(plan.grid_positioned_blanks), 0)
        self.assertEqual(plan.module_component_count, 1)
        self.assertEqual(plan.multi_layer_grid_module_count, 0)
        self.assertEqual(plan.grid_modules_with_z_placement_count, 0)
        self.assertEqual(plan.grid_module_height_variant_count, 0)
        self.assertEqual(len(plan.compact_occurrences), 1)
        self.assertEqual(len(plan.exploded_occurrences), 1)
        self.assertEqual(len(plan.rejected_grid_modules), 1)
        self.assertEqual(plan.rejected_grid_modules[0].code, "DIMENSIONS_INCOMPATIBLE")
        self.assertIn("cannot fit inside the box", plan.rejected_grid_modules[0].message)
        plan_dict = plan.to_dict()
        self.assertEqual(plan_dict["multi_layer_grid_modules"], 0)
        self.assertEqual(plan_dict["grid_modules_with_z_placement"], 0)
        self.assertEqual(plan_dict["grid_module_height_variants"], 0)
        self.assertEqual(plan_dict["rejected_grid_modules"][0]["code"], "DIMENSIONS_INCOMPATIBLE")

    def test_builds_basic_exploded_view_from_linked_compact_and_grid_occurrences(self) -> None:
        payload = _asset_product_payload_with_manual_blank()

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
        self.assertEqual(compact_occurrence.component_id, "manual-debug-reference-body")
        self.assertEqual(compact_occurrence.origin_mm.to_dict(), {"x": 0.0, "y": 0.0, "z": 25.0})
        self.assertEqual(compact_exploded.view_role, EXPLODED_OCCURRENCE_ROLE)
        self.assertEqual(compact_exploded.operation_kind, LINKED_OCCURRENCE_OPERATION_KIND)
        self.assertTrue(compact_exploded.linked_component)
        self.assertEqual(compact_exploded.component_id, compact_occurrence.component_id)
        self.assertEqual(compact_exploded.source_body_id, "manual-debug-reference-body")
        self.assertEqual(compact_exploded.occurrence_name, "manual-debug-reference rectangular blank exploded occurrence")
        self.assertEqual(compact_exploded.origin_mm.to_dict(), {"x": 140.0, "y": 0.0, "z": 0.0})
        self.assertEqual(
            grid_exploded.occurrence_name,
            "generated - asset-group-candidate - tokens - store - exact grid positioned rectangular blank exploded occurrence",
        )
        self.assertAlmostEqual(grid_exploded.origin_mm.x, 140.0)
        self.assertEqual(grid_exploded.origin_mm.y, 20.0)
        self.assertEqual(grid_exploded.origin_mm.z, 0.0)
        plan_dict = plan.to_dict()
        exploded_occurrence_dict = plan_dict["exploded_occurrences"][0]
        self.assertEqual(plan_dict["exploded_occurrences"][1]["operation_kind"], LINKED_OCCURRENCE_OPERATION_KIND)
        self.assertEqual(exploded_occurrence_dict["planned_occurrence_label"], compact_exploded.occurrence_name)
        self.assertEqual(
            exploded_occurrence_dict["occurrence_name_policy"],
            OCCURRENCE_NAME_POLICY_COMPONENT_SOURCE,
        )
        self.assertFalse(exploded_occurrence_dict["direct_occurrence_rename"])
        self.assertTrue(plan_dict["linked_exploded_occurrences"])

    def test_compact_only_generation_mode_disables_exploded_view(self) -> None:
        payload = _cad_ir_payload_from_example("simple_asset_product_scene.json")

        plan = generation_plan_from_cad_ir(
            payload,
            generation_mode=FUSION_GENERATION_MODE_COMPACT_ONLY,
        )

        self.assertEqual(len(plan.blanks), 0)
        self.assertEqual(len(plan.grid_positioned_blanks), 1)
        self.assertEqual(len(plan.exploded_occurrences), 0)
        self.assertEqual(len(plan.cavity_cuts), 2)
        self.assertEqual(plan.created_object_count, 5)

    def test_skips_refused_asset_fit_cavity_without_cutting_grid_blank(self) -> None:
        payload = _cad_ir_payload_from_example("simple_asset_product_scene.json")
        module = payload["metadata"]["executable_asset_plan"]["generated_modules"][0]
        placement = payload["metadata"]["executable_asset_plan"]["placements"][0]
        refused = {
            **module["asset_fit_cavity"],
            "status": "refused",
            "code": "TEST_REFUSED",
            "reason": "test refusal",
        }
        module["asset_fit_cavity"] = refused
        placement["asset_fit_cavity"] = refused

        plan = generation_plan_from_cad_ir(payload)

        self.assertEqual(len(plan.grid_positioned_blanks), 1)
        self.assertEqual(len(plan.cavity_cuts), 0)

    def test_rejects_asset_fit_cavity_that_exceeds_grid_blank(self) -> None:
        payload = _cad_ir_payload_from_example("simple_asset_product_scene.json")
        cavity = payload["metadata"]["executable_asset_plan"]["placements"][0]["asset_fit_cavity"]
        cavity["compartments"][0]["size_mm"]["x"] = 200.0

        with self.assertRaisesRegex(FusionSkeletonError, "exceeds printable blank width"):
            generation_plan_from_cad_ir(payload)

    def test_rejects_unknown_generation_mode_for_generation_plan(self) -> None:
        payload = _cad_ir_payload_from_example("simple_asset_product_scene.json")

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
        payload = _asset_product_payload_with_manual_blank()
        payload["components"][0]["body"]["theoretical_origin_mm"] = {"x": 0.0, "y": 0.0, "z": 0.0}
        payload["components"][0]["body"]["printable_origin_mm"] = {"x": 0.0, "y": 0.0, "z": 0.0}
        placement = payload["metadata"]["executable_asset_plan"]["placements"][0]
        placement["origin_mm"] = {"x": 0.0, "y": 0.0, "z": 0.0}
        placement["theoretical_grid_origin_mm"] = {"x": 0.0, "y": 0.0, "z": 0.0}
        placement["printable_body_origin_mm"] = {"x": 0.0, "y": 0.0, "z": 0.0}
        placement["origin_units"] = {"x": 0, "y": 0, "z": 0}

        with self.assertRaisesRegex(FusionSkeletonError, "collides"):
            generation_plan_from_cad_ir(payload)

    def test_rejects_grid_placement_outside_reference_box(self) -> None:
        payload = _cad_ir_payload_from_example("simple_asset_product_scene.json")
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

    def test_addin_entrypoint_defines_all_ui_input_ids_it_references(self) -> None:
        source = (ROOT / "fusion_addin" / "BoardGameInsertGenerator" / "BoardGameInsertGenerator.py").read_text(encoding="utf-8")
        tree = ast.parse(source)
        defined_ids: set[str] = set()
        for node in tree.body:
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id.endswith("_INPUT_ID"):
                        defined_ids.add(target.id)
            elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name) and node.target.id.endswith("_INPUT_ID"):
                defined_ids.add(node.target.id)
        referenced_ids = {
            node.id
            for node in ast.walk(tree)
            if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load) and node.id.endswith("_INPUT_ID")
        }

        self.assertFalse(referenced_ids - defined_ids, f"Undefined UI input IDs: {sorted(referenced_ids - defined_ids)}")
        self.assertIn("QUICK_ASSET_BOX_ASSETS_INPUT_ID", defined_ids)
        self.assertIn("QUICK_ASSET_BOX_MAX_STACK_HEIGHT_INPUT_ID", defined_ids)
        self.assertIn("QUICK_ASSET_BOX_TARGET_ASPECT_RATIO_INPUT_ID", defined_ids)
        self.assertIn("QUICK_ASSET_BOX_MAX_MODULE_LENGTH_INPUT_ID", defined_ids)
        self.assertIn("Assets (quick_asset_box)", source)
        self.assertIn("Max stack height mm (quick_asset_box, optional)", source)
        self.assertIn("Target aspect ratio (quick_asset_box, optional)", source)
        self.assertIn("Max module length mm (quick_asset_box, optional)", source)
        self.assertIn("BGIG_QUICK_ASSET_BOX_HELP_TEXT", source)
        self.assertIn("BGIG_QUICK_ASSET_BOX_HELP_TITLE", source)
        self.assertIn("Mode and field guide", source)
        self.assertIn("_ui_parameter_label", source)

    def test_quick_asset_box_ui_help_text_is_human_readable(self) -> None:
        source = (ROOT / "fusion_addin" / "BoardGameInsertGenerator" / "fusion_skeleton.py").read_text(encoding="utf-8")
        entrypoint_source = (ROOT / "fusion_addin" / "BoardGameInsertGenerator" / "BoardGameInsertGenerator.py").read_text(encoding="utf-8")

        self.assertIn("Quick asset format and units", source)
        self.assertIn("Format: asset_id,type,count,x_mm,y_mm,z_mm,fit", source)
        self.assertIn("Example: coin-tokens,tokens,30,20,20,2,loose", source)
        self.assertIn("count = number of items", source)
        self.assertIn("For cards/sleeved_cards, z_mm is the total deck height", source)
        self.assertIn("Optional max stack height limits token/dice/meeple/generic pile height", source)
        self.assertIn("Box fields are inner dimensions in mm", source)
        self.assertIn("Grid units split the box", source)
        self.assertIn("BGIG_QUICK_ASSET_BOX_HELP_TEXT", entrypoint_source)
        self.assertIn("bgig_quick_asset_box_help", entrypoint_source)
        self.assertIn("box inner size, mm", entrypoint_source)
        self.assertEqual(fusion_entrypoint._ui_parameter_label("grid_units_x", "Grid units X"), "Grid units X (grid cell count)")
        self.assertEqual(fusion_entrypoint._ui_parameter_label("print_profile", "Print profile"), "Print profile (default, draft or fine)")

    def test_quick_asset_fusion_smoke_presets_are_valid_configs(self) -> None:
        catalog_path = ROOT / "scripts" / "fusion" / "quick_asset_presets.json"
        catalog = json.loads(catalog_path.read_text(encoding="utf-8-sig"))
        script_source = (ROOT / "scripts" / "fusion" / "prepare_quick_asset_test.ps1").read_text(encoding="utf-8-sig")

        self.assertEqual(catalog["schema"], "bgig.quick_asset_presets.v0")
        self.assertIn('[string] $Preset = "p17_printable_export"', script_source)
        self.assertIn('ValidateSet("p17_printable_export", "p16_ergonomic_tray_packing", "p15_tray_semantics", "p14_complete", "tokens", "dice_meeples_generic", "cards_tokens")', script_source)
        self.assertIn("quick_asset_box_target_aspect_ratio", script_source)
        self.assertIn("quick_asset_box_max_module_length_mm", script_source)
        self.assertEqual(
            set(catalog["presets"]),
            {"p17_printable_export", "p16_ergonomic_tray_packing", "p15_tray_semantics", "p14_complete", "tokens", "dice_meeples_generic", "cards_tokens"},
        )
        self.assertEqual(catalog["presets"]["p15_tray_semantics"]["max_stack_height_mm"], 18)
        self.assertEqual(catalog["presets"]["p16_ergonomic_tray_packing"]["max_stack_height_mm"], 18)
        self.assertEqual(catalog["presets"]["p16_ergonomic_tray_packing"]["target_aspect_ratio"], 1.4)
        self.assertEqual(catalog["presets"]["p16_ergonomic_tray_packing"]["max_module_length_mm"], 70)
        self.assertEqual(catalog["presets"]["p17_printable_export"]["max_stack_height_mm"], 18)
        self.assertEqual(catalog["presets"]["p17_printable_export"]["target_aspect_ratio"], 1.4)
        self.assertEqual(catalog["presets"]["p17_printable_export"]["max_module_length_mm"], 70)
        self.assertIn("export_printables", catalog["presets"]["p17_printable_export"]["smoke_focus"])
        for preset_name, preset in catalog["presets"].items():
            overrides = {
                "box_inner_x_mm": str(preset["box_inner_mm"]["x"]),
                "box_inner_y_mm": str(preset["box_inner_mm"]["y"]),
                "box_inner_z_mm": str(preset["box_inner_mm"]["z"]),
                "grid_units_x": str(preset["grid_units"]["x"]),
                "grid_units_y": str(preset["grid_units"]["y"]),
                "grid_units_z": str(preset["grid_units"]["z"]),
                "wall_thickness_mm": "1.2",
                "floor_thickness_mm": "1.2",
                "peripheral_clearance_mm": "0.4",
                "inter_module_clearance_mm": "0.3",
                "print_profile": "draft",
            }

            asset_report = parse_quick_asset_box_assets_text(preset["assets_text"])
            self.assertGreater(len(asset_report["accepted_assets"]), 0, preset_name)
            self.assertEqual(asset_report["rejected_assets"], [], preset_name)

            config_payload = build_quick_asset_box_config_payload(
                overrides,
                preset["assets_text"],
                str(preset.get("max_stack_height_mm", "")),
                str(preset.get("target_aspect_ratio", "")),
                str(preset.get("max_module_length_mm", "")),
            )
            self.assertEqual(config_payload["modules"], [], preset_name)
            self.assertGreater(len(config_payload["assets"]), 0, preset_name)
            if "max_stack_height_mm" in preset:
                self.assertTrue(
                    any(asset.get("max_stack_height_mm") == float(preset["max_stack_height_mm"]) for asset in config_payload["assets"]),
                    preset_name,
                )
            if "target_aspect_ratio" in preset:
                self.assertTrue(
                    any(asset.get("target_aspect_ratio") == float(preset["target_aspect_ratio"]) for asset in config_payload["assets"]),
                    preset_name,
                )
            if "max_module_length_mm" in preset:
                self.assertTrue(
                    any(asset.get("max_module_length_mm") == float(preset["max_module_length_mm"]) for asset in config_payload["assets"]),
                    preset_name,
                )
            self.assertEqual(
                config_payload["box"]["inner_dimensions_mm"]["x"],
                float(preset["box_inner_mm"]["x"]),
                preset_name,
            )
            self.assertIn("volumetric_grid", config_payload, preset_name)
            with tempfile.TemporaryDirectory() as temp_dir:
                config_path = Path(temp_dir) / f"{preset_name}.json"
                config_path.write_text(json.dumps(config_payload), encoding="utf-8")
                config = load_config(config_path)
                report = generate_basic_layout(config)
            payload = json.loads(layout_to_json(config, report))
            self.assertGreaterEqual(payload["summary"]["module_candidate_count"], 1, preset_name)
            if preset_name in {"p16_ergonomic_tray_packing", "p17_printable_export"}:
                generated = payload["executable_asset_plan"]["generated_modules"][0]
                sizing = generated["storage_sizing"]
                self.assertEqual(sizing["tray_packing_policy"], "flat_tray_2d_v0")
                self.assertEqual(sizing["target_aspect_ratio"], 1.4)
                self.assertEqual(sizing["max_module_length_mm"], 70.0)
                self.assertGreaterEqual(sizing["pile_grid_rows"], 2)
                self.assertEqual(sizing["linear_layout_avoided"], "yes")

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
        self.assertIn('_register_command_and_show_palette', source)
        self.assertIn('_ensure_palette(addin_dir)', source)
        self.assertIn('if action == "expert"', source)
        self.assertLess(source.index("adsk.autoTerminate(False)"), source.index("_ensure_palette(addin_dir)"))
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
        self.assertIn("bgig_ui_settings_status", source)
        self.assertIn("UI settings", source)
        self.assertIn("fusion_ui_settings_summary", source)
        self.assertIn("Action", source)
        self.assertIn("FUSION_COMMAND_ACTION_REGENERATE", source)
        self.assertIn("FUSION_COMMAND_ACTION_CLEAR", source)
        self.assertIn("FUSION_COMMAND_ACTION_INSPECT", source)
        self.assertIn("inspect_bgig_scene", source)
        self.assertIn("class BgigFusionRegistry", source)
        self.assertIn("def inspect", source)
        self.assertIn("def clear", source)
        self.assertIn("registry.create_scene_id", source)
        self.assertIn("BGIG_ATTRIBUTE_SCENE_ID_KEY", source)
        self.assertIn("BGIG_ATTRIBUTE_MODULE_ID_KEY", source)
        self.assertIn("_stable_generation_result", source)
        self.assertIn("BGIG generation failed registry validation", source)
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
        self.assertIn("Active in config_file, quick_parametric_box and quick_asset_box modes", source)
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
        self.assertIn("BGIG-looking untagged entities", source)
        self.assertIn("Tagged BGIG unique entities sample", source)
        self.assertIn("Tagged BGIG unique entities", source)
        self.assertIn("BGIG scene root occurrences", source)
        self.assertIn("Registry validation", source)
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
        self.assertIn("registry = BgigFusionRegistry(design)", execute_block)
        self.assertIn("inspection_before = registry.inspect()", execute_block)
        self.assertIn("scene_roots_before = int(inspection_before", execute_block)
        self.assertIn("request.action == FUSION_COMMAND_ACTION_INSPECT", execute_block)
        self.assertIn("request.action == FUSION_COMMAND_ACTION_GENERATE and (", execute_block)
        self.assertLess(
            execute_block.index("request.action == FUSION_COMMAND_ACTION_GENERATE and ("),
            execute_block.index("cad_ir_path = request.cad_ir_path"),
        )
        self.assertIn('request.source_kind == "quick_asset_box"', execute_block)
        self.assertIn("_generate_cad_ir_from_quick_asset_box_request", execute_block)
        self.assertIn("quick_asset_box_summary", source)
        self.assertIn("asset_items_visualized", skeleton_source)
        self.assertIn("asset_cavities_generated", skeleton_source)
        self.assertIn("asset_cavity_policy", skeleton_source)
        self.assertIn("single_asset_fit_rectangular_cavity_v0", skeleton_source)
        self.assertIn("count_aware_storage_sizing", skeleton_source)
        self.assertIn("bottom_and_top_box_xy_outlines_hidden_by_default", source)
        self.assertIn("sketch.isLightBulbOn = False", source)
        self.assertIn("_create_reference_box_outlines", source)
        self.assertIn("Reference outline policy", source)
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


def _asset_product_payload_with_manual_blank() -> dict:
    payload = _cad_ir_payload_from_example("simple_asset_product_scene.json")
    payload.setdefault("components", []).append(
        {
            "id": "component:manual-debug-reference",
            "name": "manual-debug-reference",
            "module_id": "manual-debug-reference",
            "instance_id": "manual-debug-reference-01",
            "functional_type": "utility",
            "body": {
                "id": "manual-debug-reference-body",
                "name": "manual-debug-reference rectangular blank",
                "kind": "rectangular_blank",
                "theoretical_origin_mm": {"x": 0.0, "y": 0.0, "z": 25.0},
                "theoretical_size_mm": {"x": 10.0, "y": 10.0, "z": 5.0},
                "printable_origin_mm": {"x": 0.0, "y": 0.0, "z": 25.0},
                "printable_size_mm": {"x": 10.0, "y": 10.0, "z": 5.0},
                "operations": [
                    {
                        "id": "operation:create-manual-debug-reference",
                        "kind": "create_rectangular_prism",
                        "parameters": {"source": "test_manual_blank"},
                    }
                ],
            },
        }
    )
    return payload


if __name__ == "__main__":
    unittest.main()
