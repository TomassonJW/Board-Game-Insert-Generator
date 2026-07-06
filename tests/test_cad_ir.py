from __future__ import annotations

import unittest

from context import ROOT

from board_game_insert_generator.cad_ir import (
    CAD_IR_SCHEMA_VERSION,
    CAVITY_FEATURE_OPERATION_KIND,
    CAVITY_OPERATION_KIND,
    CadIrError,
    build_blank_cad_scene,
)
from board_game_insert_generator.config_loader import load_config
from board_game_insert_generator.layout import generate_basic_layout
from board_game_insert_generator.models import LayoutResult

class CadIrTests(unittest.TestCase):
    def test_blank_scene_exposes_reference_box_components_and_units(self) -> None:
        config = load_config(ROOT / "examples" / "simple_box.json")
        layout = generate_basic_layout(config)

        scene = build_blank_cad_scene(config, layout)
        payload = scene.to_dict()

        self.assertEqual(payload["schema_version"], CAD_IR_SCHEMA_VERSION)
        self.assertEqual(payload["units"], "mm")
        self.assertEqual(payload["coordinate_system"], "right_handed_z_up_mm")
        self.assertFalse(payload["box_reference"]["printable"])
        self.assertEqual(payload["box_reference"]["size_mm"]["x"], 285.0)
        self.assertEqual(len(payload["components"]), 4)
        self.assertEqual(payload["components"][0]["id"], "component:cards-main-01")
        self.assertEqual(payload["components"][0]["body"]["kind"], "rectangular_blank")
        self.assertEqual(
            payload["components"][0]["body"]["operations"][0]["kind"],
            "create_rectangular_prism",
        )
        self.assertEqual(payload["metadata"]["layout_strategy"], "row_fill")
        self.assertEqual(payload["metadata"]["print_profile"], "default")

    def test_scene_keeps_theoretical_and_printable_dimensions_separate(self) -> None:
        config = load_config(ROOT / "examples" / "simple_box.json")
        layout = generate_basic_layout(config)

        payload = build_blank_cad_scene(config, layout).to_dict()
        first_body = payload["components"][0]["body"]

        self.assertEqual(
            first_body["theoretical_origin_mm"],
            {"x": 0.0, "y": 0.0, "z": 0.0},
        )
        self.assertEqual(
            first_body["theoretical_size_mm"],
            {"x": 70.0, "y": 100.0, "z": 45.0},
        )
        self.assertEqual(
            first_body["printable_origin_mm"],
            {"x": 0.8, "y": 0.8, "z": 0.0},
        )
        self.assertEqual(
            first_body["printable_size_mm"],
            {"x": 68.9, "y": 99.2, "z": 44.0},
        )

    def test_scene_serializes_face_classifications_and_tolerance_rules(self) -> None:
        config = load_config(ROOT / "examples" / "simple_box.json")
        layout = generate_basic_layout(config)

        first_body = build_blank_cad_scene(config, layout).to_dict()["components"][0]["body"]

        self.assertEqual(first_body["face_classifications"][0]["face"], "x_min")
        self.assertEqual(first_body["face_classifications"][0]["role"], "peripheral")
        self.assertEqual(
            first_body["face_classifications"][1]["neighbor_instance_id"],
            "cards-main-02",
        )
        self.assertEqual(first_body["applied_tolerances"][0]["rule_id"], "peripheral_clearance")
        self.assertEqual(first_body["applied_tolerances"][0]["offset_mm"], 0.8)
        self.assertTrue(first_body["applied_tolerances"][0]["receives_clearance"])
        self.assertEqual(
            first_body["applied_tolerances"][3]["rule_id"],
            "exposed_printer_compensation_only",
        )
        self.assertFalse(first_body["applied_tolerances"][3]["receives_clearance"])

    def test_scene_serializes_abstract_cavity_operations(self) -> None:
        config = load_config(ROOT / "examples" / "simple_tray.json")
        layout = generate_basic_layout(config)

        body = build_blank_cad_scene(config, layout).to_dict()["components"][0]["body"]

        self.assertEqual(body["cavities"][0]["id"], "token-pocket")
        self.assertEqual(body["cavities"][0]["status"], "abstract_only")
        self.assertEqual(body["cavities"][0]["fusion_generation"], "not_implemented")
        operation_kinds = [operation["kind"] for operation in body["operations"]]
        self.assertEqual(operation_kinds, ["create_rectangular_prism", CAVITY_OPERATION_KIND])
        cavity_operation = body["operations"][1]
        self.assertEqual(cavity_operation["parameters"]["coordinate_frame"], "body.local")
        self.assertEqual(cavity_operation["parameters"]["fusion_generation"], "not_implemented")

    def test_scene_serializes_abstract_cavity_feature_operations(self) -> None:
        config = load_config(ROOT / "examples" / "simple_finger_notch_tray.json")
        layout = generate_basic_layout(config)

        body = build_blank_cad_scene(config, layout).to_dict()["components"][0]["body"]

        cavity = body["cavities"][0]
        self.assertEqual(cavity["features"][0]["id"], "front-half-moon-notch")
        self.assertEqual(cavity["features"][0]["kind"], "half_moon_notch")
        self.assertEqual(cavity["features"][0]["fusion_generation"], "not_implemented")
        self.assertEqual(cavity["features"][0]["taxonomy"]["taxonomy"], "top_open_half_moon_notch")
        self.assertEqual(cavity["features"][0]["taxonomy"]["fusion_fallback_taxonomy"], "top_open_rectangular_notch")
        self.assertEqual(cavity["features"][1]["kind"], "rounded_floor")
        operation_kinds = [operation["kind"] for operation in body["operations"]]
        self.assertEqual(
            operation_kinds,
            [
                "create_rectangular_prism",
                CAVITY_OPERATION_KIND,
                CAVITY_FEATURE_OPERATION_KIND,
                CAVITY_FEATURE_OPERATION_KIND,
            ],
        )
        feature_operation = body["operations"][2]
        self.assertEqual(feature_operation["parameters"]["cavity_id"], "token-pocket")
        self.assertEqual(feature_operation["parameters"]["feature_id"], "front-half-moon-notch")
        self.assertEqual(feature_operation["parameters"]["coordinate_frame"], "cavity.local")
        self.assertEqual(feature_operation["parameters"]["fusion_generation"], "not_implemented")
        self.assertEqual(feature_operation["parameters"]["taxonomy"]["taxonomy"], "top_open_half_moon_notch")

    def test_scene_serializes_card_cavity_profile_clearance_sources(self) -> None:
        config = load_config(ROOT / "examples" / "simple_card_tray.json")
        layout = generate_basic_layout(config)

        payload = build_blank_cad_scene(config, layout).to_dict()
        first_cavity = payload["components"][0]["body"]["cavities"][0]
        second_cavity = payload["components"][1]["body"]["cavities"][0]

        self.assertEqual(first_cavity["functional_type"], "cards")
        self.assertEqual(first_cavity["clearance_mm"], 0.45)
        self.assertEqual(first_cavity["clearance_source"], "tolerances.card_clearance_mm")
        self.assertEqual(second_cavity["functional_type"], "sleeved_cards")
        self.assertEqual(second_cavity["clearance_mm"], 0.95)
        self.assertEqual(second_cavity["clearance_source"], "tolerances.sleeved_card_clearance_mm")

    def test_scene_serializes_open_receptacle_profile_clearance_sources(self) -> None:
        config = load_config(ROOT / "examples" / "simple_open_tray.json")
        layout = generate_basic_layout(config)

        payload = build_blank_cad_scene(config, layout).to_dict()
        sources = [
            component["body"]["cavities"][0]["clearance_source"]
            for component in payload["components"]
        ]

        self.assertEqual(
            sources,
            [
                "tolerances.token_clearance_mm",
                "tolerances.token_clearance_mm",
                "tolerances.meeple_clearance_mm",
            ],
        )

    def test_scene_rejects_inconsistent_layout_result(self) -> None:
        config = load_config(ROOT / "examples" / "simple_box.json")
        layout = generate_basic_layout(config)
        inconsistent = LayoutResult(cells=layout.cells, printable_bodies=(), warnings=layout.warnings)

        with self.assertRaisesRegex(CadIrError, "Missing printable bodies"):
            build_blank_cad_scene(config, inconsistent)

if __name__ == "__main__":
    unittest.main()
