"""Regression coverage for the deterministic P64-L04V Fusion gate fixture."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest


_SCRIPT_PATH = (
    Path(__file__).resolve().parents[1]
    / "scripts"
    / "fusion"
    / "p64_l04v_preflight.py"
)
_SPEC = importlib.util.spec_from_file_location("p64_l04v_preflight", _SCRIPT_PATH)
assert _SPEC is not None and _SPEC.loader is not None
_PREFLIGHT = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_PREFLIGHT)


class P64L04VPreflightTests(unittest.TestCase):
    def test_preflight_exercises_local_success_and_explicit_fallback(self) -> None:
        result = _PREFLIGHT.assert_preflight()

        self.assertEqual("placement_reused", result["local_reuse"]["status"])
        self.assertEqual("global_solve_required", result["fallback"]["status"])
        self.assertEqual(0, result["local_reuse"]["global_solver_invocation_count"])
        self.assertEqual(0, result["fallback"]["global_solver_invocation_count"])

    def test_fixture_is_a_portable_baseline_project(self) -> None:
        with TemporaryDirectory() as directory:
            fixture_path = Path(directory) / "p64-l04v-pocket-baseline.bgig.json"
            _PREFLIGHT.write_fixture(fixture_path, _PREFLIGHT.pocket_project())

            fixture = json.loads(fixture_path.read_text(encoding="utf-8"))

        self.assertEqual("P64-L04V pocket baseline", fixture["project_name"])
        self.assertEqual({"a", "b"}, {item["id"] for item in fixture["contents"]})


if __name__ == "__main__":
    unittest.main()
