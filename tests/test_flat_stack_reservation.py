from __future__ import annotations

import unittest

from board_game_insert_generator.container_derivation import derive_container_plan
from board_game_insert_generator.flat_stack_reservation import (
    FLAT_STACK_RESERVATION_SCHEMA_V1,
    derive_flat_stack_reservation,
)
from board_game_insert_generator.project_v1 import blank_project_v1


def _project() -> dict[str, object]:
    project = blank_project_v1()
    project["container_groups"] = [
        {"id": "tokens", "name": "Jetons", "wall_thickness_mm": None, "floor_thickness_mm": None}
    ]
    project["contents"] = [
        {
            "id": "tokens",
            "name": "Jetons",
            "shape_kind": "round",
            "dimensions_mm": {"x": 10.0, "y": 10.0, "z": 5.0},
            "quantity": 12,
            "container_group_id": "tokens",
            "content_clearance_mm": None,
            "measurement_confidence": "exact",
        }
    ]
    return project


def _flat_item(
    item_id: str,
    *,
    kind: str = "rulebook",
    x: float = 100.0,
    y: float = 80.0,
    z: float = 2.0,
    quantity: int = 1,
    stack_order: int | None = None,
) -> dict[str, object]:
    return {
        "id": item_id,
        "name": item_id,
        "kind": kind,
        "dimensions_mm": {"x": x, "y": y, "z": z},
        "quantity": quantity,
        "stack_order": stack_order,
    }


class FlatStackReservationTests(unittest.TestCase):
    def test_reserves_flat_stack_and_reduces_storage_height_for_containers(self) -> None:
        project = _project()
        project["layout"]["layout_clearance_mm"] = 0.5
        project["flat_items"] = [_flat_item("rules", quantity=2)]
        before = derive_container_plan(project)

        result = derive_flat_stack_reservation(project)

        self.assertEqual(result["schema_version"], FLAT_STACK_RESERVATION_SCHEMA_V1)
        self.assertEqual(result["summary"]["status"], "ready_for_p41")
        stack = result["flat_stack"]
        self.assertEqual(stack["reservation_size_mm"], {"x": 101.0, "y": 81.0, "z": 4.5})
        self.assertEqual(stack["storage_height_mm"], 51.5)
        self.assertEqual(stack["items"][0]["stack_origin_z_mm"], 52.0)
        self.assertLessEqual(
            result["container_plan"]["containers"][0]["outer_dimensions_mm"]["z"],
            stack["storage_height_mm"],
        )
        self.assertGreaterEqual(
            result["container_plan"]["containers"][0]["compartments"][0]["quantity"]["pile_count"],
            before["containers"][0]["compartments"][0]["quantity"]["pile_count"],
        )

    def test_recalculates_pile_count_under_the_height_left_by_flat_items(self) -> None:
        project = _project()
        before = derive_container_plan(project)
        project["flat_items"] = [_flat_item("thick-board", z=30.0)]

        result = derive_flat_stack_reservation(project)

        before_piles = before["containers"][0]["compartments"][0]["quantity"]["pile_count"]
        after_container = result["container_plan"]["containers"][0]
        after_piles = after_container["compartments"][0]["quantity"]["pile_count"]
        self.assertGreater(after_piles, before_piles)
        self.assertLessEqual(after_container["outer_dimensions_mm"]["z"], result["flat_stack"]["storage_height_mm"])

    def test_explicit_stack_order_precedes_unspecified_items(self) -> None:
        project = _project()
        project["flat_items"] = [
            _flat_item("board", kind="board", stack_order=None),
            _flat_item("rules", stack_order=0),
        ]

        result = derive_flat_stack_reservation(project)

        self.assertEqual([item["id"] for item in result["flat_stack"]["items"]], ["rules", "board"])

    def test_rejects_a_stack_that_exceeds_the_usable_height(self) -> None:
        project = _project()
        project["flat_items"] = [_flat_item("too-tall", z=30.0, quantity=2)]

        result = derive_flat_stack_reservation(project)

        self.assertEqual(result["summary"]["status"], "blocked")
        self.assertEqual(result["flat_stack"]["status"], "blocked")
        self.assertTrue(any("height" in blocker for blocker in result["blockers"]))

    def test_rejects_a_flat_footprint_that_exceeds_the_box(self) -> None:
        project = _project()
        project["flat_items"] = [_flat_item("too-wide", x=250.0)]

        result = derive_flat_stack_reservation(project)

        self.assertEqual(result["summary"]["status"], "blocked")
        self.assertTrue(any("width" in blocker for blocker in result["blockers"]))

    def test_reports_support_extension_without_claiming_final_support(self) -> None:
        project = _project()
        project["flat_items"] = [_flat_item("large-board", x=100.0, y=80.0)]

        result = derive_flat_stack_reservation(project)

        support = result["support_requirement"]
        self.assertEqual(support["status"], "support_extension_required")
        self.assertLess(support["candidate_container_top_area_mm2"], support["required_area_mm2"])

    def test_reports_area_budget_as_pending_global_placement_not_a_physical_guarantee(self) -> None:
        project = _project()
        project["contents"][0]["dimensions_mm"] = {"x": 30.0, "y": 30.0, "z": 5.0}
        project["flat_items"] = [_flat_item("small-rules", x=10.0, y=10.0)]

        result = derive_flat_stack_reservation(project)

        support = result["support_requirement"]
        self.assertEqual(support["status"], "area_budget_sufficient_pending_placement")
        self.assertIn("P41", support["note"])

    def test_no_flat_item_leaves_full_height_and_no_support_requirement(self) -> None:
        result = derive_flat_stack_reservation(_project())

        self.assertEqual(result["summary"]["status"], "ready_for_p41")
        self.assertEqual(result["flat_stack"]["status"], "not_required")
        self.assertEqual(result["flat_stack"]["storage_height_mm"], 56.0)
        self.assertEqual(result["support_requirement"]["status"], "not_required")


if __name__ == "__main__":
    unittest.main()
