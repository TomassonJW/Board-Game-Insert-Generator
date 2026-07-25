from __future__ import annotations

import unittest

from board_game_insert_generator.free_3d_greedy_solver import (
    Free3DPlacement,
    TopInsetZone,
)
from board_game_insert_generator.solver_contract import SolverBudget
from board_game_insert_generator.xy_composite_closure import (
    close_xy_composite_partition,
    xy_composite_closure_to_dict,
)


def _budget() -> SolverBudget:
    return SolverBudget(
        "xy-composite-test",
        "normal",
        tuple(
            sorted(
                {
                    "max_closure_candidates": 20_000,
                    "max_closure_elapsed_ms": 5_000,
                }.items()
            )
        ),
    )


def _participant() -> dict[str, object]:
    return {
        "id": "container:a",
        "role": "container",
        "dimension_modes": {"x": "auto", "y": "auto", "z": "auto"},
    }


def _placement() -> Free3DPlacement:
    return Free3DPlacement(
        "container:a",
        "container",
        "a",
        (40.0, 30.0, 0.0),
        (20.0, 20.0, 20.0),
        (20.0, 20.0, 20.0),
        0,
        ("box-floor",),
        1.0,
    )


def _zone(*, support_plane_z_mm: float, inset_depth_mm: float) -> TopInsetZone:
    return TopInsetZone(
        origin_xy_mm=(0.0, 0.0),
        size_xy_mm=(30.0, 20.0),
        support_plane_z_mm=support_plane_z_mm,
        inset_depth_mm=inset_depth_mm,
    )


class XYCompositeClosureTests(unittest.TestCase):
    def test_corner_top_reservation_closes_exactly_with_xy_annexes(self) -> None:
        result = close_xy_composite_partition(
            (_participant(),),
            (_placement(),),
            {"x": 100.0, "y": 80.0, "z": 40.0},
            40.0,
            0.0,
            box_perimeter_xy_mm=0.0,
            between_bodies_z_mm=0.0,
            budget=_budget(),
            top_inset_zones=(
                _zone(support_plane_z_mm=30.0, inset_depth_mm=10.0),
            ),
        )

        self.assertEqual(result.status, "closed")
        self.assertEqual(result.stop_reason, "xy_composite_partition_complete")
        self.assertTrue(result.certificate["certified"])
        self.assertEqual(
            result.certificate["printable_residual_volume_mm3"],
            0.0,
        )
        self.assertEqual(
            result.certificate["reserved_subtraction_volume_mm3"],
            6_000.0,
        )
        self.assertEqual(
            result.certificate["composite_body_volume_mm3"],
            314_000.0,
        )
        self.assertTrue(result.certificate["partition_complete_by_construction"])
        self.assertEqual(len(result.owner_bodies), 1)
        self.assertGreater(
            result.owner_bodies[0].certificate["annex_count"],
            0,
        )

    def test_every_annex_has_one_owner_common_bottom_and_true_xy_face(self) -> None:
        result = close_xy_composite_partition(
            (_participant(),),
            (_placement(),),
            {"x": 100.0, "y": 80.0, "z": 40.0},
            40.0,
            0.0,
            box_perimeter_xy_mm=0.0,
            between_bodies_z_mm=0.0,
            budget=_budget(),
            top_inset_zones=(
                _zone(support_plane_z_mm=30.0, inset_depth_mm=10.0),
            ),
        )

        owner = result.owner_bodies[0]
        by_id = {value.prism_id: value for value in owner.prisms}
        self.assertTrue(owner.certificate["unique_owner"])
        self.assertTrue(owner.certificate["common_lower_z"])
        self.assertTrue(
            owner.certificate["minimum_envelope_contained_by_union"]
        )
        self.assertTrue(
            owner.certificate["all_annexes_connected_by_vertical_xy_faces"]
        )
        self.assertEqual(owner.certificate["z_only_attachment_count"], 0)
        self.assertEqual(owner.certificate["edge_or_point_attachment_count"], 0)
        for prism in owner.prisms:
            self.assertEqual(prism.owner_id, owner.owner_id)
            self.assertEqual(prism.origin_mm[2], owner.base_z_mm)
            if prism.kind == "core":
                self.assertEqual(prism.attached_to_prism_id, "")
                self.assertEqual(prism.attachment_axis, "")
                continue
            self.assertIn(prism.attached_to_prism_id, by_id)
            self.assertIn(prism.attachment_axis, {"x", "y"})

        payload = xy_composite_closure_to_dict(result)
        self.assertEqual(payload["certificate"]["z_only_attachment_count"], 0)
        self.assertEqual(
            payload["certificate"]["edge_or_point_attachment_count"],
            0,
        )

    def test_non_top_open_reservation_is_rejected(self) -> None:
        result = close_xy_composite_partition(
            (_participant(),),
            (_placement(),),
            {"x": 100.0, "y": 80.0, "z": 40.0},
            40.0,
            0.0,
            box_perimeter_xy_mm=0.0,
            between_bodies_z_mm=0.0,
            budget=_budget(),
            top_inset_zones=(
                _zone(support_plane_z_mm=20.0, inset_depth_mm=10.0),
            ),
        )

        self.assertEqual(result.status, "not_closed")
        self.assertEqual(
            result.stop_reason,
            "xy_composite_reservation_not_top_open",
        )
        self.assertFalse(result.certificate["certified"])
        self.assertFalse(result.owner_bodies)


if __name__ == "__main__":
    unittest.main()
