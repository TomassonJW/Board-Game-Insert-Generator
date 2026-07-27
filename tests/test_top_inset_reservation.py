from __future__ import annotations

from copy import deepcopy
import unittest

from board_game_insert_generator.partition_solver import solve_partition_plan
from board_game_insert_generator.project_v1 import blank_project_v1
from board_game_insert_generator.top_inset_reservation import (
    TOP_INSET_CUT_KIND,
    TOP_INSET_RESERVATION_SCHEMA_V1,
    apply_top_inset_reservations,
    certify_top_inset_reservation_prisms,
    derive_top_inset_reservations,
    resolve_top_inset_reservations,
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
    def test_upright_cavity_keeps_its_calibrated_depth_before_tray_cut(self) -> None:
        value = project()
        value["flat_items"] = [
            flat("board", x=220.0, y=160.0, z=4.0)
        ]

        result = solve_partition_plan(value)

        self.assertEqual(result["summary"]["status"], "constructed")
        self.assertEqual(
            result["top_inset_reservations"][
                "cavity_depth_compensations"
            ],
            [],
        )
        self.assertTrue(
            result["invariants"]["cavity_calibrated_depths_unchanged"]
        )
        for placement in result["placements"]:
            for cavity in placement.get("cavity_layout", []):
                self.assertNotIn("top_inset_compensation_mm", cavity)
                self.assertNotIn("depth_semantics", cavity)

    def test_automatic_xy_places_a_board_and_keeps_the_container_design_height(self) -> None:
        value = project()
        value["flat_items"] = [flat("board")]

        result = derive_top_inset_reservations(value)

        self.assertEqual(result["schema_version"], TOP_INSET_RESERVATION_SCHEMA_V1)
        self.assertEqual(result["status"], "ready_for_intersection")
        self.assertEqual(result["design_top_z_mm"], 66.0)
        reservation = result["reservations"][0]
        self.assertEqual(reservation["placement_source"], "automatic_xy")
        self.assertEqual(reservation["layer_top_z_mm"], 66.0)
        self.assertEqual(reservation["inset_depth_from_top_mm"], 3.0)
        self.assertEqual(reservation["grip_zone"]["status"], "planned")

    def test_historical_origins_migrate_and_joint_search_places_flats_side_by_side(self) -> None:
        value = project()
        value["flat_items"] = [
            flat("left-board", x=70.0, y=120.0, order=0, origin={"x": 5.0, "y": 30.0}),
            flat("right-booklet", x=110.0, y=60.0, order=1, origin={"x": 150.0, "y": 30.0}, rotation=90),
        ]

        result = derive_top_inset_reservations(value)

        self.assertEqual(result["status"], "ready_for_intersection")
        self.assertEqual([item["rotation_deg_z"] for item in result["reservations"]], [0, 90])
        self.assertTrue(result["source"]["migrated"])
        self.assertEqual([item["placement_source"] for item in result["reservations"]], ["automatic_xy", "automatic_xy"])
        self.assertEqual([item["removal_order"] for item in result["reservations"]], [2, 1])
        self.assertEqual(result["total_flat_height_mm"], 3.0)

    def test_center_collision_is_replaced_by_a_lateral_automatic_pose(self) -> None:
        value = project()
        value["box"] = {
            "inner_dimensions_mm": {"x": 100.0, "y": 60.0, "z": 12.0},
            "usable_height_mm": 10.0,
            "lid_clearance_mm": 2.0,
        }
        value["flat_items"] = [flat("board", x=30.0, y=20.0, z=2.0)]
        preview = derive_top_inset_reservations(value)
        preview_origin = deepcopy(preview["reservations"][0]["cut_origin_mm"])
        placements = [
            {
                "id": "container:blocker",
                "origin_mm": {"x": 35.0, "y": 20.0, "z": 0.0},
                "world_size_mm": {"x": 30.0, "y": 20.0, "z": 9.0},
            }
        ]

        result = resolve_top_inset_reservations(value, placements)

        self.assertEqual(result["status"], "ready_for_intersection")
        self.assertNotEqual(result["reservations"][0]["cut_origin_mm"], preview_origin)
        self.assertEqual(
            result["automatic_xy_search"]["placement_context"],
            "frozen_bodies",
        )

    def test_no_admissible_xy_pose_returns_an_honest_blocker_without_moving_body(self) -> None:
        value = project()
        value["box"] = {
            "inner_dimensions_mm": {"x": 60.0, "y": 40.0, "z": 12.0},
            "usable_height_mm": 10.0,
            "lid_clearance_mm": 2.0,
        }
        value["flat_items"] = [flat("board", x=30.0, y=20.0, z=2.0)]
        placements = [
            {
                "id": "container:blocker",
                "origin_mm": {"x": 0.0, "y": 0.0, "z": 0.0},
                "world_size_mm": {"x": 60.0, "y": 40.0, "z": 9.0},
            }
        ]
        original = deepcopy(placements)

        result = resolve_top_inset_reservations(value, placements)

        self.assertEqual(result["status"], "blocked")
        self.assertIn(
            "TOP_INSET_AUTOMATIC_PLACEMENT_NOT_FOUND",
            {item["code"] for item in result["blockers"]},
        )
        self.assertEqual(placements, original)

    def test_near_cavity_uses_existing_wall_thickness_and_keeps_cavity_frozen(self) -> None:
        value = project()
        value["box"] = {
            "inner_dimensions_mm": {"x": 100.0, "y": 60.0, "z": 12.0},
            "usable_height_mm": 10.0,
            "lid_clearance_mm": 2.0,
        }
        value["container_groups"] = [
            {
                "id": "owner",
                "name": "Bac",
                "wall_thickness_mm": 2.0,
                "floor_thickness_mm": 1.2,
            }
        ]
        value["contents"] = []
        value["flat_items"] = [flat("booklet", x=20.0, y=20.0, z=1.0)]
        placements = [
            {
                "id": "container:owner",
                "container_group_id": "owner",
                "origin_mm": {"x": 0.0, "y": 0.0, "z": 0.0},
                "world_size_mm": {"x": 100.0, "y": 60.0, "z": 10.0},
                "final_outer_dimensions_mm": {"x": 100.0, "y": 60.0, "z": 10.0},
                "minimum_envelope_origin_in_final_mm": {"x": 0.0, "y": 0.0, "z": 0.0},
                "rotation_deg_z": 0,
                "cavity_layout": [
                    {
                        "cavity_id": "cavity:owner",
                        "local_origin_mm": {"x": 61.1, "y": 20.0, "z": 1.2},
                        "inner_dimensions_mm": {"x": 20.0, "y": 20.0, "z": 2.0},
                    }
                ],
            }
        ]
        original = deepcopy(placements)

        result = resolve_top_inset_reservations(
            value,
            placements,
            require_reserved_prisms=False,
        )

        self.assertEqual(result["status"], "ready_for_intersection")
        reservation = result["reservations"][0]
        self.assertTrue(reservation["wall_envelope_certificate"]["certified"])
        self.assertGreater(result["automatic_xy_search"]["wall_rejection_count"], 0)
        self.assertEqual(placements, original)

    def test_large_overlapping_flats_keep_deterministic_vertical_order(self) -> None:
        value = project()
        value["flat_items"] = [
            flat("lower", x=220.0, y=160.0, z=2.0, order=0),
            flat("upper", x=220.0, y=160.0, z=3.0, order=1),
        ]

        first = derive_top_inset_reservations(value)
        second = derive_top_inset_reservations(value)

        self.assertEqual(first, second)
        self.assertEqual(
            [item["inset_depth_from_top_mm"] for item in first["reservations"]],
            [5.0, 3.0],
        )
        self.assertEqual(
            [item["removal_order"] for item in first["reservations"]],
            [2, 1],
        )

    def test_disjoint_flats_never_accumulate_their_depths(self) -> None:
        value = project()
        value["flat_items"] = [
            flat("left-flat", x=70.0, y=60.0, z=2.0, order=0),
            flat("right-flat", x=70.0, y=60.0, z=3.0, order=1),
        ]

        result = derive_top_inset_reservations(value)

        depths = [
            {
                region["inset_depth_from_top_mm"]
                for region in reservation["local_depth_regions"]
            }
            for reservation in result["reservations"]
        ]
        self.assertEqual(depths, [{2.0}, {3.0}])
        self.assertEqual(result["total_flat_height_mm"], 3.0)

    def test_partial_overlap_accumulates_only_inside_the_intersection(self) -> None:
        value = project()
        value["box"] = {
            "inner_dimensions_mm": {"x": 140.0, "y": 100.0, "z": 40.0},
            "usable_height_mm": 40.0,
            "lid_clearance_mm": 0.0,
        }
        value["flat_items"] = [
            flat("lower", x=110.0, y=80.0, z=2.0, order=0),
            flat("upper", x=60.0, y=50.0, z=3.0, order=1),
        ]

        result = derive_top_inset_reservations(value)
        lower = result["reservations"][0]
        lower_depths = {
            region["inset_depth_from_top_mm"]
            for region in lower["local_depth_regions"]
        }

        self.assertEqual(lower_depths, {2.0, 5.0})
        self.assertTrue(
            any(
                region["overlap_count"] == 1
                and region["inset_depth_from_top_mm"] == 2.0
                for region in lower["local_depth_regions"]
            )
        )
        self.assertTrue(
            any(
                region["overlap_count"] == 2
                and region["inset_depth_from_top_mm"] == 5.0
                for region in lower["local_depth_regions"]
            )
        )

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

    def test_p64_applies_a_top_inset_only_to_intersected_upper_stage_bodies(self) -> None:
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
        value["flat_items"] = [flat("board", x=25.0, y=20.0, z=2.0, origin={"x": 1.0, "y": 1.0})]

        result = solve_partition_plan(value)
        lower = [item for item in result["placements"] if item["stage_id"] == "stage-1"]
        upper = [item for item in result["placements"] if item["stage_id"] == "stage-2"]

        self.assertEqual(result["summary"]["status"], "constructed")
        self.assertEqual(result["summary"]["stage_count"], 2)
        self.assertEqual(result["top_inset_reservations"]["status"], "applied")
        self.assertTrue(all(not item.get("top_inset_cuts") for item in lower))
        self.assertTrue(any(item.get("top_inset_cuts") for item in upper))
        self.assertEqual(result["stage_support"]["status"], "supported")

    def test_overlapping_boards_preserve_asset_depth_without_compensation(self) -> None:
        value = project()
        value["flat_items"] = [
            flat("lower-board", x=220.0, y=160.0, z=2.0, order=0),
            flat("upper-board", x=220.0, y=160.0, z=3.0, order=1),
        ]

        result = solve_partition_plan(value)
        compensations = result["top_inset_reservations"]["cavity_depth_compensations"]

        self.assertEqual(result["summary"]["status"], "constructed")
        self.assertEqual(compensations, [])
        self.assertTrue(result["invariants"]["fixed_cavity_layouts"])
        self.assertTrue(result["invariants"]["base_cavity_layouts_fixed"])
        self.assertFalse(result["invariants"]["top_inset_cavity_depth_compensated"])
        self.assertTrue(
            result["invariants"]["cavity_z_anchor_deferred_to_finalization"]
        )
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


    def test_recent_limit_case_keeps_31_6_mm_body_and_allows_gap_under_tray(self) -> None:
        value = project()
        value["box"] = {
            "inner_dimensions_mm": {"x": 200.0, "y": 150.0, "z": 60.0},
            "usable_height_mm": 59.6,
            "lid_clearance_mm": 0.4,
        }
        value["flat_items"] = [
            flat(
                "tray",
                x=100.0,
                y=80.0,
                z=1.0,
                origin={"x": 10.0, "y": 10.0},
            )
        ]
        placements = [
            {
                "id": "container:018",
                "name": "Conteneur limite",
                "origin_mm": {"x": 20.0, "y": 20.0, "z": 21.2},
                "world_size_mm": {"x": 23.2, "y": 23.2, "z": 31.6},
            }
        ]

        result = certify_top_inset_reservation_prisms(value, placements)

        self.assertEqual(result["status"], "reserved_prisms_certified")
        self.assertEqual(result["placements"][0]["world_size_mm"]["z"], 31.6)
        self.assertNotEqual(result["placements"][0]["world_size_mm"]["z"], 38.4)
        support_plane = result["reserved_prisms"][0]["origin_mm"]["z"]
        body_top = 21.2 + result["placements"][0]["world_size_mm"]["z"]
        self.assertAlmostEqual(support_plane - body_top, 5.8)
        self.assertTrue(result["reservation_certificates"][0]["certified"])
        self.assertEqual(
            result["support"]["status"],
            "not_required_for_minimal_layout",
        )


if __name__ == "__main__":
    unittest.main()
