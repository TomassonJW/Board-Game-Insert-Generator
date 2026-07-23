from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import unittest

from board_game_insert_generator.external_solver_tournament import (
    validate_external_tournament_selection_evidence,
)
from board_game_insert_generator.incremental_project_state import canonical_digest


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = (
    ROOT
    / "tests"
    / "fixtures"
    / "p64_l07d_external_tournament_evidence.v1.json"
)
RECOVERY = (
    ROOT
    / "tests"
    / "fixtures"
    / "p64_l07d_holdout_recovery_receipt.v1.json"
)


def _read(path: Path) -> dict[str, object]:
    value = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


def _assert_digest(
    testcase: unittest.TestCase,
    value: dict[str, object],
    field: str,
) -> None:
    payload = deepcopy(value)
    supplied = payload.pop(field)
    testcase.assertEqual(canonical_digest(payload), supplied)


class ExternalSolverTournamentEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.evidence = _read(EVIDENCE)
        cls.recovery = _read(RECOVERY)

    def test_compact_evidence_covers_four_real_engines_and_two_sources(
        self,
    ) -> None:
        _assert_digest(self, self.evidence, "evidence_digest")
        public = self.evidence["public_method_evidence"]

        self.assertEqual(public["source_count"], 2)
        self.assertEqual(public["control_count"], 8)
        self.assertFalse(
            public["invariants"]["product_ranking_eligible"]
        )
        discovery = self.evidence["open_summaries"]["discovery"]
        self.assertEqual(discovery["candidate_count"], 4)
        self.assertEqual(discovery["external_family_count"], 4)
        self.assertEqual(
            {item["candidate_id"] for item in discovery["candidates"]},
            {"ortools_cp_sat", "highs", "scip", "laff"},
        )
        self.assertTrue(
            all(
                item["worker_invocation_count"] == 8
                for item in discovery["candidates"]
            )
        )

    def test_selection_precedes_unique_holdout_without_portfolio(self) -> None:
        selection = validate_external_tournament_selection_evidence(
            self.evidence["selection"]
        )
        opening = self.evidence["opening_receipt"]
        opening_payload = deepcopy(opening)
        supplied = opening_payload.pop("opening_receipt_digest")

        self.assertEqual(canonical_digest(opening_payload), supplied)
        self.assertEqual(selection["primary_candidate_id"], "highs")
        self.assertEqual(selection["complementary_candidate_ids"], [])
        self.assertEqual(
            opening["selection_digest"],
            selection["holdout_selection"]["selection_digest"],
        )
        self.assertEqual(self.evidence["invariants"]["holdout_opening_count"], 1)
        self.assertEqual(self.evidence["invariants"]["post_open_tuning_count"], 0)
        self.assertFalse(
            selection["portfolio_analysis"]["portfolio_vs_primary"][
                "beats_best_single"
            ]
        )

    def test_holdout_is_truthful_on_its_common_scope(self) -> None:
        summary = self.evidence["holdout_portfolio_summary"]
        comparison = self.evidence[
            "holdout_selected_vs_bgig_baseline"
        ]
        results = self.evidence["holdout_results"]

        self.assertEqual(summary["case_count"], 64)
        self.assertEqual(summary["representable_count"], 7)
        self.assertEqual(summary["oracle_evaluable_count"], 7)
        self.assertEqual(summary["oracle_pass_count"], 5)
        self.assertEqual(summary["certified_solution_count"], 5)
        self.assertEqual(summary["candidate_failure_count"], 0)
        self.assertEqual(summary["statuses"]["bounded_unknown"], 2)
        self.assertEqual(len(results), 64)
        for result in results:
            if result["status"] == "solution_found":
                self.assertTrue(result["certified"])
            else:
                self.assertFalse(result["certified"])
        self.assertEqual(comparison["baseline_unsupported_count"], 7)
        self.assertFalse(comparison["product_gain_demonstrated"])
        self.assertEqual(
            comparison["comparison_status"],
            "baseline_cannot_represent_declared_benchmark_constraint",
        )

    def test_postprocessing_recovery_reused_every_expensive_checkpoint(
        self,
    ) -> None:
        _assert_digest(
            self, self.recovery, "recovery_receipt_digest"
        )
        recovery = self.recovery["recovery"]

        self.assertEqual(recovery["external_worker_reexecution_count"], 0)
        self.assertEqual(recovery["baseline_worker_reexecution_count"], 0)
        self.assertEqual(recovery["external_checkpoint_reuse_count"], 7)
        self.assertEqual(recovery["baseline_checkpoint_reuse_count"], 7)
        self.assertFalse(recovery["selection_changed"])
        self.assertFalse(recovery["router_changed"])
        self.assertFalse(recovery["settings_changed"])
        self.assertEqual(recovery["post_open_tuning_count"], 0)
        self.assertEqual(
            self.recovery["compact_evidence_digest"],
            self.evidence["evidence_digest"],
        )


if __name__ == "__main__":
    unittest.main()
