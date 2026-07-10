from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from context import ROOT

from board_game_insert_generator.config_loader import ConfigError, load_config
from board_game_insert_generator.models import BOX_FILL_PLAN_SCHEMA_V0, BoxFillReservationKind


class BoxFillPlanLoaderTests(unittest.TestCase):
    def test_loads_additive_manual_box_fill_plan(self) -> None:
        config = load_config(ROOT / "examples" / "box_fill_manual_v0.json")

        plan = config.box_fill_plan
        self.assertIsNotNone(plan)
        assert plan is not None
        self.assertEqual(plan.schema_version, BOX_FILL_PLAN_SCHEMA_V0)
        self.assertEqual(plan.box.id, "demo-game-box")
        self.assertEqual(plan.box.inner_dimensions.x, 120.0)
        self.assertEqual(plan.box.usable_height_mm, 38.0)
        self.assertEqual(plan.box.origin.z, 0.0)
        self.assertEqual([asset.id for asset in plan.assets], ["coin-tokens", "wooden-dice"])
        self.assertEqual(len(plan.layers), 1)
        self.assertEqual(plan.reservations[0].kind, BoxFillReservationKind.RULEBOOK)
        self.assertEqual(plan.modules[0].compartment_ids, ("coin-compartment",))
        self.assertEqual(plan.allocations[0].quantity, 30)
        self.assertEqual(plan.compartments[0].id, "coin-compartment")
        self.assertEqual(plan.access_features[0].id, "coin-notch")

    def test_existing_configuration_remains_compatible_without_plan(self) -> None:
        config = load_config(ROOT / "examples" / "simple_box.json")

        self.assertIsNone(config.box_fill_plan)

    def test_rejects_unknown_plan_field(self) -> None:
        payload = _payload()
        payload["box_fill_plan"]["solver"] = "not-yet"

        with self.assertRaisesRegex(ConfigError, "Unknown field"):
            _load_payload(payload)

    def test_rejects_unknown_schema_version(self) -> None:
        payload = _payload()
        payload["box_fill_plan"]["schema_version"] = "box_fill_plan.v9"

        with self.assertRaisesRegex(ConfigError, "Unsupported box_fill_plan.schema_version"):
            _load_payload(payload)


def _payload() -> dict:
    return json.loads((ROOT / "examples" / "box_fill_manual_v0.json").read_text(encoding="utf-8"))


def _load_payload(payload: dict):
    with tempfile.TemporaryDirectory() as temporary_directory:
        path = Path(temporary_directory) / "config.json"
        path.write_text(json.dumps(payload), encoding="utf-8")
        return load_config(path)


if __name__ == "__main__":
    unittest.main()