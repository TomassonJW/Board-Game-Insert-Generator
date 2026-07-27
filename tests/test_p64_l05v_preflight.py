"""Regression coverage for the deterministic P64-L05V Fusion fixture."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest


_SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "fusion" / "p64_l05v_preflight.py"
_SPEC = importlib.util.spec_from_file_location("p64_l05v_preflight", _SCRIPT_PATH)
assert _SPEC is not None and _SPEC.loader is not None
_PREFLIGHT = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_PREFLIGHT)


class P64L05VPreflightTests(unittest.TestCase):
    def test_historical_preflight_confirms_explicit_recalculation(self) -> None:
        result = _PREFLIGHT.assert_preflight()

        self.assertEqual(
            "superseded_by_explicit_recalculation",
            result["status"],
        )
        self.assertEqual("stale", result["small_container_edit"]["status"])
        self.assertEqual("stale", result["oversized_container_edit"]["status"])

    def test_fixture_is_portable_and_starts_without_the_new_container(self) -> None:
        with TemporaryDirectory() as directory:
            fixture_path = Path(directory) / "p64-l05v-global-void-baseline.bgig.json"
            _PREFLIGHT.write_fixture(
                fixture_path,
                _PREFLIGHT.global_void_project(),
            )
            fixture = json.loads(fixture_path.read_text(encoding="utf-8"))

        self.assertEqual("P64-L05V global void baseline", fixture["project_name"])
        self.assertEqual(["g"], [group["id"] for group in fixture["container_groups"]])
        self.assertEqual(["a"], [item["id"] for item in fixture["contents"]])


if __name__ == "__main__":
    unittest.main()
