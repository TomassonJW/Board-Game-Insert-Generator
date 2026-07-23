from __future__ import annotations

import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from board_game_insert_generator.incremental_project_state import canonical_digest
from board_game_insert_generator.solver_benchmark_adapters import (
    CURRENT_BGIG_ADAPTER_ID,
    INTERNAL_EXACT_ADAPTER_ID,
)
from board_game_insert_generator.solver_benchmark_campaign import (
    CampaignPhaseConfig,
    SolverBenchmarkCampaignError,
    run_campaign_phase,
)
from board_game_insert_generator.solver_benchmark_corpus import (
    SolverBenchmarkCorpusError,
    validate_solver_benchmark_manifest,
)


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "tests" / "fixtures" / "p64_l06_solver_benchmark.v1.json"
REPORT = ROOT / "tests" / "fixtures" / "p64_l06d_campaign_report.v1.json"


def _read(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


class SolverBenchmarkCampaignTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.manifest = validate_solver_benchmark_manifest(_read(MANIFEST))

    def test_phase_checkpoints_each_result_and_resumes_without_rerun(self) -> None:
        config = CampaignPhaseConfig(
            split="discovery",
            adapter_ids=(INTERNAL_EXACT_ADAPTER_ID,),
            base_sha="a" * 40,
            branch="codex/test-campaign",
            max_case_executions=2,
            case_ids=("discovery-e-005", "discovery-b-002"),
        )
        with TemporaryDirectory() as temporary:
            output = Path(temporary) / "run"
            first = run_campaign_phase(self.manifest, config, output)
            checkpoint_bytes = (output / "checkpoint.json").read_bytes()
            summary = _read(output / "summary.json")
            second = run_campaign_phase(self.manifest, config, output)
            checkpoint_bytes_after = (output / "checkpoint.json").read_bytes()

        self.assertEqual(first.executed_now, 2)
        self.assertEqual(first.skipped_existing, 0)
        self.assertEqual(first.checkpoint["stop_reason"], "phase_complete")
        self.assertEqual(second.executed_now, 0)
        self.assertEqual(second.skipped_existing, 2)
        self.assertEqual(second.checkpoint["stop_reason"], "phase_complete")
        self.assertEqual(len(second.checkpoint["completed"]), 2)
        self.assertEqual(summary["row_count"], 2)
        self.assertEqual(
            {row["comparison"] for row in summary["rows"]},
            {"feasible_found", "impossible_proven"},
        )
        self.assertEqual(checkpoint_bytes, checkpoint_bytes_after)

    def test_corrupt_result_is_recomputed_once(self) -> None:
        config = CampaignPhaseConfig(
            split="discovery",
            adapter_ids=(INTERNAL_EXACT_ADAPTER_ID,),
            base_sha="b" * 40,
            branch="codex/test-recovery",
            max_case_executions=1,
            case_ids=("discovery-e-005",),
        )
        with TemporaryDirectory() as temporary:
            output = Path(temporary) / "run"
            first = run_campaign_phase(self.manifest, config, output)
            record = first.checkpoint["completed"][0]
            result_path = output / record["result_path"]
            result_path.write_text("{}\n", encoding="utf-8")
            resumed = run_campaign_phase(self.manifest, config, output)
            repaired = _read(result_path)

        self.assertEqual(resumed.executed_now, 1)
        self.assertEqual(resumed.skipped_existing, 0)
        self.assertEqual(repaired["case_id"], "discovery-e-005")

    def test_regression_phase_uses_historical_expectations(self) -> None:
        config = CampaignPhaseConfig(
            split="regression",
            adapter_ids=(CURRENT_BGIG_ADAPTER_ID,),
            base_sha="c" * 40,
            branch="codex/test-regression",
            max_case_executions=1,
            case_ids=("simple-quick",),
        )
        with TemporaryDirectory() as temporary:
            output = Path(temporary) / "run"
            run_campaign_phase(self.manifest, config, output)
            summary = _read(output / "summary.json")

        self.assertEqual(summary["rows"][0]["comparison"], "regression_expectation_met")
        self.assertTrue(summary["rows"][0]["certificate_certified"])

    def test_discovery_relaxations_are_explicit_and_remove_confounded_refusals(self) -> None:
        config = CampaignPhaseConfig(
            split="discovery",
            adapter_ids=(CURRENT_BGIG_ADAPTER_ID,),
            base_sha="9" * 40,
            branch="codex/test-relaxations",
            max_case_executions=2,
            case_ids=("discovery-e-005", "discovery-b-007"),
            experiment_id="relax_rotation_and_reservations",
        )
        with TemporaryDirectory() as temporary:
            output = Path(temporary) / "run"
            run_campaign_phase(self.manifest, config, output)
            summary = _read(output / "summary.json")
            results = [
                _read(path)
                for path in sorted((output / "results").glob("*.json"))
            ]

        self.assertTrue(
            all(row["solver_status"] != "unsupported" for row in summary["rows"])
        )
        self.assertTrue(
            all(
                row["experiment_id"] == "relax_rotation_and_reservations"
                for row in summary["rows"]
            )
        )
        self.assertTrue(
            all(result["experiment"]["monotone_relaxation"] for result in results)
        )
        self.assertTrue(
            all(result["experiment"]["truth_preservation"] for result in results)
        )
    def test_lane_hypothesis_changes_only_the_quick_lane_selection(self) -> None:
        config = CampaignPhaseConfig(
            split="discovery",
            adapter_ids=(CURRENT_BGIG_ADAPTER_ID,),
            base_sha="8" * 40,
            branch="codex/test-lane-hypothesis",
            max_case_executions=1,
            case_ids=("discovery-b-007",),
            experiment_id="lane_center_quick_v1",
        )
        with TemporaryDirectory() as temporary:
            output = Path(temporary) / "run"
            run_campaign_phase(self.manifest, config, output)
            result = _read(next((output / "results").glob("*.json")))
            summary = _read(output / "summary.json")

        self.assertEqual(result["adapter_id"], CURRENT_BGIG_ADAPTER_ID)
        self.assertEqual(
            result["experiment"]["lane_ids"],
            [
                "historical_legacy_corner",
                "historical_bridge_edge",
                "variant_center_footprint",
            ],
        )
        self.assertFalse(result["experiment"]["monotone_relaxation"])
        self.assertEqual(
            result["project_digest"],
            result["experiment"]["original_project_digest"],
        )
        self.assertNotEqual(result["adapter_result"]["status"], "unsupported")
        self.assertEqual(
            summary["config"]["experiment_id"], "lane_center_quick_v1"
        )

    def test_schedule_cap_and_checkpoint_tampering_fail_closed(self) -> None:
        too_small = CampaignPhaseConfig(
            split="discovery",
            adapter_ids=(INTERNAL_EXACT_ADAPTER_ID,),
            base_sha="d" * 40,
            branch="codex/test-cap",
            max_case_executions=1,
            case_ids=("discovery-e-005", "discovery-b-002"),
        )
        valid = CampaignPhaseConfig(
            split="discovery",
            adapter_ids=(INTERNAL_EXACT_ADAPTER_ID,),
            base_sha="e" * 40,
            branch="codex/test-tamper",
            max_case_executions=1,
            case_ids=("discovery-e-005",),
        )
        with TemporaryDirectory() as temporary:
            output = Path(temporary) / "run"
            with self.assertRaisesRegex(SolverBenchmarkCampaignError, "execution cap"):
                run_campaign_phase(self.manifest, too_small, output)
            run_campaign_phase(self.manifest, valid, output)
            checkpoint_path = output / "checkpoint.json"
            checkpoint = _read(checkpoint_path)
            checkpoint["branch"] = "tampered"
            checkpoint_path.write_text(
                json.dumps(checkpoint, ensure_ascii=False, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(SolverBenchmarkCampaignError, "digest mismatch"):
                run_campaign_phase(self.manifest, valid, output)

    def test_versioned_report_records_the_complete_negative_tournament(self) -> None:
        report = _read(REPORT)
        supplied_report_digest = report.pop("report_digest")
        self.assertEqual(canonical_digest(report), supplied_report_digest)
        selection = dict(report["selection"])
        supplied_selection_digest = selection.pop("selection_digest")
        self.assertEqual(canonical_digest(selection), supplied_selection_digest)
        self.assertEqual(report["costs"]["case_adapter_executions"], 904)
        self.assertFalse(report["costs"]["soak_executed"])
        self.assertFalse(
            report["decision"]["accepted_algorithmic_candidate"]
        )
        self.assertFalse(report["decision"]["algorithm_change_integrated"])
        self.assertEqual(
            report["decision"]["selected_hypothesis_id"],
            "no_algorithm_change_v1",
        )
        self.assertEqual(len(report["diagnostic_controls"]), 3)
        self.assertEqual(len(report["hypotheses"]), 4)
        self.assertEqual(report["phases"][-1]["split"], "holdout")
        self.assertTrue(report["invariants"]["no_public_budget_change"])
        self.assertEqual(
            report["invariants"]["oracle_contradiction_count"], 0
        )

    def test_holdout_remains_closed_without_selection(self) -> None:
        config = CampaignPhaseConfig(
            split="holdout",
            adapter_ids=(INTERNAL_EXACT_ADAPTER_ID,),
            base_sha="f" * 40,
            branch="codex/test-holdout",
            max_case_executions=64,
        )
        with TemporaryDirectory() as temporary:
            with self.assertRaises(SolverBenchmarkCorpusError):
                run_campaign_phase(self.manifest, config, Path(temporary) / "run")


if __name__ == "__main__":
    unittest.main()
