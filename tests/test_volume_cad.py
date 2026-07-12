from __future__ import annotations

import unittest

from board_game_insert_generator.project_v1 import blank_project_v1
from board_game_insert_generator.volume_cad import (
    FUNCTIONAL_CAD_BUILD_SCHEMA_V1,
    build_functional_cad,
)
from fusion_addin.BoardGameInsertGenerator.fusion_skeleton import (
    FUSION_GENERATION_MODE_COMPACT_ONLY,
    generation_plan_from_cad_ir,
)


def _project() -> dict[str, object]:
    project = blank_project_v1()
    project["project_name"] = "Jeu temoin P42"
    project["container_groups"] = [
        {"id": "cards", "name": "Cartes", "wall_thickness_mm": None, "floor_thickness_mm": None},
        {"id": "tokens", "name": "Jetons", "wall_thickness_mm": None, "floor_thickness_mm": None},
    ]
    project["contents"] = [
        {"id": "deck", "name": "Cartes", "shape_kind": "cards", "dimensions_mm": {"x": 63.0, "y": 88.0, "z": 18.0}, "quantity": 100, "container_group_id": "cards", "content_clearance_mm": None, "measurement_confidence": "exact"},
        {"id": "tokens", "name": "Jetons", "shape_kind": "round", "dimensions_mm": {"x": 14.0, "y": 14.0, "z": 3.0}, "quantity": 72, "container_group_id": "tokens", "content_clearance_mm": None, "measurement_confidence": "exact"},
    ]
    project["flat_items"] = [
        {"id": "board", "name": "Plateau", "kind": "board", "dimensions_mm": {"x": 190.0, "y": 140.0, "z": 2.0}, "quantity": 1, "stack_order": 0}
    ]
    project["fill_elements"] = [
        {"id": "spare", "name": "Bac vide", "kind": "hollow", "mode": "exact", "dimensions_mm": {"x": 20.0, "y": 20.0, "z": 10.0}, "container_group_id": None},
        {"id": "weight", "name": "Poids", "kind": "solid", "mode": "exact", "dimensions_mm": {"x": 15.0, "y": 15.0, "z": 8.0}, "container_group_id": None},
    ]
    return project


class VolumeCadTests(unittest.TestCase):
    def test_builds_functional_cad_ir_from_a_complete_volume_plan(self) -> None:
        result = build_functional_cad(_project())

        self.assertEqual(result["schema_version"], FUNCTIONAL_CAD_BUILD_SCHEMA_V1)
        self.assertEqual(result["status"], "planned_for_fusion_smoke")
        cad_ir = result["cad_ir"]
        self.assertIsInstance(cad_ir, dict)
        self.assertEqual(cad_ir["schema_version"], "cad_ir.v0")
        self.assertGreaterEqual(result["materialization"]["container_component_count"], 2)
        self.assertGreaterEqual(result["materialization"]["hollow_fill_component_count"], 1)
        self.assertGreaterEqual(result["materialization"]["solid_component_count"], 1)
        cards = next(component for component in cad_ir["components"] if component["metadata"].get("container_group_id") == "cards")
        self.assertEqual(cards["body"]["operations"][0]["kind"], "create_rectangular_prism")
        self.assertTrue(all(operation["kind"] == "subtract_rectangular_cavity" for operation in cards["body"]["operations"][1:]))
        self.assertTrue(all(cavity["fusion_generation"] == "planned_for_fusion_smoke" for cavity in cards["body"]["cavities"]))

    def test_scene_is_accepted_by_the_existing_fusion_adapter(self) -> None:
        result = build_functional_cad(_project())

        plan = generation_plan_from_cad_ir(result["cad_ir"], FUSION_GENERATION_MODE_COMPACT_ONLY)

        self.assertEqual(len(plan.blanks), result["materialization"]["component_count"])
        self.assertEqual(len(plan.cavity_cuts), result["materialization"]["cavity_count"])
        self.assertEqual(len(plan.exploded_occurrences), 0)

    def test_does_not_fabricate_cad_from_an_impossible_volume_plan(self) -> None:
        project = _project()
        project["box"] = {"inner_dimensions_mm": {"x": 70.0, "y": 70.0, "z": 40.0}, "usable_height_mm": 36.0, "lid_clearance_mm": 2.0}

        result = build_functional_cad(project)

        self.assertEqual(result["status"], "impossible")
        self.assertIsNone(result["cad_ir"])
        self.assertTrue(result["blockers"])

    def test_refuses_an_exact_empty_bin_that_cannot_keep_minimum_walls(self) -> None:
        project = _project()
        project["fill_elements"] = [
            {"id": "too-thin", "name": "Bac vide trop fin", "kind": "hollow", "mode": "exact", "dimensions_mm": {"x": 2.0, "y": 20.0, "z": 10.0}, "container_group_id": None},
        ]

        result = build_functional_cad(project)

        self.assertEqual(result["status"], "impossible")
        self.assertIsNone(result["cad_ir"])
        self.assertIn("trop petit", " ".join(result["blockers"]))


    def test_supports_high_cardinality_in_compact_fusion_mode(self) -> None:
        project = blank_project_v1()
        project["box"] = {"inner_dimensions_mm": {"x": 800.0, "y": 800.0, "z": 120.0}, "usable_height_mm": 116.0, "lid_clearance_mm": 2.0}
        project["container_groups"] = [
            {"id": f"g{index}", "name": f"Bac {index}", "wall_thickness_mm": None, "floor_thickness_mm": None}
            for index in range(50)
        ]
        project["contents"] = [
            {"id": f"c{index}", "name": f"Piece {index}", "shape_kind": "square", "dimensions_mm": {"x": 8.0, "y": 8.0, "z": 3.0}, "quantity": 1, "container_group_id": f"g{index % 50}", "content_clearance_mm": None, "measurement_confidence": "exact"}
            for index in range(72)
        ]
        project["flat_items"] = [
            {"id": f"flat{index}", "name": f"Livret {index}", "kind": "rulebook", "dimensions_mm": {"x": 200.0, "y": 200.0, "z": 0.5}, "quantity": 1, "stack_order": index}
            for index in range(25)
        ]

        result = build_functional_cad(project)

        self.assertEqual(result["status"], "planned_for_fusion_smoke")
        plan = generation_plan_from_cad_ir(result["cad_ir"], FUSION_GENERATION_MODE_COMPACT_ONLY)
        self.assertGreaterEqual(result["materialization"]["container_component_count"], 50)
        self.assertEqual(len(plan.exploded_occurrences), 0)
        for component in result["cad_ir"]["components"]:
            origin = component["body"]["printable_origin_mm"]
            size = component["body"]["printable_size_mm"]
            self.assertGreaterEqual(origin["x"], 0.0)
            self.assertGreaterEqual(origin["y"], 0.0)
            self.assertGreaterEqual(origin["z"], 0.0)
            self.assertLessEqual(origin["x"] + size["x"], 800.0)
            self.assertLessEqual(origin["y"] + size["y"], 800.0)
            self.assertLessEqual(origin["z"] + size["z"], 116.0)
if __name__ == "__main__":
    unittest.main()
