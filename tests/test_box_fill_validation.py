from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from context import ROOT

from board_game_insert_generator.box_fill import analyze_box_fill_plan
from board_game_insert_generator.config_loader import load_config
from board_game_insert_generator.validation import validate_config


class BoxFillPlanValidationTests(unittest.TestCase):
    def test_valid_manual_plan_has_coverage_and_aggregate_free_volume(self) -> None:
        config = _load_payload(_payload())
        plan = config.box_fill_plan
        assert plan is not None

        analysis = analyze_box_fill_plan(plan)

        self.assertTrue(analysis.valid)
        self.assertEqual(validate_config(config), [])
        self.assertEqual([entry.status for entry in analysis.coverage], ["covered", "covered"])
        self.assertEqual(analysis.free_volume.total_free_volume_mm3, 205325.0)
        self.assertEqual(analysis.free_volume.qualification, "exact_aabb_cells_v0")

    def test_rejects_module_collision(self) -> None:
        payload = _payload()
        payload["box_fill_plan"]["modules"][1]["origin_mm"]["x"] = 50.0

        self.assertIn("BOX_FILL_MODULE_COLLISION", _codes(_load_payload(payload)))

    def test_rejects_volume_outside_usable_box(self) -> None:
        payload = _payload()
        payload["box_fill_plan"]["modules"][1]["size_mm"]["x"] = 70.0

        self.assertIn("BOX_FILL_VOLUME_OUTSIDE_BOX", _codes(_load_payload(payload)))

    def test_rejects_module_reservation_collision(self) -> None:
        payload = _payload()
        payload["box_fill_plan"]["reservations"][0]["origin_mm"]["y"] = 50.0

        self.assertIn("BOX_FILL_MODULE_RESERVATION_COLLISION", _codes(_load_payload(payload)))

    def test_reports_over_allocation_in_coverage(self) -> None:
        payload = _payload()
        payload["box_fill_plan"]["allocations"][0]["quantity"] = 31
        config = _load_payload(payload)
        plan = config.box_fill_plan
        assert plan is not None

        analysis = analyze_box_fill_plan(plan)

        self.assertIn("BOX_FILL_ALLOCATION_OVER_CAPACITY", _codes(config))
        coin_coverage = analysis.coverage[0]
        self.assertEqual(coin_coverage.over_allocated_quantity, 1)
        self.assertEqual(coin_coverage.status, "over_allocated")

    def test_rejects_unknown_allocation_asset(self) -> None:
        payload = _payload()
        payload["box_fill_plan"]["allocations"][0]["asset_id"] = "missing-asset"

        codes = _codes(_load_payload(payload))
        self.assertIn("BOX_FILL_UNKNOWN_ASSET", codes)
        self.assertIn("BOX_FILL_ASSET_UNCOVERED", codes)


    def test_rejects_reservation_collision_without_mutual_permission(self) -> None:
        payload = _payload()
        payload["box_fill_plan"]["reservations"].append(
            {
                "id": "overlay-reservation",
                "kind": "generic",
                "origin_mm": {"x": 0.0, "y": 70.0, "z": 0.0},
                "size_mm": {"x": 20.0, "y": 10.0, "z": 2.0},
            }
        )

        self.assertIn("BOX_FILL_RESERVATION_COLLISION", _codes(_load_payload(payload)))

    def test_allows_reservation_collision_only_with_mutual_permission(self) -> None:
        payload = _payload()
        payload["box_fill_plan"]["reservations"][0]["allow_overlap"] = True
        payload["box_fill_plan"]["reservations"].append(
            {
                "id": "overlay-reservation",
                "kind": "generic",
                "origin_mm": {"x": 0.0, "y": 70.0, "z": 0.0},
                "size_mm": {"x": 20.0, "y": 10.0, "z": 2.0},
                "allow_overlap": True,
            }
        )

        self.assertNotIn("BOX_FILL_RESERVATION_COLLISION", _codes(_load_payload(payload)))

    def test_rejects_duplicate_id_across_plan_families(self) -> None:
        payload = _payload()
        payload["box_fill_plan"]["modules"][1]["id"] = "rulebook-slot"

        self.assertIn("BOX_FILL_DUPLICATE_ID", _codes(_load_payload(payload)))

    def test_rejects_unknown_module_allocation(self) -> None:
        payload = _payload()
        payload["box_fill_plan"]["allocations"][1]["module_id"] = "missing-module"

        self.assertIn("BOX_FILL_UNKNOWN_MODULE", _codes(_load_payload(payload)))
def _payload() -> dict:
    return json.loads((ROOT / "examples" / "box_fill_manual_v0.json").read_text(encoding="utf-8"))


def _load_payload(payload: dict):
    with tempfile.TemporaryDirectory() as temporary_directory:
        path = Path(temporary_directory) / "config.json"
        path.write_text(json.dumps(payload), encoding="utf-8")
        return load_config(path)


def _codes(config) -> set[str]:
    return {issue.code for issue in validate_config(config)}


if __name__ == "__main__":
    unittest.main()
