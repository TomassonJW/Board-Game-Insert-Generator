from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
from statistics import median
import unittest

from scripts.solver import derive_p64_l09w_performance_thresholds as derived


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = (
    ROOT
    / "tests/fixtures/p64_l09w_performance_thresholds.v1.json"
)


class P64L09WPerformanceThresholdTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.thresholds = derived.validate_thresholds(
            json.loads(FIXTURE.read_text(encoding="utf-8"))
        )

    def test_thresholds_use_measured_robust_bounds_not_fixed_percent(
        self,
    ) -> None:
        method = self.thresholds["method"]

        self.assertIsNone(method["fixed_percentage_margin"])
        self.assertEqual(
            method["case_multiplicity_correction"],
            "bonferroni",
        )
        for value in self.thresholds["case_thresholds"].values():
            timing = value["timing"]
            self.assertGreaterEqual(
                timing["upper_median_limit_ms"],
                timing["maximum_ms"],
            )
            self.assertAlmostEqual(
                timing["median_ms"],
                median(timing["samples_ms"]),
            )

    def test_thresholds_cover_16_cases_and_three_aggregates(self) -> None:
        self.assertEqual(len(self.thresholds["case_thresholds"]), 16)
        self.assertEqual(
            set(self.thresholds["aggregate_thresholds"]),
            {"overall", "common", "stress"},
        )
        self.assertEqual(
            self.thresholds["aggregate_thresholds"]["common"][
                "case_count"
            ],
            8,
        )
        self.assertEqual(
            self.thresholds["aggregate_thresholds"]["stress"][
                "case_count"
            ],
            8,
        )

    def test_baseline_evaluates_green_and_detects_regression(self) -> None:
        timings = {
            case_id: {
                "sample_count": value["timing"]["sample_count"],
                "samples_ms": deepcopy(value["timing"]["samples_ms"]),
                "minimum_ms": value["timing"]["minimum_ms"],
                "median_ms": value["timing"]["median_ms"],
                "maximum_ms": value["timing"]["maximum_ms"],
                "mad_ms": value["timing"]["mad_ms"],
            }
            for case_id, value in self.thresholds[
                "case_thresholds"
            ].items()
        }
        report = {
            "schema_version": derived.runner.SCHEMA_VERSION,
            "mission": "P64-L09W-D-P",
            "tier": "sentinel",
            "status": "complete",
            "decision": "sentinel_baseline_passed",
            "bindings": {
                "plan_digest": self.thresholds["bindings"][
                    "plan_digest"
                ]
            },
            "execution": {
                "completed_case_count": 16,
                "repetitions_per_case": 5,
            },
            "functional": {
                "hard_gate_failure_count": 0,
                "assessments": [
                    {
                        "case_id": case_id,
                        "selected_product_digests": deepcopy(
                            value["selected_product_digests"]
                        ),
                    }
                    for case_id, value in self.thresholds[
                        "case_thresholds"
                    ].items()
                ],
            },
            "performance": {"timings_by_case": timings},
            "invariants": {
                "holdout_file_read": False,
                "holdout_opening_count": 0,
                "holdout_solver_invocation_count": 0,
            },
        }
        report["report_digest"] = derived.canonical_digest(report)

        passed = derived.evaluate_report(self.thresholds, report)
        self.assertEqual(passed["status"], "passed")

        changed = deepcopy(report)
        changed.pop("report_digest")
        case_id = next(iter(self.thresholds["case_thresholds"]))
        changed["performance"]["timings_by_case"][case_id][
            "median_ms"
        ] = (
            self.thresholds["case_thresholds"][case_id]["timing"][
                "upper_median_limit_ms"
            ]
            + 1.0
        )
        changed["report_digest"] = derived.canonical_digest(changed)
        failed = derived.evaluate_report(self.thresholds, changed)
        self.assertIn(
            f"case_median_regression:{case_id}",
            failed["failures"],
        )

        changed_product = deepcopy(report)
        changed_product.pop("report_digest")
        ready_case_id = next(
            case_id
            for case_id, value in self.thresholds[
                "case_thresholds"
            ].items()
            if value["expected_status"] == "certified_solution"
        )
        ready_assessment = next(
            value
            for value in changed_product["functional"]["assessments"]
            if value["case_id"] == ready_case_id
        )
        ready_assessment[
            "selected_product_digests"
        ] = ["changed"]
        changed_product["report_digest"] = derived.canonical_digest(
            changed_product
        )
        failed_product = derived.evaluate_report(
            self.thresholds,
            changed_product,
        )
        self.assertTrue(
            any(
                value.startswith("selected_product_regression:")
                for value in failed_product["failures"]
            )
        )

        bounded_improvement = deepcopy(report)
        bounded_improvement.pop("report_digest")
        bounded_case_id = next(
            case_id
            for case_id, value in self.thresholds[
                "case_thresholds"
            ].items()
            if value["expected_status"] == "bounded_unknown"
        )
        bounded_assessment = next(
            value
            for value in bounded_improvement["functional"]["assessments"]
            if value["case_id"] == bounded_case_id
        )
        bounded_assessment["selected_product_digests"] = [
            "new-certified-product"
        ]
        bounded_improvement["report_digest"] = derived.canonical_digest(
            bounded_improvement
        )
        improved = derived.evaluate_report(
            self.thresholds,
            bounded_improvement,
        )
        self.assertNotIn(
            f"selected_product_regression:{bounded_case_id}",
            improved["failures"],
        )

    def test_holdout_remains_absent(self) -> None:
        invariants = self.thresholds["invariants"]

        self.assertFalse(invariants["holdout_file_read"])
        self.assertEqual(invariants["holdout_opening_count"], 0)
        self.assertEqual(invariants["holdout_solver_invocation_count"], 0)


if __name__ == "__main__":
    unittest.main()
