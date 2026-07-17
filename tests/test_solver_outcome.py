from __future__ import annotations

import unittest

from board_game_insert_generator.partition_solver import solve_partition_plan
from board_game_insert_generator.solver_outcome import (
    INVALID_INPUT,
    NO_SOLUTION_WITHIN_BUDGET,
    PROVEN_IMPOSSIBLE,
    SOLUTION_FOUND,
)
from p64_h04_fixture_cases import (
    formal_conflict_project,
    h01_dense_project,
    h02_reservations_project,
    h03_contextual_unresolved_project,
    simple_success_project,
)


class SolverOutcomeTests(unittest.TestCase):
    def test_successful_fixture_exposes_versioned_telemetry_without_changing_placements(self) -> None:
        first = solve_partition_plan(simple_success_project(), request_id="h04-simple", request_revision=7)
        second = solve_partition_plan(simple_success_project(), request_id="other-request", request_revision=8)

        self.assertEqual(first["summary"]["result_status"], SOLUTION_FOUND)
        self.assertEqual(first["solver"]["result"]["label"], "Solution trouvée")
        self.assertEqual(first["solver"]["telemetry"]["family"]["id"], "stage_stack")
        self.assertEqual(first["solver"]["telemetry"]["request"], {"id": "h04-simple", "revision": 7})
        self.assertEqual(first["solver"]["telemetry"]["counters"]["z_start_levels"], 1)
        self.assertEqual(first["placements"], second["placements"])
        self.assertEqual(first["plan_digest"], second["plan_digest"])

        unrequested_first = solve_partition_plan(simple_success_project())
        unrequested_second = solve_partition_plan(simple_success_project())
        self.assertEqual(unrequested_first, unrequested_second)
        self.assertEqual(unrequested_first["solver"]["telemetry"]["elapsed_ms"], "not_applicable")

    def test_anonymised_h01_and_h02_regressions_remain_complete_and_observable(self) -> None:
        for fixture in (h01_dense_project, h02_reservations_project):
            with self.subTest(fixture=fixture.__name__):
                result = solve_partition_plan(fixture())
                telemetry = result["solver"]["telemetry"]
                self.assertEqual(result["summary"]["result_status"], SOLUTION_FOUND)
                self.assertGreaterEqual(telemetry["counters"]["candidate_proposals"], 1)
                self.assertIn(telemetry["stop_reason"], {"validated_complete_proposal"})

    def test_contextual_h03_fixture_is_not_presented_as_an_impossibility_proof(self) -> None:
        result = solve_partition_plan(h03_contextual_unresolved_project())

        self.assertNotEqual(result["summary"]["result_status"], PROVEN_IMPOSSIBLE)
        self.assertIn(result["summary"]["result_status"], {SOLUTION_FOUND, NO_SOLUTION_WITHIN_BUDGET})
        self.assertIn("stop_reason", result["solver"]["telemetry"])

    def test_formal_minimum_envelope_conflict_is_the_only_proven_impossibility_fixture(self) -> None:
        result = solve_partition_plan(formal_conflict_project())

        self.assertEqual(result["summary"]["result_status"], PROVEN_IMPOSSIBLE)
        proof = result["solver"]["result"]["proof"]
        self.assertEqual(proof["code"], "minimum_outer_envelope_exceeds_box_limit_v1")
        self.assertIn("MINIMUM_ENVELOPE_EXCEEDS_BOX", {item["code"] for item in result["diagnostics"]})

    def test_invalid_input_stops_before_stage_search(self) -> None:
        project = simple_success_project()
        project["fill_elements"] = [{"id": "legacy", "name": "Auto", "kind": "solid", "mode": "auto", "dimensions_mm": None, "container_group_id": None}]

        result = solve_partition_plan(project)

        self.assertEqual(result["summary"]["result_status"], INVALID_INPUT)
        self.assertEqual(result["solver"]["telemetry"]["stop_reason"], "input_validation_failed")
        self.assertEqual(result["solver"]["telemetry"]["counters"]["candidate_proposals"], "not_applicable")


if __name__ == "__main__":
    unittest.main()
