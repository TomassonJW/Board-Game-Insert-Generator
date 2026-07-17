from __future__ import annotations

from dataclasses import FrozenInstanceError
from copy import deepcopy
import unittest

from board_game_insert_generator.partition_solver import (
    _solve_stage_stack_baseline,
    solve_partition_plan,
)
from board_game_insert_generator.solver_contract import (
    SolverBudget,
    SolverContractViolation,
    inspect_stage_stack_plan,
    run_stage_stack_adapter,
)
from p64_h04_fixture_cases import (
    formal_conflict_project,
    h01_dense_project,
    h02_reservations_project,
    simple_success_project,
)


class SolverContractTests(unittest.TestCase):
    def test_stage_stack_adapter_preserves_the_h04_reference_plans_bit_for_bit(self) -> None:
        for fixture in (simple_success_project, h01_dense_project, h02_reservations_project):
            with self.subTest(fixture=fixture.__name__):
                baseline = _solve_stage_stack_baseline(fixture())
                adapted = solve_partition_plan(fixture())

                self.assertEqual(adapted, baseline)
                self.assertEqual(adapted["plan_digest"], baseline["plan_digest"])

    def test_complete_h04_plan_gets_one_immutable_candidate_and_certificate(self) -> None:
        run = inspect_stage_stack_plan(solve_partition_plan(h02_reservations_project()))

        self.assertEqual(run.strategy.family_id, "stage_stack")
        self.assertEqual(run.budget.effort_profile, "baseline")
        self.assertEqual(len(run.candidates), 1)
        self.assertEqual(len(run.certificates), 1)
        self.assertTrue(run.certificates[0].certified)
        self.assertEqual(run.certificates[0].rejection_codes, ())
        self.assertEqual(run.candidates[0].strategy, run.strategy)
        with self.assertRaises(FrozenInstanceError):
            run.candidates[0].candidate_id = "mutated"  # type: ignore[misc]

    def test_non_solution_exposes_no_candidate_to_the_portfolio(self) -> None:
        run = inspect_stage_stack_plan(solve_partition_plan(formal_conflict_project()))

        self.assertEqual(run.candidates, ())
        self.assertEqual(run.certificates, ())

    def test_common_budget_snapshots_are_immutable_and_monotone(self) -> None:
        quick = SolverBudget("stage_stack", "baseline", (("max_candidates", 4), ("max_orderings", 1)))
        deeper = SolverBudget("stage_stack", "baseline", (("max_candidates", 8), ("max_orderings", 2)))

        self.assertTrue(deeper.is_at_least_as_permissive_as(quick))
        self.assertFalse(quick.is_at_least_as_permissive_as(deeper))
        with self.assertRaises(FrozenInstanceError):
            quick.effort_profile = "changed"  # type: ignore[misc]

    def test_adapter_rejects_a_solution_that_fails_the_common_certificate(self) -> None:
        malformed = _solve_stage_stack_baseline(simple_success_project())
        malformed = deepcopy(malformed)
        malformed["placements"][0]["origin_mm"]["x"] = -1.0

        def dishonest_strategy(*args: object, **kwargs: object) -> dict[str, object]:
            return malformed

        with self.assertRaisesRegex(SolverContractViolation, "without a common certificate"):
            run_stage_stack_adapter(dishonest_strategy, simple_success_project())


if __name__ == "__main__":
    unittest.main()
