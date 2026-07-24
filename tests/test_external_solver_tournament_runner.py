from __future__ import annotations

from importlib import import_module
from pathlib import Path
import sys
import unittest


SOLVER_SCRIPTS = Path(__file__).resolve().parents[1] / "scripts" / "solver"
sys.path.insert(0, str(SOLVER_SCRIPTS))

runner = import_module("run_external_solver_tournament")


def _row(
    case_id: str,
    *,
    status: str = "unsupported",
) -> dict[str, object]:
    return {
        "candidate_id": "highs",
        "case_id": case_id,
        "expected_truth": "regression_open",
        "report": {
            "model": None,
            "recertification": None,
            "status": status,
            "timing": None,
        },
    }


class ExternalSolverTournamentRunnerTests(unittest.TestCase):
    def test_holdout_summary_accepts_nullable_timing(self) -> None:
        summary = runner._summarize_holdout_rows([_row("unsupported-1")])

        self.assertEqual(summary["case_count"], 1)
        self.assertEqual(summary["total_wall_seconds"], 0.0)
        self.assertEqual(summary["certified_solution_count"], 0)
        self.assertEqual(summary["statuses"], {"unsupported": 1})

    def test_result_comparison_accepts_nullable_nested_reports(self) -> None:
        comparison = runner._compare_result_sets(
            [_row("same")],
            [_row("same")],
        )

        self.assertEqual(comparison["common_case_count"], 1)
        self.assertEqual(comparison["first_total_wall_seconds"], 0.0)
        self.assertEqual(comparison["second_total_wall_seconds"], 0.0)
        self.assertFalse(comparison["beats_second"])


if __name__ == "__main__":
    unittest.main()
