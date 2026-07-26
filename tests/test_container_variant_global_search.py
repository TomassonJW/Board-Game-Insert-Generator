from __future__ import annotations

import json
import unittest

from board_game_insert_generator.container_internal_variants import (
    derive_container_internal_variant_frontiers,
)
from board_game_insert_generator.container_variant_global_search import (
    container_variant_global_execution_to_dict,
    effort_prefix,
    run_container_variant_global_search,
)
from board_game_insert_generator.partition_solver import solve_partition_plan
from board_game_insert_generator.solver_outcome import (
    NO_SOLUTION_WITHIN_BUDGET,
    SOLUTION_FOUND,
    STALE_OR_CANCELLED,
)
from board_game_insert_generator.solver_portfolio import (
    CONTAINER_VARIANT_SEARCH_REPORT_ID,
    EFFORT_NORMAL,
    EFFORT_QUICK,
    portfolio_effort_profiles,
    solve_partition_portfolio,
)
from p64_h04_fixture_cases import simple_success_project
from p64_v2h03b_fixture_cases import dense_11_containers_34_contents_project
from p64_v2h03c_fixture_cases import (
    localized_variant_compatibility_project,
    multi_container_variant_dead_end_project,
    multi_container_variant_unsolved_project,
)


class ContainerVariantGlobalSearchTests(unittest.TestCase):
    def _budgets(self):
        return {
            value.profile_id: value.beam_budget
            for value in portfolio_effort_profiles()
        }

    def test_effort_profiles_are_prefix_monotone(self) -> None:
        self.assertEqual(effort_prefix("quick"), ("quick",))
        self.assertEqual(effort_prefix("short"), ("quick", "short"))
        self.assertEqual(
            effort_prefix("normal"),
            ("quick", "short", "normal"),
        )
        self.assertEqual(
            effort_prefix("long"),
            ("quick", "short", "normal", "long"),
        )
        self.assertEqual(
            effort_prefix("deep"),
            ("quick", "short", "normal", "long", "deep"),
        )

    def test_quick_lane_does_not_use_minimum_reduction_as_packing_escape(self) -> None:
        execution = run_container_variant_global_search(
            multi_container_variant_dead_end_project(),
            requested_effort_profile=EFFORT_QUICK,
            beam_budgets_by_effort=self._budgets(),
        )

        self.assertEqual(execution.status, NO_SOLUTION_WITHIN_BUDGET)
        self.assertEqual(execution.candidates, ())
        self.assertTrue(execution.lane_reports)
        self.assertNotEqual(execution.status, "proven_impossible")
    def test_localized_top_reservation_rejects_full_height_variants(self) -> None:
        project = localized_variant_compatibility_project()
        frontier = derive_container_internal_variant_frontiers(
            project,
            effort_profile=EFFORT_NORMAL,
        ).frontiers[0]
        self.assertGreaterEqual(len(frontier.variants), 2)
        self.assertTrue(
            all(value.local_certificate.certified for value in frontier.variants)
        )

        execution = solve_partition_portfolio(
            project,
            effort_profile=EFFORT_NORMAL,
        )

        self.assertEqual(execution.status, NO_SOLUTION_WITHIN_BUDGET)
        self.assertIsNotNone(execution.container_variant_search)
        self.assertEqual(
            execution.container_variant_search.lane_reports[0].status,
            NO_SOLUTION_WITHIN_BUDGET,
        )

    def test_normal_replays_quick_lane_with_identical_trace_prefix(self) -> None:
        project = multi_container_variant_dead_end_project()
        quick = run_container_variant_global_search(
            project,
            requested_effort_profile=EFFORT_QUICK,
            beam_budgets_by_effort=self._budgets(),
        )
        normal = run_container_variant_global_search(
            project,
            requested_effort_profile=EFFORT_NORMAL,
            beam_budgets_by_effort=self._budgets(),
        )

        self.assertEqual(len(normal.lane_reports), 3)
        self.assertEqual(
            normal.lane_reports[0].deterministic_digest,
            quick.lane_reports[0].deterministic_digest,
        )
        self.assertTrue(
            set(quick.lane_reports[0].candidate_digests).issubset(
                {
                    digest
                    for lane in normal.lane_reports
                    for digest in lane.candidate_digests
                }
            )
        )

    def test_variant_limits_are_observed_and_unsolved_is_not_impossibility(self) -> None:
        execution = run_container_variant_global_search(
            multi_container_variant_unsolved_project(),
            requested_effort_profile=EFFORT_QUICK,
            beam_budgets_by_effort=self._budgets(),
        )

        self.assertEqual(execution.status, NO_SOLUTION_WITHIN_BUDGET)
        lane = execution.lane_reports[0]
        self.assertLessEqual(
            lane.search_states,
            lane.variant_budget.max_variant_assignment_states,
        )
        self.assertLessEqual(
            lane.placement_trials,
            lane.variant_budget.max_variant_placement_trials,
        )
        self.assertNotEqual(execution.status, "proven_impossible")

    def test_dense_mechanism_remains_bounded_and_truthful(self) -> None:
        execution = run_container_variant_global_search(
            dense_11_containers_34_contents_project(),
            requested_effort_profile=EFFORT_QUICK,
            beam_budgets_by_effort=self._budgets(),
        )

        self.assertIn(
            execution.status,
            {SOLUTION_FOUND, NO_SOLUTION_WITHIN_BUDGET},
        )
        lane = execution.lane_reports[0]
        self.assertLessEqual(
            lane.search_states,
            lane.variant_budget.max_variant_assignment_states,
        )
        self.assertLessEqual(
            lane.placement_trials,
            lane.variant_budget.max_variant_placement_trials,
        )

    def test_cancellation_produces_stale_without_candidate(self) -> None:
        calls = 0

        def cancel() -> bool:
            nonlocal calls
            calls += 1
            return calls >= 3

        execution = run_container_variant_global_search(
            multi_container_variant_dead_end_project(),
            requested_effort_profile=EFFORT_QUICK,
            beam_budgets_by_effort=self._budgets(),
            cancel_check=cancel,
        )

        self.assertEqual(execution.status, STALE_OR_CANCELLED)
        self.assertEqual(execution.candidates, ())
        self.assertTrue(execution.lane_reports[0].cancelled)

    def test_canonical_fast_path_does_not_run_variant_search(self) -> None:
        execution = solve_partition_portfolio(
            simple_success_project(),
            effort_profile=EFFORT_QUICK,
        )

        self.assertEqual(execution.status, SOLUTION_FOUND)
        self.assertTrue(execution.fast_path_used)
        self.assertIsNone(execution.container_variant_search)
        self.assertNotIn(
            CONTAINER_VARIANT_SEARCH_REPORT_ID,
            {value.family_id for value in execution.family_reports},
        )

    def test_portfolio_fallback_remains_truthful_without_undersized_variants(self) -> None:
        execution = solve_partition_portfolio(
            multi_container_variant_dead_end_project(),
            effort_profile=EFFORT_QUICK,
        )

        self.assertEqual(execution.status, NO_SOLUTION_WITHIN_BUDGET)
        self.assertIsNotNone(execution.container_variant_search)
        self.assertEqual(
            execution.family_reports[-1].family_id,
            CONTAINER_VARIANT_SEARCH_REPORT_ID,
        )
        self.assertTrue(
            all(
                report.certified_candidate_count == 0
                for report in execution.family_reports
            )
        )
    def test_public_plan_refuses_to_publish_an_undersized_variant_solution(self) -> None:
        plan = solve_partition_plan(
            multi_container_variant_dead_end_project(),
            solver_method="auto",
            effort_profile=EFFORT_QUICK,
        )

        self.assertEqual(
            plan["solver"]["result"]["status"],
            NO_SOLUTION_WITHIN_BUDGET,
        )
        self.assertFalse(plan["summary"]["materializable"])
        self.assertIn("container_variants", plan["solver"]["budgets"])
        json.dumps(plan, sort_keys=True)



if __name__ == "__main__":
    unittest.main()
