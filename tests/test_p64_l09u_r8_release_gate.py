from __future__ import annotations

import json
from pathlib import Path
import unittest

from scripts.fusion.p64_l09u_r8v_preflight import (
    ADDIN_VERSION,
    AUTHORIZED_EXCLUDED_TEST_MODULES,
    build_preflight,
    stable_digest,
)


ROOT = Path(__file__).resolve().parents[1]
EXPECTED_EXCLUSIONS = {
    "test_anonymized_solver_case_corpus_builder",
    "test_external_solver_benchmark_corpus",
    "test_external_solver_tournament",
    "test_external_solver_tournament_evidence",
    "test_external_solver_tournament_runner",
    "test_external_solver_tournament_selection",
    "test_real_3d_solver_corpus",
    "test_real_3d_solver_tournament",
    "test_solver_benchmark_adapters",
    "test_solver_benchmark_campaign",
    "test_solver_benchmark_corpus",
    "test_solver_case_corpus",
}


class P64L09UR8ReleaseGateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.preflight = build_preflight()

    def test_preflight_proves_strict_subtraction_and_keeps_gate_open(
        self,
    ) -> None:
        preflight = self.preflight
        strict = preflight["strict_subtractive_pipeline"]
        contract = preflight["r8_contract"]

        self.assertEqual(ADDIN_VERSION, "0.1.79")
        self.assertEqual(preflight["addin_version"], ADDIN_VERSION)
        self.assertEqual(
            preflight["gate_status"],
            "prepared_not_human_observed",
        )
        self.assertGreater(strict["operation_count"], 0)
        self.assertEqual(strict["flat_positive_volume_mm3"], 0.0)
        self.assertEqual(strict["flat_positive_body_count"], 0)
        self.assertEqual(strict["flat_positive_union_count"], 0)
        self.assertEqual(strict["flat_positive_operation_count"], 0)
        self.assertEqual(
            strict[
                "new_printable_body_count_attributed_to_flat_items"
            ],
            0,
        )
        self.assertTrue(strict["positive_geometry_unchanged"])
        self.assertTrue(strict["all_operations_difference_only"])
        self.assertTrue(strict["cad_plan_identical"])
        self.assertTrue(strict["fusion_certificate_identical"])
        self.assertTrue(
            strict["fusion_and_brep_intervals_identical"]
        )
        self.assertTrue(
            contract[
                "final_result_is_finalized_containers_minus_local_insets"
            ]
        )
        self.assertEqual(contract["product_grid_step_mm"], 0.1)
        self.assertTrue(
            contract["numeric_epsilon_is_not_product_resolution"]
        )
        self.assertFalse(contract["source_project_written"])
        self.assertFalse(contract["fusion_validated"])
        self.assertFalse(contract["print_validated"])

    def test_authorized_suite_excludes_exactly_twelve_modules_before_import(
        self,
    ) -> None:
        suite = self.preflight["authorized_suite"]

        self.assertEqual(
            set(AUTHORIZED_EXCLUDED_TEST_MODULES),
            EXPECTED_EXCLUSIONS,
        )
        self.assertEqual(len(AUTHORIZED_EXCLUDED_TEST_MODULES), 12)
        self.assertEqual(suite["excluded_module_count"], 12)
        self.assertTrue(suite["excluded_before_import"])
        self.assertFalse(
            suite["forbidden_solver_campaigns_executed"]
        )

    def test_preflight_digest_ignores_only_volatile_timings(self) -> None:
        first = {
            "contract": {"value": 7, "observed_ms": 12.5},
            "calculation_observed_ms": 10.0,
        }
        second = {
            "contract": {"value": 7, "observed_ms": 99.9},
            "calculation_observed_ms": 88.8,
        }

        self.assertEqual(stable_digest(first), stable_digest(second))
        second["contract"]["value"] = 8
        self.assertNotEqual(stable_digest(first), stable_digest(second))

    def test_preflight_digest_keeps_inherited_contract_not_run_artifacts(
        self,
    ) -> None:
        first = {
            "inherited_r7_preflight": {
                "r7_contract": {"grid_step_mm": 0.1},
                "inherited_r6_preflight": {
                    "runtime_contract": {"cavity_access": True},
                    "end_to_end": {"artifact_digest": "first"},
                    "preflight_digest": "first",
                },
            }
        }
        second = json.loads(json.dumps(first))
        second["inherited_r7_preflight"]["inherited_r6_preflight"][
            "end_to_end"
        ]["artifact_digest"] = "second"
        second["inherited_r7_preflight"]["inherited_r6_preflight"][
            "preflight_digest"
        ] = "second"

        self.assertEqual(stable_digest(first), stable_digest(second))
        second["inherited_r7_preflight"]["inherited_r6_preflight"][
            "runtime_contract"
        ]["cavity_access"] = False
        self.assertNotEqual(stable_digest(first), stable_digest(second))

    def test_manifest_and_preparer_pin_candidate(self) -> None:
        manifest = json.loads(
            (
                ROOT
                / "fusion_addin/BoardGameInsertGenerator/BoardGameInsertGenerator.manifest"
            ).read_text(encoding="utf-8")
        )
        preparer = (
            ROOT / "scripts/fusion/prepare_p64_l09u_r8v_gate.ps1"
        ).read_text(encoding="utf-8")

        self.assertEqual(manifest["version"], "0.1.80")
        for marker in (
            'expectedVersion -ne "0.1.79"',
            "p64_l09u_r8v_preflight.py",
            "--case-id case02_plus",
            "--case-id case02_plus_plus",
            "subtractive_flat_inset_certificate",
            "strictly_subtractive_flat_inset_v1",
            "flat_inset_subtraction_plan",
            "Fusion transient cuts accept difference operations only.",
            "bgig_installed_commit.txt",
            "fusion-validated=false",
            "print-validated=false",
        ):
            self.assertIn(marker, preparer)

    def test_personal_replay_pins_hashes_and_strict_contract(self) -> None:
        replay = (
            ROOT / "scripts/fusion/p64_l09t_local_replay.py"
        ).read_text(encoding="utf-8")

        for marker in (
            "5e84fe6f5c0b3e5f046201d442c414504dd95d4db8e711169a2624485466d7dc",
            "83e9e90a6bfd86b18d3a157077a0e63dc2f543ddab626adb2151e269e01d9743",
            "strict_flat_inset_operation_count",
            "strict_flat_inset_intervals_identical",
            "new_printable_body_count_attributed_to_flat_items",
            "EXPECTED_STRICT_LOCAL_DEPTHS_MM",
            "source_sha256_before",
            "source_sha256_after",
        ):
            self.assertIn(marker, replay)


if __name__ == "__main__":
    unittest.main()
