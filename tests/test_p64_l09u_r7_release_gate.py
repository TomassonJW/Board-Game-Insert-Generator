from __future__ import annotations

import json
from pathlib import Path
import unittest

from scripts.fusion.p64_l09u_r7v_preflight import (
    ADDIN_VERSION,
    build_preflight,
)


ROOT = Path(__file__).resolve().parents[1]


class P64L09UR7ReleaseGateTests(unittest.TestCase):
    def test_preflight_keeps_human_validation_open(self) -> None:
        preflight = build_preflight()
        self.assertEqual(ADDIN_VERSION, "0.1.78")
        self.assertEqual(preflight["addin_version"], ADDIN_VERSION)
        self.assertEqual(
            preflight["gate_status"],
            "prepared_not_human_observed",
        )
        contract = preflight["r7_contract"]
        self.assertEqual(contract["product_grid_step_mm"], 0.1)
        self.assertTrue(contract["numeric_epsilon_is_not_product_resolution"])
        self.assertTrue(contract["canonical_wall_minimum_from_project_settings"])
        self.assertTrue(contract["final_material_envelope_recertified"])
        self.assertTrue(
            contract[
                "automatic_flat_stack_smallest_oriented_footprint_first"
            ]
        )
        self.assertFalse(contract["source_project_written"])
        self.assertFalse(contract["fusion_validated"])
        self.assertFalse(contract["print_validated"])
        self.assertFalse(preflight["forbidden_solver_campaigns_executed"])

    def test_manifest_and_preparer_pin_candidate(self) -> None:
        manifest = json.loads(
            (
                ROOT
                / "fusion_addin/BoardGameInsertGenerator/BoardGameInsertGenerator.manifest"
            ).read_text(encoding="utf-8")
        )
        preparer = (
            ROOT / "scripts/fusion/prepare_p64_l09u_r7v_gate.ps1"
        ).read_text(encoding="utf-8")
        self.assertEqual(manifest["version"], "0.1.80")
        for marker in (
            'expectedVersion -ne "0.1.78"',
            "p64_l09u_r7v_preflight.py",
            "--case-id case02_plus",
            "--case-id case02_plus_plus",
            "PRODUCT_GRID_STEP_MM = 0.1",
            "automatic_stack_key_v1",
            "final_material_envelope_certificate",
            "bgig_installed_commit.txt",
            "fusion-validated=false",
            "print-validated=false",
        ):
            self.assertIn(marker, preparer)


if __name__ == "__main__":
    unittest.main()
