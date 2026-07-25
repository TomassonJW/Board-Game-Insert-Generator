from __future__ import annotations

import unittest

from board_game_insert_generator.partition_solver import solve_partition_plan
from p64_h04_fixture_cases import p64_v2_continuous_closure_project


class P64V2H01RealCaseSolverTests(unittest.TestCase):
    def test_contextual_case_rejects_artificial_top_reservation_support(self) -> None:
        project = p64_v2_continuous_closure_project()

        plans = [
            solve_partition_plan(
                project,
                solver_method=method,
                effort_profile="deep",
            )
            for method in ("stage_stack", "free_3d", "auto")
        ]

        for plan in plans:
            self.assertEqual(
                plan["solver"]["result"]["status"],
                "no_solution_within_budget",
            )
            self.assertFalse(plan["summary"]["materializable"])





if __name__ == "__main__":
    unittest.main()