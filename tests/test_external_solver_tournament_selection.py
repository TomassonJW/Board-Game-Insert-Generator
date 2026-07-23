from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import unittest

from board_game_insert_generator.external_solver_tournament import (
    ExternalSolverTournamentError,
    validate_external_tournament_selection_evidence,
)


ROOT = Path(__file__).resolve().parents[1]
SELECTION = (
    ROOT
    / "tests"
    / "fixtures"
    / "p64_l07d_external_tournament_selection.v1.json"
)


class ExternalSolverTournamentSelectionEvidenceTests(unittest.TestCase):
    def test_real_selection_is_sealed_before_holdout(self) -> None:
        value = json.loads(SELECTION.read_text(encoding="utf-8"))
        selection = validate_external_tournament_selection_evidence(value)

        self.assertEqual(selection["primary_candidate_id"], "highs")
        self.assertEqual(selection["complementary_candidate_ids"], [])
        self.assertEqual(selection["selected_candidate_ids"], ["highs"])
        self.assertEqual(
            selection["invariants"]["external_candidate_count"], 4
        )
        self.assertEqual(
            selection["invariants"]["external_family_count"], 4
        )
        self.assertEqual(
            selection["invariants"]["holdout_case_count_seen"], 0
        )
        self.assertFalse(
            selection["invariants"]["post_open_tuning_allowed"]
        )
        decisions = {
            item["candidate_id"]: item
            for item in selection["candidate_decisions"]
        }
        self.assertTrue(decisions["highs"]["selection_eligible"])
        self.assertTrue(decisions["ortools_cp_sat"]["selection_eligible"])
        self.assertFalse(decisions["scip"]["selection_eligible"])
        self.assertFalse(decisions["laff"]["selection_eligible"])
        self.assertFalse(
            selection["portfolio_analysis"]["portfolio_vs_primary"][
                "beats_best_single"
            ]
        )

    def test_real_selection_refuses_late_router_or_setting_change(self) -> None:
        value = json.loads(SELECTION.read_text(encoding="utf-8"))
        tampered_router = deepcopy(value)
        tampered_router["router"]["default_candidate_id"] = "ortools_cp_sat"
        with self.assertRaises(ExternalSolverTournamentError):
            validate_external_tournament_selection_evidence(tampered_router)

        tampered_settings = deepcopy(value)
        tampered_settings["selected_settings"]["holdout"]["seed"] += 1
        with self.assertRaises(ExternalSolverTournamentError):
            validate_external_tournament_selection_evidence(
                tampered_settings
            )


if __name__ == "__main__":
    unittest.main()
