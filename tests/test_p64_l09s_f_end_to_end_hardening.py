from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PREFLIGHT = ROOT / "scripts" / "fusion" / "p64_l09sv_preflight.py"
PREPARER = ROOT / "scripts" / "fusion" / "prepare_p64_l09sv_gate.ps1"
HISTORICAL_PREPARER = ROOT / "scripts" / "fusion" / "prepare_p64_l09rv_gate.ps1"
HISTORICAL_EVIDENCE = ROOT / "docs" / "P64_L09R_V_0165_HUMAN_KO_EVIDENCE.md"
MANIFEST = (
    ROOT
    / "fusion_addin"
    / "BoardGameInsertGenerator"
    / "BoardGameInsertGenerator.manifest"
)


def _load_preflight_module():
    spec = importlib.util.spec_from_file_location("p64_l09sv_preflight", PREFLIGHT)
    if spec is None or spec.loader is None:
        raise RuntimeError("Cannot load P64-L09S-V preflight module.")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class P64L09SFEndToEndHardeningTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = _load_preflight_module()
        cls.project, cls.summary = cls.module.build_preflight()
        cls.preparer = PREPARER.read_text(encoding="utf-8")
        cls.historical_preparer = HISTORICAL_PREPARER.read_text(encoding="utf-8")
        cls.historical_evidence = HISTORICAL_EVIDENCE.read_text(encoding="utf-8")
        cls.manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))

    def test_0166_is_distinct_from_frozen_human_ko_0165(self) -> None:
        self.assertEqual(self.manifest["version"], "0.1.70")
        self.assertEqual(self.summary["addin_version"], "0.1.69")
        self.assertIn('expectedVersion -ne "0.1.69"', self.preparer)
        self.assertIn("calculate in Normal", self.preparer)
        self.assertIn("without imposing one winning lane", self.preparer)
        self.assertIn("67.6 mm final upright-card cavity", self.preparer)
        self.assertNotIn("with one tray, then with several trays", self.preparer)
        self.assertNotIn("require a certified solution from the SCIP lane", self.preparer)
        self.assertIn('expectedVersion -ne "0.1.65"', self.historical_preparer)
        self.assertIn("human-KO", self.historical_evidence)
        self.assertIn("ne doit pas", self.historical_evidence)

    def test_recent_limit_contract_keeps_minimum_and_gap(self) -> None:
        contract = self.summary["recent_limit_contract"]
        self.assertEqual(
            contract["body_size_mm"],
            {"x": 23.2, "y": 23.2, "z": 31.6},
        )
        self.assertEqual(contract["body_top_z_mm"], 52.8)
        self.assertEqual(contract["support_plane_z_mm"], 58.6)
        self.assertEqual(contract["gap_below_tray_mm"], 5.8)
        self.assertEqual(contract["artificial_growth_mm"], 0.0)
        self.assertTrue(contract["reserved_prisms_certified"])
        self.assertFalse(contract["support_required"])

    def test_public_fixture_runs_minimal_to_composite_fusion_plan(self) -> None:
        flow = self.summary["end_to_end"]
        self.assertEqual(
            flow["minimal"]["minimum_outer_envelope_mm"],
            {"x": 23.2, "y": 23.2, "z": 31.6},
        )
        self.assertEqual(
            flow["minimal"]["reservation_required_z_compensation_mm"],
            0.0,
        )
        self.assertTrue(flow["minimal"]["materializable"])
        self.assertEqual(
            flow["finalization"]["selected_plan_source"],
            "f_xy_composite_v2_union_cavities_insets",
        )
        self.assertTrue(
            flow["finalization"]["composite_certificate"]["certified"]
        )
        self.assertEqual(
            flow["finalization"]["composite_certificate"]
            ["printable_residual_volume_mm3"],
            0.0,
        )
        self.assertTrue(
            flow["finalization"]["composite_certificate"]
            ["cavity_world_poses_match_frozen_contract"]
        )
        self.assertTrue(
            flow["finalization"]["composite_certificate"]
            ["cavity_vertical_access_open"]
        )
        self.assertEqual(flow["fusion_plan"]["user_component_count"], 1)
        self.assertGreater(flow["fusion_plan"]["joined_annex_count"], 0)
        self.assertGreater(flow["fusion_plan"]["top_inset_cut_count"], 0)
        self.assertTrue(flow["fusion_plan"]["all_annexes_xy"])
        self.assertFalse(flow["fusion_plan"]["fusion_observed"])

    def test_preflight_declares_no_forbidden_external_validation(self) -> None:
        self.assertFalse(self.summary["holdout_opened"])
        self.assertFalse(self.summary["benchmark_executed"])
        self.assertFalse(self.summary["fusion_validated"])
        self.assertFalse(self.summary["print_validated"])
        source = PREFLIGHT.read_text(encoding="utf-8")
        self.assertNotIn("p64_l08l_scip_repeated_fill_regression", source)
        self.assertNotIn("solver_benchmark", source)
        self.assertIn("P64_L09SV_PREFLIGHT_OK", source)

    def test_preparer_installs_exact_commit_and_leaves_only_human_gate(self) -> None:
        for marker in (
            "bgig.bounded_coupled_finalization.v8",
            "e_xy_composite_union_and_exact_insets",
            "bgig.xy_composite_cad_body.v1",
            "bounded_xy_composite_v1",
            "Bounded XY-composite",
            "palette_project.py",
            "finalized_plan_not_published",
            "bgig_installed_commit.txt",
            "Local AppData write blocked. Use Local/Handoff or approve filesystem write.",
            "one user component per owner",
            "print-validated=false",
        ):
            self.assertIn(marker, self.preparer)
        self.assertIn("install_addin.ps1", self.preparer)
        self.assertIn("check_installed_addin.ps1", self.preparer)
        self.assertIn("Prepared P64-L09S-V gate", self.preparer)


if __name__ == "__main__":
    unittest.main()
