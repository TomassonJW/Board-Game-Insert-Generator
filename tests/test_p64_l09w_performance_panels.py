from __future__ import annotations

import json
from pathlib import Path
import unittest

from scripts.solver import build_p64_l09w_performance_panels as panels


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests/fixtures/p64_l09w_performance_panels.v1.json"


class P64L09WPerformancePanelsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.plan = panels.validate_plan(
            json.loads(FIXTURE.read_text(encoding="utf-8"))
        )

    def test_panels_are_nested_balanced_and_holdout_free(self) -> None:
        selection = self.plan["selection"]
        sentinel = set(selection["sentinel_case_ids"])
        candidate = set(selection["candidate_case_ids"])

        self.assertEqual(len(sentinel), 16)
        self.assertEqual(len(candidate), 48)
        self.assertLess(sentinel, candidate)
        self.assertFalse(selection["sample_is_rate_estimator"])
        self.assertEqual(
            self.plan["invariants"]["holdout_opening_count"],
            0,
        )
        self.assertEqual(
            self.plan["invariants"]["holdout_solver_invocation_count"],
            0,
        )

    def test_sentinels_cover_every_declared_feature_value(self) -> None:
        selection = self.plan["selection"]

        self.assertEqual(
            selection["sentinel_axis_values"],
            selection["population_axis_values"],
        )

    def test_causal_determinism_ready_and_bounded_roles_exist(self) -> None:
        cases = {
            value["case_id"]: value for value in self.plan["cases"]
        }

        for case_id in panels.CAUSAL_CASE_IDS:
            self.assertIn("causal", cases[case_id]["roles"])
        self.assertIn(
            "determinism",
            cases[panels.DETERMINISM_CASE_ID]["roles"],
        )
        sentinel_cases = [
            cases[case_id]
            for case_id in self.plan["selection"]["sentinel_case_ids"]
        ]
        self.assertGreaterEqual(
            sum(
                "ready_non_regression" in value["roles"]
                for value in sentinel_cases
            ),
            4,
        )
        self.assertGreaterEqual(
            sum(
                "bounded_control" in value["roles"]
                for value in sentinel_cases
            ),
            2,
        )

    def test_cli_has_no_holdout_surface(self) -> None:
        help_text = panels._parser().format_help()

        self.assertNotIn("holdout", help_text.lower())
        self.assertIn("--manifest", help_text)
        self.assertIn("--reference-checkpoint", help_text)

    def test_full_open_tier_is_reserved_after_candidate(self) -> None:
        tiers = self.plan["tiers"]

        self.assertTrue(tiers["candidate"]["requires_sentinel_pass"])
        self.assertTrue(tiers["open_frozen"]["requires_candidate_pass"])
        self.assertEqual(tiers["open_frozen"]["case_count"], 400)


if __name__ == "__main__":
    unittest.main()
