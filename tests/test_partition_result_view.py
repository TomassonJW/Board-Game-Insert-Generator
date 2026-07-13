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


def tight_multistage_project() -> dict[str, object]:
    value = blank_project_v1()
    value["box"] = {"inner_dimensions_mm": {"x": 50.0, "y": 25.0, "z": 50.0}, "usable_height_mm": 50.0, "lid_clearance_mm": 0.0}
    value["container_groups"] = [
        {"id": f"g{index}", "name": f"Bac {index}", "wall_thickness_mm": None, "floor_thickness_mm": None}
        for index in range(4)
    ]
    value["contents"] = [
        {"id": f"c{index}", "name": f"Pieces {index}", "shape_kind": "square", "dimensions_mm": {"x": 18.0, "y": 18.0, "z": 5.0}, "quantity": 4, "container_group_id": f"g{index}", "content_clearance_mm": None, "measurement_confidence": "exact"}
        for index in range(4)
    ]
    return value


def fixed_residual_project() -> dict[str, object]:
    value = project()
    value["container_groups"] = [value["container_groups"][0]]
    value["contents"] = [value["contents"][0]]
    minimum = solve_partition_plan(value)["placements"][0]["minimum_outer_envelope_mm"]
    group = value["container_groups"][0]
    group["expansion_axes"] = {"x": False, "y": False, "z": False}
    group["locked_outer_dimensions_mm"] = minimum
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
        self.assertEqual(len(view["top_view"]["top_inset_reservations"]), 1)
        self.assertEqual(len(view["section_xz"]["top_inset_reservations"]), 1)
        self.assertEqual(view["top_view"]["top_inset_reservations"][0]["depth_mm"], 2.0)
        self.assertEqual(view["support"]["status"], "supported_by_requested_bodies")
        self.assertTrue(view["invariants"]["localized_top_insets"])

    def test_p64_exposes_real_stages_support_and_removal_in_the_read_only_view(self) -> None:
        plan = solve_partition_plan(tight_multistage_project())
        view = build_partition_result_view(plan)

        self.assertEqual(plan["summary"]["status"], "constructed")
        self.assertEqual(view["status"], "constructed")
        self.assertTrue(view["materializable"])
        self.assertEqual(len(view["stages"]), 2)
        self.assertEqual({body["z_mm"] for body in view["top_view"]["bodies"]}, {0.0, 25.0})
        self.assertEqual({body["stage_id"] for body in view["top_view"]["bodies"]}, {"stage-1", "stage-2"})
        self.assertEqual(view["stage_support"]["status"], "supported")
        self.assertEqual(view["removal_sequence"][0]["stage_id"], "stage-2")
        self.assertTrue(view["invariants"]["stage_aware"])

    def test_p64_draws_residuals_but_never_marks_a_partial_proposal_materializable(self) -> None:
        plan = solve_partition_plan(fixed_residual_project())
        view = build_partition_result_view(plan)

        self.assertEqual(plan["summary"]["status"], "proposal_with_residuals")
        self.assertEqual(view["status"], "proposal_with_residuals")
        self.assertFalse(view["materializable"])
        self.assertTrue(view["top_view"]["residuals"])
        self.assertTrue(view["residuals"]["zones"])
        self.assertTrue(view["suggestions"])
        self.assertTrue(view["invariants"]["residuals_are_non_printable"])
        self.assertTrue(view["invariants"]["partial_never_materializable"])

    def test_never_draws_an_impossible_or_wrong_schema_plan_as_a_solution(self) -> None:
        impossible = solve_partition_plan(blank_project_v1())
        with self.assertRaisesRegex(PartitionResultViewError, "impossible"):
            build_partition_result_view(impossible)
        with self.assertRaisesRegex(PartitionResultViewError, "bgig.partition_plan.v1"):
            build_partition_result_view({"schema_version": "wrong", "summary": {"status": "constructed"}})


if __name__ == "__main__":
    unittest.main()
