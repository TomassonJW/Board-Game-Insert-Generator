from __future__ import annotations

import unittest

from board_game_insert_generator.free_3d_greedy_solver import (
    Free3DPlacement,
    TopInsetZone,
)
from board_game_insert_generator.global_rectangular_closure import (
    close_global_rectangular_partition,
)
from board_game_insert_generator.solver_contract import SolverBudget


def _budget() -> SolverBudget:
    return SolverBudget(
        "global-closure-test",
        "normal",
        tuple(
            sorted(
                {
                    "max_closure_candidates": 20_000,
                    "max_closure_elapsed_ms": 5_000,
                }.items()
            )
        ),
    )


def _participant(
    identifier: str,
    *,
    modes: tuple[str, str, str] = ("auto", "auto", "auto"),
) -> dict[str, object]:
    return {
        "id": identifier,
        "role": "container",
        "dimension_modes": dict(zip(("x", "y", "z"), modes)),
    }


def _placement(
    identifier: str,
    origin: tuple[float, float, float],
    size: tuple[float, float, float],
) -> Free3DPlacement:
    return Free3DPlacement(
        identifier,
        "container",
        identifier,
        origin,
        size,
        size,
        0,
        ("box-floor",) if origin[2] == 0.0 else (),
        1.0 if origin[2] == 0.0 else 0.0,
    )


class GlobalRectangularClosureTests(unittest.TestCase):
    def test_fragmented_slicing_incumbent_closes_by_construction_and_balances(self) -> None:
        placements = (
            _placement("a", (0.0, 0.0, 0.0), (20.0, 20.0, 20.0)),
            _placement("b", (80.0, 0.0, 0.0), (20.0, 20.0, 20.0)),
            _placement("c", (0.0, 60.0, 0.0), (20.0, 20.0, 20.0)),
            _placement("d", (80.0, 60.0, 0.0), (20.0, 20.0, 20.0)),
        )
        result = close_global_rectangular_partition(
            tuple(_participant(value.participant_id) for value in placements),
            placements,
            {"x": 100.0, "y": 80.0, "z": 20.0},
            20.0,
            0.0,
            box_perimeter_xy_mm=0.0,
            between_bodies_z_mm=0.0,
            budget=_budget(),
        )

        self.assertEqual(result.status, "closed")
        self.assertFalse(result.empty_spaces)
        self.assertTrue(result.partition_certificate["certified"])
        self.assertTrue(
            result.partition_certificate["partition_complete_by_construction"]
        )
        self.assertEqual(
            result.partition_certificate["printable_residual_volume_mm3"],
            0.0,
        )
        self.assertEqual(result.objective_score[0], 0.0)
        self.assertEqual(
            {value.world_size_mm for value in result.placements},
            {(50.0, 40.0, 20.0)},
        )

    def test_fixed_axis_is_preserved_and_split_gap_is_certified_technical_void(self) -> None:
        placements = (
            _placement("fixed", (0.0, 0.0, 0.0), (20.0, 40.0, 20.0)),
            _placement("auto", (40.0, 0.0, 0.0), (20.0, 40.0, 20.0)),
        )
        result = close_global_rectangular_partition(
            (
                _participant("fixed", modes=("fixed", "auto", "auto")),
                _participant("auto"),
            ),
            placements,
            {"x": 100.0, "y": 40.0, "z": 20.0},
            20.0,
            2.0,
            box_perimeter_xy_mm=0.0,
            between_bodies_z_mm=0.0,
            budget=_budget(),
        )

        by_id = {value.participant_id: value for value in result.placements}
        self.assertEqual(result.status, "closed")
        self.assertEqual(by_id["fixed"].world_size_mm[0], 20.0)
        self.assertEqual(by_id["auto"].origin_mm[0], 22.0)
        self.assertEqual(by_id["auto"].world_size_mm[0], 78.0)
        self.assertEqual(
            result.partition_certificate["technical_void_volume_mm3"],
            1600.0,
        )
        self.assertTrue(
            result.partition_certificate["technical_voids_certified"]
        )

    def test_upper_reservation_is_one_fixed_void_and_side_volume_remains_printable(self) -> None:
        placements = (
            _placement("below", (0.0, 0.0, 0.0), (20.0, 20.0, 10.0)),
            _placement("side", (60.0, 0.0, 0.0), (20.0, 20.0, 20.0)),
        )
        result = close_global_rectangular_partition(
            (_participant("below"), _participant("side")),
            placements,
            {"x": 100.0, "y": 60.0, "z": 40.0},
            40.0,
            0.0,
            box_perimeter_xy_mm=0.0,
            between_bodies_z_mm=0.0,
            budget=_budget(),
            top_inset_zones=(
                TopInsetZone(
                    origin_xy_mm=(0.0, 0.0),
                    size_xy_mm=(60.0, 60.0),
                    support_plane_z_mm=30.0,
                    inset_depth_mm=10.0,
                ),
            ),
        )

        by_id = {value.participant_id: value for value in result.placements}
        self.assertEqual(result.status, "closed")
        self.assertEqual(by_id["below"].world_size_mm, (60.0, 60.0, 30.0))
        self.assertEqual(by_id["side"].world_size_mm, (40.0, 60.0, 40.0))
        self.assertEqual(
            result.partition_certificate["reserved_prism_volume_mm3"],
            36_000.0,
        )
        self.assertEqual(
            result.partition_certificate["printable_residual_volume_mm3"],
            0.0,
        )
        self.assertFalse(
            result.partition_certificate["composite_annexes_used"]
        )

    def test_fixed_single_body_cannot_claim_unowned_printable_volume(self) -> None:
        placement = _placement(
            "fixed",
            (0.0, 0.0, 0.0),
            (20.0, 20.0, 20.0),
        )
        result = close_global_rectangular_partition(
            (_participant("fixed", modes=("fixed", "fixed", "fixed")),),
            (placement,),
            {"x": 100.0, "y": 40.0, "z": 20.0},
            20.0,
            0.0,
            box_perimeter_xy_mm=0.0,
            between_bodies_z_mm=0.0,
            budget=_budget(),
        )

        self.assertEqual(
            result.status,
            "no_global_rectangular_partition",
        )
        self.assertTrue(result.empty_spaces)
        self.assertFalse(result.partition_certificate["certified"])
        self.assertGreater(
            result.partition_certificate["printable_residual_volume_mm3"],
            0.0,
        )


if __name__ == "__main__":
    unittest.main()
