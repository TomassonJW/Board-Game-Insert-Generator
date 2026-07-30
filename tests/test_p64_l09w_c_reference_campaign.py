from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SOLVER_SCRIPTS = ROOT / "scripts" / "solver"
if str(SOLVER_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SOLVER_SCRIPTS))

import run_p64_l09w_c_reference_campaign as campaign


FIXTURE = (
    ROOT / "tests/fixtures/p64_l09w_b_product_corpus.v1.json"
)


def _run(
    *,
    status: str,
    lane: str,
    calculation_ms: float,
    finalization: str = "solution_found",
    cad_ir: str = "ready_for_fusion",
) -> dict[str, object]:
    return {
        "status": status,
        "solver_status": (
            "solution_found"
            if status == campaign.RESULT_CERTIFIED
            else "no_solution_within_budget"
        ),
        "stop_reason": (
            "minimal_placement_certified"
            if status == campaign.RESULT_CERTIFIED
            else "portfolio_budget_exhausted"
        ),
        "functional_digest": "f" * 64,
        "selected_product_digest": "s" * 64,
        "execution_trace_digest": "f" * 64,
        "placement_digest": "p" * 64,
        "plan_digest": "d" * 64,
        "route": {
            "candidate_source": "portfolio_lane",
            "lane_id": lane,
            "external_status": (
                "certificate_rejected"
                if status != campaign.RESULT_CERTIFIED
                else "not_run"
            ),
        },
        "certificate": {
            "attempted": status == campaign.RESULT_CERTIFIED,
            "certified": status == campaign.RESULT_CERTIFIED,
            "rejection_codes": [],
        },
        "timings": {
            "project_reconstruction_ms": 1.0,
            "local_analysis_ms": 2.0,
            "session_projection_ms": 3.0,
            "calculation_ms": calculation_ms,
            "time_to_first_certified_ms": (
                calculation_ms + 0.5
                if status == campaign.RESULT_CERTIFIED
                else None
            ),
            "runner_recertification_ms": 0.5,
            "internal_lanes_ms": calculation_ms / 2,
            "scip_ms": calculation_ms / 4,
            "solver_projection_ms": 0.1,
            "common_certificate_ms": 0.2,
            "finalization_ms": 4.0,
            "cad_ir_ms": 5.0,
        },
        "finalization": {
            "attempted": status == campaign.RESULT_CERTIFIED,
            "status": finalization,
            "stop_reason": "test",
        },
        "cad_ir": {
            "attempted": status == campaign.RESULT_CERTIFIED,
            "status": cad_ir,
            "stop_reason": "test",
        },
    }


def _row(
    case_id: str,
    *,
    status: str,
    stratum: str,
    density: int,
    calculation_ms: float,
) -> dict[str, object]:
    first = _run(
        status=status,
        lane=f"lane-{stratum}",
        calculation_ms=calculation_ms,
    )
    row: dict[str, object] = {
        "case_id": case_id,
        "split": "discovery" if stratum == "common" else "tuning",
        "stratum": stratum,
        "status": status,
        "deterministic": True,
        "features": {
            "split": "discovery" if stratum == "common" else "tuning",
            "stratum": stratum,
            "target_density_pct": density,
            "container_count": 2,
            "contents_per_container": 4,
            "flat_count": 0,
            "layer_bucket": "1",
            "layer_count": 1,
            "box_size": "medium",
            "execution": "cold",
            "aspect_profile": "balanced",
            "fragmentation_class": "single-layer",
            "difficulty": stratum,
        },
        "runs": [first, dict(first)],
        "resources": {
            "peak_working_set_bytes": 1000,
            "measurement_method": "test",
        },
        "losses": [],
    }
    row["losses"] = campaign.classify_case_losses(row)
    return row


class P64L09WCReferenceCampaignTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.manifest = json.loads(FIXTURE.read_text(encoding="utf-8"))
        cls.built = campaign.build_open_inventory(cls.manifest)

    def test_inventory_exposes_only_400_open_cases_and_closed_receipt(
        self,
    ) -> None:
        inventory = self.built["inventory"]

        self.assertEqual(inventory["case_count"], 400)
        self.assertEqual(
            inventory["split_counts"],
            {"discovery": 240, "tuning": 160},
        )
        self.assertEqual(
            inventory["stratum_counts"],
            {"common": 240, "stress": 160},
        )
        self.assertFalse(inventory["holdout_case_records_loaded"])
        self.assertEqual(
            inventory["sealed_holdout_receipt"]["opening_count"],
            0,
        )
        self.assertNotIn(
            "case_records",
            inventory["sealed_holdout_receipt"],
        )

    def test_cli_has_no_holdout_input_and_requires_bounded_batch(self) -> None:
        help_text = campaign._parser().format_help()

        self.assertNotIn("--holdout", help_text)
        self.assertIn("--max-new-records", help_text)
        self.assertEqual(campaign.MAX_BATCH_SIZE, 25)

    def test_functional_replay_ignores_request_bound_plan_digest(self) -> None:
        first = _run(
            status=campaign.RESULT_CERTIFIED,
            lane="lane-a",
            calculation_ms=10.0,
        )
        second = dict(first)
        second["plan_digest"] = "e" * 64

        self.assertTrue(
            campaign._functional_runs_identical([first, second])
        )

    def test_selected_product_replay_ignores_trace_progress(self) -> None:
        first = _run(
            status=campaign.RESULT_CERTIFIED,
            lane="lane-a",
            calculation_ms=10.0,
        )
        second = dict(first)
        second["functional_digest"] = "g" * 64
        second["execution_trace_digest"] = "g" * 64

        self.assertTrue(
            campaign._functional_runs_identical([first, second])
        )
        self.assertFalse(
            campaign._execution_traces_identical([first, second])
        )

    def test_selected_product_replay_detects_product_change(self) -> None:
        first = _run(
            status=campaign.RESULT_CERTIFIED,
            lane="lane-a",
            calculation_ms=10.0,
        )
        second = dict(first)
        second["selected_product_digest"] = "t" * 64

        self.assertFalse(
            campaign._functional_runs_identical([first, second])
        )

    def test_summary_keeps_censored_cases_and_nearest_rank_percentiles(
        self,
    ) -> None:
        rows = [
            _row(
                "common-1",
                status=campaign.RESULT_CERTIFIED,
                stratum="common",
                density=30,
                calculation_ms=10.0,
            ),
            _row(
                "common-2",
                status=campaign.RESULT_CERTIFIED,
                stratum="common",
                density=30,
                calculation_ms=20.0,
            ),
            _row(
                "stress-1",
                status=campaign.RESULT_BOUNDED_UNKNOWN,
                stratum="stress",
                density=95,
                calculation_ms=30.0,
            ),
        ]

        summary = campaign.build_summary(rows)

        self.assertEqual(summary["overall"]["case_count"], 3)
        self.assertEqual(summary["overall"]["certified_count"], 2)
        self.assertEqual(summary["overall"]["censored_count"], 1)
        self.assertEqual(
            summary["overall"]["timings_certified_only"][
                "calculation_ms"
            ],
            {
                "sample_count": 2,
                "p50": 10.0,
                "p95": 20.0,
                "p99": 20.0,
            },
        )
        self.assertEqual(
            summary["by_axis"]["stratum"]["stress"][
                "censored_count"
            ],
            1,
        )

    def test_loss_attribution_separates_solver_and_downstream(self) -> None:
        bounded = _row(
            "bounded",
            status=campaign.RESULT_BOUNDED_UNKNOWN,
            stratum="stress",
            density=95,
            calculation_ms=20.0,
        )
        finalized_loss = _row(
            "finalization",
            status=campaign.RESULT_CERTIFIED,
            stratum="common",
            density=30,
            calculation_ms=5.0,
        )
        finalized_loss["runs"][0]["finalization"]["status"] = (
            "no_solution_within_budget"
        )
        finalized_loss["losses"] = campaign.classify_case_losses(
            finalized_loss
        )

        self.assertEqual(
            bounded["losses"][0]["cause"],
            "internal_lanes_exhausted_and_scip_not_certified",
        )
        self.assertEqual(
            finalized_loss["losses"][0]["cause"],
            "certified_minimal_not_finalized",
        )

    def test_checkpoint_refuses_ambiguous_active_case_until_exact_recovery(
        self,
    ) -> None:
        temp_root = ROOT / ".codex-work"
        temp_root.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=temp_root) as raw:
            path = Path(raw) / "checkpoint.json"
            binding = {"manifest_digest": "a" * 64}
            digest = campaign.canonical_digest(binding)
            checkpoint = campaign._checkpoint(
                path,
                binding_digest=digest,
                binding_payload=binding,
                resume=False,
                recover_interrupted_case=None,
            )
            checkpoint["active_case_id"] = "case-001"
            campaign._save_checkpoint(path, checkpoint)

            with self.assertRaisesRegex(
                RuntimeError,
                "ambiguous active case",
            ):
                campaign._checkpoint(
                    path,
                    binding_digest=digest,
                    binding_payload=binding,
                    resume=True,
                    recover_interrupted_case=None,
                )
            recovered = campaign._checkpoint(
                path,
                binding_digest=digest,
                binding_payload=binding,
                resume=True,
                recover_interrupted_case="case-001",
            )
            self.assertIsNone(recovered["active_case_id"])

    def test_timing_probe_restores_product_functions(self) -> None:
        import board_game_insert_generator.minimal_layout_solver as solver

        original = solver.solve_scip_product_3d
        with campaign._SolverTimingProbe():
            self.assertIsNot(solver.solve_scip_product_3d, original)
        self.assertIs(solver.solve_scip_product_3d, original)


if __name__ == "__main__":
    unittest.main()
