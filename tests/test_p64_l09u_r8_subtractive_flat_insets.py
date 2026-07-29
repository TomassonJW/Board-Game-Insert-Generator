from copy import deepcopy
import unittest

from board_game_insert_generator.flat_inset_subtraction import (
    FlatInsetSubtractionError,
    assert_flat_inset_subtraction_plan,
    build_flat_inset_subtraction_plan,
)
from board_game_insert_generator.incremental_project_state import (
    canonical_digest,
)


def _positive_fixture() -> tuple[
    list[dict[str, object]],
    dict[str, object],
]:
    owner_id = "container:strict"
    positive_digest = "owner-positive-digest"
    placement = {
        "id": owner_id,
        "role": "container",
        "origin_mm": {"x": 0.0, "y": 0.0, "z": 0.0},
        "world_size_mm": {"x": 100.0, "y": 20.0, "z": 20.0},
        "composite_body": {
            "schema_version": "bgig.xy_composite_container_body.v3",
            "owner_id": owner_id,
            "positive_geometry_digest": positive_digest,
            "prisms": [
                {
                    "prism_id": f"{owner_id}:container-prism:0000",
                    "owner_id": owner_id,
                    "kind": "core",
                    "geometry_role": "finalized_container",
                    "positive_geometry_source": "container_finalization",
                    "final_origin_mm": {
                        "x": 0.0,
                        "y": 0.0,
                        "z": 0.0,
                    },
                    "final_size_mm": {
                        "x": 100.0,
                        "y": 20.0,
                        "z": 20.0,
                    },
                }
            ],
        },
    }
    digest_payload = {
        "schema_version": "bgig.finalized_container_geometry.v1",
        "body_positive_geometry_digests": [
            {
                "owner_id": owner_id,
                "positive_geometry_digest": positive_digest,
            }
        ],
    }
    certificate = {
        "schema_version": "bgig.finalized_container_geometry.v1",
        "certified": True,
        "flat_positive_body_count": 0,
        "flat_positive_union_count": 0,
        "flat_positive_operation_count": 0,
        "flat_positive_volume_mm3": 0.0,
        "positive_geometry_digest": canonical_digest(digest_payload),
        "bodies": [
            {
                "owner_id": owner_id,
                "positive_geometry_digest": positive_digest,
            }
        ],
    }
    return [placement], certificate


def _reservations_fixture() -> list[dict[str, object]]:
    return [
        {
            "id": "top-inset:board",
            "flat_item_id": "board",
            "support_plane_z_mm": 16.0,
            "inset_depth_from_top_mm": 4.0,
            "total_thickness_mm": 4.0,
            "removal_order": 1,
            "grip_zone": {
                "origin_mm": {"x": 200.0, "y": 0.0},
                "size_mm": {"x": 1.0, "y": 1.0},
            },
            "local_depth_regions": [
                {
                    "id": "board-only",
                    "cut_origin_mm": {"x": 0.0, "y": 0.0},
                    "cut_size_mm": {"x": 40.0, "y": 20.0},
                    "layer_bottom_z_mm": 16.0,
                    "layer_top_z_mm": 20.0,
                    "inset_depth_from_top_mm": 4.0,
                    "overlapping_reservation_ids": [
                        "top-inset:board"
                    ],
                },
                {
                    "id": "board-overlap",
                    "cut_origin_mm": {"x": 40.0, "y": 0.0},
                    "cut_size_mm": {"x": 20.0, "y": 20.0},
                    "layer_bottom_z_mm": 16.0,
                    "layer_top_z_mm": 20.0,
                    "inset_depth_from_top_mm": 4.0,
                    "overlapping_reservation_ids": [
                        "top-inset:board",
                        "top-inset:booklet",
                    ],
                },
            ],
        },
        {
            "id": "top-inset:booklet",
            "flat_item_id": "booklet",
            "support_plane_z_mm": 18.0,
            "inset_depth_from_top_mm": 2.0,
            "total_thickness_mm": 2.0,
            "removal_order": 0,
            "grip_zone": {
                "origin_mm": {"x": 200.0, "y": 2.0},
                "size_mm": {"x": 1.0, "y": 1.0},
            },
            "local_depth_regions": [
                {
                    "id": "booklet-overlap",
                    "cut_origin_mm": {"x": 40.0, "y": 0.0},
                    "cut_size_mm": {"x": 20.0, "y": 20.0},
                    "layer_bottom_z_mm": 14.0,
                    "layer_top_z_mm": 16.0,
                    "inset_depth_from_top_mm": 2.0,
                    "overlapping_reservation_ids": [
                        "top-inset:board",
                        "top-inset:booklet",
                    ],
                },
                {
                    "id": "booklet-only",
                    "cut_origin_mm": {"x": 60.0, "y": 0.0},
                    "cut_size_mm": {"x": 40.0, "y": 20.0},
                    "layer_bottom_z_mm": 18.0,
                    "layer_top_z_mm": 20.0,
                    "inset_depth_from_top_mm": 2.0,
                    "overlapping_reservation_ids": [
                        "top-inset:booklet"
                    ],
                },
            ],
        },
    ]


class P64L09UR8SubtractiveFlatInsetTests(unittest.TestCase):
    def setUp(self) -> None:
        self.placements, self.positive_certificate = (
            _positive_fixture()
        )
        self.reservations = _reservations_fixture()
        self.plan = build_flat_inset_subtraction_plan(
            self.placements,
            self.reservations,
            design_top_z_mm=20.0,
            positive_geometry_certificate=self.positive_certificate,
        )

    def test_plan_is_difference_only_and_keeps_positive_digest(self) -> None:
        certificate = self.plan["certificate"]

        self.assertEqual(
            self.plan["schema_version"],
            "bgig.flat_inset_subtraction_plan.v1",
        )
        self.assertTrue(certificate["certified"])
        self.assertTrue(self.plan["operations"])
        self.assertTrue(
            all(
                operation["boolean_operation"] == "difference"
                and operation["geometry_attribution"]
                in {"flat_inset", "flat_grip"}
                and operation["creates_positive_geometry"] is False
                and operation["creates_printable_body"] is False
                and operation["creates_union"] is False
                for operation in self.plan["operations"]
            )
        )
        self.assertEqual(certificate["flat_positive_volume_mm3"], 0.0)
        self.assertEqual(certificate["flat_positive_body_count"], 0)
        self.assertEqual(certificate["flat_positive_union_count"], 0)
        self.assertEqual(
            certificate[
                "new_printable_body_count_attributed_to_flat_items"
            ],
            0,
        )
        self.assertEqual(
            certificate["positive_geometry_digest_before"],
            self.positive_certificate["positive_geometry_digest"],
        )
        self.assertEqual(
            certificate["positive_geometry_digest_after"],
            self.positive_certificate["positive_geometry_digest"],
        )
        self.assertTrue(certificate["positive_geometry_unchanged"])

    def test_local_covering_depths_are_exactly_two_four_and_six(self) -> None:
        certificate = self.plan["certificate"]
        witnesses = self.plan["local_depth_witnesses"]

        self.assertEqual(
            certificate["observed_combined_local_depths_mm"],
            [2.0, 4.0, 6.0],
        )
        self.assertTrue(
            all(
                witness["stack_contiguous"]
                and witness["stack_non_overlapping"]
                and witness["declared_covering_set_exact"]
                and witness["combined_depth_mm"]
                == witness["interval_span_depth_mm"]
                for witness in witnesses
            )
        )

    def test_validator_rejects_any_positive_or_union_operation(self) -> None:
        corrupted = deepcopy(self.plan)
        corrupted["operations"][0]["boolean_operation"] = "union"
        supplied = deepcopy(corrupted)
        supplied.pop("deterministic_digest")
        corrupted["deterministic_digest"] = canonical_digest(supplied)

        with self.assertRaises(FlatInsetSubtractionError):
            assert_flat_inset_subtraction_plan(
                corrupted,
                self.placements,
                self.reservations,
                design_top_z_mm=20.0,
                positive_geometry_certificate=(
                    self.positive_certificate
                ),
            )


if __name__ == "__main__":
    unittest.main()
