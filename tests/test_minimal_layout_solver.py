from __future__ import annotations

from copy import deepcopy
from dataclasses import replace
import unittest
from unittest.mock import patch

from board_game_insert_generator.container_internal_variants import (
    derive_container_internal_variant_frontiers,
)
from board_game_insert_generator.container_variant_global_search import (
    _participants_with_variant_options,
)
from board_game_insert_generator.contextual_local_analysis import (
    IncrementalLocalAnalysisEngine,
)
from board_game_insert_generator.free_3d_beam_solver import (
    VariantFree3DPlacement,
)
from board_game_insert_generator.free_3d_plan_adapter import (
    certify_minimal_free_3d_plan,
    prepare_free_3d_problem,
)
from board_game_insert_generator.minimal_layout_solver import (
    minimal_effort_budgets,
    minimal_lane_specs,
    minimal_participant_orderings,
    solve_minimal_layout,
)
from board_game_insert_generator.project_v1 import blank_project_v1
from board_game_insert_generator.solver_contract import SolverStrategy
from board_game_insert_generator.solver_outcome import (
    INVALID_INPUT,
    NO_SOLUTION_WITHIN_BUDGET,
    SOLUTION_FOUND,
    STALE_OR_CANCELLED,
)
from p64_h04_fixture_cases import simple_success_project
from p64_v2h03b_fixture_cases import (
    dense_11_containers_34_contents_project,
    localized_reservation_project,
)


def _project_from_dimensions(
    dimensions: dict[str, tuple[float, float, float]],
    *,
    box: tuple[float, float, float],
) -> dict[str, object]:
    project = blank_project_v1()
    project["box"] = {
        "inner_dimensions_mm": {
            "x": box[0],
            "y": box[1],
            "z": box[2],
        },
        "usable_height_mm": box[2],
        "lid_clearance_mm": 0.0,
    }
    project["container_groups"] = [
        {
            "id": group_id,
            "name": group_id,
            "wall_thickness_mm": None,
            "floor_thickness_mm": None,
        }
        for group_id in dimensions
    ]
    project["contents"] = [
        {
            "id": f"{group_id}-content",
            "name": group_id,
            "shape_kind": "custom",
            "dimensions_mm": {"x": x, "y": y, "z": z},
            "quantity": 1,
            "container_group_id": group_id,
            "content_clearance_mm": None,
            "measurement_confidence": "exact",
        }
        for group_id, (x, y, z) in dimensions.items()
    ]
    return project


class MinimalLayoutSolverTests(unittest.TestCase):
    def test_single_container_stays_minimal_and_residual_is_unassigned(self) -> None:
        plan = solve_minimal_layout(
            simple_success_project(),
            effort_profile="quick",
        )

        self.assertEqual(plan["solver"]["result"]["status"], SOLUTION_FOUND)
        self.assertFalse(plan["solver"]["result"]["materializable"])
        self.assertTrue(plan["summary"]["placement_certified"])
        self.assertFalse(plan["summary"]["complete_printable_partition"])
        self.assertGreater(plan["summary"]["residual_volume_mm3"], 0.0)
        self.assertEqual(plan["summary"]["automatic_body_count"], 0)
        self.assertEqual(plan["residuals"]["status"], "unassigned")
        self.assertFalse(plan["residuals"]["residual_is_distributed"])
        self.assertFalse(plan["minimal_layout"]["finalization_applied"])
        self.assertTrue(
            plan["minimal_layout"]["global_certificate"]["certified"]
        )
        for placement in plan["placements"]:
            if placement["role"] != "container":
                continue
            self.assertEqual(
                placement["final_outer_dimensions_mm"],
                placement["minimum_outer_envelope_mm"],
            )
            self.assertEqual(
                set(placement["surplus_distribution_mm"]),
                {"left", "right", "front", "back", "below", "above"},
            )
            self.assertEqual(
                set(placement["surplus_distribution_mm"].values()),
                {0.0},
            )

    def test_multiseed_portfolio_is_deterministic_and_keeps_full_frontier(self) -> None:
        project = _project_from_dimensions(
            {
                "long-a": (65.0, 12.0, 8.0),
                "long-b": (61.0, 14.0, 9.0),
            },
            box=(100.0, 80.0, 45.0),
        )

        first = solve_minimal_layout(project, effort_profile="normal")
        second = solve_minimal_layout(
            deepcopy(project),
            effort_profile="normal",
        )

        self.assertEqual(first["solver"]["result"]["status"], SOLUTION_FOUND)
        self.assertEqual(first["plan_digest"], second["plan_digest"])
        portfolio = first["minimal_layout"]["search_provenance"]
        seeds = {
            lane["seed_participant_id"]
            for lane in portfolio["lanes"]
        }
        self.assertGreaterEqual(len(seeds), 2)
        self.assertGreater(
            portfolio["candidate_count_before_deduplication"],
            portfolio["candidate_count_after_deduplication"],
        )
        self.assertGreaterEqual(portfolio["pareto_candidate_count"], 1)
        self.assertEqual(
            portfolio["historical_comparator_lane_ids"],
            [
                "historical_legacy_corner",
                "historical_bridge_edge",
            ],
        )
        self.assertEqual(
            portfolio["selected"]["statement"],
            "best_certified_proposal_found_within_budget",
        )
        self.assertNotIn("opaque_total", portfolio)
        self.assertFalse(portfolio["finalization_invocation_count"])
        self.assertFalse(
            portfolio["fusion_materialization_invocation_count"]
        )

    def test_normalized_rarity_beats_absolute_height_when_more_constrained(self) -> None:
        participants = (
            {
                "id": "rare-footprint",
                "minimum_local_mm": {"x": 95.0, "y": 45.0, "z": 10.0},
                "dimension_modes": {"x": "fixed", "y": "fixed", "z": "fixed"},
            },
            {
                "id": "absolute-tall",
                "minimum_local_mm": {"x": 10.0, "y": 10.0, "z": 90.0},
                "dimension_modes": {"x": "fixed", "y": "fixed", "z": "fixed"},
            },
        )

        orderings = minimal_participant_orderings(
            participants,
            {"x": 100.0, "y": 60.0, "z": 100.0},
            100.0,
        )

        self.assertEqual(
            orderings["placement_rarity"][0],
            "rare-footprint",
        )
        self.assertEqual(orderings["height"][0], "absolute-tall")

    def test_effort_lanes_and_hard_caps_are_monotone_prefixes(self) -> None:
        quick_lanes = minimal_lane_specs("quick")
        normal_lanes = minimal_lane_specs("normal")
        deep_lanes = minimal_lane_specs("deep")
        quick, normal, deep = minimal_effort_budgets()

        self.assertEqual(normal_lanes[: len(quick_lanes)], quick_lanes)
        self.assertEqual(deep_lanes[: len(normal_lanes)], normal_lanes)
        self.assertTrue(normal.is_at_least_as_permissive_as(quick))
        self.assertTrue(deep.is_at_least_as_permissive_as(normal))
        self.assertEqual(
            [len(quick_lanes), len(normal_lanes), len(deep_lanes)],
            [3, 6, 9],
        )
        self.assertNotIn(
            "max_deep_extension_elapsed_ms",
            dict(normal.limits),
        )
        self.assertEqual(
            dict(deep.limits)["max_deep_extension_elapsed_ms"],
            30_000,
        )

    def test_deep_deadline_preserves_the_normal_incumbent(self) -> None:
        project = simple_success_project()
        clock_values = [0.0, 0.0]

        def deadline_clock() -> float:
            return clock_values.pop(0) if clock_values else 30_000.0

        with patch(
            "board_game_insert_generator.minimal_layout_solver._monotonic_ms",
            side_effect=deadline_clock,
        ):
            plan = solve_minimal_layout(project, effort_profile="deep")

        self.assertEqual(plan["solver"]["result"]["status"], SOLUTION_FOUND)
        provenance = plan["minimal_layout"]["search_provenance"]
        anytime = provenance["anytime"]
        self.assertTrue(anytime["initial_incumbent_available"])
        self.assertTrue(anytime["deep_extension_deadline_reached"])
        self.assertEqual(
            anytime["selected_phase"],
            "normal_incumbent",
        )
        self.assertTrue(anytime["incumbent_preserved"])
        self.assertEqual(
            anytime["stop_reason"],
            "deep_deadline_reached_incumbent_preserved",
        )
        self.assertEqual(
            provenance["selected"]["placement_digest"],
            anytime["initial_incumbent_placement_digest"],
        )
        self.assertEqual(
            len(provenance["phases"]["normal_prefix"]["attempted_lane_ids"]),
            6,
        )
        self.assertEqual(
            len(provenance["phases"]["deep_extension"]["attempted_lane_ids"]),
            1,
        )
        self.assertFalse(plan["solver"]["deterministic"])
        self.assertEqual(plan["solver"]["telemetry"]["elapsed_ms"], 30_000)
        self.assertEqual(
            plan["solver"]["telemetry"]["search_stop_reason"],
            "deep_deadline_reached_incumbent_preserved",
        )
        self.assertTrue(
            plan["minimal_layout"]["global_certificate"]["certified"]
        )

    def test_deep_deadline_without_incumbent_stays_truthful(self) -> None:
        project = localized_reservation_project()
        clock_values = [0.0, 0.0]

        def deadline_clock() -> float:
            return clock_values.pop(0) if clock_values else 30_000.0

        with patch(
            "board_game_insert_generator.minimal_layout_solver._monotonic_ms",
            side_effect=deadline_clock,
        ):
            plan = solve_minimal_layout(project, effort_profile="deep")

        self.assertEqual(
            plan["solver"]["result"]["status"],
            NO_SOLUTION_WITHIN_BUDGET,
        )
        provenance = plan["minimal_layout"]["search_provenance"]
        anytime = provenance["anytime"]
        self.assertFalse(anytime["initial_incumbent_available"])
        self.assertTrue(anytime["deep_extension_deadline_reached"])
        self.assertIsNone(anytime["selected_phase"])
        self.assertEqual(
            anytime["stop_reason"],
            "deep_deadline_reached_without_incumbent",
        )
        self.assertFalse(plan["solver"]["result"]["materializable"])

    def test_deep_completion_preserves_or_improves_normal(self) -> None:
        project = simple_success_project()
        deep = solve_minimal_layout(project, effort_profile="deep")

        self.assertEqual(deep["solver"]["result"]["status"], SOLUTION_FOUND)
        anytime = deep["minimal_layout"]["search_provenance"]["anytime"]
        self.assertIn(
            anytime["selected_phase"],
            {"normal_incumbent", "deep_extension"},
        )
        metrics = deep["minimal_layout"]["metrics"]
        selected_rank_axes = (
            metrics["cluster_volume_mm3"],
            metrics["internal_gap_mm3"],
            metrics["cluster_height_mm"],
            metrics["cluster_footprint_mm2"],
            metrics["residual_fragmentation"],
            -metrics["contact_count"],
            -metrics["minimum_support_ratio"],
        )
        self.assertLessEqual(
            selected_rank_axes,
            tuple(anytime["initial_incumbent_rank_axes"]),
        )
        self.assertEqual(
            deep["minimal_layout"]["search_provenance"][
                "finalization_invocation_count"
            ],
            0,
        )

    def test_tall_body_stays_beside_a_supported_thin_stack(self) -> None:
        project = _project_from_dimensions(
            {
                "tall": (20.0, 20.0, 50.0),
                "thin-a": (30.0, 30.0, 10.0),
                "thin-b": (30.0, 30.0, 10.0),
            },
            box=(70.0, 40.0, 65.0),
        )

        plan = solve_minimal_layout(project, effort_profile="normal")

        self.assertEqual(plan["solver"]["result"]["status"], SOLUTION_FOUND)
        by_id = {value["id"]: value for value in plan["placements"]}
        self.assertEqual(by_id["container:tall"]["origin_mm"]["z"], 0.0)
        thin_z = sorted(
            (
                by_id["container:thin-a"]["origin_mm"]["z"],
                by_id["container:thin-b"]["origin_mm"]["z"],
            )
        )
        self.assertEqual(thin_z[0], 0.0)
        self.assertGreater(thin_z[1], 0.0)
        self.assertEqual(plan["stage_support"]["status"], "supported")
        stacked = next(
            value
            for value in plan["stage_support"]["supports"]
            if value["placement_id"]
            == (
                "container:thin-a"
                if by_id["container:thin-a"]["origin_mm"]["z"] > 0.0
                else "container:thin-b"
            )
        )
        self.assertTrue(stacked["supported"])
        self.assertEqual(stacked["coverage_ratio"], 1.0)

    def test_floating_body_is_rejected_by_the_common_support_contract(self) -> None:
        project = simple_success_project()
        preparation = prepare_free_3d_problem(project)
        self.assertIsNotNone(preparation.problem)
        problem = preparation.problem
        assert problem is not None
        run = derive_container_internal_variant_frontiers(
            project,
            effort_profile="quick",
            max_container_height_mm=problem.storage_height_mm,
        )
        participants = _participants_with_variant_options(
            problem.participants,
            run.frontiers,
        )
        problem = replace(
            problem,
            participants=participants,
            container_variant_frontiers=run.frontiers,
        )
        variant = next(
            value
            for value in run.frontiers[0].variants
            if value.canonical
        )
        size = variant.draft.minimum_outer_envelope_mm
        placement = VariantFree3DPlacement(
            participant_id="container:simple",
            role="container",
            name="Bac simple",
            origin_mm=(10.0, 10.0, 5.0),
            world_size_mm=size,
            local_size_mm=size,
            rotation_deg_z=0,
            supporting_ids=(),
            support_coverage_ratio=1.0,
            container_variant_id=variant.variant_id,
            container_variant_digest=variant.geometry_digest,
            container_variant_canonical=True,
        )

        certified, rejections = certify_minimal_free_3d_plan(
            problem,
            strategy=SolverStrategy("test-minimal", "v1"),
            budget=minimal_effort_budgets()[0],
            candidate_id="floating",
            placements=(placement,),
            empty_spaces=(),
            search_telemetry={},
            search_provenance={},
        )

        self.assertIsNone(certified)
        self.assertIn("SUPPORT_COVERAGE", rejections)

    def test_incremental_frontiers_are_consumed_only_on_explicit_solve(self) -> None:
        project = simple_success_project()
        engine = IncrementalLocalAnalysisEngine(
            project,
            effort_profile="quick",
        )
        edited = deepcopy(project)
        edited["contents"][0]["quantity"] = 2

        local_snapshot = engine.update_project(edited)

        self.assertEqual(
            local_snapshot["invariants"]["global_solver_invocation_count"],
            0,
        )
        plan = solve_minimal_layout(
            edited,
            effort_profile="quick",
            container_frontiers=engine.certified_frontiers(),
            frontier_digests=engine.frontier_digests(),
        )
        self.assertEqual(plan["solver"]["result"]["status"], SOLUTION_FOUND)
        self.assertEqual(
            plan["minimal_layout"]["search_provenance"][
                "frontier_source"
            ],
            "incremental_local_analysis",
        )
        self.assertEqual(
            engine.snapshot()["invariants"]["global_solver_invocation_count"],
            0,
        )
        tampered = solve_minimal_layout(
            edited,
            effort_profile="quick",
            container_frontiers=engine.certified_frontiers(),
            frontier_digests=tuple(
                (group_id, "tampered")
                for group_id, _ in engine.frontier_digests()
            ),
        )
        self.assertEqual(
            tampered["solver"]["result"]["status"],
            INVALID_INPUT,
        )
        self.assertIn(
            "LOCAL_FRONTIER_DIGEST_MISMATCH",
            {value["code"] for value in tampered["diagnostics"]},
        )

    def test_localized_top_reservation_reopens_anchors_and_stays_hard(self) -> None:
        plan = solve_minimal_layout(
            localized_reservation_project(),
            effort_profile="quick",
        )

        self.assertEqual(
            plan["solver"]["result"]["status"],
            NO_SOLUTION_WITHIN_BUDGET,
        )
        self.assertIsNone(plan["solver"]["result"]["proof"])
        self.assertIn(
            "TOP_INSET_WITHOUT_SUPPORTING_BODY",
            {value["code"] for value in plan["diagnostics"]},
        )
        lanes = plan["minimal_layout"]["search_provenance"]["lanes"]
        bridge = next(
            value
            for value in lanes
            if value["lane_id"] == "historical_bridge_edge"
        )
        self.assertGreater(bridge["anchor_point_count"], 0)
        self.assertEqual(len(plan["placements"]), 0)

    def test_dense_11_by_34_case_stays_bounded_and_truthful(self) -> None:
        plan = solve_minimal_layout(
            dense_11_containers_34_contents_project(),
            effort_profile="quick",
        )

        self.assertEqual(
            plan["solver"]["result"]["status"],
            NO_SOLUTION_WITHIN_BUDGET,
        )
        self.assertIsNone(plan["solver"]["result"]["proof"])
        self.assertEqual(len(plan["placements"]), 0)
        self.assertIn(
            plan["solver"]["telemetry"]["stop_reason"],
            {"hard_budget_reached", "hard_time_budget_reached"},
        )
        provenance = plan["minimal_layout"]["search_provenance"]
        self.assertEqual(provenance["finalization_invocation_count"], 0)
        self.assertEqual(
            provenance["fusion_materialization_invocation_count"],
            0,
        )

    def test_one_shot_cancel_during_lane_stays_cancelled(self) -> None:
        calls = {"count": 0}

        def cancel_once_inside_lane() -> bool:
            calls["count"] += 1
            return calls["count"] == 3

        plan = solve_minimal_layout(
            simple_success_project(),
            effort_profile="quick",
            cancel_check=cancel_once_inside_lane,
        )

        self.assertEqual(
            plan["solver"]["result"]["status"],
            STALE_OR_CANCELLED,
        )
        self.assertEqual(
            plan["solver"]["telemetry"]["stop_reason"],
            "cancelled_during_search",
        )
        self.assertEqual(
            plan["minimal_layout"]["search_provenance"]["lanes"][0][
                "status"
            ],
            STALE_OR_CANCELLED,
        )

    def test_mismatched_incremental_effort_fails_closed(self) -> None:
        project = simple_success_project()
        engine = IncrementalLocalAnalysisEngine(
            project,
            effort_profile="normal",
        )

        plan = solve_minimal_layout(
            project,
            effort_profile="quick",
            container_frontiers=engine.certified_frontiers(),
            frontier_digests=engine.frontier_digests(),
        )

        self.assertEqual(plan["solver"]["result"]["status"], INVALID_INPUT)
        self.assertIn(
            "LOCAL_FRONTIER_EFFORT_MISMATCH",
            {value["code"] for value in plan["diagnostics"]},
        )


if __name__ == "__main__":
    unittest.main()
