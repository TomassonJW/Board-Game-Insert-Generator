from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = (
    ROOT / "tests" / "fixtures" / "p64_l07e_highs_product_gate.v1.json"
)


class HighsProductEvidenceTests(unittest.TestCase):
    def test_product_gate_proves_gain_without_reopening_holdout(self) -> None:
        evidence = json.loads(EVIDENCE.read_text(encoding="utf-8"))

        self.assertEqual(
            evidence["schema_version"],
            "bgig.highs_product_gate_evidence.v1",
        )
        self.assertEqual(evidence["candidate"]["candidate_id"], "highs")
        comparison = evidence["comparison"]
        self.assertEqual(comparison["common_case_count"], 5)
        self.assertEqual(comparison["certified_solution_delta"], 0)
        self.assertEqual(comparison["quality_wins"], 2)
        self.assertEqual(comparison["quality_losses"], 0)
        self.assertTrue(comparison["product_gain_demonstrated"])
        self.assertFalse(evidence["invariants"]["holdout_reopened"])
        self.assertEqual(
            evidence["invariants"]["post_holdout_tuning_count"],
            0,
        )
        integrated = evidence["integrated_runtime_gate"]
        self.assertEqual(integrated["seed"], 640708)
        self.assertEqual(integrated["status_change_count"], 0)
        self.assertEqual(integrated["quality_win_count"], 2)
        self.assertEqual(integrated["quality_loss_count"], 0)
        self.assertEqual(integrated["external_invocation_count"], 5)
        self.assertEqual(integrated["holdout_opening_count"], 0)

    def test_cli_probe_matches_the_sealed_python_adapter(self) -> None:
        evidence = json.loads(EVIDENCE.read_text(encoding="utf-8"))
        probe = evidence["cli_equivalence_probe"]

        self.assertEqual(probe["exact_control_count"], 3)
        self.assertEqual(probe["regression_case_count"], 8)
        self.assertEqual(probe["status_mismatch_count"], 0)
        self.assertEqual(probe["quality_mismatch_count"], 0)
        self.assertEqual(
            probe["probe_digest"],
            "3ea1e213bf26cdc667e7f23abdc6ca0b8d730956af857005f24e177c858bed63",
        )


if __name__ == "__main__":
    unittest.main()
