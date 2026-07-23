from __future__ import annotations

import json
from pathlib import Path
import unittest

from board_game_insert_generator.incremental_project_state import canonical_digest


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = (
    ROOT / "tests" / "fixtures" / "p64_l07c_external_adapter_controls.v1.json"
)


class ExternalSolverAdapterEvidenceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.evidence = json.loads(EVIDENCE.read_text(encoding="utf-8"))

    def test_control_evidence_digest_and_scope_are_canonical(self) -> None:
        payload = dict(self.evidence)
        digest = payload.pop("evidence_digest")

        self.assertEqual(canonical_digest(payload), digest)
        self.assertEqual(self.evidence["candidate_count"], 4)
        self.assertEqual(self.evidence["family_count"], 4)
        self.assertEqual(self.evidence["summary"]["status"], "passed")
        self.assertEqual(self.evidence["summary"]["passed_count"], 12)
        self.assertEqual(self.evidence["invariants"]["holdout_case_count"], 0)
        self.assertEqual(
            self.evidence["invariants"]["heavy_processes_run_concurrently"], 1
        )

    def test_every_positive_control_has_a_fresh_bgig_certificate(self) -> None:
        positives = [
            item
            for item in self.evidence["results"]
            if item["exact_truth"] == "feasible"
        ]

        self.assertEqual(len(positives), 8)
        self.assertTrue(all(item["certified"] for item in positives))
        self.assertTrue(
            all(
                item["certificate_schema"]
                == "bgig.minimal_layout_certificate.v1"
                for item in positives
            )
        )
        self.assertTrue(all(item["placement_digest"] for item in positives))

    def test_negative_control_keeps_heuristic_status_truthful(self) -> None:
        negatives = {
            item["candidate_id"]: item
            for item in self.evidence["results"]
            if item["exact_truth"] == "infeasible"
        }

        self.assertEqual(
            negatives["ortools_cp_sat"]["observed_status"],
            "infeasible_proven",
        )
        self.assertEqual(negatives["highs"]["observed_status"], "infeasible_proven")
        self.assertEqual(negatives["scip"]["observed_status"], "infeasible_proven")
        self.assertEqual(negatives["laff"]["observed_status"], "bounded_unknown")


if __name__ == "__main__":
    unittest.main()
