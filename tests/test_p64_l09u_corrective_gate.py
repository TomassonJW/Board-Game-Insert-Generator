from __future__ import annotations

from pathlib import Path
import json
import unittest

from scripts.fusion.p64_l09uv_preflight import (
    ADDIN_VERSION,
    TARGETED_MATRIX,
    build_preflight,
)


ROOT = Path(__file__).resolve().parents[1]


class P64L09UCorrectiveGateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.project, cls.preflight = build_preflight()

    def test_preflight_proves_batched_features_without_claiming_human_gates(
        self,
    ) -> None:
        self.assertEqual(ADDIN_VERSION, "0.1.71")
        self.assertEqual(self.preflight["addin_version"], ADDIN_VERSION)
        self.assertEqual(
            set(self.preflight["targeted_matrix"]["required_case_ids"]),
            set(TARGETED_MATRIX),
        )
        fusion = self.preflight["end_to_end"]["fusion_plan"]
        self.assertLess(
            fusion["additive_prism_join_batch_count"],
            fusion["logical_additive_prism_join_count"],
        )
        self.assertLess(
            fusion["cavity_cut_batch_count"],
            fusion["logical_cavity_cut_count"],
        )
        self.assertFalse(self.preflight["holdout_opened"])
        self.assertFalse(self.preflight["benchmark_executed"])
        self.assertFalse(self.preflight["fusion_validated"])
        self.assertFalse(self.preflight["print_validated"])
        self.assertEqual(
            self.preflight["gate_status"],
            "prepared_not_human_observed",
        )

    def test_runtime_contract_forbids_restart_reuse(self) -> None:
        contract = self.preflight["runtime_contract"]
        self.assertEqual(
            contract["session_start_policy"],
            "fresh_unsaved_project",
        )
        self.assertFalse(contract["legacy_recovery_file_read"])
        self.assertFalse(contract["cross_session_witness_reuse"])
        self.assertFalse(contract["cross_session_witness_persistence"])
        self.assertTrue(contract["explicit_calculation_required"])
        self.assertTrue(contract["logical_cad_operations_preserved"])
        self.assertTrue(contract["fusion_features_batched_per_owner"])

    def test_package_and_preparer_pin_the_0171_candidate(self) -> None:
        addin = ROOT / "fusion_addin" / "BoardGameInsertGenerator"
        manifest = json.loads(
            (addin / "BoardGameInsertGenerator.manifest").read_text(
                encoding="utf-8"
            )
        )
        preparer = (
            ROOT / "scripts" / "fusion" / "prepare_p64_l09uv_gate.ps1"
        ).read_text(encoding="utf-8")
        self.assertEqual(manifest["version"], "0.1.71")
        for marker in (
            'expectedVersion -ne "0.1.71"',
            "p64_l09uv_preflight.py",
            "p64_l09t_local_replay.py",
            "fresh_unsaved_project",
            "_persist_temporary_box_tools",
            "current_path = \"\"",
            "fusion-validated=false",
            "print-validated=false",
        ):
            self.assertIn(marker, preparer)

    def test_personal_replay_is_read_only_and_has_no_witness(self) -> None:
        replay = (
            ROOT / "scripts" / "fusion" / "p64_l09t_local_replay.py"
        ).read_text(encoding="utf-8")
        self.assertIn("initial_incumbent=None", replay)
        self.assertIn('"witness_status": "disabled"', replay)
        self.assertIn("source_projects_unchanged", replay)
        self.assertNotIn(r"C:\Users", replay)


if __name__ == "__main__":
    unittest.main()
