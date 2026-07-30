from __future__ import annotations

from pathlib import Path
import unittest

from scripts.solver import run_p64_l09w_performance_panel as runner


ROOT = Path(__file__).resolve().parents[1]


def _result(
    *,
    placement: str = "placement",
    deterministic: bool = True,
    ready: bool = True,
    target_loss: bool = False,
) -> dict[str, object]:
    return {
        "status": runner.campaign.RESULT_CERTIFIED,
        "deterministic": deterministic,
        "losses": (
            [{"detail": runner.stratified.TARGET_LOSS}]
            if target_loss
            else []
        ),
        "runs": [
            {
                "placement_digest": placement,
                "selected_product_digest": "selected",
                "execution_trace_digest": "trace-a",
                "timings": {"calculation_ms": value},
                "finalization": {
                    "status": (
                        "solution_found"
                        if ready
                        else "no_solution_within_budget"
                    )
                },
                "cad_ir": {
                    "status": (
                        "ready_for_fusion"
                        if ready
                        else "not_attempted"
                    )
                },
            }
            for value in (10.0, 12.0, 11.0, 13.0, 9.0)
        ],
    }


def _plan_case(*roles: str) -> dict[str, object]:
    return {
        "case_id": "case",
        "stratum": "common",
        "roles": list(roles),
        "reference": {
            "status": runner.campaign.RESULT_CERTIFIED,
            "placement_digest": "placement",
        },
    }


class P64L09WPerformancePanelRunnerTests(unittest.TestCase):
    def test_functional_gate_separates_selected_result_from_trace(self) -> None:
        result = _result()
        result["runs"][1]["execution_trace_digest"] = "trace-b"

        assessment = runner._assess_case(
            _plan_case("sentinel", "ready_non_regression"),
            result,
        )

        self.assertTrue(assessment["hard_gate_passed"])
        self.assertEqual(assessment["selected_product_digest_count"], 1)
        self.assertEqual(assessment["execution_trace_digest_count"], 2)

    def test_functional_gate_separates_selected_result_from_route(self) -> None:
        result = _result()
        result["runs"][0]["route"] = {
            "candidate_source": "portfolio_lane",
            "lane_id": "lane-a",
        }
        for run in result["runs"][1:]:
            run["route"] = {
                "candidate_source": "portfolio_lane",
                "lane_id": "lane-b",
            }

        assessment = runner._assess_case(
            _plan_case("sentinel"),
            result,
        )

        self.assertTrue(assessment["hard_gate_passed"])
        self.assertEqual(assessment["execution_route_variant_count"], 2)

    def test_functional_gate_stops_product_ready_and_causal_regressions(
        self,
    ) -> None:
        changed = runner._assess_case(
            _plan_case("sentinel"),
            _result(placement="changed"),
        )
        self.assertIn(
            "selected_placement_regression",
            changed["failures"],
        )

        not_ready = runner._assess_case(
            _plan_case("sentinel", "ready_non_regression"),
            _result(ready=False),
        )
        self.assertIn("ready_result_regression", not_ready["failures"])

        causal = runner._assess_case(
            _plan_case("sentinel", "causal"),
            _result(ready=False, target_loss=True),
        )
        self.assertIn("causal_case_failure", causal["failures"])

    def test_bounded_control_does_not_require_a_placement(self) -> None:
        result = _result()
        result["status"] = runner.campaign.RESULT_BOUNDED_UNKNOWN
        result["deterministic"] = True
        for run in result["runs"]:
            run["placement_digest"] = None
            run["selected_product_digest"] = None

        assessment = runner._assess_case(
            {
                "case_id": "bounded",
                "stratum": "common",
                "roles": ["sentinel", "bounded_control"],
                "reference": {
                    "status": runner.campaign.RESULT_BOUNDED_UNKNOWN,
                    "placement_digest": None,
                },
            },
            result,
        )

        self.assertTrue(assessment["hard_gate_passed"])

    def test_timing_summary_uses_observed_median_range_and_mad(self) -> None:
        summary = runner._timing_summary(_result())

        self.assertEqual(summary["sample_count"], 5)
        self.assertEqual(summary["minimum_ms"], 9.0)
        self.assertEqual(summary["median_ms"], 11.0)
        self.assertEqual(summary["maximum_ms"], 13.0)
        self.assertEqual(summary["range_ms"], 4.0)
        self.assertEqual(summary["mad_ms"], 1.0)

    def test_cli_has_no_holdout_surface_and_bounded_batch(self) -> None:
        help_text = runner._parser().format_help()

        self.assertNotIn("holdout", help_text.lower())
        self.assertIn("--max-new-cases", help_text)
        self.assertIn("--seed-checkpoint", help_text)
        self.assertEqual(runner.MAX_BATCH_SIZE, 4)


if __name__ == "__main__":
    unittest.main()
