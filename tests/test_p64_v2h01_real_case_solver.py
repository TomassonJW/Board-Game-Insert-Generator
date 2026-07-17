from __future__ import annotations

import unittest

from board_game_insert_generator.partition_solver import solve_partition_plan
from p64_h04_fixture_cases import p64_v2_continuous_closure_project


class P64V2H01RealCaseSolverTests(unittest.TestCase):
    def test_contextual_case_distinguishes_stage_and_free_3d_and_certifies_closure(self) -> None:
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
        self.assertEqual(free_3d["solver"]["result"]["status"], "solution_found")
        self.assertTrue(free_3d["summary"]["materializable"])
        self.assertEqual(free_3d["solver"]["portfolio"]["selected_family_id"], "free_3d_beam")
        self.assertEqual(len(free_3d["placements"]), 9)
        self.assertGreaterEqual(free_3d["summary"]["stage_count"], 2)
        self.assertEqual(free_3d["solver"]["search"]["closure_status"], "closed")
        self.assertEqual(
            free_3d["solver"]["search"]["closure_final_residual_metric"],
            (0.0, 0.0, 0),
        )
        reports = free_3d["solver"]["portfolio"]["family_reports"]
        beam = next(value for value in reports if value["family_id"] == "free_3d_beam")
        self.assertEqual(beam["certified_candidate_count"], 1)
        self.assertEqual(free_3d["validation"]["unassigned_printable_volume_mm3"], 0.0)
        self.assertEqual(auto["solver"]["result"]["status"], "solution_found")
        self.assertTrue(auto["summary"]["materializable"])
        self.assertEqual(
            auto["solver"]["portfolio"]["selected_family_id"],
            "free_3d_beam",
        )
        self.assertEqual(auto["placements"], free_3d["placements"])


if __name__ == "__main__":
    unittest.main()