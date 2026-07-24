from __future__ import annotations

import unittest

from board_game_insert_generator.partition_solver import solve_partition_plan
from p64_h04_fixture_cases import p64_v2_continuous_closure_project


class P64V2H01RealCaseSolverTests(unittest.TestCase):
    def test_contextual_case_is_not_published_with_void_support(self) -> None:
        project = p64_v2_continuous_closure_project()

        stage = solve_partition_plan(
            project,
            solver_method="stage_stack",
            effort_profile="deep",
        )
        free_3d = solve_partition_plan(
            project,
            solver_method="free_3d",
            effort_profile="deep",
        )
        auto = solve_partition_plan(
            project,
            solver_method="auto",
            effort_profile="deep",
        )

        for plan in (stage, free_3d, auto):
            self.assertEqual(
                plan["solver"]["result"]["status"],
                "no_solution_within_budget",
            )
            self.assertFalse(plan["summary"]["materializable"])
            self.assertEqual(plan["placements"], [])
        reports = free_3d["solver"]["portfolio"]["family_reports"]
        beam = next(
            value for value in reports
            if value["family_id"] == "free_3d_beam"
        )
        self.assertEqual(beam["certified_candidate_count"], 0)
        self.assertEqual(beam["status"], "no_solution_within_budget")



if __name__ == "__main__":
    unittest.main()