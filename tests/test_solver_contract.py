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
    def test_stage_stack_adapter_preserves_geometry_and_adds_material_certificate(self) -> None:
        for fixture in (simple_success_project, h01_dense_project):
            with self.subTest(fixture=fixture.__name__):
                baseline = _solve_stage_stack_baseline(fixture())
                adapted = solve_partition_plan(fixture())

                self.assertEqual(adapted["placements"], baseline["placements"])
                self.assertEqual(
                    adapted["stage_support"]["certificate_kind"],
                    "material_surface_v1",
                )
                self.assertEqual(adapted["stage_support"]["status"], "supported")
                self.assertTrue(adapted["validation"]["material_support_certified"])
                self.assertTrue(adapted["invariants"]["material_support_certified"])

    def test_complete_h04_plan_gets_one_immutable_candidate_and_certificate(self) -> None:
        run = inspect_stage_stack_plan(solve_partition_plan(h01_dense_project()))

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

    def test_adapter_demotes_a_solution_that_fails_the_common_certificate(self) -> None:
        malformed = _solve_stage_stack_baseline(simple_success_project())
        malformed = deepcopy(malformed)
        malformed["placements"][0]["origin_mm"]["x"] = -1.0

        def dishonest_strategy(*args: object, **kwargs: object) -> dict[str, object]:
            return malformed

        result = run_stage_stack_adapter(
            dishonest_strategy,
            simple_success_project(),
        )

        self.assertEqual(
            result["solver"]["result"]["status"],
            "no_solution_within_budget",
        )
        self.assertFalse(result["summary"]["materializable"])
        self.assertEqual(result["placements"], [])
        self.assertEqual(result["diagnostics"][0]["code"], "COMMON_CERTIFICATE_REJECTED")

    def test_h02_void_support_is_demoted_instead_of_published(self) -> None:
        result = solve_partition_plan(h02_reservations_project())

        self.assertEqual(
            result["solver"]["result"]["status"],
            "no_solution_within_budget",
        )
        self.assertFalse(result["summary"]["materializable"])
        self.assertIn(
            "insufficient_material_support",
            result["stage_support"]["rejection_statuses"],
        )


if __name__ == "__main__":
    unittest.main()
