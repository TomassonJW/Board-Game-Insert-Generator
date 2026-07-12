from __future__ import annotations

from copy import deepcopy
import unittest

from board_game_insert_generator.partition_result_view import (
    PARTITION_RESULT_VIEW_SCHEMA_V1,
    PartitionResultViewError,
    build_partition_result_view,
)
from board_game_insert_generator.partition_solver import PARTITION_PLAN_SCHEMA_V1, solve_partition_plan
from board_game_insert_generator.project_v1 import blank_project_v1


def project() -> dict[str, object]:
    value = blank_project_v1()
    value["box"] = {"inner_dimensions_mm": {"x": 200.0, "y": 150.0, "z": 60.0}, "usable_height_mm": 56.0, "lid_clearance_mm": 2.0}
    value["container_groups"] = [
        {"id": "cards", "name": "Cartes", "wall_thickness_mm": None, "floor_thickness_mm": None},
        {"id": "tokens", "name": "Jetons", "wall_thickness_mm": None, "floor_thickness_mm": None},
    ]
    value["contents"] = [
        {"id": "deck", "name": "Deck", "shape_kind": "cards", "dimensions_mm": {"x": 63.0, "y": 88.0, "z": 18.0}, "quantity": 50, "container_group_id": "cards", "content_clearance_mm": None, "measurement_confidence": "exact"},
        {"id": "coin", "name": "Pieces", "shape_kind": "round", "dimensions_mm": {"x": 15.0, "y": 15.0, "z": 3.0}, "quantity": 20, "container_group_id": "tokens", "content_clearance_mm": None, "measurement_confidence": "exact"},
    ]
    return value


class PartitionResultViewTests(unittest.TestCase):
    def test_top_view_reuses_exact_body_bounds_and_real_cavity_count(self) -> None:
        plan = solve_partition_plan(project())
        original = deepcopy(plan)
        view = build_partition_result_view(plan)

        self.assertEqual(view["schema_version"], PARTITION_RESULT_VIEW_SCHEMA_V1)
        self.assertEqual(view["source_plan_digest"], plan["plan_digest"])
        self.assertEqual(len(view["top_view"]["bodies"]), len(plan["placements"]))
        self.assertEqual(len(view["top_view"]["cavities"]), sum(len(item["cavity_layout"]) for item in plan["placements"]))
        self.assertEqual({item["content_name"] for item in view["top_view"]["cavities"]}, {"Deck", "Pieces"})
        self.assertTrue(all(item["source_contents"] for item in view["details"]))
        first_plan = plan["placements"][0]
        first_view = view["top_view"]["bodies"][0]
        self.assertEqual((first_view["x_mm"], first_view["y_mm"]), (first_plan["origin_mm"]["x"], first_plan["origin_mm"]["y"]))
        self.assertEqual((first_view["width_mm"], first_view["height_mm"]), (first_plan["world_size_mm"]["x"], first_plan["world_size_mm"]["y"]))
        self.assertEqual(plan, original)
        self.assertFalse(view["invariants"]["indicative_geometry"])

    def test_rotated_cavity_is_transformed_from_its_local_p55_frame(self) -> None:
        plan = {
            "schema_version": PARTITION_PLAN_SCHEMA_V1,
            "plan_digest": "rotation-test", "project_name": "Rotation",
            "box": {"inner_dimensions_mm": {"x": 100.0, "y": 80.0, "z": 40.0}, "storage_height_mm": 40.0},
            "flat_stack": {"reservation_size_mm": None}, "support": {}, "diagnostics": [],
            "summary": {"status": "constructed", "automatic_body_count": 0},
            "placements": [{
                "id": "container:g", "role": "container", "name": "Bac tourne",
                "origin_mm": {"x": 10.0, "y": 10.0, "z": 0.0},
                "world_size_mm": {"x": 20.0, "y": 30.0, "z": 40.0},
                "rotation_deg_z": 90,
                "final_outer_dimensions_mm": {"x": 30.0, "y": 20.0, "z": 40.0},
                "minimum_outer_envelope_mm": {"x": 10.0, "y": 10.0, "z": 10.0},
                "minimum_envelope_origin_in_final_mm": {"x": 5.0, "y": 3.0, "z": 2.0},
                "surplus_distribution_mm": {}, "source_content_ids": ["c"],
                "cavity_layout": [{"cavity_id": "cavity:c", "content_id": "c", "shape_kind": "rectangle", "local_origin_mm": {"x": 1.0, "y": 2.0, "z": 1.0}, "inner_dimensions_mm": {"x": 4.0, "y": 6.0, "z": 5.0}}],
            }],
        }
        cavity = build_partition_result_view(plan)["top_view"]["cavities"][0]

        self.assertEqual((cavity["x_mm"], cavity["y_mm"]), (19.0, 16.0))
        self.assertEqual((cavity["width_mm"], cavity["height_mm"]), (6.0, 4.0))
        self.assertEqual((cavity["z_mm"], cavity["depth_mm"]), (3.0, 5.0))

    def test_section_is_declared_at_box_center_and_contains_only_crossed_real_bodies(self) -> None:
        plan = solve_partition_plan(project())
        view = build_partition_result_view(plan)
        section = view["section_xz"]

        self.assertEqual(section["section_y_mm"], 75.0)
        expected = [item["id"] for item in plan["placements"] if item["origin_mm"]["y"] <= 75.0 <= item["origin_mm"]["y"] + item["world_size_mm"]["y"]]
        self.assertEqual([item["id"] for item in section["bodies"]], expected)

    def test_flat_stack_is_visible_in_top_and_section_views(self) -> None:
        value = project()
        value["flat_items"] = [{"id": "board", "name": "Plateau", "kind": "board", "dimensions_mm": {"x": 190.0, "y": 140.0, "z": 2.0}, "quantity": 1, "stack_order": 0}]
        view = build_partition_result_view(solve_partition_plan(value))

        self.assertIsNotNone(view["top_view"]["flat_stack_reservation"])
        self.assertIsNotNone(view["section_xz"]["flat_stack_reservation"])
        self.assertEqual(view["support"]["status"], "supported_by_requested_bodies")

    def test_never_draws_an_impossible_or_wrong_schema_plan_as_a_solution(self) -> None:
        impossible = solve_partition_plan(blank_project_v1())
        with self.assertRaisesRegex(PartitionResultViewError, "impossible"):
            build_partition_result_view(impossible)
        with self.assertRaisesRegex(PartitionResultViewError, "bgig.partition_plan.v1"):
            build_partition_result_view({"schema_version": "wrong", "summary": {"status": "constructed"}})


if __name__ == "__main__":
    unittest.main()
