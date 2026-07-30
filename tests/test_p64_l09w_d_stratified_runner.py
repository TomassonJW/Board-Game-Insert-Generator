from __future__ import annotations

from pathlib import Path
import unittest

from scripts.solver import run_p64_l09w_d_stratified_validation as runner


ROOT = Path(__file__).resolve().parents[1]


def _case_result(
    *,
    ready: bool,
    target_loss: bool = False,
    deterministic: bool = True,
    functional_digest: str = "functional",
) -> dict[str, object]:
    return {
        "status": runner.campaign.RESULT_CERTIFIED,
        "deterministic": deterministic,
        "losses": (
            [{"detail": runner.planner.TARGET_LOSS}]
            if target_loss
            else []
        ),
        "runs": [
            {
                "solver_status": "solution_found",
                "functional_digest": functional_digest,
                "placement_digest": "placement",
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
        ],
    }


class P64L09WDStratifiedRunnerTests(unittest.TestCase):
    def test_ready_non_regression_requires_same_function_and_ready_chain(
        self,
    ) -> None:
        row = {
            "case_id": "ready",
            "stratum": "common",
            "tiers": ["ready_non_regression"],
            "required_repeats": 1,
        }
        reference = _case_result(ready=True)
        passed = runner.assess_case(
            schedule_row=row,
            reference_result=reference,
            candidate_result=_case_result(ready=True),
        )
        self.assertTrue(passed["hard_gate_passed"])

        regressed = runner.assess_case(
            schedule_row=row,
            reference_result=reference,
            candidate_result=_case_result(
                ready=True,
                functional_digest="changed",
            ),
        )
        self.assertIn(
            "ready_functional_digest_regression",
            regressed["failures"],
        )

    def test_causal_case_requires_ready_chain_and_removed_target_loss(
        self,
    ) -> None:
        row = {
            "case_id": "causal",
            "stratum": "stress",
            "tiers": ["causal", "target_stratified"],
            "required_repeats": 2,
        }
        reference = _case_result(ready=False, target_loss=True)
        passed = runner.assess_case(
            schedule_row=row,
            reference_result=reference,
            candidate_result=_case_result(ready=True),
        )
        self.assertTrue(passed["hard_gate_passed"])

        failed = runner.assess_case(
            schedule_row=row,
            reference_result=reference,
            candidate_result=_case_result(
                ready=False,
                target_loss=True,
            ),
        )
        self.assertIn("causal_case_failure", failed["failures"])

        nondeterministic = runner.assess_case(
            schedule_row=row,
            reference_result={
                **reference,
                "deterministic": True,
            },
            candidate_result=_case_result(
                ready=True,
                deterministic=False,
            ),
        )
        self.assertIn(
            "target_replay_nondeterminism_regression",
            nondeterministic["failures"],
        )

        preexisting = runner.assess_case(
            schedule_row=row,
            reference_result={
                **reference,
                "deterministic": False,
            },
            candidate_result=_case_result(
                ready=True,
                deterministic=False,
            ),
        )
        self.assertTrue(preexisting["hard_gate_passed"])
        self.assertTrue(preexisting["preexisting_nondeterminism"])

    def test_execution_order_starts_with_stress_causal_then_ready(self) -> None:
        rows = [
            {
                "case_id": "target",
                "stratum": "stress",
                "tiers": ["target_stratified"],
                "reference_calculation_ms": 1,
            },
            {
                "case_id": "ready",
                "stratum": "common",
                "tiers": ["ready_non_regression"],
                "reference_calculation_ms": 1,
            },
            {
                "case_id": "causal-common",
                "stratum": "common",
                "tiers": ["causal"],
                "reference_calculation_ms": 1,
            },
            {
                "case_id": "causal-stress",
                "stratum": "stress",
                "tiers": ["causal"],
                "reference_calculation_ms": 100,
            },
        ]
        self.assertEqual(
            [row["case_id"] for row in runner._execution_order(rows)],
            ["causal-stress", "causal-common", "ready", "target"],
        )

    def test_cli_has_no_holdout_input(self) -> None:
        source = (
            ROOT
            / "scripts/solver/run_p64_l09w_d_stratified_validation.py"
        ).read_text(encoding="utf-8")
        self.assertNotIn("--holdout", source)


if __name__ == "__main__":
    unittest.main()
