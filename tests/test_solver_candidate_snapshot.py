from __future__ import annotations

from dataclasses import replace
import unittest

from board_game_insert_generator.partition_solver import solve_partition_plan
from board_game_insert_generator.solver_contract import (
    certify_partition_candidate,
    inspect_stage_stack_plan,
)
from p64_h04_fixture_cases import simple_success_project


class SolverCandidateSnapshotTests(unittest.TestCase):
    def test_common_certificate_rejects_a_candidate_that_does_not_match_the_plan(self) -> None:
        plan = solve_partition_plan(simple_success_project())
        candidate = inspect_stage_stack_plan(plan).candidates[0]
        first = candidate.placements[0]
        forged = replace(
            candidate,
            placements=(replace(first, origin_mm=(first.origin_mm[0] + 1.0, *first.origin_mm[1:])),)
            + candidate.placements[1:],
        )

        certificate = certify_partition_candidate(plan, forged)

        self.assertFalse(certificate.certified)
        self.assertIn("CANDIDATE_PLAN_MISMATCH", certificate.rejection_codes)


if __name__ == "__main__":
    unittest.main()
