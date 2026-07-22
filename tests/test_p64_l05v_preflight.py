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
    def test_preflight_exercises_global_void_success_and_fallback(self) -> None:
        result = _PREFLIGHT.assert_preflight()

        success = result["global_void_success"]
        fallback = result["global_void_fallback"]
        self.assertEqual("container_placed_in_global_void", success["status"])
        self.assertEqual("global_solve_required", fallback["status"])
        self.assertEqual(0, success["global_solver_invocation_count"])
        self.assertEqual(0, fallback["global_solver_invocation_count"])
        self.assertFalse(success["existing_world_placements_changed"])

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
