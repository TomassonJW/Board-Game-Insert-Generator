from __future__ import annotations

import json
import unittest

from context import ROOT

from board_game_insert_generator.cad_ir import build_blank_cad_scene
from board_game_insert_generator.config_loader import load_config
from board_game_insert_generator.layout import generate_basic_layout
from fusion_addin.BoardGameInsertGenerator.fusion_skeleton import (
    DOCUMENT_STATUS_READY,
    DOCUMENT_STATUS_ZERO_DOC,
    FUSION_MANUAL_VALIDATION_REQUIRED,
    PLAN_STATUS_PLANNED_ONLY,
    FusionSkeletonError,
    describe_document_state,
    generation_plan_from_cad_ir,
    load_cad_ir_json,
    mm_to_cm,
    planned_operations_from_cad_ir,
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
        self.assertIn("compatible with Part Design documents", source)


def _cad_ir_payload() -> dict:
    config = load_config(ROOT / "examples" / "simple_box.json")
    layout = generate_basic_layout(config)
    return build_blank_cad_scene(config, layout).to_dict()


if __name__ == "__main__":
    unittest.main()
