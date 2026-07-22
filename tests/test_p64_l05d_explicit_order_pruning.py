from __future__ import annotations

import unittest
from unittest.mock import patch

import board_game_insert_generator.free_3d_beam_solver as beam_solver
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


def _budget() -> SolverBudget:
    return SolverBudget(
        beam_solver.FREE_3D_BEAM_FAMILY_ID,
        "p64-l05d2-test",
        tuple(
            sorted(
                {
                    "beam_width": 1,
                    "max_complete_candidates": 1,
                    "max_elapsed_ms": 5_000,
                    "max_empty_spaces": 64,
                    "max_extreme_points": 64,
                    "max_options_per_participant": 1,
                    "max_participant_branches": 2,
                    "max_placement_trials": 10_000,
                    "max_search_states": 32,
                }.items()
            )
        ),
    )


def _root_participants(mocked: object) -> list[str]:
    return [str(call.args[0]["id"]) for call in mocked.call_args_list if not call.args[3]]


class ExplicitParticipantOrderPruningTests(unittest.TestCase):
    def test_explicit_order_evaluates_only_selectable_nonempty_participants(
        self,
    ) -> None:
        participants = [_participant(value) for value in ("a", "b", "c", "d")]
        arguments = (
            participants,
            {"x": 100.0, "y": 100.0, "z": 40.0},
            40.0,
            0.0,
        )
        common = {
            "box_perimeter_xy_mm": 0.0,
            "between_bodies_z_mm": 0.0,
            "budget": _budget(),
        }

        with patch.object(
            beam_solver,
            "_placement_options",
            wraps=beam_solver._placement_options,
        ) as explicit_options:
            explicit = beam_solver.solve_free_3d_beam(
                *arguments,
                participant_order=("a", "b", "c", "d"),
                **common,
            )
        with patch.object(
            beam_solver,
            "_placement_options",
            wraps=beam_solver._placement_options,
        ) as heuristic_options:
            heuristic = beam_solver.solve_free_3d_beam(*arguments, **common)

        self.assertEqual(_root_participants(explicit_options), ["a", "b"])
        self.assertEqual(
            _root_participants(heuristic_options),
            ["a", "b", "c", "d"],
        )
        self.assertEqual(explicit.status, heuristic.status)
        self.assertTrue(explicit.solutions)
        self.assertLess(
            explicit.telemetry.placement_trials,
            heuristic.telemetry.placement_trials,
        )


if __name__ == "__main__":
    unittest.main()
