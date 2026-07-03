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
    PLAN_STATUS_PLANNED_ONLY,
    FusionSkeletonError,
    describe_document_state,
    load_cad_ir_json,
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
        self.assertIn("does not create geometry", state.message)

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


def _cad_ir_payload() -> dict:
    config = load_config(ROOT / "examples" / "simple_box.json")
    layout = generate_basic_layout(config)
    return build_blank_cad_scene(config, layout).to_dict()


if __name__ == "__main__":
    unittest.main()
