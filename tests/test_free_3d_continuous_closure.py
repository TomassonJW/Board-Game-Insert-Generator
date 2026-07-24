from __future__ import annotations

import unittest

from board_game_insert_generator.free_3d_continuous_closure import (
    FINISHING_OBJECTIVE_BALANCED_ADDED_VOLUME,
    FINISHING_OBJECTIVE_PROPORTIONAL_EXPANSION,
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


def _placement(
    identifier: str,
    origin_x: float,
    size_x: float,
) -> Free3DPlacement:
    return Free3DPlacement(
        identifier,
        "container",
        identifier,
        (origin_x, 0.0, 0.0),
        (size_x, 40.0, 20.0),
        (size_x, 40.0, 20.0),
        0,
        ("box-floor",),
        1.0,
    )


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

    def test_local_repair_moves_one_incumbent_before_growth_closes_volume(self) -> None:
        participants = (
            _participant("fixed", (20.0, 40.0, 20.0), x_mode="fixed"),
            _participant("auto", (20.0, 40.0, 20.0)),
        )
        placements = (
            Free3DPlacement(
                "auto",
                "container",
                "auto",
                (0.0, 0.0, 0.0),
                (20.0, 40.0, 20.0),
                (20.0, 40.0, 20.0),
                0,
                ("box-floor",),
                1.0,
            ),
            Free3DPlacement(
                "fixed",
                "container",
                "fixed",
                (40.0, 0.0, 0.0),
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
        self.assertGreaterEqual(result.repair_attempts, 1)
        self.assertGreaterEqual(result.repairs_applied, 1)
        self.assertEqual(result.global_resolve_invocation_count, 0)
        self.assertFalse(result.deadline_reached)
        self.assertTrue(result.incumbent_digest)
        by_id = {value.participant_id: value for value in result.placements}
        self.assertEqual(by_id["fixed"].origin_mm[0], 80.0)
        self.assertEqual(by_id["fixed"].world_size_mm[0], 20.0)
        self.assertEqual(by_id["auto"].world_size_mm[0], 80.0)

    def test_balanced_objective_equalizes_added_volume_across_one_gap(self) -> None:
        participants = (
            _participant("left", (20.0, 40.0, 20.0)),
            _participant("right", (20.0, 40.0, 20.0)),
        )
        placements = (
            _placement("left", 0.0, 20.0),
            _placement("right", 80.0, 20.0),
        )

        first = close_free_3d_residual(
            participants,
            placements,
            {"x": 100.0, "y": 40.0, "z": 20.0},
            20.0,
            0.0,
            box_perimeter_xy_mm=0.0,
            between_bodies_z_mm=0.0,
            budget=_budget(),
            finishing_objective=(FINISHING_OBJECTIVE_BALANCED_ADDED_VOLUME),
        )
        second = close_free_3d_residual(
            participants,
            placements,
            {"x": 100.0, "y": 40.0, "z": 20.0},
            20.0,
            0.0,
            box_perimeter_xy_mm=0.0,
            between_bodies_z_mm=0.0,
            budget=_budget(),
            finishing_objective=(FINISHING_OBJECTIVE_BALANCED_ADDED_VOLUME),
        )

        by_id = {value.participant_id: value for value in first.placements}
        self.assertEqual(first.status, "closed")
        self.assertEqual(by_id["left"].world_size_mm[0], 50.0)
        self.assertEqual(by_id["right"].world_size_mm[0], 50.0)
        self.assertEqual(first.objective_score[0], 0.0)
        self.assertEqual(
            first.selected_objective_id,
            FINISHING_OBJECTIVE_BALANCED_ADDED_VOLUME,
        )
        self.assertGreaterEqual(first.objective_candidate_count, 1)
        self.assertEqual(first.deterministic_digest, second.deterministic_digest)

    def test_proportional_objective_equalizes_relative_expansion(self) -> None:
        participants = (
            _participant("small", (20.0, 40.0, 20.0)),
            _participant("large", (40.0, 40.0, 20.0)),
        )
        placements = (
            _placement("small", 0.0, 20.0),
            _placement("large", 80.0, 40.0),
        )

        result = close_free_3d_residual(
            participants,
            placements,
            {"x": 120.0, "y": 40.0, "z": 20.0},
            20.0,
            0.0,
            box_perimeter_xy_mm=0.0,
            between_bodies_z_mm=0.0,
            budget=_budget(),
            finishing_objective=(FINISHING_OBJECTIVE_PROPORTIONAL_EXPANSION),
        )

        by_id = {value.participant_id: value for value in result.placements}
        self.assertEqual(result.status, "closed")
        self.assertEqual(by_id["small"].world_size_mm[0], 40.0)
        self.assertEqual(by_id["large"].world_size_mm[0], 80.0)
        self.assertEqual(result.objective_score[2], 0.0)
        self.assertEqual(
            result.selected_objective_id,
            FINISHING_OBJECTIVE_PROPORTIONAL_EXPANSION,
        )
        self.assertEqual(result.global_resolve_invocation_count, 0)

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
