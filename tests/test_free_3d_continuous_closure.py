from __future__ import annotations

import unittest

from board_game_insert_generator.free_3d_continuous_closure import (
    close_free_3d_residual,
)
from board_game_insert_generator.free_3d_greedy_solver import (
    FREE_3D_GREEDY_FAMILY_ID,
    Free3DPlacement,
    TopInsetZone,
    solve_free_3d_greedy,
)
from board_game_insert_generator.solver_contract import SolverBudget


def _budget() -> SolverBudget:
    return SolverBudget(
        FREE_3D_GREEDY_FAMILY_ID,
        "closure-test",
        tuple(
            sorted(
                {
                    "max_empty_spaces": 512,
                    "max_extreme_points": 512,
                    "max_placement_trials": 20_000,
                    "max_search_states": 256,
                }.items()
            )
        ),
    )


def _participant(
    identifier: str,
    size: tuple[float, float, float],
    *,
    x_mode: str = "auto",
) -> dict[str, object]:
    dimensions = dict(zip(("x", "y", "z"), size))
    return {
        "id": identifier,
        "role": "container",
        "name": identifier,
        "minimum_local_mm": dimensions,
        "dimension_modes": {"x": x_mode, "y": "auto", "z": "auto"},
        "target_local_mm": {
            "x": size[0] if x_mode == "fixed" else None,
            "y": None,
            "z": None,
        },
    }


class Free3DContinuousClosureTests(unittest.TestCase):
    def test_closure_absorbs_residual_without_body_or_fixed_axis_mutation(self) -> None:
        participants = (
            _participant("fixed", (20.0, 40.0, 20.0), x_mode="fixed"),
            _participant("auto", (20.0, 40.0, 20.0)),
        )
        placements = (
            Free3DPlacement(
                "fixed",
                "container",
                "fixed",
                (0.0, 0.0, 0.0),
                (20.0, 40.0, 20.0),
                (20.0, 40.0, 20.0),
                0,
                ("box-floor",),
                1.0,
            ),
            Free3DPlacement(
                "auto",
                "container",
                "auto",
                (20.0, 0.0, 0.0),
                (20.0, 40.0, 20.0),
                (20.0, 40.0, 20.0),
                0,
                ("box-floor",),
                1.0,
            ),
        )

        result = close_free_3d_residual(
            participants,
            placements,
            {"x": 100.0, "y": 40.0, "z": 20.0},
            20.0,
            0.0,
            box_perimeter_xy_mm=0.0,
            between_bodies_z_mm=0.0,
            budget=_budget(),
        )

        self.assertEqual(result.status, "closed")
        self.assertFalse(result.empty_spaces)
        self.assertEqual(len(result.placements), 2)
        by_id = {value.participant_id: value for value in result.placements}
        self.assertEqual(by_id["fixed"].world_size_mm[0], 20.0)
        self.assertEqual(by_id["auto"].world_size_mm[0], 80.0)
        self.assertGreater(result.aligned_face_count, 0)

    def test_top_inset_constraint_routes_incompatible_tall_body_outside_footprint(self) -> None:
        participants = (
            _participant("tall", (50.0, 60.0, 35.0)),
            _participant("short", (60.0, 60.0, 10.0)),
        )
        execution = solve_free_3d_greedy(
            participants,
            {"x": 120.0, "y": 60.0, "z": 40.0},
            40.0,
            0.0,
            box_perimeter_xy_mm=0.0,
            between_bodies_z_mm=0.0,
            budget=_budget(),
            top_inset_zones=(
                TopInsetZone(
                    origin_xy_mm=(0.0, 0.0),
                    size_xy_mm=(60.0, 60.0),
                    support_plane_z_mm=30.0,
                    inset_depth_mm=10.0,
                ),
            ),
        )

        self.assertEqual(execution.status, "solution_found")
        by_id = {value.participant_id: value for value in execution.placements}
        self.assertGreaterEqual(by_id["tall"].origin_mm[0], 60.0)
        self.assertEqual(by_id["short"].origin_mm[0], 0.0)


if __name__ == "__main__":
    unittest.main()