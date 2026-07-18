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
        self.assertEqual(effort_prefix("normal"), ("quick", "normal"))
        self.assertEqual(
            effort_prefix("deep"),
            ("quick", "normal", "deep"),
        )

    def test_quick_lane_solves_true_multi_container_canonical_dead_end(self) -> None:
        execution = run_container_variant_global_search(
            multi_container_variant_dead_end_project(),
            requested_effort_profile=EFFORT_QUICK,
            beam_budgets_by_effort=self._budgets(),
        )

        self.assertEqual(execution.status, SOLUTION_FOUND)
        self.assertEqual(len(execution.candidates), 1)
        candidate = execution.candidates[0]
        self.assertEqual(len(candidate.selected_container_variants), 2)
        self.assertTrue(
            all(
                not value.canonical
                for value in candidate.selected_container_variants
            )
        )
        certificate = candidate.container_variant_global_certificate
        self.assertIsNotNone(certificate)
        self.assertTrue(certificate.certified)
        self.assertTrue(candidate.certificate.certified)
        self.assertTrue(candidate.plan["summary"]["materializable"])
        frontiers = {
            value.container_group_id: value
            for value in derive_container_internal_variant_frontiers(
                multi_container_variant_dead_end_project(),
                effort_profile=EFFORT_QUICK,
            ).frontiers
        }
        contracts = {
            value["container_group_id"]: value
            for value in candidate.plan["envelope_contract"]["containers"]
        }
        for selected in candidate.selected_container_variants:
            local = next(
                value
                for value in frontiers[selected.container_group_id].variants
                if value.geometry_digest == selected.geometry_digest
            )
            actual = contracts[selected.container_group_id]["cavity_layout"]
            self.assertEqual(
                [value["local_origin_mm"] for value in actual],
                [
                    dict(zip(("x", "y", "z"), value.local_origin_mm))
                    for value in local.draft.cavities
                ],
            )
            self.assertEqual(
                [value["inner_dimensions_mm"] for value in actual],
                [
                    dict(zip(("x", "y", "z"), value.inner_dimensions_mm))
                    for value in local.draft.cavities
                ],
            )
        payload = container_variant_global_execution_to_dict(execution)
        self.assertTrue(payload["canonical_portfolio_completed_first"])
        self.assertFalse(payload["cartesian_product_materialized"])
        self.assertTrue(payload["global_certificate"]["certified"])
        json.dumps(payload, sort_keys=True)

    def test_localized_top_inset_is_decided_by_global_variant_certificate(self) -> None:
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

        self.assertEqual(execution.status, SOLUTION_FOUND)
        self.assertIsNotNone(execution.container_variant_search)
        quick_lane = execution.container_variant_search.lane_reports[0]
        self.assertEqual(quick_lane.status, NO_SOLUTION_WITHIN_BUDGET)
        self.assertEqual(
            quick_lane.stop_reason,
            "variant_geometry_not_common_certified",
        )
        selected = execution.container_variant_search.candidates[0]
        self.assertEqual(len(selected.selected_container_variants), 1)
        self.assertFalse(selected.selected_container_variants[0].canonical)
        self.assertTrue(
            selected.container_variant_global_certificate.certified
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

        self.assertEqual(len(normal.lane_reports), 2)
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

    def test_portfolio_runs_variant_fallback_only_after_canonical_failure(self) -> None:
        execution = solve_partition_portfolio(
            multi_container_variant_dead_end_project(),
            effort_profile=EFFORT_QUICK,
        )

        self.assertEqual(execution.status, SOLUTION_FOUND)
        self.assertIsNotNone(execution.container_variant_search)
        self.assertEqual(
            execution.family_reports[-1].family_id,
            CONTAINER_VARIANT_SEARCH_REPORT_ID,
        )
        self.assertTrue(
            all(
                report.certified_candidate_count == 0
                for report in execution.family_reports[:-1]
            )
        )
        self.assertEqual(execution.selected_family_id, "free_3d_beam")

    def test_public_plan_exposes_selected_variants_budgets_and_certificate(self) -> None:
        plan = solve_partition_plan(
            multi_container_variant_dead_end_project(),
            solver_method="auto",
            effort_profile=EFFORT_QUICK,
        )

        self.assertEqual(plan["solver"]["result"]["status"], SOLUTION_FOUND)
        self.assertTrue(plan["summary"]["materializable"])
        trace = plan["solver"]["portfolio"]["container_variant_search"]
        self.assertEqual(len(trace["selected_variants"]), 2)
        self.assertTrue(trace["global_certificate"]["certified"])
        self.assertFalse(trace["cartesian_product_materialized"])
        self.assertIn("container_variants", plan["solver"]["budgets"])
        self.assertEqual(
            plan["solver"]["telemetry"]["portfolio"][
                "container_variant_search"
            ]["deterministic_digest"],
            trace["deterministic_digest"],
        )
        placements = {
            value["container_group_id"]: value
            for value in plan["placements"]
            if value["role"] == "container"
        }
        for selected in trace["selected_variants"]:
            self.assertEqual(
                placements[selected["container_group_id"]][
                    "container_internal_variant_v1"
                ]["geometry_digest"],
                selected["geometry_digest"],
            )
        json.dumps(plan, sort_keys=True)


if __name__ == "__main__":
    unittest.main()
