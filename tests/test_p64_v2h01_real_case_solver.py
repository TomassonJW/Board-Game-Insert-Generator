from __future__ import annotations

import unittest

from board_game_insert_generator.partition_solver import solve_partition_plan
from p64_h04_fixture_cases import p64_v2_continuous_closure_project


class P64V2H01RealCaseSolverTests(unittest.TestCase):
    def test_contextual_case_uses_envelope_support_and_keeps_material_diagnostic(self) -> None:
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

        self.assertEqual(
            stage["solver"]["result"]["status"],
            "no_solution_within_budget",
        )
        self.assertFalse(stage["summary"]["materializable"])
        for plan in (free_3d, auto):
            self.assertEqual(plan["solver"]["result"]["status"], "solution_found")
            self.assertTrue(plan["summary"]["materializable"])
            self.assertTrue(plan["validation"]["envelope_support_certified"])
            self.assertEqual(
                plan["validation"]["envelope_support_contract"]["status"],
                "supported",
            )
            self.assertFalse(plan["validation"]["material_support_certified"])
            self.assertEqual(
                plan["validation"]["material_support_contract"]["status"],
                "unsupported",
            )
        reports = free_3d["solver"]["portfolio"]["family_reports"]
        beam = next(
            value for value in reports
            if value["family_id"] == "free_3d_beam"
        )
        self.assertGreater(beam["certified_candidate_count"], 0)
        self.assertEqual(beam["status"], "solution_found")



if __name__ == "__main__":
    unittest.main()