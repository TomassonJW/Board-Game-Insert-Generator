from __future__ import annotations

from types import SimpleNamespace
import unittest

from board_game_insert_generator.reserved_floor_stack_solver import (
    RESERVED_FLOOR_STACK_VERSION,
    solve_reserved_floor_stacks,
)
from board_game_insert_generator.solver_outcome import (
    NO_SOLUTION_WITHIN_BUDGET,
    SOLUTION_FOUND,
)


def _variant(
    variant_id: str,
    size: tuple[float, float, float],
    *,
    canonical: bool,
) -> dict[str, object]:
    return {
        "variant_id": variant_id,
        "geometry_digest": f"digest-{variant_id}",
        "canonical": canonical,
        "minimum_outer_envelope_mm": {
            "x": size[0],
            "y": size[1],
            "z": size[2],
        },
    }


def _participant(
    participant_id: str,
    size: tuple[float, float, float],
    *,
    alternatives: tuple[tuple[str, tuple[float, float, float]], ...] = (),
) -> dict[str, object]:
    options = [_variant(f"{participant_id}-canonical", size, canonical=True)]
    options.extend(
        _variant(variant_id, variant_size, canonical=False)
        for variant_id, variant_size in alternatives
    )
    return {
        "id": participant_id,
        "role": "container",
        "name": participant_id,
        "container_internal_variant_options_v1": options,
    }


def _limit_case_participants() -> list[dict[str, object]]:
    participants = [
        _participant(
            "container:layout",
            (76.0, 76.0, 31.8),
            alternatives=(("layout-relayout", (76.0, 98.4, 31.8)),),
        )
    ]
    participants.extend(
        _participant(f"container:cards-{index}", (67.1, 92.5, 21.0))
        for index in range(5)
    )
    participants.extend(
        _participant(f"container:tall-{index}", (19.6, 36.2, 49.8))
        for index in range(2)
    )
    participants.append(
        _participant("container:small-low", (23.6, 23.6, 11.8))
    )
    participants.extend(
        _participant(f"container:small-{index}", (23.6, 23.6, 31.8))
        for index in range(9)
    )
    return participants


def _problem() -> SimpleNamespace:
    return SimpleNamespace(
        box={"x": 200.0, "y": 150.0, "z": 65.0},
        storage_height_mm=64.6,
        z_clearance_mm=0.6,
        xy_clearance_mm=0.6,
        box_xy_clearance_mm=0.6,
        top_inset_zones=(
            SimpleNamespace(
                origin_xy_mm=(49.4, 24.4),
                size_xy_mm=(101.2, 101.2),
                support_plane_z_mm=62.6,
            ),
        ),
    )


class ReservedFloorStackSolverTests(unittest.TestCase):
    def test_limit_case_builds_floor_stacks_below_the_virtual_tray(self) -> None:
        first = solve_reserved_floor_stacks(
            _limit_case_participants(),
            _problem(),
        )
        second = solve_reserved_floor_stacks(
            _limit_case_participants(),
            _problem(),
        )

        self.assertEqual(first.status, SOLUTION_FOUND)
        self.assertEqual(first.deterministic_digest, second.deterministic_digest)
        self.assertEqual(len(first.candidates[0]), 18)
        self.assertEqual(
            first.telemetry()["solver_version"],
            RESERVED_FLOOR_STACK_VERSION,
        )
        placements = first.candidates[0]
        self.assertTrue(
            any(value.supporting_ids != ("box-floor",) for value in placements)
        )
        layout = next(
            value
            for value in placements
            if value.participant_id == "container:layout"
        )
        self.assertEqual(layout.container_variant_id, "layout-relayout")
        zone = _problem().top_inset_zones[0]
        for placement in placements:
            x, y, z = placement.origin_mm
            width, depth, height = placement.world_size_mm
            overlaps = not (
                x + width <= zone.origin_xy_mm[0]
                or zone.origin_xy_mm[0] + zone.size_xy_mm[0] <= x
                or y + depth <= zone.origin_xy_mm[1]
                or zone.origin_xy_mm[1] + zone.size_xy_mm[1] <= y
            )
            if overlaps:
                self.assertLessEqual(
                    z + height,
                    zone.support_plane_z_mm + 0.0001,
                )

    def test_stops_without_claiming_impossibility(self) -> None:
        execution = solve_reserved_floor_stacks(
            _limit_case_participants(),
            _problem(),
            should_stop=lambda: True,
        )

        self.assertEqual(execution.status, NO_SOLUTION_WITHIN_BUDGET)
        self.assertTrue(execution.stopped)
        self.assertEqual(
            execution.stop_reason,
            "reserved_floor_stack_deadline_or_cancel_reached",
        )


if __name__ == "__main__":
    unittest.main()
