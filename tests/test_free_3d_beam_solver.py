from __future__ import annotations

import unittest

from board_game_insert_generator.free_3d_continuous_closure import (
    close_free_3d_residual,
)
from board_game_insert_generator.free_3d_beam_solver import (
    FREE_3D_BEAM_FAMILY_ID,
    solve_free_3d_beam,
)
from board_game_insert_generator.free_3d_plan_adapter import (
    certify_free_3d_plan,
    prepare_free_3d_problem,
)
from board_game_insert_generator.solver_contract import SolverBudget
from p64_h04_fixture_cases import simple_success_project


def _budget(**overrides: int) -> SolverBudget:
    limits = {
        "beam_width": 24,
        "max_complete_candidates": 4,
        "max_elapsed_ms": 5_000,
        "max_empty_spaces": 512,
        "max_extreme_points": 512,
        "max_options_per_participant": 24,
        "max_participant_branches": 3,
        "max_placement_trials": 100_000,
        "max_search_states": 4_096,
    }
    limits.update(overrides)
    return SolverBudget(
        FREE_3D_BEAM_FAMILY_ID,
        "h07-test",
        tuple(sorted(limits.items())),
    )


def _participant(identifier: str, size: tuple[float, float, float]) -> dict[str, object]:
    dimensions = dict(zip(("x", "y", "z"), size))
    return {
        "id": identifier,
        "role": "container",
        "name": identifier,
        "minimum_local_mm": dimensions,
        "dimension_modes": {"x": "auto", "y": "auto", "z": "auto"},
        "target_local_mm": {"x": None, "y": None, "z": None},
        "surplus_preference": "balanced",
    }


class Free3DBeamSolverTests(unittest.TestCase):
    def test_beam_places_all_requested_minimum_envelopes_for_deferred_closure(self) -> None:
        execution = solve_free_3d_beam(
            [
                _participant("a", (20.0, 20.0, 10.0)),
                _participant("b", (20.0, 20.0, 10.0)),
                _participant("c", (20.0, 20.0, 10.0)),
            ],
            {"x": 100.0, "y": 60.0, "z": 40.0},
            40.0,
            0.0,
            box_perimeter_xy_mm=0.0,
            between_bodies_z_mm=0.0,
            budget=_budget(),
        )

        self.assertEqual(execution.status, "solution_found")
        self.assertTrue(execution.solutions)
        self.assertTrue(all(value.geometry_admission.admitted for value in execution.solutions))
        self.assertEqual(execution.solutions[0].candidate.automatic_body_count, 0)

    def test_effort_exhaustion_is_honest_and_cancellation_is_not_painted(self) -> None:
        participants = [
            _participant("a", (10.0, 10.0, 10.0)),
            _participant("b", (10.0, 10.0, 10.0)),
        ]
        exhausted = solve_free_3d_beam(
            participants,
            {"x": 100.0, "y": 100.0, "z": 100.0},
            100.0,
            0.0,
            box_perimeter_xy_mm=0.0,
            between_bodies_z_mm=0.0,
            budget=_budget(max_placement_trials=1),
        )
        cancelled = solve_free_3d_beam(
            participants,
            {"x": 100.0, "y": 100.0, "z": 100.0},
            100.0,
            0.0,
            box_perimeter_xy_mm=0.0,
            between_bodies_z_mm=0.0,
            budget=_budget(),
            cancel_check=lambda: True,
        )

        self.assertEqual(exhausted.status, "no_solution_within_budget")
        self.assertNotEqual(exhausted.status, "proven_impossible")
        self.assertEqual(cancelled.status, "stale_or_cancelled")
        self.assertTrue(cancelled.telemetry.cancelled)

    def test_execution_is_deterministic_without_a_time_cutoff(self) -> None:
        arguments = (
            [_participant("a", (20.0, 20.0, 10.0)), _participant("b", (20.0, 20.0, 10.0))],
            {"x": 60.0, "y": 40.0, "z": 30.0},
            30.0,
            0.0,
        )
        first = solve_free_3d_beam(
            *arguments,
            box_perimeter_xy_mm=0.0,
            between_bodies_z_mm=0.0,
            budget=_budget(),
        )
        second = solve_free_3d_beam(
            *arguments,
            box_perimeter_xy_mm=0.0,
            between_bodies_z_mm=0.0,
            budget=_budget(),
        )

        self.assertEqual(first, second)
        self.assertEqual(first.deterministic_digest, second.deterministic_digest)

    def test_complete_geometry_is_reconstructed_and_common_product_certified(self) -> None:
        preparation = prepare_free_3d_problem(simple_success_project())
        self.assertEqual(preparation.status, "ready")
        problem = preparation.problem
        self.assertIsNotNone(problem)
        assert problem is not None
        budget = _budget()
        execution = solve_free_3d_beam(
            problem.participants,
            problem.box,
            problem.storage_height_mm,
            problem.xy_clearance_mm,
            box_perimeter_xy_mm=problem.box_xy_clearance_mm,
            between_bodies_z_mm=problem.z_clearance_mm,
            budget=budget,
        )

        self.assertEqual(execution.status, "solution_found")
        closure = close_free_3d_residual(
            problem.participants,
            execution.solutions[0].placements,
            problem.box,
            problem.storage_height_mm,
            problem.xy_clearance_mm,
            box_perimeter_xy_mm=problem.box_xy_clearance_mm,
            between_bodies_z_mm=problem.z_clearance_mm,
            budget=budget,
            top_inset_zones=problem.top_inset_zones,
        )
        self.assertFalse(closure.empty_spaces)
        certified, rejection_codes = certify_free_3d_plan(
            problem,
            strategy=execution.strategy,
            budget=budget,
            candidate_id=execution.solutions[0].candidate.candidate_id,
            placements=closure.placements,
            search_telemetry={
                **execution.telemetry.__dict__,
                "closure_status": closure.status,
            },
        )

        self.assertEqual(rejection_codes, ())
        self.assertIsNotNone(certified)
        assert certified is not None
        self.assertTrue(certified.certificate.certified)
        self.assertTrue(certified.plan["summary"]["materializable"])
        self.assertEqual(certified.plan["summary"]["residual_volume_mm3"], 0.0)


if __name__ == "__main__":
    unittest.main()
