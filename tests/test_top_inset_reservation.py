from __future__ import annotations

from copy import deepcopy
import unittest

from board_game_insert_generator.partition_solver import solve_partition_plan
from board_game_insert_generator.project_v1 import blank_project_v1
from board_game_insert_generator.top_inset_reservation import (
    TOP_INSET_CUT_KIND,
    TOP_INSET_RESERVATION_SCHEMA_V1,
    apply_top_inset_reservations,
    derive_top_inset_reservations,
)


def project() -> dict[str, object]:
    value = blank_project_v1()
    value["box"] = {
        "inner_dimensions_mm": {"x": 240.0, "y": 180.0, "z": 70.0},
        "usable_height_mm": 66.0,
        "lid_clearance_mm": 2.0,
    }
    value["container_groups"] = [
        {"id": "left", "name": "Bac gauche", "wall_thickness_mm": None, "floor_thickness_mm": None},
        {"id": "right", "name": "Bac droit", "wall_thickness_mm": None, "floor_thickness_mm": None},
    ]
    value["contents"] = [
        {
            "id": "tokens", "name": "Jetons", "shape_kind": "square",
            "dimensions_mm": {"x": 18.0, "y": 18.0, "z": 12.0}, "quantity": 4,
            "container_group_id": "left", "content_clearance_mm": None,
            "measurement_confidence": "exact",
        },
        {
            "id": "cards", "name": "Cartes", "shape_kind": "rectangle",
            "dimensions_mm": {"x": 30.0, "y": 20.0, "z": 12.0}, "quantity": 2,
            "container_group_id": "right", "content_clearance_mm": None,
            "measurement_confidence": "exact",
        },
    ]
    return value


def flat(
    item_id: str,
    *,
    x: float = 200.0,
    y: float = 140.0,
    z: float = 3.0,
    order: int | None = None,
    origin: dict[str, float] | None = None,
    rotation: int | None = None,
) -> dict[str, object]:
    return {
        "id": item_id,
        "name": item_id,
        "kind": "board",
        "dimensions_mm": {"x": x, "y": y, "z": z},
        "quantity": 1,
        "stack_order": order,
        "origin_mm": origin,
        "rotation_deg_z": rotation,
    }


class TopInsetReservationTests(unittest.TestCase):
    def test_auto_centres_a_board_and_keeps_the_container_design_height(self) -> None:
        value = project()
        value["flat_items"] = [flat("board")]

        result = derive_top_inset_reservations(value)

        self.assertEqual(result["schema_version"], TOP_INSET_RESERVATION_SCHEMA_V1)
        self.assertEqual(result["status"], "ready_for_intersection")
        self.assertEqual(result["design_top_z_mm"], 66.0)
        reservation = result["reservations"][0]
        self.assertEqual(reservation["placement_source"], "auto_center")
        self.assertEqual(reservation["layer_top_z_mm"], 66.0)
        self.assertEqual(reservation["inset_depth_from_top_mm"], 3.0)
        self.assertEqual(reservation["grip_zone"]["status"], "planned")

    def test_explicit_origins_and_rotations_allow_side_by_side_flat_items(self) -> None:
        value = project()
        value["flat_items"] = [
            flat("left-board", x=70.0, y=120.0, order=0, origin={"x": 5.0, "y": 30.0}),
            flat("right-booklet", x=110.0, y=60.0, order=1, origin={"x": 150.0, "y": 30.0}, rotation=90),
        ]

        result = derive_top_inset_reservations(value)

        self.assertEqual(result["status"], "ready_for_intersection")
        self.assertEqual([item["rotation_deg_z"] for item in result["reservations"]], [0, 90])
        self.assertEqual([item["placement_source"] for item in result["reservations"]], ["explicit_origin", "explicit_origin"])
        self.assertEqual([item["removal_order"] for item in result["reservations"]], [2, 1])
        self.assertEqual(result["total_flat_height_mm"], 3.0)

    def test_solver_intersects_the_inset_across_requested_bodies_without_reducing_all_heights(self) -> None:
        value = project()
        value["flat_items"] = [flat("board", x=220.0, y=160.0, z=3.0)]

        result = solve_partition_plan(value)

        self.assertEqual(result["summary"]["status"], "constructed")
        self.assertEqual(result["box"]["storage_height_mm"], 66.0)
        self.assertTrue(all(item["world_size_mm"]["z"] == 66.0 for item in result["placements"]))
        top = result["top_inset_reservations"]
        self.assertEqual(top["status"], "applied")
        self.assertGreaterEqual(len(top["cuts"]), 2)
        self.assertTrue(all(cut["non_perforating"] for cut in top["cuts"]))
        self.assertEqual(result["support"]["status"], "supported_by_requested_bodies")
        self.assertEqual(
            result["support"]["top_support_count"],
            sum(cut["kind"] == TOP_INSET_CUT_KIND for cut in top["cuts"]),
        )
        self.assertEqual(result["summary"]["automatic_body_count"], 0)

    def test_rejects_an_inset_that_would_cut_below_an_intersected_cavity_floor(self) -> None:
        value = project()
        value["flat_items"] = [flat("too-deep", x=220.0, y=160.0, z=30.0)]

        result = solve_partition_plan(value)

        self.assertEqual(result["summary"]["status"], "impossible")
        self.assertIn("TOP_INSET_PIERCES_CAVITY_FLOOR", {item["code"] for item in result["diagnostics"]})
        self.assertEqual(result["summary"]["automatic_body_count"], 0)

    def test_rejects_a_cut_that_would_leave_less_than_the_minimum_body_floor(self) -> None:
        value = project()
        value["contents"][0]["dimensions_mm"] = {"x": 18.0, "y": 18.0, "z": 1.0}
        value["contents"][1]["dimensions_mm"] = {"x": 30.0, "y": 20.0, "z": 1.0}
        value["flat_items"] = [flat("almost-through", x=220.0, y=160.0, z=65.5)]

        result = solve_partition_plan(value)

        self.assertEqual(result["summary"]["status"], "impossible")
        self.assertIn("TOP_INSET_PIERCES_BODY_FLOOR", {item["code"] for item in result["diagnostics"]})

    def test_application_does_not_mutate_the_source_placements_and_is_deterministic(self) -> None:
        value = project()
        value["flat_items"] = [flat("board", x=80.0, y=60.0, z=2.0, origin={"x": 10.0, "y": 10.0})]
        base = solve_partition_plan({**value, "flat_items": []})["placements"]
        original = deepcopy(base)

        first = apply_top_inset_reservations(value, base)
        second = apply_top_inset_reservations(value, base)

        self.assertEqual(base, original)
        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
