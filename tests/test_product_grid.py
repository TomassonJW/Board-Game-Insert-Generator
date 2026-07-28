from __future__ import annotations

import unittest

from board_game_insert_generator.product_grid import (
    PRODUCT_GRID_SCHEMA_V1,
    PRODUCT_GRID_STEP_MM,
    ceil_mm,
    floor_mm,
    is_on_product_grid,
    nearest_mm,
    nearest_ticks,
    outward_interval_mm,
    outward_size_mm,
    ticks_to_mm,
)
from scripts.fusion.p64_l09u_r7_grid_audit import (
    audit_replay_summary,
)


class ProductGridTests(unittest.TestCase):
    def test_replay_audit_excludes_source_and_rejects_derived_off_grid(
        self,
    ) -> None:
        payload = {
            "results": [
                {
                    "diagnostics": {
                        "minimal_plan": {
                            "top_inset_reservations": {
                                "product_grid_migration_v1": {
                                    "source_physical_dimensions_mm": {
                                        "x": 10.04,
                                    }
                                },
                                "cut_origin_mm": {"x": 10.0},
                            },
                            "placements": [],
                        },
                        "cad_ir": {
                            "derived_origin_mm": {"x": 2.24}
                        },
                        "fusion_plan": {},
                    }
                }
            ]
        }

        report = audit_replay_summary(payload)

        self.assertEqual(report["status"], "failed")
        self.assertEqual(report["audited_length_count"], 2)
        self.assertEqual(report["off_grid_count"], 1)
        self.assertEqual(report["off_grid"][0]["value"], 2.24)

    def test_nearest_uses_half_away_from_zero(self) -> None:
        self.assertEqual(PRODUCT_GRID_SCHEMA_V1, "bgig.product_grid.v1")
        self.assertEqual(PRODUCT_GRID_STEP_MM, 0.1)
        self.assertEqual(nearest_ticks(1.25), 13)
        self.assertEqual(nearest_ticks(-1.25), -13)
        self.assertEqual(nearest_mm(78.88), 78.9)
        self.assertEqual(ticks_to_mm(789), 78.9)

    def test_directional_rounding_preserves_required_envelopes(self) -> None:
        self.assertEqual(floor_mm(4.88), 4.8)
        self.assertEqual(ceil_mm(4.88), 4.9)
        self.assertEqual(outward_size_mm(1.18), 1.2)
        self.assertEqual(outward_interval_mm(10.04, 11.18), (10.0, 11.2))

    def test_grid_membership_is_distinct_from_numeric_epsilon(self) -> None:
        self.assertTrue(is_on_product_grid(22.2))
        self.assertFalse(is_on_product_grid(22.24))
        self.assertFalse(is_on_product_grid(0.0001))


if __name__ == "__main__":
    unittest.main()
