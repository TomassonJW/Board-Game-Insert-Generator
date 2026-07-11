from __future__ import annotations

import unittest

from board_game_insert_generator.mechanism import (
    MECHANISM_SCHEMA_V0,
    MechanismError,
    default_mechanism,
    normalize_mechanism,
    sliding_lid_readiness,
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


if __name__ == "__main__":
    unittest.main()
