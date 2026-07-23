from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import unittest

from board_game_insert_generator.solver_benchmark_adapters import (
    CURRENT_BGIG_ADAPTER_ID,
    INTERNAL_EXACT_ADAPTER_ID,
    STATUS_BOUNDED_UNKNOWN,
    STATUS_PROVEN_IMPOSSIBLE,
    STATUS_UNSUPPORTED,
    ExactOracleCaps,
    SolverBenchmarkAdapterError,
    available_benchmark_adapters,
    recertify_minimal_layout_plan,
    run_benchmark_adapter,
)
from board_game_insert_generator.solver_benchmark_corpus import (
    materialize_benchmark_split,
    validate_solver_benchmark_manifest,
)
from board_game_insert_generator.solver_outcome import SOLUTION_FOUND


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "tests" / "fixtures" / "p64_l06_solver_benchmark.v1.json"
REGRESSION = ROOT / "tests" / "fixtures" / "p64_l05d_solver_case_corpus.v1.json"


def _read(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


class SolverBenchmarkAdapterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.manifest = validate_solver_benchmark_manifest(_read(MANIFEST))
        cls.discovery = {
            case["case_id"]: case
            for case in materialize_benchmark_split(cls.manifest, "discovery")
        }
        regression = _read(REGRESSION)
        cls.regression = {case["case_id"]: case for case in regression["cases"]}

    def test_protocol_exposes_exactly_two_dependency_free_candidates(self) -> None:
        adapters = available_benchmark_adapters()

        self.assertEqual(
            {item["adapter_id"] for item in adapters},
            {CURRENT_BGIG_ADAPTER_ID, INTERNAL_EXACT_ADAPTER_ID},
        )
        self.assertEqual(len(adapters), 2)
        self.assertTrue(all(item["external_dependency_count"] == 0 for item in adapters))

    def test_current_bgig_solution_is_freshly_recertified(self) -> None:
        execution = run_benchmark_adapter(
            self.regression["simple-quick"], CURRENT_BGIG_ADAPTER_ID
        )

        self.assertEqual(execution.report["status"], SOLUTION_FOUND)
        self.assertIsNotNone(execution.certified_plan)
        self.assertTrue(execution.report["recertification"]["attempted"])
        self.assertTrue(execution.report["recertification"]["certified"])
        certificate = recertify_minimal_layout_plan(execution.certified_plan)
        self.assertTrue(certificate.certified)

    def test_current_bgig_refuses_unexposed_rotation_constraint(self) -> None:
        execution = run_benchmark_adapter(
            self.discovery["discovery-e-005"], CURRENT_BGIG_ADAPTER_ID
        )

        self.assertEqual(execution.report["status"], STATUS_UNSUPPORTED)
        self.assertIsNone(execution.certified_plan)
        self.assertIn(
            "rotation_disable_control_not_exposed_by_project_v1",
            execution.report["unsupported_constraints"],
        )

    def test_internal_exact_finds_and_certifies_small_feasible_case(self) -> None:
        execution = run_benchmark_adapter(
            self.discovery["discovery-e-005"], INTERNAL_EXACT_ADAPTER_ID
        )

        self.assertEqual(execution.report["status"], SOLUTION_FOUND)
        self.assertTrue(execution.report["exact"]["complete_for_declared_model"])
        self.assertTrue(execution.report["recertification"]["certified"])
        self.assertEqual(execution.report["solution"]["rotation_count"], 0)
        self.assertIsNotNone(execution.certified_plan)

    def test_internal_exact_proves_small_impossible_case(self) -> None:
        execution = run_benchmark_adapter(
            self.discovery["discovery-b-002"], INTERNAL_EXACT_ADAPTER_ID
        )

        self.assertEqual(execution.report["status"], STATUS_PROVEN_IMPOSSIBLE)
        self.assertTrue(execution.report["exact"]["complete_for_declared_model"])
        self.assertIsNone(execution.certified_plan)
        self.assertFalse(execution.report["counters"]["cap_reached"])

    def test_internal_exact_reports_scope_and_cap_without_overclaiming(self) -> None:
        unsupported = run_benchmark_adapter(
            self.discovery["discovery-b-007"], INTERNAL_EXACT_ADAPTER_ID
        )
        capped = run_benchmark_adapter(
            self.discovery["discovery-e-005"],
            INTERNAL_EXACT_ADAPTER_ID,
            exact_caps=ExactOracleCaps(max_search_states=1),
        )

        self.assertEqual(unsupported.report["status"], STATUS_UNSUPPORTED)
        self.assertIn(
            "exact_model_does_not_cover_top_reservations",
            unsupported.report["unsupported_constraints"],
        )
        self.assertEqual(capped.report["status"], STATUS_BOUNDED_UNKNOWN)
        self.assertFalse(capped.report["exact"]["complete_for_declared_model"])
        self.assertTrue(capped.report["counters"]["cap_reached"])

    def test_exact_report_is_deterministic_and_does_not_consume_oracle_payload(self) -> None:
        first = run_benchmark_adapter(
            self.discovery["discovery-e-005"], INTERNAL_EXACT_ADAPTER_ID
        ).report
        second = run_benchmark_adapter(
            self.discovery["discovery-e-005"], INTERNAL_EXACT_ADAPTER_ID
        ).report

        self.assertEqual(first, second)
        self.assertFalse(first["invariants"]["oracle_payload_consumed_by_adapter"])

    def test_exact_matches_every_open_case_inside_its_declared_scope(self) -> None:
        supported = 0
        for case in self.discovery.values():
            execution = run_benchmark_adapter(case, INTERNAL_EXACT_ADAPTER_ID)
            if execution.report["status"] == STATUS_UNSUPPORTED:
                continue
            supported += 1
            expected = case["oracle"]["expected_truth"]
            with self.subTest(case_id=case["case_id"], expected=expected):
                self.assertEqual(
                    execution.report["status"],
                    SOLUTION_FOUND if expected == "feasible" else STATUS_PROVEN_IMPOSSIBLE,
                )
                self.assertTrue(
                    execution.report["exact"]["complete_for_declared_model"]
                )
        self.assertEqual(supported, 6)
    def test_project_digest_tampering_fails_closed(self) -> None:
        tampered = deepcopy(self.discovery["discovery-e-005"])
        tampered["project"]["project_name"] = "tampered"

        with self.assertRaisesRegex(SolverBenchmarkAdapterError, "digest mismatch"):
            run_benchmark_adapter(tampered, INTERNAL_EXACT_ADAPTER_ID)


if __name__ == "__main__":
    unittest.main()
