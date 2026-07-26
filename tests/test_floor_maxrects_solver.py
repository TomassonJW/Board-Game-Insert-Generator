from __future__ import annotations

import unittest

from board_game_insert_generator.floor_maxrects_solver import solve_floor_maxrects
from board_game_insert_generator.free_3d_greedy_solver import TopInsetZone
from board_game_insert_generator.solver_contract import validate_placement_geometry


RECENT_DENSE_DIMENSIONS = (
    (23.6, 23.6, 11.8),
    *((92.5, 22.8, 65.3),) * 5,
    *((19.6, 36.2, 49.8),) * 2,
    *((23.6, 23.6, 31.8),) * 2,
    (76.0, 76.0, 31.8),
    *((23.6, 23.6, 31.8),) * 7,
    *((23.6, 23.6, 11.8),) * 10,
)


def _participant(index: int, dimensions: tuple[float, float, float]) -> dict[str, object]:
    minimum = dict(zip(("x", "y", "z"), dimensions))
    return {
        "id": f"container-{index:03d}",
        "role": "container",
        "name": f"container-{index:03d}",
        "minimum_local_mm": minimum,
        "dimension_modes": {"x": "fixed", "y": "fixed", "z": "fixed"},
        "target_local_mm": minimum,
    }


class FloorMaxRectsSolverTests(unittest.TestCase):
    def test_recent_dense_floor_case_preserves_all_28_minimum_envelopes(self) -> None:
        participants = tuple(
            _participant(index, dimensions)
            for index, dimensions in enumerate(RECENT_DENSE_DIMENSIONS, start=1)
        )

        first = solve_floor_maxrects(
            participants,
            {"x": 220.0, "y": 170.0, "z": 70.0},
            70.0,
            0.6,
            box_perimeter_xy_mm=0.6,
        )
        second = solve_floor_maxrects(
            participants,
            {"x": 220.0, "y": 170.0, "z": 70.0},
            70.0,
            0.6,
            box_perimeter_xy_mm=0.6,
        )

        self.assertEqual(len(participants), 28)
        self.assertEqual(first.status, "solution_found")
        self.assertEqual(len(first.placements), 28)
        self.assertTrue(all(value.origin_mm[2] == 0.0 for value in first.placements))
        by_id = {value.participant_id: value for value in first.placements}
        for participant in participants:
            placement = by_id[str(participant["id"])]
            minimum = participant["minimum_local_mm"]
            self.assertEqual(
                placement.local_size_mm,
                tuple(float(minimum[axis]) for axis in ("x", "y", "z")),
            )
        geometry = validate_placement_geometry(
            [
                {
                    "id": value.participant_id,
                    "role": value.role,
                    "origin_mm": dict(zip(("x", "y", "z"), value.origin_mm)),
                    "world_size_mm": dict(zip(("x", "y", "z"), value.world_size_mm)),
                    "rotation_deg_z": value.rotation_deg_z,
                }
                for value in first.placements
            ],
            {"x": 220.0, "y": 170.0, "z": 70.0},
            70.0,
            0.6,
            0.6,
            0.6,
        )
        self.assertTrue(geometry["inside_box"])
        self.assertTrue(geometry["no_collisions"])
        self.assertTrue(geometry["clearances_respected"])
        self.assertEqual(first.deterministic_digest, second.deterministic_digest)

    def test_full_footprint_top_reservation_rejects_an_overheight_floor_body(self) -> None:
        result = solve_floor_maxrects(
            (_participant(1, (80.0, 60.0, 35.0)),),
            {"x": 100.0, "y": 80.0, "z": 40.0},
            40.0,
            0.0,
            box_perimeter_xy_mm=0.0,
            top_inset_zones=(
                TopInsetZone(
                    origin_xy_mm=(0.0, 0.0),
                    size_xy_mm=(100.0, 80.0),
                    support_plane_z_mm=30.0,
                    inset_depth_mm=10.0,
                ),
            ),
        )

        self.assertEqual(result.status, "no_solution_within_budget")
        self.assertFalse(result.placements)


if __name__ == "__main__":
    unittest.main()