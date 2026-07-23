from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import unittest

from board_game_insert_generator.external_solver_tournament import (
    ExternalSolverTournamentError,
    build_external_tournament_selection_evidence,
    quality_axes_from_report,
    summarize_external_tournament_stage,
    summarize_external_tournament_tuning,
    validate_external_tournament_config,
    validate_external_tournament_selection_evidence,
)
from board_game_insert_generator.incremental_project_state import canonical_digest


ROOT = Path(__file__).resolve().parents[1]
CONFIG = (
    ROOT
    / "tests"
    / "fixtures"
    / "p64_l07d_external_tournament_config.v1.json"
)
MANIFEST = (
    ROOT / "tests" / "fixtures" / "p64_l07b_solver_benchmark.v2.json"
)
ARTIFACT_LOCK = (
    ROOT
    / "tests"
    / "fixtures"
    / "p64_l07c_external_solver_artifacts.v1.json"
)
CANDIDATE_IDS = ("ortools_cp_sat", "highs", "scip", "laff")


def _read(path: Path) -> dict[str, object]:
    value = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


def _report(
    candidate_id: str,
    case_id: str,
    *,
    status: str,
    wall_seconds: float,
    footprint: float = 100.0,
) -> dict[str, object]:
    certified = status == "solution_found"
    report: dict[str, object] = {
        "schema_version": "bgig.external_adapter_result.v2",
        "candidate": {"candidate_id": candidate_id},
        "case": {
            "case_id": case_id,
            "family": "family-a",
            "project_digest": "1" * 64,
            "split": "test",
        },
        "limits": {
            "wall_seconds": 3.0,
            "memory_mebibytes": 1024,
            "threads": 1,
            "seed": 640707,
        },
        "model": (
            {"schema_version": "test-model"}
            if status
            not in {"unsupported", "invalid_input"}
            else None
        ),
        "status": status,
        "stop_reason": "test",
        "unsupported_constraints": [],
        "errors": [],
        "timing": {
            "total_wall_seconds": wall_seconds,
            "checkpoint_reused": False,
        },
        "resources": {
            "cpu_seconds": wall_seconds / 2,
            "peak_working_set_bytes": 1024,
            "threads_requested": 1,
        },
        "recertification": {
            "attempted": certified,
            "certified": certified,
            "candidate_digest": "2" * 64 if certified else None,
            "schema_version": (
                "bgig.minimal_layout_certificate.v1"
                if certified
                else None
            ),
            "rejection_codes": [],
        },
        "solution": (
            {
                "metrics": {
                    "cluster_volume_mm3": 1000.0,
                    "internal_gap_mm3": 0.0,
                    "cluster_height_mm": 10.0,
                    "cluster_footprint_mm2": footprint,
                    "residual_fragmentation": 0.0,
                    "contact_count": 1.0,
                    "minimum_support_ratio": 1.0,
                }
            }
            if certified
            else None
        ),
        "invariants": {"worker_invocation_count": 1},
    }
    report["report_digest"] = canonical_digest(report)
    return report


def _rows(
    trial_id: str,
    *,
    ortools_footprint: float = 100.0,
    highs_footprint: float = 100.0,
) -> list[dict[str, object]]:
    result = []
    times = {
        "ortools_cp_sat": 0.1,
        "highs": 0.2,
        "scip": 0.3,
        "laff": 0.4,
    }
    footprints = {
        "ortools_cp_sat": ortools_footprint,
        "highs": highs_footprint,
        "scip": 105.0,
        "laff": 110.0,
    }
    for candidate_id in CANDIDATE_IDS:
        for case_id, family, truth in (
            ("case-feasible-a", "family-a", "feasible"),
            ("case-feasible-b", "family-b", "feasible"),
            ("case-impossible", "family-c", "impossible"),
        ):
            status = (
                "solution_found"
                if truth == "feasible"
                else (
                    "bounded_unknown"
                    if candidate_id == "laff"
                    else "infeasible_proven"
                )
            )
            report = _report(
                candidate_id,
                case_id,
                status=status,
                wall_seconds=times[candidate_id],
                footprint=footprints[candidate_id],
            )
            report["case"]["family"] = family
            report["report_digest"] = canonical_digest(
                {
                    key: value
                    for key, value in report.items()
                    if key != "report_digest"
                }
            )
            result.append(
                {
                    "candidate_id": candidate_id,
                    "case_id": case_id,
                    "family": family,
                    "expected_truth": truth,
                    "trial_id": trial_id,
                    "report": report,
                }
            )
    return result


class ExternalSolverTournamentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.config = _read(CONFIG)
        cls.manifest = _read(MANIFEST)
        cls.lock = _read(ARTIFACT_LOCK)

    def test_checked_in_config_is_sealed_and_has_four_families(self) -> None:
        validated = validate_external_tournament_config(self.config)

        self.assertEqual(validated["candidate_ids"], list(CANDIDATE_IDS))
        self.assertEqual(len(validated["stages"]["tuning_trials"]), 2)
        self.assertFalse(
            validated["ranking"][
                "public_method_controls_product_ranked"
            ]
        )
        tampered = deepcopy(self.config)
        tampered["stages"]["holdout"]["seed"] += 1
        with self.assertRaises(ExternalSolverTournamentError):
            validate_external_tournament_config(tampered)

    def test_stage_summary_uses_truth_quality_resources_and_four_engines(
        self,
    ) -> None:
        summary = summarize_external_tournament_stage(
            "discovery",
            _rows("discovery"),
            artifact_lock=self.lock,
            candidate_ids=CANDIDATE_IDS,
        )

        self.assertEqual(summary["candidate_count"], 4)
        self.assertEqual(summary["external_family_count"], 4)
        self.assertEqual(summary["ranking"][0], "ortools_cp_sat")
        laff = next(
            item
            for item in summary["candidates"]
            if item["candidate_id"] == "laff"
        )
        self.assertEqual(laff["oracle_miss_count"], 1)
        self.assertEqual(laff["certified_solution_count"], 2)

    def test_stage_summary_rejects_report_tampering_and_input_skew(
        self,
    ) -> None:
        tampered = _rows("discovery")
        tampered[0]["report"]["status"] = "external_error"
        with self.assertRaises(ExternalSolverTournamentError):
            summarize_external_tournament_stage(
                "discovery",
                tampered,
                artifact_lock=self.lock,
                candidate_ids=CANDIDATE_IDS,
            )
        skewed = _rows("discovery")[:-1]
        with self.assertRaisesRegex(
            ExternalSolverTournamentError, "same stage inputs"
        ):
            summarize_external_tournament_stage(
                "discovery",
                skewed,
                artifact_lock=self.lock,
                candidate_ids=CANDIDATE_IDS,
            )

    def test_selection_is_bound_before_holdout_and_rejects_late_change(
        self,
    ) -> None:
        control_rows = _rows("exact-controls")
        regression_rows = deepcopy(control_rows)
        for row in regression_rows:
            row["trial_id"] = "regression"
            row["expected_truth"] = "regression_open"
        discovery_rows = _rows("discovery")
        tuning_rows = [
            *_rows("seed-640707"),
            *_rows("seed-640708"),
        ]
        controls = summarize_external_tournament_stage(
            "exact_controls",
            control_rows,
            artifact_lock=self.lock,
            candidate_ids=CANDIDATE_IDS,
        )
        regressions = summarize_external_tournament_stage(
            "regression",
            regression_rows,
            artifact_lock=self.lock,
            candidate_ids=CANDIDATE_IDS,
        )
        discovery = summarize_external_tournament_stage(
            "discovery",
            discovery_rows,
            artifact_lock=self.lock,
            candidate_ids=CANDIDATE_IDS,
        )
        tuning = summarize_external_tournament_tuning(
            tuning_rows,
            artifact_lock=self.lock,
            candidate_ids=CANDIDATE_IDS,
            trial_ids=("seed-640707", "seed-640708"),
        )
        public: dict[str, object] = {
            "schema_version": (
                "bgig.external_solver_public_method_evidence.v1"
            ),
            "source_count": 2,
            "control_count": 8,
        }
        public["evidence_digest"] = canonical_digest(public)

        selection = build_external_tournament_selection_evidence(
            config=self.config,
            manifest=self.manifest,
            artifact_lock=self.lock,
            code_bundle_digest="a" * 64,
            public_evidence=public,
            exact_control_summary=controls,
            regression_summary=regressions,
            discovery_summary=discovery,
            tuning_summary=tuning,
            tuning_rows=tuning_rows,
        )

        self.assertEqual(
            selection["primary_candidate_id"], "ortools_cp_sat"
        )
        self.assertEqual(selection["complementary_candidate_ids"], [])
        self.assertEqual(
            selection["invariants"]["holdout_case_count_seen"], 0
        )
        self.assertTrue(
            selection["holdout_selection"]["selected_before_holdout"]
        )
        tampered = deepcopy(selection)
        tampered["router"]["default_candidate_id"] = "highs"
        with self.assertRaises(ExternalSolverTournamentError):
            validate_external_tournament_selection_evidence(tampered)

    def test_quality_requires_fresh_certificate(self) -> None:
        report = _report(
            "ortools_cp_sat",
            "case",
            status="solution_found",
            wall_seconds=0.1,
        )
        self.assertIsNotNone(quality_axes_from_report(report))
        report["recertification"]["certified"] = False
        self.assertIsNone(quality_axes_from_report(report))


if __name__ == "__main__":
    unittest.main()
