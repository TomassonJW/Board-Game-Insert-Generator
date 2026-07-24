from __future__ import annotations

import json
from pathlib import Path
import unittest

from board_game_insert_generator.incremental_project_state import canonical_digest


ROOT = Path(__file__).resolve().parents[1]
RECEIPT = ROOT / "tests" / "fixtures" / "p64_l08e_real_3d_adapter_controls_receipt.v1.json"


class Real3DAdapterControlsReceiptTests(unittest.TestCase):
    def test_receipt_is_bound_and_exceeds_the_three_engine_gate(self) -> None:
        payload = json.loads(RECEIPT.read_text(encoding="utf-8"))
        supplied = payload.pop("receipt_digest")
        self.assertEqual(canonical_digest(payload), supplied)
        self.assertEqual(payload["candidate_count"], 4)
        self.assertEqual(payload["candidate_family_count"], 4)
        self.assertEqual(payload["invariants"]["external_engines_executed"], 4)
        self.assertFalse(payload["invariants"]["positive_witness_transmitted"])
        self.assertFalse(payload["invariants"]["holdout_opened"])
        self.assertEqual(payload["invariants"]["unsupported_hidden_count"], 0)

    def test_full_models_pass_all_exact_controls(self) -> None:
        payload = json.loads(RECEIPT.read_text(encoding="utf-8"))
        records = payload["records"]
        for candidate in ("ortools_cp_sat", "scip"):
            candidate_records = [value for value in records if value["candidate_id"] == candidate]
            self.assertEqual(len(candidate_records), payload["control_count"])
            self.assertTrue(
                all(value["worker_invocation_count"] == 1 for value in candidate_records)
            )
            self.assertTrue(
                all(
                    value["status"]
                    == (
                        "infeasible_proven"
                        if value["expected"] == "infeasible"
                        else "solution_found"
                    )
                    for value in candidate_records
                )
            )

    def test_specialized_engines_execute_real_stacks_and_refuse_missing_rules(self) -> None:
        payload = json.loads(RECEIPT.read_text(encoding="utf-8"))
        for candidate in ("packingsolver_box", "laff"):
            records = {
                value["control_id"]: value
                for value in payload["records"]
                if value["candidate_id"] == candidate
            }
            stack = records["stacking-feasible"]
            self.assertEqual(stack["status"], "solution_found")
            self.assertTrue(stack["recertification"]["certified"])
            z_values = sorted(value["z"] for value in stack["engine"]["placements"])
            self.assertEqual(z_values[0], 0)
            self.assertGreater(z_values[1], 0)
            for control_id in (
                "multi-support-feasible",
                "reservation-feasible",
                "fragmentation-feasible",
                "variant-rotation-feasible",
            ):
                self.assertEqual(records[control_id]["status"], "unsupported")
                self.assertEqual(records[control_id]["worker_invocation_count"], 0)
                self.assertTrue(records[control_id]["unsupported_constraints"])


if __name__ == "__main__":
    unittest.main()
