from __future__ import annotations

import unittest

from board_game_insert_generator.mechanism import (
    MECHANISM_SCHEMA_V0,
    MechanismError,
    default_mechanism,
    normalize_mechanism,
    sliding_lid_readiness,
    sliding_lid_coupon_geometry,
)


class MechanismTests(unittest.TestCase):
    def test_default_mechanism_is_versioned_and_independent(self) -> None:
        first = default_mechanism()
        second = default_mechanism()

        self.assertEqual(first["schema_version"], MECHANISM_SCHEMA_V0)
        first["kind"] = "sliding_lid"
        self.assertEqual(second["kind"], "none")

    def test_normalizes_the_bounded_sliding_lid_contract(self) -> None:
        mechanism = normalize_mechanism(
            {
                "schema_version": MECHANISM_SCHEMA_V0,
                "kind": "sliding_lid",
                "slide_axis": "y",
                "lid_thickness_mm": 1.6,
                "rail_height_mm": 1.4,
                "rail_clearance_mm": 0.3,
                "end_overlap_mm": 9.0,
            }
        )

        self.assertEqual(mechanism["kind"], "sliding_lid")
        self.assertEqual(mechanism["slide_axis"], "y")
        self.assertEqual(mechanism["rail_height_mm"], 1.4)

    def test_rejects_out_of_range_mechanism_values(self) -> None:
        mechanism = default_mechanism()
        mechanism["rail_clearance_mm"] = 0.7

        with self.assertRaisesRegex(MechanismError, "rail_clearance_mm"):
            normalize_mechanism(mechanism)

    def test_reports_coupon_readiness_and_explicit_refusals(self) -> None:
        mechanism = default_mechanism()
        mechanism["kind"] = "sliding_lid"
        planned = sliding_lid_readiness("tray", {"x": 60, "y": 30, "z": 18}, mechanism)
        too_short = sliding_lid_readiness("short", {"x": 20, "y": 30, "z": 18}, mechanism)
        too_narrow = sliding_lid_readiness("narrow", {"x": 60, "y": 8, "z": 18}, mechanism)

        self.assertEqual(planned["status"], "planned_for_coupon")
        self.assertEqual(planned["materialization_status"], "not_materialized")
        self.assertEqual(planned["added_envelope_mm"], {"x": 0.0, "y": 3.0, "z": 2.4})
        self.assertEqual(too_short["code"], "SLIDING_LID_MODULE_TOO_SHORT")
        self.assertEqual(too_narrow["code"], "SLIDING_LID_MODULE_TOO_NARROW")

    def test_open_tray_keeps_mechanism_not_requested(self) -> None:
        readiness = sliding_lid_readiness(
            "tray", {"x": 60, "y": 30, "z": 18}, default_mechanism()
        )

        self.assertEqual(readiness["status"], "not_requested")
        self.assertEqual(readiness["physical_validation"], "required")


    def test_resolves_a_two_piece_coupon_with_joined_side_rails(self) -> None:
        mechanism = default_mechanism()
        mechanism["kind"] = "sliding_lid"

        coupon = sliding_lid_coupon_geometry(
            "tray",
            {"x": 100, "y": 40, "z": 20},
            {"x": 60, "y": 30, "z": 18},
            mechanism,
        )

        self.assertIsNotNone(coupon)
        assert coupon is not None
        self.assertEqual(coupon["piece_count"], 2)
        self.assertEqual(coupon["policy"], "sliding_lid_external_rail_coupon_v0")
        lid = coupon["lid"]
        self.assertEqual(lid["origin_mm"], {"x": 100.0, "y": 38.5, "z": 38.0})
        self.assertEqual(lid["base_slab_size_mm"], {"x": 60.0, "y": 33.0, "z": 1.2})
        self.assertEqual(len(lid["rails"]), 2)
        self.assertEqual(lid["rails"][0]["local_origin_mm"], {"x": 0.0, "y": 0.0, "z": -1.2})
        self.assertEqual(lid["rails"][1]["local_origin_mm"]["y"], 31.8)

    def test_does_not_resolve_geometry_for_an_incompatible_module(self) -> None:
        mechanism = default_mechanism()
        mechanism["kind"] = "sliding_lid"

        coupon = sliding_lid_coupon_geometry(
            "short", {"x": 0, "y": 0, "z": 0}, {"x": 20, "y": 30, "z": 18}, mechanism
        )

        self.assertIsNone(coupon)

if __name__ == "__main__":
    unittest.main()
