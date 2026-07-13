from __future__ import annotations

from copy import deepcopy
import unittest

from board_game_insert_generator.volumetric_stage_solver import (
    MAX_CANDIDATES,
    SOLUTION_COMPLETE,
    SOLUTION_WITH_RESIDUALS,
    VOLUMETRIC_STAGE_SOLVER_SCHEMA_V1,
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
        self.assertEqual(result["clearances_mm"], {"xy": 0.6, "z": 0.6})
        self.assertEqual({item["origin_mm"]["z"] for item in plan["placements"]}, {0.0, 25.3})
        self.assertEqual(plan["support"]["status"], "supported")
        self.assertTrue(all(item["supported"] for item in plan["support"]["supports"]))
        self.assertEqual(
            [item["stage_id"] for item in plan["removal_sequence"][:2]],
            ["stage-2", "stage-2"],
        )

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


if __name__ == "__main__":
    unittest.main()
