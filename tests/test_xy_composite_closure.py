from __future__ import annotations

import unittest
from unittest.mock import patch

from board_game_insert_generator.free_3d_greedy_solver import (
    EmptySpace,
    Free3DPlacement,
    TopInsetZone,
)
from board_game_insert_generator.free_3d_continuous_closure import (
    Free3DClosureResult,
)
from board_game_insert_generator.global_rectangular_closure import (
    GlobalRectangularClosureResult,
)
from board_game_insert_generator.solver_contract import SolverBudget
from board_game_insert_generator.xy_composite_closure import (
    close_xy_composite_partition,
    xy_composite_closure_to_dict,
)


def _budget(
    *,
    max_candidates: int = 20_000,
    max_elapsed_ms: int = 5_000,
) -> SolverBudget:
    return SolverBudget(
        "xy-composite-test",
        "normal",
        tuple(
            sorted(
                {
                    "max_closure_candidates": max_candidates,
                    "max_closure_elapsed_ms": max_elapsed_ms,
                }.items()
            )
        ),
    )


def _participant() -> dict[str, object]:
    return {
        "id": "container:a",
        "role": "container",
        "dimension_modes": {"x": "auto", "y": "auto", "z": "auto"},
    }


def _participant_for(owner_id: str) -> dict[str, object]:
    return {
        "id": owner_id,
        "role": "container",
        "dimension_modes": {"x": "auto", "y": "auto", "z": "auto"},
    }


def _placement() -> Free3DPlacement:
    return Free3DPlacement(
        "container:a",
        "container",
        "a",
        (40.0, 30.0, 0.0),
        (20.0, 20.0, 20.0),
        (20.0, 20.0, 20.0),
        0,
        ("box-floor",),
        1.0,
    )


def _placement_for(
    owner_id: str,
    origin_mm: tuple[float, float, float],
    size_mm: tuple[float, float, float],
) -> Free3DPlacement:
    return Free3DPlacement(
        owner_id,
        "container",
        owner_id,
        origin_mm,
        size_mm,
        size_mm,
        0,
        ("box-floor",),
        1.0,
    )


def _continuous_prefill(
    placements: tuple[Free3DPlacement, ...],
    spaces: tuple[EmptySpace, ...],
) -> Free3DClosureResult:
    residual_volume = sum(value.volume_mm3 for value in spaces)
    metric = (
        residual_volume,
        max((value.volume_mm3 for value in spaces), default=0.0),
        len(spaces),
    )
    return Free3DClosureResult(
        "not_closed",
        placements,
        spaces,
        1,
        1,
        metric,
        metric,
        0,
        0,
        0,
        0,
        False,
        "prefill-incumbent",
        "closure_only",
        (0.0, 0.0, 0.0, 0.0),
        1,
        "prefill",
        "prefill-digest",
    )


def _failed_rectangular_attempt(
    placements: tuple[Free3DPlacement, ...],
    spaces: tuple[EmptySpace, ...],
) -> GlobalRectangularClosureResult:
    residual_volume = sum(value.volume_mm3 for value in spaces)
    metric = (
        residual_volume,
        max((value.volume_mm3 for value in spaces), default=0.0),
        len(spaces),
    )
    return GlobalRectangularClosureResult(
        "not_closed",
        placements,
        spaces,
        "rectangular-digest",
        "rectangular-incumbent",
        1,
        1,
        0,
        0,
        0,
        False,
        metric,
        metric,
        0,
        "closure_only",
        (0.0, 0.0, 0.0, 0.0),
        1,
        "rectangular",
        {
            "certified": False,
            "printable_residual_volume_mm3": residual_volume,
        },
    )


def _hybrid_result(
    placements: tuple[Free3DPlacement, ...],
    spaces: tuple[EmptySpace, ...],
    *,
    box: dict[str, float],
    xy_clearance_mm: float = 2.0,
    budget: SolverBudget | None = None,
    top_inset_zones: tuple[TopInsetZone, ...] = (),
):
    return close_xy_composite_partition(
        tuple(_participant_for(value.participant_id) for value in placements),
        placements,
        box,
        box["z"],
        xy_clearance_mm,
        box_perimeter_xy_mm=0.0,
        between_bodies_z_mm=2.0,
        budget=budget or _budget(),
        top_inset_zones=top_inset_zones,
        rectangular_attempt=_failed_rectangular_attempt(placements, spaces),
        continuous_prefill=_continuous_prefill(placements, spaces),
    )


def _zone(*, support_plane_z_mm: float, inset_depth_mm: float) -> TopInsetZone:
    return TopInsetZone(
        origin_xy_mm=(0.0, 0.0),
        size_xy_mm=(30.0, 20.0),
        support_plane_z_mm=support_plane_z_mm,
        inset_depth_mm=inset_depth_mm,
    )


class XYCompositeClosureTests(unittest.TestCase):
    def test_dense_reserved_composition_tries_rectangular_closure_first(
        self,
    ) -> None:
        placements = tuple(
            _placement_for(
                f"container:{index:02d}",
                (float(index * 10), 0.0, 0.0),
                (10.0, 10.0, 5.0),
            )
            for index in range(12)
        )
        spaces = (EmptySpace((0.0, 0.0, 5.0), (120.0, 10.0, 3.0)),)

        result = _hybrid_result(
            placements,
            spaces,
            box={"x": 120.0, "y": 10.0, "z": 10.0},
            xy_clearance_mm=0.0,
            top_inset_zones=(
                TopInsetZone((0.0, 0.0), (120.0, 10.0), 8.0, 2.0),
            ),
        )

        self.assertEqual(result.status, "closed")
        self.assertEqual(
            result.stop_reason,
            "xy_composite_partition_complete",
        )
        self.assertEqual(
            result.certificate["schema_version"],
            "bgig.xy_composite_partition_certificate.v1",
        )
        self.assertEqual(len(result.owner_bodies), 12)
        self.assertTrue(
            result.certificate[
                "reservation_subtractions_deferred_to_cad_ir"
            ]
        )

    def test_hybrid_uses_rectangular_extension_before_xy_annexes(self) -> None:
        source = _placement_for(
            "container:a",
            (0.0, 0.0, 0.0),
            (10.0, 10.0, 10.0),
        )
        spaces = (EmptySpace((0.0, 0.0, 12.0), (10.0, 10.0, 8.0)),)

        result = _hybrid_result(
            (source,),
            spaces,
            box={"x": 10.0, "y": 10.0, "z": 20.0},
        )

        self.assertEqual(result.status, "closed")
        self.assertEqual(
            result.certificate["schema_version"],
            "bgig.xy_composite_partition_certificate.v2",
        )
        self.assertEqual(
            result.certificate["assignment_trace"][0]["attachment_axis"],
            "rectangular_z_extension",
        )
        self.assertTrue(result.certificate["owner_unions_connected"])

    def test_annex_consumes_every_covered_residual_cell(self) -> None:
        source = _placement_for(
            "container:a",
            (0.0, 0.0, 0.0),
            (10.0, 10.0, 20.0),
        )
        spaces = (
            EmptySpace((12.0, 0.0, 0.0), (8.0, 10.0, 15.0)),
            EmptySpace((12.0, 0.0, 15.0), (8.0, 10.0, 5.0)),
        )

        result = _hybrid_result(
            (source,),
            spaces,
            box={"x": 20.0, "y": 10.0, "z": 20.0},
        )

        self.assertEqual(result.status, "closed")
        trace = result.certificate["assignment_trace"]
        self.assertEqual(len(trace), 1)
        self.assertEqual(trace[0]["covered_residual_cell_count"], 2)
        self.assertEqual(
            result.certificate["assigned_residual_cell_count"],
            2,
        )
        self.assertEqual(
            result.certificate["printable_residual_volume_mm3"],
            0.0,
        )

    def test_hybrid_closes_an_inner_hole_without_moving_any_source(self) -> None:
        placements = (
            _placement_for("container:a", (0.0, 0.0, 0.0), (10.0, 30.0, 10.0)),
            _placement_for("container:b", (20.0, 0.0, 0.0), (10.0, 30.0, 10.0)),
            _placement_for("container:c", (12.0, 0.0, 0.0), (6.0, 10.0, 10.0)),
            _placement_for("container:d", (12.0, 20.0, 0.0), (6.0, 10.0, 10.0)),
        )
        spaces = (EmptySpace((12.0, 12.0, 0.0), (6.0, 6.0, 10.0)),)

        result = _hybrid_result(
            placements,
            spaces,
            box={"x": 30.0, "y": 30.0, "z": 10.0},
        )

        self.assertEqual(result.status, "closed")
        self.assertEqual(
            result.stop_reason,
            "xy_composite_residual_partition_complete",
        )
        self.assertEqual(
            result.certificate["printable_residual_volume_mm3"],
            0.0,
        )
        self.assertTrue(result.certificate["source_minimum_envelopes_frozen"])
        self.assertTrue(result.certificate["cavity_world_poses_unchanged"])
        self.assertEqual(
            tuple(value.source_placement for value in result.owner_bodies),
            placements,
        )

    def test_hybrid_reclaims_only_the_owner_seam_at_an_edge(self) -> None:
        source = _placement_for(
            "container:a",
            (0.0, 0.0, 0.0),
            (10.0, 10.0, 10.0),
        )
        spaces = (EmptySpace((12.0, 2.0, 0.0), (8.0, 6.0, 10.0)),)
        result = _hybrid_result(
            (source,),
            spaces,
            box={"x": 20.0, "y": 10.0, "z": 20.0},
            top_inset_zones=(
                TopInsetZone((10.0, 0.0), (10.0, 10.0), 10.0, 10.0),
            ),
        )

        self.assertEqual(result.status, "closed")
        owner = result.owner_bodies[0]
        self.assertEqual(owner.source_placement, source)
        self.assertGreater(owner.certificate["annex_count"], 0)
        self.assertEqual(
            result.certificate["internal_owner_annex_clearance_mm"],
            0.0,
        )
        self.assertGreater(
            result.certificate["internal_clearance_removed_volume_mm3"],
            0.0,
        )
        self.assertTrue(result.certificate["top_reservations_excluded"])
        self.assertTrue(
            result.certificate[
                "unions_before_cavities_and_reservation_cuts"
            ]
        )

    def test_two_owner_choice_is_stable_and_keeps_external_corridor(self) -> None:
        left = _placement_for(
            "container:a",
            (0.0, 0.0, 0.0),
            (10.0, 10.0, 10.0),
        )
        right = _placement_for(
            "container:b",
            (20.0, 0.0, 0.0),
            (10.0, 10.0, 10.0),
        )
        spaces = (EmptySpace((12.0, 2.0, 0.0), (6.0, 6.0, 10.0)),)

        forward = _hybrid_result(
            (left, right),
            spaces,
            box={"x": 30.0, "y": 10.0, "z": 10.0},
        )
        reverse = _hybrid_result(
            (right, left),
            spaces,
            box={"x": 30.0, "y": 10.0, "z": 10.0},
        )

        self.assertEqual(forward.status, "closed")
        self.assertEqual(
            forward.deterministic_digest,
            reverse.deterministic_digest,
        )
        self.assertEqual(
            forward.certificate["assignment_trace"][0]["owner_id"],
            "container:a",
        )
        self.assertTrue(forward.certificate["external_clearances_certified"])
        left_owner = next(
            value
            for value in forward.owner_bodies
            if value.owner_id == "container:a"
        )
        left_upper_x = max(
            value.origin_mm[0] + value.size_mm[0]
            for value in left_owner.prisms
        )
        self.assertEqual(left_upper_x, 18.0)
        self.assertEqual(right.origin_mm[0] - left_upper_x, 2.0)

    def test_vertical_inter_owner_clearance_is_not_printable_residual(
        self,
    ) -> None:
        lower = _placement_for(
            "container:lower",
            (0.0, 0.0, 0.0),
            (10.0, 10.0, 10.0),
        )
        upper = _placement_for(
            "container:upper",
            (0.0, 0.0, 12.0),
            (10.0, 10.0, 8.0),
        )

        result = _hybrid_result(
            (lower, upper),
            (EmptySpace((0.0, 0.0, 10.0), (10.0, 10.0, 2.0)),),
            box={"x": 10.0, "y": 10.0, "z": 20.0},
        )

        self.assertEqual(result.status, "closed")
        self.assertEqual(
            result.certificate["printable_residual_volume_mm3"],
            0.0,
        )
        self.assertEqual(result.certificate["assignment_trace"], [])
        self.assertTrue(result.certificate["external_clearances_certified"])

    def test_xy_z_clearance_junction_is_split_and_kept_void(self) -> None:
        lower = _placement_for(
            "container:lower",
            (0.0, 0.0, 0.0),
            (10.0, 5.4, 10.0),
        )
        upper = _placement_for(
            "container:upper",
            (0.0, 0.0, 12.0),
            (10.0, 6.0, 8.0),
        )
        side = _placement_for(
            "container:side",
            (0.0, 6.0, 0.0),
            (10.0, 4.0, 10.0),
        )

        result = _hybrid_result(
            (lower, upper, side),
            (EmptySpace((0.0, 0.0, 10.0), (10.0, 6.0, 2.0)),),
            box={"x": 10.0, "y": 10.0, "z": 20.0},
            xy_clearance_mm=0.6,
        )

        self.assertEqual(result.status, "closed")
        self.assertEqual(
            result.certificate["printable_residual_volume_mm3"],
            0.0,
        )
        self.assertTrue(result.certificate["external_clearances_certified"])

    def test_hybrid_rejects_z_only_edge_point_and_floating_cells(self) -> None:
        source = _placement_for(
            "container:a",
            (0.0, 0.0, 0.0),
            (10.0, 10.0, 10.0),
        )
        rejected = (
            EmptySpace((0.0, 0.0, 14.0), (10.0, 10.0, 6.0)),
            EmptySpace((15.0, 15.0, 5.0), (2.0, 2.0, 2.0)),
            EmptySpace((12.0, 10.0, 0.0), (8.0, 10.0, 10.0)),
            EmptySpace((10.0, 10.0, 0.0), (10.0, 10.0, 10.0)),
        )
        for residual in rejected:
            with self.subTest(residual=residual):
                result = _hybrid_result(
                    (source,),
                    (residual,),
                    box={"x": 20.0, "y": 20.0, "z": 20.0},
                )
                self.assertEqual(result.status, "not_closed")
                self.assertEqual(
                    result.stop_reason,
                    "xy_composite_residual_owner_not_found",
                )

    def test_hybrid_timeout_preserves_the_minimum_placement(self) -> None:
        source = _placement_for(
            "container:a",
            (0.0, 0.0, 0.0),
            (10.0, 10.0, 10.0),
        )
        spaces = (EmptySpace((12.0, 0.0, 0.0), (2.0, 2.0, 2.0)),)
        before = source

        with patch(
            "board_game_insert_generator.xy_composite_closure.perf_counter",
            side_effect=(0.0, 1.0),
        ):
            result = _hybrid_result(
                (source,),
                spaces,
                box={"x": 20.0, "y": 10.0, "z": 10.0},
                budget=_budget(max_elapsed_ms=1),
            )

        self.assertEqual(result.status, "not_closed")
        self.assertEqual(
            result.stop_reason,
            "xy_composite_deadline_reached",
        )
        self.assertEqual(source, before)
        self.assertFalse(result.owner_bodies)

    def test_corner_top_reservation_closes_exactly_with_xy_annexes(self) -> None:
        result = close_xy_composite_partition(
            (_participant(),),
            (_placement(),),
            {"x": 100.0, "y": 80.0, "z": 40.0},
            40.0,
            0.0,
            box_perimeter_xy_mm=0.0,
            between_bodies_z_mm=0.0,
            budget=_budget(),
            top_inset_zones=(
                _zone(support_plane_z_mm=30.0, inset_depth_mm=10.0),
            ),
        )

        self.assertEqual(result.status, "closed")
        self.assertEqual(result.stop_reason, "xy_composite_partition_complete")
        self.assertTrue(result.certificate["certified"])
        self.assertEqual(
            result.certificate["printable_residual_volume_mm3"],
            0.0,
        )
        self.assertEqual(
            result.certificate["reserved_subtraction_volume_mm3"],
            6_000.0,
        )
        self.assertEqual(
            result.certificate["composite_body_volume_mm3"],
            314_000.0,
        )
        self.assertTrue(result.certificate["partition_complete_by_construction"])
        self.assertEqual(len(result.owner_bodies), 1)
        self.assertGreater(
            result.owner_bodies[0].certificate["annex_count"],
            0,
        )

    def test_every_annex_has_one_owner_common_bottom_and_true_xy_face(self) -> None:
        result = close_xy_composite_partition(
            (_participant(),),
            (_placement(),),
            {"x": 100.0, "y": 80.0, "z": 40.0},
            40.0,
            0.0,
            box_perimeter_xy_mm=0.0,
            between_bodies_z_mm=0.0,
            budget=_budget(),
            top_inset_zones=(
                _zone(support_plane_z_mm=30.0, inset_depth_mm=10.0),
            ),
        )

        owner = result.owner_bodies[0]
        by_id = {value.prism_id: value for value in owner.prisms}
        self.assertTrue(owner.certificate["unique_owner"])
        self.assertTrue(owner.certificate["common_lower_z"])
        self.assertTrue(
            owner.certificate["minimum_envelope_contained_by_union"]
        )
        self.assertTrue(
            owner.certificate["all_annexes_connected_by_vertical_xy_faces"]
        )
        self.assertEqual(owner.certificate["z_only_attachment_count"], 0)
        self.assertEqual(owner.certificate["edge_or_point_attachment_count"], 0)
        for prism in owner.prisms:
            self.assertEqual(prism.owner_id, owner.owner_id)
            self.assertEqual(prism.origin_mm[2], owner.base_z_mm)
            if prism.kind == "core":
                self.assertEqual(prism.attached_to_prism_id, "")
                self.assertEqual(prism.attachment_axis, "")
                continue
            self.assertIn(prism.attached_to_prism_id, by_id)
            self.assertIn(prism.attachment_axis, {"x", "y"})

        payload = xy_composite_closure_to_dict(result)
        self.assertEqual(payload["certificate"]["z_only_attachment_count"], 0)
        self.assertEqual(
            payload["certificate"]["edge_or_point_attachment_count"],
            0,
        )

    def test_non_top_open_reservation_is_rejected(self) -> None:
        result = close_xy_composite_partition(
            (_participant(),),
            (_placement(),),
            {"x": 100.0, "y": 80.0, "z": 40.0},
            40.0,
            0.0,
            box_perimeter_xy_mm=0.0,
            between_bodies_z_mm=0.0,
            budget=_budget(),
            top_inset_zones=(
                _zone(support_plane_z_mm=20.0, inset_depth_mm=10.0),
            ),
        )

        self.assertEqual(result.status, "not_closed")
        self.assertEqual(
            result.stop_reason,
            "xy_composite_reservation_not_top_open",
        )
        self.assertFalse(result.certificate["certified"])
        self.assertFalse(result.owner_bodies)


if __name__ == "__main__":
    unittest.main()
