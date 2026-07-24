from __future__ import annotations

import json
from pathlib import Path
import unittest

from board_game_insert_generator.real_3d_solver_adapters import (
    prepare_real_3d_problem,
)
from board_game_insert_generator.incremental_project_state import canonical_digest
from board_game_insert_generator.real_3d_solver_corpus import FAMILIES
from board_game_insert_generator.real_3d_solver_tournament import (
    EXTERNAL_CANDIDATE_IDS,
    build_holdout_decision,
    build_selection_evidence,
    materialize_tournament_problem,
    sanitize_oracle_leaked_baseline_rows,
    validate_selection_evidence,
)


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "tests" / "fixtures" / "p64_l08d_real_3d_corpus.v1.json"
SELECTION = ROOT / "tests" / "fixtures" / "p64_l08f_real_3d_selection.v1.json"
OPENING_RECEIPT = ROOT / "tests" / "fixtures" / "p64_l08f_holdout_opening_receipt.v1.json"
TOURNAMENT_EVIDENCE = ROOT / "tests" / "fixtures" / "p64_l08f_real_3d_tournament_evidence.v1.json"
RECOVERY_RECEIPT = ROOT / "tests" / "fixtures" / "p64_l08f_holdout_recovery_receipt.v1.json"


class Real3DSolverTournamentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        cls.records = cls.manifest["open_case_records"]

    def test_negative_records_become_real_impossible_inputs_without_witness(self) -> None:
        negatives = {
            value["family"]: value for value in self.records if value["expected"] == "infeasible"
        }
        self.assertEqual(set(negatives), set(FAMILIES))
        for family, record in negatives.items():
            problem = materialize_tournament_problem(record)
            self.assertIsNotNone(problem)
            self.assertNotIn("witness", problem)
            self.assertNotIn("placements", problem)
            self.assertNotIn("expected", problem)
            self.assertNotIn("formal_negative_bound", problem)
            self.assertNotEqual(problem["problem_digest"], record["problem_digest"])
            if family == "access":
                self.assertEqual(len(problem["access_precedence_edges"]), 2)
                self.assertEqual(
                    problem["access_precedence_edges"][0],
                    list(reversed(problem["access_precedence_edges"][1])),
                )
            if family == "support":
                self.assertFalse(problem["participants"][0]["ground_allowed"])
                self.assertGreater(
                    problem["participants"][0]["required_support_area_mm2"],
                    problem["world_mm"][0] * problem["world_mm"][1],
                )

    def test_complete_models_accept_many_assets_and_real_derived_rules(self) -> None:
        selected = [
            value
            for value in self.records
            if value["expected"] == "feasible"
            and value["family"] in {"many-assets", "real-anonymized"}
        ]
        self.assertTrue(selected)
        for record in selected:
            problem = materialize_tournament_problem(record)
            for candidate_id in ("ortools_cp_sat", "scip", "current_bgig"):
                prepared, reasons = prepare_real_3d_problem(problem, candidate_id)
                self.assertIsNotNone(prepared, (record["case_id"], candidate_id, reasons))
                self.assertEqual(reasons, ())

    def test_reviewed_project_reference_stays_baseline_only(self) -> None:
        record = next(value for value in self.records if value["split"] == "regression")
        self.assertIsNone(materialize_tournament_problem(record))

    def test_external_workers_do_not_read_corpus_oracle_metadata(self) -> None:
        workers = ROOT / "scripts" / "solver" / "external_workers"
        for name in (
            "ortools_real_3d_worker.py",
            "scip_real_3d_worker.py",
            "packingsolver_real_3d_worker.py",
            "laff_real_3d_worker.py",
        ):
            source = (workers / name).read_text(encoding="utf-8")
            self.assertNotIn('problem["expected"]', source)
            self.assertNotIn('problem.get("expected")', source)
            self.assertNotIn('problem["formal_negative_bound"]', source)
            self.assertNotIn('problem.get("formal_negative_bound")', source)

    def test_oracle_leak_is_sanitized_without_changing_external_rows(self) -> None:
        leaked = _row(
            "current_bgig",
            "negative",
            "access",
            "holdout-baseline",
            "holdout-baseline",
            "infeasible",
            "infeasible_proven",
            0.0,
        )
        external = _row(
            "scip",
            "negative",
            "access",
            "holdout-primary",
            "holdout-primary",
            "infeasible",
            "infeasible_proven",
            0.2,
        )
        sanitized = sanitize_oracle_leaked_baseline_rows([leaked, external])
        self.assertEqual(sanitized[0]["status"], "bounded_unknown")
        self.assertFalse(sanitized[0]["truth_pass"])
        self.assertEqual(
            sanitized[0]["recovery"]["reason"],
            "benchmark_oracle_metadata_leak",
        )
        self.assertNotEqual(sanitized[0]["row_digest"], leaked["row_digest"])
        self.assertEqual(sanitized[1], external)

    def test_holdout_rejects_losing_portfolio_and_retains_primary(self) -> None:
        portfolio = [
            _row(
                "laff",
                "case-1",
                "many-containers",
                "holdout",
                "p",
                "feasible",
                "solution_found",
                0.1,
            ),
            _row(
                "laff",
                "case-2",
                "many-containers",
                "holdout",
                "p",
                "infeasible",
                "bounded_unknown",
                0.1,
            ),
            _row("scip", "case-3", "access", "holdout", "p", "feasible", "solution_found", 0.2),
        ]
        primary = [
            _row(
                "scip",
                "case-1",
                "many-containers",
                "holdout",
                "s",
                "feasible",
                "bounded_unknown",
                0.2,
            ),
            _row(
                "scip",
                "case-2",
                "many-containers",
                "holdout",
                "s",
                "infeasible",
                "infeasible_proven",
                0.2,
            ),
            _row("scip", "case-3", "access", "holdout", "s", "feasible", "solution_found", 0.2),
        ]
        baseline = [
            _row(
                "current_bgig",
                "case-1",
                "many-containers",
                "holdout",
                "b",
                "feasible",
                "bounded_unknown",
                0.1,
            ),
            _row(
                "current_bgig",
                "case-2",
                "many-containers",
                "holdout",
                "b",
                "infeasible",
                "bounded_unknown",
                0.1,
            ),
            _row(
                "current_bgig",
                "case-3",
                "access",
                "holdout",
                "b",
                "feasible",
                "bounded_unknown",
                0.1,
            ),
        ]
        decision = build_holdout_decision(
            portfolio_rows=portfolio,
            primary_rows=primary,
            baseline_rows=baseline,
            selected_candidate_ids=["scip", "laff"],
            primary_candidate_id="scip",
        )
        verdict = decision["verdict"]
        self.assertFalse(verdict["portfolio_beats_primary"])
        self.assertEqual(verdict["retained_candidate_ids"], ["scip"])
        self.assertTrue(verdict["benchmark_winner_demonstrated"])
        self.assertFalse(verdict["retained_product_redistribution_ready"])
        self.assertFalse(verdict["product_integration_authorized"])
        self.assertEqual(verdict["decision"], "negative_no_product_integrable_winner")

    def test_versioned_holdout_evidence_is_recovered_and_product_blocked(self) -> None:
        selection = validate_selection_evidence(json.loads(SELECTION.read_text(encoding="utf-8")))
        receipt = json.loads(OPENING_RECEIPT.read_text(encoding="utf-8"))
        evidence = json.loads(TOURNAMENT_EVIDENCE.read_text(encoding="utf-8"))
        recovery_receipt = json.loads(RECOVERY_RECEIPT.read_text(encoding="utf-8"))

        for payload, digest_key in (
            (receipt, "opening_receipt_digest"),
            (evidence, "evidence_digest"),
            (recovery_receipt, "recovery_receipt_digest"),
        ):
            supplied = payload[digest_key]
            unsigned = dict(payload)
            unsigned.pop(digest_key)
            self.assertEqual(supplied, canonical_digest(unsigned))

        self.assertEqual(receipt["holdout_opening_count"], 1)
        self.assertFalse(receipt["post_open_tuning_allowed"])
        self.assertEqual(receipt["selection_digest"], selection["selection_digest"])
        self.assertEqual(
            evidence["opening_receipt"]["opening_receipt_digest"],
            receipt["opening_receipt_digest"],
        )
        self.assertEqual(evidence["selection"]["selection_digest"], selection["selection_digest"])
        self.assertEqual(selection["external_candidate_count"], 4)
        self.assertEqual(
            selection["selected_candidate_ids"],
            ["scip", "ortools_cp_sat", "laff"],
        )
        for summary in evidence["holdout_summaries"].values():
            self.assertEqual(summary["row_count"], 40)
        self.assertEqual(len(evidence["holdout_results"]), 40)
        self.assertFalse(evidence["portfolio_vs_primary"]["no_functional_loss"])
        self.assertEqual(evidence["portfolio_vs_primary"]["first_truth_loss_count"], 3)
        self.assertTrue(evidence["retained_vs_current_bgig"]["no_functional_loss"])
        self.assertEqual(evidence["retained_vs_current_bgig"]["first_truth_gain_count"], 18)
        self.assertEqual(evidence["retained_vs_current_bgig"]["first_truth_loss_count"], 0)
        self.assertEqual(evidence["verdict"]["retained_candidate_ids"], ["scip"])
        self.assertTrue(evidence["verdict"]["benchmark_winner_demonstrated"])
        self.assertFalse(evidence["verdict"]["portfolio_beats_primary"])
        self.assertFalse(evidence["verdict"]["product_integration_authorized"])
        self.assertEqual(
            evidence["verdict"]["decision"],
            "negative_no_product_integrable_winner",
        )
        recovery = evidence["recovery"]
        self.assertEqual(recovery["sanitized_baseline_row_count"], 10)
        self.assertEqual(recovery["external_worker_reexecution_count"], 0)
        self.assertEqual(recovery["baseline_worker_reexecution_count"], 0)
        self.assertEqual(recovery["private_holdout_reopen_count"], 0)
        self.assertEqual(
            recovery_receipt["recovered_evidence_digest"],
            evidence["evidence_digest"],
        )
        serialized = json.dumps(evidence, sort_keys=True)
        for private_key in ('"recipe"', '"nonce"', '"placements"', '"witness"'):
            self.assertNotIn(private_key, serialized)

    def test_selection_requires_full_semantics_before_speed(self) -> None:
        rows = []
        baseline = []
        for family_index, family in enumerate(FAMILIES):
            cases = [
                (f"{family}-small", "discovery", "discovery", "feasible"),
                (f"{family}-large", "discovery", "discovery", "feasible"),
                (f"{family}-negative", "discovery", "discovery", "infeasible"),
                (f"{family}-xl", "tuning", "balanced-seed-6408", "feasible"),
                (f"{family}-xl", "tuning", "wide-seed-6419", "feasible"),
            ]
            for candidate_id in EXTERNAL_CANDIDATE_IDS:
                for case_id, stage, trial_id, expected in cases:
                    complete = candidate_id in {"ortools_cp_sat", "scip"} or (
                        family == "many-containers"
                        and candidate_id in {"packingsolver_box", "laff"}
                    )
                    status = (
                        "unsupported"
                        if not complete
                        else "infeasible_proven"
                        if expected == "infeasible"
                        else "solution_found"
                    )
                    wall = (
                        0.1
                        if candidate_id == "packingsolver_box"
                        else 0.2
                        if candidate_id == "ortools_cp_sat"
                        else 0.3
                    )
                    rows.append(
                        _row(
                            candidate_id,
                            case_id,
                            family,
                            stage,
                            trial_id,
                            expected,
                            status,
                            wall,
                        )
                    )
            for case_id, stage, _, expected in cases[:3] + cases[3:4]:
                baseline.append(
                    _row(
                        "current_bgig",
                        case_id,
                        family,
                        stage,
                        "baseline",
                        expected,
                        "infeasible_proven" if expected == "infeasible" else "bounded_unknown",
                        0.5,
                    )
                )
        selection = build_selection_evidence(
            open_rows=rows,
            baseline_rows=baseline,
            config_digest="1" * 64,
            manifest_digest="2" * 64,
            artifact_bundle_digest="3" * 64,
            code_bundle_digest="4" * 64,
            holdout_limits={
                "wall_seconds": 30.0,
                "memory_mebibytes": 1024,
                "threads": 1,
                "profile": "selected_tuning_seed",
            },
        )
        accepted = validate_selection_evidence(selection)
        self.assertEqual(accepted["primary_candidate_id"], "ortools_cp_sat")
        self.assertTrue(accepted["primary_full_semantic_coverage"])
        self.assertIn("packingsolver_box", accepted["complement_candidate_ids"])
        self.assertEqual(accepted["family_routes"]["many-containers"], "packingsolver_box")
        self.assertFalse(accepted["holdout_opened"])
        self.assertFalse(accepted["post_selection_tuning_allowed"])


def _row(
    candidate_id: str,
    case_id: str,
    family: str,
    stage: str,
    trial_id: str,
    expected: str,
    status: str,
    wall: float,
) -> dict[str, object]:
    certified = status == "solution_found"
    truth_pass = certified if expected == "feasible" else status == "infeasible_proven"
    return {
        "candidate_id": candidate_id,
        "case_id": case_id,
        "case_digest": "a" * 64,
        "family": family,
        "tier": "xl" if stage == "tuning" else "small",
        "expected": expected,
        "stage": stage,
        "trial_id": trial_id,
        "status": status,
        "truth_pass": truth_pass,
        "representable": status != "unsupported",
        "candidate_failure": False,
        "certified": certified,
        "worker_invocation_count": int(status != "unsupported"),
        "unsupported_constraints": ["partial"] if status == "unsupported" else [],
        "quality": (
            {
                "max_top_mm": 10,
                "bounding_envelope_volume_mm3": 1000,
                "max_rear_mm": 10,
                "max_right_mm": 10,
            }
            if certified
            else {}
        ),
        "execution": {"total_wall_seconds": wall},
        "report_digest": "b" * 64,
        "row_digest": "c" * 64,
    }


if __name__ == "__main__":
    unittest.main()
