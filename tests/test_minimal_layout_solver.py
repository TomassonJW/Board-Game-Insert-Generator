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
    _floor_first_rank_axes,
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
    def test_floor_first_rank_precedes_compactness_between_complete_plans(self) -> None:
        common = {
            "base_z_sum_mm": 0.0,
            "elevated_volume_mm3": 0.0,
            "top_inset_obstructive_height_mm": 0.0,
            "cluster_footprint_mm2": 10_000.0,
            "elevated_stack_count": 0.0,
            "cluster_volume_mm3": 100_000.0,
            "internal_gap_mm3": 20_000.0,
            "cluster_height_mm": 10.0,
            "residual_fragmentation": 12.0,
            "contact_count": 0.0,
            "minimum_support_ratio": 1.0,
        }
        floor_plan = {
            "minimal_layout": {
                "metrics": {
                    **common,
                    "elevated_container_count": 0.0,
                }
            }
        }
        compact_stack_plan = {
            "minimal_layout": {
                "metrics": {
                    **common,
                    "elevated_container_count": 1.0,
                    "base_z_sum_mm": 10.6,
                    "elevated_volume_mm3": 4_000.0,
                    "cluster_footprint_mm2": 400.0,
                    "cluster_volume_mm3": 8_240.0,
                    "internal_gap_mm3": 240.0,
                    "cluster_height_mm": 20.6,
                    "elevated_stack_count": 1.0,
                }
            }
        }

        self.assertLess(
            _floor_first_rank_axes(floor_plan),
            _floor_first_rank_axes(compact_stack_plan),
        )
        low_obstruction_plan = deepcopy(compact_stack_plan)
        low_obstruction_metrics = low_obstruction_plan["minimal_layout"]["metrics"]
        low_obstruction_metrics["top_inset_obstructive_height_mm"] = 5.0
        low_obstruction_metrics["cluster_footprint_mm2"] = 8_000.0
        obstructive_compact_plan = deepcopy(compact_stack_plan)
        obstructive_metrics = obstructive_compact_plan["minimal_layout"]["metrics"]
        obstructive_metrics["top_inset_obstructive_height_mm"] = 20.0
        obstructive_metrics["cluster_footprint_mm2"] = 400.0
        self.assertLess(
            _floor_first_rank_axes(low_obstruction_plan),
            _floor_first_rank_axes(obstructive_compact_plan),
        )

    def test_every_container_stays_on_floor_when_the_complete_plan_fits(self) -> None:
        plan = solve_minimal_layout(
            _project_from_dimensions(
                {
                    "a": (15.0, 15.0, 8.0),
                    "b": (15.0, 15.0, 8.0),
                    "c": (15.0, 15.0, 8.0),
                },
                box=(90.0, 50.0, 30.0),
            ),
            effort_profile="quick",
        )

        self.assertEqual(plan["solver"]["result"]["status"], SOLUTION_FOUND)
        metrics = plan["minimal_layout"]["metrics"]
        self.assertEqual(metrics["elevated_container_count"], 0.0)
        self.assertEqual(metrics["base_z_sum_mm"], 0.0)
        self.assertEqual(metrics["elevated_volume_mm3"], 0.0)
        self.assertTrue(
            all(
                placement["origin_mm"]["z"] == 0.0
                for placement in plan["placements"]
                if placement["role"] == "container"
            )
        )
        selected = plan["minimal_layout"]["search_provenance"]["selected"]
        self.assertEqual(
            selected["floor_first_rank"]["elevated_container_count"],
            0.0,
        )

    def test_single_container_stays_minimal_and_residual_is_unassigned(self) -> None:
        plan = solve_minimal_layout(
            simple_success_project(),
            effort_profile="quick",
        )

        self.assertEqual(plan["solver"]["result"]["status"], SOLUTION_FOUND)
        self.assertTrue(plan["solver"]["result"]["materializable"])
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
        self.assertEqual(
            [item["name"] for item in portfolio["ranking_axes"][:6]],
            [
                "elevated_container_count",
                "base_z_sum_mm",
                "elevated_volume_mm3",
                "top_inset_obstructive_height_mm",
                "cluster_footprint_mm2",
                "elevated_stack_count",
            ],
        )
        self.assertEqual(
            set(portfolio["selected"]["floor_first_rank"]),
            {
                "elevated_container_count",
                "base_z_sum_mm",
                "elevated_volume_mm3",
                "top_inset_obstructive_height_mm",
                "cluster_footprint_mm2",
                "elevated_stack_count",
                "cluster_volume_mm3",
                "internal_gap_mm3",
                "cluster_height_mm",
                "residual_fragmentation",
                "contact_count",
                "minimum_support_ratio",
            },
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
        self.assertEqual(orderings["small_footprint_base"][0], "absolute-tall")

    def test_effort_lanes_and_total_deadlines_are_monotone_prefixes(self) -> None:
        efforts = ("quick", "short", "normal", "long", "deep")
        lanes = [minimal_lane_specs(value) for value in efforts]
        budgets = minimal_effort_budgets()

        for previous, current in zip(lanes, lanes[1:]):
            self.assertEqual(current[: len(previous)], previous)
        for previous, current in zip(budgets, budgets[1:]):
            self.assertTrue(current.is_at_least_as_permissive_as(previous))
        self.assertEqual([len(value) for value in lanes], [3, 4, 6, 8, 9])
        self.assertEqual(
            [dict(value.limits)["max_total_elapsed_ms"] for value in budgets],
            [3_000, 10_000, 20_000, 60_000, 180_000],
        )

    def test_global_deadline_preserves_a_certified_incumbent(self) -> None:
        project = simple_success_project()
        incumbent = solve_minimal_layout(project, effort_profile="normal")
        clock_values = [0.0, 0.0, 180_000.0]

        def deadline_clock() -> float:
            return clock_values.pop(0) if clock_values else 180_000.0

        with patch(
            "board_game_insert_generator.minimal_layout_solver._monotonic_ms",
            side_effect=deadline_clock,
        ):
            plan = solve_minimal_layout(
                project,
                effort_profile="deep",
                initial_incumbent=incumbent,
            )

        self.assertEqual(plan["solver"]["result"]["status"], SOLUTION_FOUND)
        provenance = plan["minimal_layout"]["search_provenance"]
        self.assertTrue(provenance["deadline_reached"])
        self.assertEqual(
            provenance["stop_reason"],
            "global_deadline_reached_with_candidate",
        )
        self.assertEqual(provenance["selected"]["candidate_source"], "certified_witness")
        self.assertTrue(plan["minimal_layout"]["global_certificate"]["certified"])

    def test_global_deadline_without_incumbent_is_not_impossibility(self) -> None:
        project = localized_reservation_project()
        clock_values = [0.0, 0.0, 180_000.0]

        def deadline_clock() -> float:
            return clock_values.pop(0) if clock_values else 180_000.0

        with patch(
            "board_game_insert_generator.minimal_layout_solver._monotonic_ms",
            side_effect=deadline_clock,
        ):
            plan = solve_minimal_layout(project, effort_profile="deep")

        self.assertEqual(
            plan["solver"]["result"]["status"],
            NO_SOLUTION_WITHIN_BUDGET,
        )
        self.assertIsNone(plan["solver"]["result"]["proof"])
        self.assertEqual(
            plan["solver"]["telemetry"]["stop_reason"],
            "global_deadline_reached_without_candidate",
        )
        self.assertFalse(plan["summary"]["materializable"])

    def test_deep_uses_one_prefix_without_hidden_finishing(self) -> None:
        plan = solve_minimal_layout(simple_success_project(), effort_profile="deep")

        self.assertEqual(plan["solver"]["result"]["status"], SOLUTION_FOUND)
        provenance = plan["minimal_layout"]["search_provenance"]
        self.assertEqual(provenance["budget"]["max_total_elapsed_ms"], 180_000)
        self.assertLessEqual(len(provenance["lanes"]), 9)
        self.assertEqual(provenance["finalization_invocation_count"], 0)

    def test_deep_flat_project_certifies_internal_prefix_before_scip(self) -> None:
        project = localized_reservation_project()

        with (
            patch(
                "board_game_insert_generator.minimal_layout_solver."
                "scip_product_runtime_configured",
                return_value=True,
            ),
            patch(
                "board_game_insert_generator.minimal_layout_solver."
                "solve_scip_product_3d"
            ) as external_solver,
        ):
            plan = solve_minimal_layout(project, effort_profile="deep")

        self.assertEqual(plan["solver"]["result"]["status"], SOLUTION_FOUND)
        external_solver.assert_not_called()
        provenance = plan["minimal_layout"]["search_provenance"]
        self.assertTrue(provenance["first_certified_lane_authority"])
        self.assertFalse(provenance["scip_fallback_invoked"])
        self.assertEqual(
            provenance["lane_prefix_ids"],
            ["historical_legacy_corner"],
        )
        self.assertIn(
            "external_scip_real_3d",
            provenance["skipped_lane_ids"],
        )
        self.assertEqual(
            provenance["selected"]["statement"],
            "best_certified_proposal_from_first_certified_lane_within_budget",
        )

    def test_deep_flat_prefix_failure_keeps_scip_as_honest_fallback(self) -> None:
        project = localized_reservation_project()
        prefix_report = {
            "lane_id": "historical_legacy_corner",
            "telemetry": {"search_states": 12},
        }

        def plan(
            status: str,
            *,
            lanes: list[dict[str, object]] | None = None,
        ) -> dict[str, object]:
            return {
                "solver": {
                    "result": {"status": status},
                    "telemetry": {"stop_reason": "bounded_test_result"},
                },
                "minimal_layout": {
                    "search_provenance": {
                        "lanes": lanes or [],
                    }
                },
            }

        prefix_failure = plan(
            NO_SOLUTION_WITHIN_BUDGET,
            lanes=[prefix_report],
        )
        projection_failure = plan(NO_SOLUTION_WITHIN_BUDGET)
        scip_success = plan(SOLUTION_FOUND)

        with (
            patch(
                "board_game_insert_generator.minimal_layout_solver."
                "scip_product_runtime_configured",
                return_value=True,
            ),
            patch(
                "board_game_insert_generator.minimal_layout_solver."
                "_solve_minimal_layout_once",
                side_effect=(
                    prefix_failure,
                    projection_failure,
                    scip_success,
                ),
            ) as solve_once,
        ):
            result = solve_minimal_layout(project, effort_profile="deep")

        self.assertIs(result, scip_success)
        self.assertEqual(solve_once.call_count, 3)
        first_call = solve_once.call_args_list[0].kwargs
        self.assertEqual(
            [value.lane_id for value in first_call["lane_specs_override"]],
            ["historical_legacy_corner"],
        )
        fallback_call = solve_once.call_args_list[2].kwargs
        self.assertTrue(fallback_call["external_lane_enabled"])
        self.assertEqual(
            fallback_call["prior_lane_reports"],
            (prefix_report,),
        )

    def test_open_thin_stack_is_allowed_by_envelope_support(self) -> None:
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
        self.assertTrue(plan["summary"]["materializable"])
        self.assertEqual(plan["stage_support"]["status"], "supported")
        self.assertEqual(plan["stage_support"]["certificate_kind"], "outer_envelope_v1")

    def test_necessary_large_below_small_inversion_remains_admissible(self) -> None:
        project = _project_from_dimensions(
            {
                "large": (20.0, 20.0, 10.0),
                "small": (4.0, 4.0, 10.0),
            },
            box=(25.6, 25.6, 25.0),
        )

        plan = solve_minimal_layout(project, effort_profile="normal")

        self.assertEqual(plan["solver"]["result"]["status"], SOLUTION_FOUND)
        placements = {value["container_group_id"]: value for value in plan["placements"]}
        self.assertLess(
            placements["large"]["origin_mm"]["z"],
            placements["small"]["origin_mm"]["z"],
        )
        small_support = next(
            value for value in plan["stage_support"]["supports"]
            if value["placement_id"] == "container:small"
        )
        self.assertEqual(small_support["supporting_ids"], ["container:large"])
        ranking = plan["minimal_layout"]["search_provenance"]["ranking_axes"]
        preference = next(
            value for value in ranking
            if value["name"] == "stacking_preference_violation_count"
        )
        self.assertFalse(preference["hard_constraint"])
        metrics = plan["minimal_layout"]["metrics"]
        self.assertEqual(metrics["elevated_container_count"], 1.0)
        self.assertGreater(metrics["base_z_sum_mm"], 0.0)
        self.assertGreater(metrics["elevated_volume_mm3"], 0.0)

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
            SOLUTION_FOUND,
        )
        self.assertTrue(plan["summary"]["materializable"])
        self.assertEqual(
            plan["top_inset_reservations"]["status"],
            "reserved_prisms_certified",
        )
        self.assertNotIn(
            "TOP_INSET_RESERVED_PRISM_COLLISION",
            {value["code"] for value in plan["diagnostics"]},
        )
        self.assertTrue(
            plan["minimal_layout"]["search_provenance"][
                "global_deadline_enforced"
            ]
        )
        lanes = plan["minimal_layout"]["search_provenance"]["lanes"]
        bridge = next(
            value
            for value in lanes
            if value["lane_id"] == "historical_bridge_edge"
        )
        self.assertGreater(bridge["anchor_point_count"], 0)
        self.assertEqual(len(plan["placements"]), 1)
        placement = plan["placements"][0]
        self.assertEqual(
            placement["final_outer_dimensions_mm"],
            placement["minimum_outer_envelope_mm"],
        )
        self.assertNotIn("reservation_required_z_compensation_mm", placement)
        self.assertTrue(plan["invariants"]["minimum_outer_dimensions_only"])
        self.assertTrue(plan["invariants"]["reservation_prisms_post_certified"])
        self.assertTrue(
            plan["invariants"]["minimal_flat_geometry_certified"]
        )
        self.assertFalse(
            plan["invariants"]["flat_items_create_positive_geometry"]
        )
        self.assertEqual(plan["summary"]["flat_positive_body_count"], 0)
        self.assertEqual(plan["summary"]["flat_positive_union_count"], 0)
        self.assertEqual(
            plan["summary"]["flat_positive_volume_mm3"],
            0.0,
        )
        flat_certificate = plan["minimal_layout"][
            "flat_geometry_certificate"
        ]
        self.assertTrue(flat_certificate["certified"])
        self.assertEqual(
            flat_certificate[
                "reservation_required_z_compensation_count"
            ],
            0,
        )
        self.assertIn(
            "minimal_flat_geometry_strictly_non_positive",
            {
                check["name"]
                for check in plan["minimal_layout"][
                    "global_certificate"
                ]["checks"]
                if check["passed"]
            },
        )
        self.assertFalse(plan["top_inset_reservations"]["cuts"])

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
