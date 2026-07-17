from __future__ import annotations

import unittest
from unittest.mock import patch

from board_game_insert_generator.free_3d_beam_solver import (
    FREE_3D_BEAM_FAMILY_ID,
    solve_free_3d_beam,
)
from board_game_insert_generator.solver_contract import SolverBudget


def _participant(identifier: str) -> dict[str, object]:
    return {
        "id": identifier,
        "role": "container",
        "name": identifier,
        "minimum_local_mm": {"x": 10.0, "y": 10.0, "z": 10.0},
        "dimension_modes": {"x": "auto", "y": "auto", "z": "auto"},
        "target_local_mm": {"x": None, "y": None, "z": None},
        "surplus_preference": "balanced",
    }


def _budget(max_elapsed_ms: int = 5_000) -> SolverBudget:
    return SolverBudget(
        FREE_3D_BEAM_FAMILY_ID,
        "stop-test",
        tuple(
            sorted(
                {
                    "beam_width": 8,
                    "max_complete_candidates": 2,
                    "max_elapsed_ms": max_elapsed_ms,
                    "max_empty_spaces": 128,
                    "max_extreme_points": 128,
                    "max_options_per_participant": 12,
                    "max_participant_branches": 2,
                    "max_placement_trials": 10_000,
                    "max_search_states": 1_000,
                }.items()
            )
        ),
    )


class Free3DBeamStopConditionTests(unittest.TestCase):
    def test_hard_time_budget_is_reported_as_budget_exhaustion_not_impossibility(self) -> None:
        with patch(
            "board_game_insert_generator.free_3d_beam_solver.perf_counter",
            side_effect=(0.0, 0.002),
        ):
            execution = solve_free_3d_beam(
                [_participant("a"), _participant("b")],
                {"x": 100.0, "y": 100.0, "z": 100.0},
                100.0,
                0.0,
                box_perimeter_xy_mm=0.0,
                between_bodies_z_mm=0.0,
                budget=_budget(max_elapsed_ms=1),
            )

        self.assertEqual(execution.status, "no_solution_within_budget")
        self.assertEqual(execution.stop_reason, "hard_time_budget_reached")
        self.assertTrue(execution.telemetry.timed_out)

    def test_mid_search_cancellation_stops_without_a_current_candidate(self) -> None:
        calls = 0

        def cancel_after_start() -> bool:
            nonlocal calls
            calls += 1
            return calls >= 2

        execution = solve_free_3d_beam(
            [_participant("a"), _participant("b"), _participant("c")],
            {"x": 100.0, "y": 100.0, "z": 100.0},
            100.0,
            0.0,
            box_perimeter_xy_mm=0.0,
            between_bodies_z_mm=0.0,
            budget=_budget(),
            cancel_check=cancel_after_start,
        )

        self.assertEqual(execution.status, "stale_or_cancelled")
        self.assertFalse(execution.solutions)
        self.assertTrue(execution.telemetry.cancelled)


if __name__ == "__main__":
    unittest.main()
