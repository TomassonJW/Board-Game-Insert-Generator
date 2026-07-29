from __future__ import annotations

from collections import Counter
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
SOLVER_SCRIPTS = ROOT / "scripts" / "solver"
if str(SOLVER_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SOLVER_SCRIPTS))

import run_p64_l09w_a_baseline as baseline
import audit_p64_l09w_a_downstream as downstream
import build_p64_l09w_a_evidence as evidence


class P64L09WASolverRobustnessTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.built = baseline.build_fixture_inventory()

    def test_inventory_separates_reconstructible_drift_and_core_only(self) -> None:
        inventory = self.built["inventory"]

        self.assertEqual(
            inventory["class_counts"],
            {
                "current-reconstructible": 162,
                "historical-semantic-drift": 165,
            },
        )
        self.assertEqual(
            inventory["drift_by_source"],
            {"L05": 3, "L06": 94, "L07": 68},
        )
        self.assertEqual(
            inventory["drift_by_reservation_mode"],
            {"constraining": 162, "historical": 3},
        )
        self.assertEqual(inventory["generated_current_duplicate_count"], 15)
        self.assertEqual(inventory["product_case_count"], 147)
        self.assertEqual(inventory["core_only_case_count"], 41)
        self.assertFalse(
            inventory["invariants"]["l08_counted_as_product_path"]
        )

    def test_product_schedule_uses_only_current_unique_projects(self) -> None:
        product_cases = self.built["product_cases"]
        project_digests = [value["project_digest"] for value in product_cases]

        self.assertEqual(len(product_cases), 147)
        self.assertEqual(len(project_digests), len(set(project_digests)))
        self.assertEqual(
            dict(
                sorted(
                    Counter(
                        str(value["expected"]) for value in product_cases
                    ).items()
                )
            ),
            {"feasible": 101, "historical": 4, "impossible": 42},
        )
        self.assertTrue(
            all(
                value["features"]["flat_item_count"] in {0, 1, 2}
                for value in product_cases
            )
        )

    def test_rotation_relaxation_is_monotone_only_for_positive_truths(self) -> None:
        generated = [
            value
            for value in self.built["product_cases"]
            if value["source"] in {"L06", "L07"}
        ]
        relaxed_positives = [
            value
            for value in generated
            if value.get("rotation_relaxed_for_positive") is True
        ]
        unsupported_negative_proofs = [
            value
            for value in generated
            if value["expected"] == "impossible"
            and value.get("negative_rotation_proof_supported") is False
        ]

        self.assertTrue(relaxed_positives)
        self.assertTrue(unsupported_negative_proofs)
        self.assertTrue(
            all(value["expected"] == "feasible" for value in relaxed_positives)
        )
        self.assertTrue(
            all(
                value["expected"] == "impossible"
                for value in unsupported_negative_proofs
            )
        )

    def test_summary_keeps_positive_negative_and_downstream_gates_separate(
        self,
    ) -> None:
        certified_run = {
            "preparation_ms": 1.0,
            "calculation_ms": 2.0,
            "time_to_first_certified_ms": 2.5,
            "certification_ms": 0.5,
            "finalization": {
                "attempted": True,
                "status": "solution_found",
                "elapsed_ms": 3.0,
            },
            "cad_ir": {
                "attempted": True,
                "status": "ready_for_fusion",
                "elapsed_ms": 4.0,
            },
        }
        rows = [
            {
                "baseline_case_id": "positive-ok",
                "source": "L06",
                "family": "family-a",
                "expected": "feasible",
                "status": "certified_solution",
                "stop_reason": "minimal_placement_certified",
                "features": {
                    "density_target": "ample",
                    "container_group_count": 2,
                    "contents_per_container_maximum": 4,
                    "flat_item_count": 0,
                    "layer_target": 1,
                    "execution_mode": "cold",
                },
                "runs": [certified_run],
                "deterministic": True,
                "resources": {"peak_working_set_bytes": 100},
            },
            {
                "baseline_case_id": "positive-miss",
                "source": "L06",
                "family": "family-b",
                "expected": "feasible",
                "status": "bounded_unknown",
                "stop_reason": "budget",
                "features": {
                    "density_target": "dense",
                    "container_group_count": 8,
                    "contents_per_container_maximum": 8,
                    "flat_item_count": 1,
                    "layer_target": 2,
                    "execution_mode": "cold",
                },
                "runs": [],
                "deterministic": None,
                "resources": {"peak_working_set_bytes": None},
            },
            {
                "baseline_case_id": "negative-control",
                "source": "L07",
                "family": "family-c",
                "expected": "impossible",
                "status": "bounded_unknown",
                "stop_reason": "bounded",
                "features": {},
                "runs": [],
                "deterministic": None,
                "resources": {"peak_working_set_bytes": None},
            },
        ]

        summary = baseline.build_summary(rows, [])
        product = summary["product"]

        self.assertEqual(product["feasible_case_count"], 2)
        self.assertEqual(product["certified_feasible_count"], 1)
        self.assertEqual(product["certified_feasible_rate"], 0.5)
        self.assertEqual(product["negative_control_count"], 1)
        self.assertEqual(product["negative_oracle_contradiction_count"], 0)
        self.assertEqual(product["downstream"]["finalization_success_count"], 1)
        self.assertEqual(product["downstream"]["cad_ir_success_count"], 1)
        self.assertEqual(
            product["timings_and_memory"]["calculation_ms"]["p99"], 2.0
        )

    def test_functional_replay_ignores_request_bound_plan_digest(self) -> None:
        common = {
            "status": "certified_solution",
            "solver_status": "solution_found",
            "functional_digest": "f" * 64,
            "placement_digest": "p" * 64,
            "route": {
                "candidate_source": "external_scip_real_3d",
                "lane_id": "external_scip_real_3d",
            },
        }
        first = {**common, "plan_digest": "a" * 64}
        second = {**common, "plan_digest": "b" * 64}

        self.assertTrue(
            baseline._functional_runs_identical([first, second])
        )

    def test_downstream_summary_preserves_strategy_exhaustion_reason(self) -> None:
        rows = [
            {
                "placement_digest": "a",
                "source_placement_digest": "a",
                "calculation": {"status": "certified_solution"},
                "finalization": {
                    "status": "no_solution_within_budget",
                    "stop_reason": "flat_inset_subtraction_plan_rejected",
                    "deadline_reached": False,
                    "proof_of_impossibility": False,
                },
                "cad_ir": {
                    "attempted": False,
                    "status": "not_applicable",
                },
            },
            {
                "placement_digest": "b",
                "source_placement_digest": "b",
                "calculation": {"status": "certified_solution"},
                "finalization": {
                    "status": "solution_found",
                    "stop_reason": "finalized_plan_certified",
                    "deadline_reached": False,
                    "proof_of_impossibility": False,
                },
                "cad_ir": {
                    "attempted": True,
                    "status": "ready_for_fusion",
                },
            },
        ]

        summary = downstream.summarize(rows)

        self.assertEqual(summary["case_count"], 2)
        self.assertEqual(
            summary["finalization_status_counts"],
            {
                "no_solution_within_budget": 1,
                "solution_found": 1,
            },
        )
        self.assertEqual(
            summary["finalization_stop_reason_counts"],
            {
                "finalized_plan_certified": 1,
                "flat_inset_subtraction_plan_rejected": 1,
            },
        )
        self.assertEqual(summary["cad_ir_success_count"], 1)

    def test_runtime_attribution_does_not_count_unexecuted_negatives(
        self,
    ) -> None:
        rows = [
            {
                "expected": "feasible",
                "status": "certified_solution",
                "stop_reason": "minimal_placement_certified",
                "runs": [
                    {
                        "route": {
                            "candidate_source": "external_scip_real_3d",
                            "lane_id": "external_scip_real_3d",
                            "external_status": "solution_found",
                            "external_invocation_count": 1,
                            "internal_lane_count": 0,
                        },
                        "counters": {
                            "external_lane_invocation_count": 1,
                            "placement_trials": 12,
                        },
                    }
                ],
            },
            {
                "expected": "impossible",
                "status": "unsupported",
                "stop_reason": "negative_rotation_proof_not_supported",
                "runs": [],
            },
        ]

        result = evidence.aggregate_runtime_attribution(rows)

        self.assertEqual(result["scheduled_case_count"], 2)
        self.assertEqual(result["executed_case_count"], 1)
        self.assertEqual(result["negative_control_executed_count"], 0)
        self.assertEqual(result["external_invocation_count_first_run"], 1)
        self.assertEqual(
            result["internal_lane_count_distribution_first_run"],
            {"0": 1},
        )
        self.assertEqual(
            result["negative_status_counts"], {"unsupported": 1}
        )
        self.assertEqual(
            result["counter_totals_first_run"],
            {
                "external_lane_invocation_count": 1,
                "placement_trials": 12,
            },
        )

    def test_versioned_evidence_is_self_certifying_and_bound_to_raw_reports(
        self,
    ) -> None:
        fixture_path = (
            ROOT
            / "tests"
            / "fixtures"
            / "p64_l09w_a_solver_robustness_baseline.v1.json"
        )

        fixture = evidence._verify(fixture_path, "evidence_digest")

        self.assertEqual(
            fixture["schema_version"],
            "bgig.p64_l09w_a_solver_robustness_evidence.v1",
        )
        self.assertEqual(
            fixture["bindings"]["baseline_report_digest"],
            "26aed0b36c47396ed54291193e89913c680f603c02090936fc4932e311987105",
        )
        self.assertEqual(
            fixture["bindings"]["downstream_report_digest"],
            "925fa00b22f6d9648a2ed3f52c80c381abbc937457d68dd94314337d2cefc15c",
        )
        self.assertEqual(
            fixture["product"]["certified_feasible_rate"],
            0.188119,
        )


if __name__ == "__main__":
    unittest.main()
