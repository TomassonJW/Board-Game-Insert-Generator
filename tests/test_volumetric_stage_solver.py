from __future__ import annotations

from copy import deepcopy
import unittest

from board_game_insert_generator.volumetric_stage_solver import (
    MAX_ADAPTIVE_STAGE_COUNTS,
    MAX_CANDIDATES,
    MAX_ORDERINGS,
    SOLUTION_COMPLETE,
    SOLUTION_WITH_RESIDUALS,
    VOLUMETRIC_STAGE_SOLVER_SCHEMA_V1,
    _rebalance_stack_top_height_for_inset,
    solve_stage_portfolio,
)


def participant(
    index: int,
    *,
    x: float = 20.0,
    y: float = 20.0,
    z: float = 10.0,
    modes: dict[str, str] | None = None,
    targets: dict[str, float | None] | None = None,
) -> dict[str, object]:
    return {
        "id": f"container:g{index}",
        "role": "container",
        "container_group_id": f"g{index}",
        "name": f"Bac {index}",
        "minimum_local_mm": {"x": x, "y": y, "z": z},
        "dimension_modes": modes or {"x": "auto", "y": "auto", "z": "auto"},
        "target_local_mm": targets or {"x": None, "y": None, "z": None},
        "surplus_preference": "balanced",
    }


class VolumetricStageSolverTests(unittest.TestCase):
    def test_single_stage_complete_plan_is_deterministic_and_bounded(self) -> None:
        values = [participant(0), participant(1)]

        first = solve_stage_portfolio(values, {"x": 100.0, "y": 60.0, "z": 40.0}, 40.0, 1.0)
        second = solve_stage_portfolio(values, {"x": 100.0, "y": 60.0, "z": 40.0}, 40.0, 1.0)

        self.assertEqual(first, second)
        self.assertEqual(first["schema_version"], VOLUMETRIC_STAGE_SOLVER_SCHEMA_V1)
        self.assertEqual(first["status"], SOLUTION_COMPLETE)
        self.assertEqual(first["best_candidate"]["stage_count"], 1)
        self.assertLessEqual(first["search"]["candidate_count"], MAX_CANDIDATES)
        self.assertFalse(first["search"]["globally_optimal"])

    def test_xy_pressure_creates_two_supported_stages_with_nonzero_z(self) -> None:
        values = [participant(index, x=21.6, y=21.6, z=21.8) for index in range(4)]

        result = solve_stage_portfolio(values, {"x": 50.0, "y": 25.0, "z": 50.0}, 50.0, 0.6)
        plan = result["best_candidate"]

        self.assertEqual(result["status"], SOLUTION_COMPLETE)
        self.assertEqual(plan["stage_count"], 2)
        self.assertEqual(result["clearances_mm"], {"xy": 0.6, "z": 0.6, "box_xy": 0.6, "between_xy": 0.6, "between_z": 0.6})
        self.assertEqual({item["origin_mm"]["z"] for item in plan["placements"]}, {0.0, 25.3})
        self.assertEqual(plan["support"]["status"], "supported")
        self.assertTrue(all(item["supported"] for item in plan["support"]["supports"]))
        self.assertEqual(
            [item["stage_id"] for item in plan["removal_sequence"][:2]],
            ["stage-2", "stage-2"],
        )

    def test_box_xy_and_between_xy_clearances_are_independent(self) -> None:
        values = [
            participant(index, x=10.0, y=5.0, z=5.0, modes={"x": "fixed", "y": "fixed", "z": "fixed"}, targets={"x": 10.0, "y": 5.0, "z": 5.0})
            for index in range(2)
        ]

        separated = solve_stage_portfolio(
            values, {"x": 30.0, "y": 10.0, "z": 10.0}, 10.0, 2.0, box_clearance_mm=1.0
        )
        touching = solve_stage_portfolio(
            values, {"x": 30.0, "y": 10.0, "z": 10.0}, 10.0, 0.0, box_clearance_mm=1.0
        )

        separated_placements = sorted(separated["best_candidate"]["placements"], key=lambda item: item["origin_mm"]["x"])
        edge_aligned = solve_stage_portfolio(
            values, {"x": 30.0, "y": 10.0, "z": 10.0}, 10.0, 2.0, box_clearance_mm=0.0
        )

        touching_placements = sorted(touching["best_candidate"]["placements"], key=lambda item: item["origin_mm"]["x"])
        edge_aligned_placements = sorted(edge_aligned["best_candidate"]["placements"], key=lambda item: item["origin_mm"]["x"])
        self.assertEqual(separated["clearances_mm"]["box_xy"], 1.0)
        self.assertEqual(separated["clearances_mm"]["between_xy"], 2.0)
        self.assertEqual(separated_placements[0]["origin_mm"]["x"], 1.0)
        self.assertEqual(separated_placements[1]["origin_mm"]["x"] - separated_placements[0]["origin_mm"]["x"] - 10.0, 2.0)
        self.assertEqual(touching_placements[0]["origin_mm"]["x"], 1.0)
        self.assertEqual(touching_placements[1]["origin_mm"]["x"] - touching_placements[0]["origin_mm"]["x"] - 10.0, 0.0)
        self.assertEqual(edge_aligned["clearances_mm"]["box_xy"], 0.0)
        self.assertEqual(edge_aligned_placements[0]["origin_mm"]["x"], 0.0)
        self.assertEqual(edge_aligned_placements[1]["origin_mm"]["x"] - edge_aligned_placements[0]["origin_mm"]["x"] - 10.0, 2.0)

    def test_fixed_axis_is_hard_and_target_axis_is_soft(self) -> None:
        fixed = participant(
            0,
            modes={"x": "fixed", "y": "auto", "z": "auto"},
            targets={"x": 30.0, "y": None, "z": None},
        )
        target = participant(
            1,
            modes={"x": "target", "y": "auto", "z": "auto"},
            targets={"x": 50.0, "y": None, "z": None},
        )

        result = solve_stage_portfolio([fixed, target], {"x": 100.0, "y": 50.0, "z": 40.0}, 40.0, 1.0)
        by_id = {item["id"]: item for item in result["best_candidate"]["placements"]}
        fixed_axis = by_id["container:g0"]["dimension_contract"]["axes"]["x"]
        target_axis = by_id["container:g1"]["dimension_contract"]["axes"]["x"]

        self.assertEqual(result["status"], SOLUTION_COMPLETE)
        self.assertEqual(fixed_axis["mode"], "fixed")
        self.assertEqual(fixed_axis["calculated_mm"], 30.0)
        self.assertEqual(target_axis["mode"], "target")
        self.assertIn(target_axis["status"], {"satisfied", "deviated"})

    def test_fixed_small_body_returns_residual_and_non_mutating_suggestion(self) -> None:
        value = participant(
            0,
            modes={"x": "fixed", "y": "fixed", "z": "fixed"},
            targets={"x": 20.0, "y": 20.0, "z": 10.0},
        )
        original = deepcopy(value)

        result = solve_stage_portfolio([value], {"x": 100.0, "y": 80.0, "z": 40.0}, 40.0, 1.0)
        plan = result["best_candidate"]

        self.assertEqual(result["status"], SOLUTION_WITH_RESIDUALS)
        self.assertGreater(plan["residuals"]["residual_volume_mm3"], 0.0)
        self.assertTrue(plan["suggestions"])
        self.assertTrue(plan["suggestions"][0]["requires_confirmation"])
        self.assertFalse(plan["suggestions"][0]["automatic"])
        self.assertTrue(plan["volume_conservation"]["conserved"])
        self.assertEqual(value, original)
        self.assertEqual(len(plan["placements"]), 1)

    def test_hybrid_columns_allow_a_tall_body_beside_three_short_stacks(self) -> None:
        values = [participant(0, x=36.0, y=28.2, z=49.8)]
        values.extend(
            participant(index, x=69.6, y=94.6, z=25.8)
            for index in range(1, 7)
        )

        result = solve_stage_portfolio(
            values,
            {"x": 240.0, "y": 180.0, "z": 70.0},
            70.0,
            0.6,
        )
        plan = result["best_candidate"]

        self.assertEqual(result["status"], SOLUTION_COMPLETE)
        self.assertIn("stack_partition_index", plan["search_origin"])
        self.assertEqual({item["origin_mm"]["z"] for item in plan["placements"]}, {0.0, 35.3})
        self.assertTrue(any(stage["spanning_body_ids"] for stage in plan["stages"]))
        self.assertEqual(plan["support"]["status"], "supported")
        self.assertTrue(plan["volume_conservation"]["conserved"])
        self.assertEqual(plan["residuals"]["residual_volume_mm3"], 0.0)
    def test_preference_changes_scores_without_changing_hard_constraints(self) -> None:
        values = [participant(index, x=20.0 + index * 2.0) for index in range(3)]

        balanced = solve_stage_portfolio(values, {"x": 120.0, "y": 70.0, "z": 50.0}, 50.0, 1.0)
        reduced = solve_stage_portfolio(
            values,
            {"x": 120.0, "y": 70.0, "z": 50.0},
            50.0,
            1.0,
            preference="material_reduced",
        )

        self.assertEqual(balanced["status"], SOLUTION_COMPLETE)
        self.assertEqual(reduced["status"], SOLUTION_COMPLETE)
        self.assertEqual(
            {item["id"] for item in balanced["best_candidate"]["placements"]},
            {item["id"] for item in reduced["best_candidate"]["placements"]},
        )
        self.assertNotEqual(
            balanced["best_candidate"]["score_breakdown"]["total"],
            reduced["best_candidate"]["score_breakdown"]["total"],
        )

    def test_balanced_builds_z_progressively_while_compact_stays_simple(self) -> None:
        box = {"x": 160.0, "y": 120.0, "z": 100.0}

        stage_counts = []
        for count in (2, 8, 32):
            result = solve_stage_portfolio(
                [participant(index, z=20.0) for index in range(count)],
                box,
                100.0,
                1.0,
                preference="balanced",
            )
            stage_counts.append(result["best_candidate"]["stage_count"])
            self.assertIn("spatial_balance", result["best_candidate"]["score_breakdown"])
            self.assertIn("stage_load_balance", result["best_candidate"]["score_breakdown"])

        compact = solve_stage_portfolio(
            [participant(index, z=20.0) for index in range(8)],
            box,
            100.0,
            1.0,
            preference="compact",
        )

        self.assertEqual(stage_counts, [1, 2, 3])
        self.assertEqual(compact["best_candidate"]["stage_count"], 1)

    def test_diversified_order_seed_is_single_order_bounded_and_deterministic(self) -> None:
        values = [participant(index) for index in range(6)]
        first = solve_stage_portfolio(
            values,
            {"x": 160.0, "y": 120.0, "z": 80.0},
            80.0,
            0.6,
            diversified_order_seed=2,
        )
        second = solve_stage_portfolio(
            values,
            {"x": 160.0, "y": 120.0, "z": 80.0},
            80.0,
            0.6,
            diversified_order_seed=2,
        )

        self.assertEqual(first["search"]["ordering_count"], 1)
        self.assertEqual(first["search"]["diversified_order_seed"], 2)
        self.assertEqual(first["candidates"], second["candidates"])
        self.assertTrue(
            all(
                item["search_origin"]["order"] == "diversified_2"
                for item in first["candidates"]
            )
        )

    def test_constraint_directed_stack_transfers_lower_surplus_to_safe_top(self) -> None:
        lower = participant(0, z=10.0)
        upper = participant(1, z=10.0)
        upper["top_inset_search_hint_v1"] = {
            "required_safe_height_mm": 16.0,
            "floor_thickness_mm": 1.0,
            "cavities": [
                {
                    "local_origin_mm": {"x": 0.0, "y": 0.0, "z": 1.0},
                    "inner_dimensions_mm": {"x": 20.0, "y": 20.0, "z": 10.0},
                }
            ],
        }
        descriptor = {
            "stack_members": [
                {"participant": lower},
                {"participant": upper},
            ],
            "top_inset_layout_subject": {
                "participant": upper,
                "body_height_mm": 15.0,
                "rotated_xy": False,
            },
        }
        item_layout = {
            "origin_mm": {"x": 0.0, "y": 0.0},
            "world_size_mm": {"x": 20.0, "y": 20.0},
        }
        context = {
            "reservations": [
                {
                    "cut_origin_mm": {"x": 0.0, "y": 0.0},
                    "cut_size_mm": {"x": 20.0, "y": 20.0},
                    "inset_depth_from_top_mm": 5.0,
                }
            ]
        }

        adjusted = _rebalance_stack_top_height_for_inset(
            descriptor,
            item_layout,
            [15.0, 15.0],
            context,
        )

        self.assertEqual(adjusted, [14.0, 16.0])
        self.assertEqual(sum(adjusted), 30.0)
        self.assertGreaterEqual(adjusted[0], 10.0)
    def test_structured_headroom_order_is_single_order_bounded_and_deterministic(self) -> None:
        values = [participant(index) for index in range(3)]
        for value, deficit in zip(values, (5.0, 0.0, 2.0)):
            value["top_inset_search_hint_v1"] = {
                "headroom_deficit_mm": deficit,
            }

        first = solve_stage_portfolio(
            values,
            {"x": 90.0, "y": 40.0, "z": 30.0},
            30.0,
            0.6,
            structured_order_strategy="top_inset_headroom_asc",
        )
        second = solve_stage_portfolio(
            values,
            {"x": 90.0, "y": 40.0, "z": 30.0},
            30.0,
            0.6,
            structured_order_strategy="top_inset_headroom_asc",
        )

        self.assertEqual(first["candidates"], second["candidates"])
        self.assertEqual(first["search"]["ordering_count"], 1)
        self.assertEqual(
            first["search"]["structured_order_strategy"],
            "top_inset_headroom_asc",
        )

        single_row = next(
            item for item in first["candidates"]
            if ":g3:width:1s" in item["candidate_id"]
        )
        ordered_ids = [
            item["id"]
            for item in sorted(
                single_row["placements"],
                key=lambda item: item["origin_mm"]["x"],
            )
        ]
        self.assertEqual(
            ordered_ids,
            ["container:g1", "container:g2", "container:g0"],
        )

    def test_structured_and_hash_orders_are_mutually_exclusive(self) -> None:
        with self.assertRaisesRegex(
            ValueError,
            "cannot combine hash diversification",
        ):
            solve_stage_portfolio(
                [participant(0)],
                {"x": 40.0, "y": 40.0, "z": 20.0},
                20.0,
                0.6,
                diversified_order_seed=0,
                structured_order_strategy="area_interleave",
            )

    def test_adaptive_partition_solves_dense_variable_footprints(self) -> None:
        dimensions = [
            (198.9, 233.6, 90.7),
            (133.0, 88.4, 90.7),
            (67.1, 131.6, 90.7),
            (67.1, 88.4, 90.7),
            (67.1, 87.6, 90.7),
            *[(67.1, 22.8, 90.7) for _ in range(25)],
        ]
        values = [
            participant(index, x=x, y=y, z=z)
            for index, (x, y, z) in enumerate(dimensions)
        ]

        result = solve_stage_portfolio(
            values,
            {"x": 400.0, "y": 300.0, "z": 183.0},
            183.0,
            0.6,
            box_clearance_mm=0.6,
            vertical_clearance_mm=0.6,
            preference="balanced",
        )
        plan = result["best_candidate"]

        self.assertEqual(result["status"], SOLUTION_COMPLETE)
        self.assertEqual(plan["stage_count"], 2)
        self.assertIn("adaptive_stage_count", plan["search_origin"])
        self.assertEqual(sum(stage["body_count"] for stage in plan["stages"]), 30)
        self.assertTrue(all(stage["body_count"] > 0 for stage in plan["stages"]))
        self.assertGreater(plan["score_breakdown"]["stage_load_balance"], 95.0)
        self.assertLessEqual(
            result["search"]["adaptive_partitions_evaluated"],
            MAX_ORDERINGS * MAX_ADAPTIVE_STAGE_COUNTS,
        )


if __name__ == "__main__":
    unittest.main()
