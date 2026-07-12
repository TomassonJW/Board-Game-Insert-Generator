from __future__ import annotations

import unittest

from board_game_insert_generator.project_v1 import blank_project_v1
from board_game_insert_generator.volume_closure import VOLUME_CLOSURE_SCHEMA_V1, solve_project_volume


def _project() -> dict[str, object]:
    project = blank_project_v1()
    project["container_groups"] = [
        {"id": "cards", "name": "Cartes", "wall_thickness_mm": None, "floor_thickness_mm": None},
        {"id": "tokens", "name": "Jetons", "wall_thickness_mm": None, "floor_thickness_mm": None},
    ]
    project["contents"] = [
        {"id": "deck", "name": "Cartes", "shape_kind": "cards", "dimensions_mm": {"x": 63.0, "y": 88.0, "z": 18.0}, "quantity": 100, "container_group_id": "cards", "content_clearance_mm": None, "measurement_confidence": "exact"},
        {"id": "tokens", "name": "Jetons", "shape_kind": "round", "dimensions_mm": {"x": 14.0, "y": 14.0, "z": 3.0}, "quantity": 72, "container_group_id": "tokens", "content_clearance_mm": None, "measurement_confidence": "exact"},
    ]
    return project


class VolumeClosureTests(unittest.TestCase):
    def test_constructs_a_collision_free_volume_plan_and_classifies_free_regions(self) -> None:
        result = solve_project_volume(_project())

        self.assertEqual(result["schema_version"], VOLUME_CLOSURE_SCHEMA_V1)
        self.assertEqual(result["summary"]["status"], "constructed_plan")
        self.assertEqual(result["summary"]["placed_container_count"], 2)
        self.assertTrue(result["validation"]["no_collisions"])
        self.assertTrue(result["validation"]["volume_conserved"])
        self.assertGreater(result["summary"]["classified_free_region_count"], 0)
        self.assertTrue(all("classification" in region for region in result["free_regions"]))

    def test_reserves_upper_stack_and_plans_support_with_hollow_fillers(self) -> None:
        project = _project()
        project["flat_items"] = [
            {"id": "board", "name": "Plateau", "kind": "board", "dimensions_mm": {"x": 190.0, "y": 140.0, "z": 2.0}, "quantity": 1, "stack_order": 0}
        ]

        result = solve_project_volume(project)

        self.assertEqual(result["summary"]["status"], "constructed_plan")
        self.assertEqual(result["reservations"][0]["kind"], "upper_flat_stack")
        self.assertEqual(result["support"]["status"], "planned_continuous_with_hollow_fillers")
        self.assertTrue(any(region["classification"] == "support_hollow_fill_candidate" for region in result["free_regions"]))

    def test_respects_requested_clearance_between_placed_containers(self) -> None:
        project = _project()
        project["layout"]["layout_clearance_mm"] = 1.0
        result = solve_project_volume(project)
        left, right = result["placements"]
        separated = (
            left["origin_mm"]["x"] + left["size_mm"]["x"] + 1.0 <= right["origin_mm"]["x"]
            or right["origin_mm"]["x"] + right["size_mm"]["x"] + 1.0 <= left["origin_mm"]["x"]
            or left["origin_mm"]["y"] + left["size_mm"]["y"] + 1.0 <= right["origin_mm"]["y"]
            or right["origin_mm"]["y"] + right["size_mm"]["y"] + 1.0 <= left["origin_mm"]["y"]
        )
        self.assertTrue(separated)

    def test_handles_50_containers_72_content_families_and_25_flat_items_without_a_business_limit(self) -> None:
        project = blank_project_v1()
        project["box"] = {"inner_dimensions_mm": {"x": 800.0, "y": 800.0, "z": 120.0}, "usable_height_mm": 116.0, "lid_clearance_mm": 2.0}
        project["container_groups"] = [{"id": f"g{index}", "name": f"Bac {index}", "wall_thickness_mm": None, "floor_thickness_mm": None} for index in range(50)]
        project["contents"] = [{"id": f"c{index}", "name": f"Piece {index}", "shape_kind": "square", "dimensions_mm": {"x": 8.0, "y": 8.0, "z": 3.0}, "quantity": 1, "container_group_id": f"g{index % 50}", "content_clearance_mm": None, "measurement_confidence": "exact"} for index in range(72)]
        project["flat_items"] = [{"id": f"flat{index}", "name": f"Livret {index}", "kind": "rulebook", "dimensions_mm": {"x": 200.0, "y": 200.0, "z": 0.5}, "quantity": 1, "stack_order": index} for index in range(25)]

        result = solve_project_volume(project)

        self.assertIn(result["summary"]["status"], {"constructed_plan", "impossible"})
        self.assertEqual(result["container_plan"]["summary"]["content_family_count"], 72)
        self.assertEqual(result["summary"]["placed_container_count"], 50)

    def test_places_user_requested_exact_hollow_and_solid_fill_volumes(self) -> None:
        project = _project()
        project["fill_elements"] = [
            {"id": "spare", "name": "Bac vide", "kind": "hollow", "mode": "exact", "dimensions_mm": {"x": 20.0, "y": 20.0, "z": 10.0}, "container_group_id": None},
            {"id": "weight", "name": "Poids", "kind": "solid", "mode": "exact", "dimensions_mm": {"x": 15.0, "y": 15.0, "z": 8.0}, "container_group_id": None},
        ]

        result = solve_project_volume(project)

        self.assertEqual(result["summary"]["status"], "constructed_plan")
        self.assertEqual({item["requested_fill_id"] for item in result["fill_placements"]}, {"spare", "weight"})
        self.assertTrue(result["validation"]["no_collisions"])

    def test_reports_impossible_when_a_container_cannot_be_placed(self) -> None:
        project = _project()
        project["box"] = {"inner_dimensions_mm": {"x": 70.0, "y": 70.0, "z": 40.0}, "usable_height_mm": 36.0, "lid_clearance_mm": 2.0}

        result = solve_project_volume(project)

        self.assertEqual(result["summary"]["status"], "impossible")
        self.assertTrue(result["blockers"])


if __name__ == "__main__":
    unittest.main()
