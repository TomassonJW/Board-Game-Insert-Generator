from __future__ import annotations

import unittest

from board_game_insert_generator.solver_portfolio import solve_partition_portfolio
from test_solver_portfolio import _two_level_project


class SolverPortfolioStaleTests(unittest.TestCase):
    def test_cancellation_after_stage_candidate_prevents_any_plan_from_being_painted(self) -> None:
        calls = 0

        def cancel_after_stage_start() -> bool:
            nonlocal calls
            calls += 1
            return calls >= 2

        execution = solve_partition_portfolio(
            _two_level_project(),
            cancel_check=cancel_after_stage_start,
        )

        self.assertEqual(execution.status, "stale_or_cancelled")
        self.assertIsNone(execution.selected_plan)
        self.assertEqual(execution.certified_candidates, ())


if __name__ == "__main__":
    unittest.main()
