from __future__ import annotations

from pathlib import Path
import json
import unittest

from scripts.fusion.p64_l09uw_preflight import (
    ADDIN_VERSION,
    TARGETED_MATRIX,
    build_preflight,
)


ROOT = Path(__file__).resolve().parents[1]


class P64L09UR4CorrectiveGateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.project, cls.preflight = build_preflight()

    def test_preflight_proves_exact_transient_path_without_human_claims(
        self,
    ) -> None:
        self.assertEqual(ADDIN_VERSION, "0.1.75")
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
        contract = self.preflight["runtime_contract"]
        self.assertTrue(
            contract["finalization_uses_exact_selected_minimal_plan"]
        )
        self.assertTrue(contract["transient_boolean_body_per_module"])
        self.assertEqual(contract["parametric_combine_feature_count"], 0)
        self.assertEqual(
            contract["top_inset_cavity_interface"],
            "direct_void_to_removable_top_inset",
        )
        self.assertEqual(
            contract["intermediate_material_thickness_mm"],
            0.0,
        )
        self.assertTrue(contract["top_void_continuity_certified"])
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
        self.assertFalse(contract["alternate_minimal_candidate_attempted"])
        self.assertTrue(contract["composite_preview_uses_cad_prisms"])
        self.assertTrue(contract["fusion_ui_yield_between_modules"])
        self.assertTrue(contract["failed_generation_partial_scene_rollback"])

    def test_package_and_preparer_pin_the_0175_candidate(self) -> None:
        addin = ROOT / "fusion_addin" / "BoardGameInsertGenerator"
        manifest = json.loads(
            (addin / "BoardGameInsertGenerator.manifest").read_text(
                encoding="utf-8"
            )
        )
        preparer = (
            ROOT / "scripts" / "fusion" / "prepare_p64_l09uw_gate.ps1"
        ).read_text(encoding="utf-8")
        self.assertEqual(manifest["version"], "0.1.75")
        for marker in (
            'expectedVersion -ne "0.1.75"',
            "p64_l09uw_preflight.py",
            "p64_l09t_local_replay.py",
            "fresh_unsaved_project",
            "_create_boolean_rectangular_blank",
            "BooleanTypes.UnionBooleanType",
            "BooleanTypes.DifferenceBooleanType",
            "_refresh_fusion_generation_ui",
            "_rollback_failed_generation",
            "direct_void_to_removable_top_inset",
            "without intermediate material",
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
        self.assertIn("source_sha256_before", replay)
        self.assertIn("source_sha256_after", replay)
        self.assertIn("CasLimite01++.bgig.json", replay)
        self.assertIn("calibrated_cavity_depths_unchanged", replay)
        self.assertNotIn(r"C:\Users", replay)


if __name__ == "__main__":
    unittest.main()
