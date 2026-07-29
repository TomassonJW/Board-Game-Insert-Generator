from __future__ import annotations

import json
from pathlib import Path
import unittest

from scripts.fusion.p64_l09u_r9v_preflight import (
    ADDIN_VERSION,
    AUTHORITATIVE_PLACEMENT_DIGEST,
    AUTHORITATIVE_PROJECT_SHA256,
    AUTHORIZED_EXCLUDED_TEST_MODULES,
    EXPECTED_DEEP_BUDGET,
    R9_SELECTED_STATEMENT,
    R9_SOLVER_VERSION,
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


class P64L09UR9ReleaseGateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.preflight = build_preflight()

    def test_preflight_selects_certified_internal_prefix_without_scip(
        self,
    ) -> None:
        route = self.preflight["performance_route"]

        self.assertEqual(ADDIN_VERSION, "0.1.80")
        self.assertEqual(self.preflight["addin_version"], ADDIN_VERSION)
        self.assertEqual(
            self.preflight["gate_status"],
            "prepared_not_human_observed",
        )
        self.assertEqual(
            route["minimal_layout_solver_version"],
            R9_SOLVER_VERSION,
        )
        self.assertEqual(
            route["selected_statement"],
            R9_SELECTED_STATEMENT,
        )
        self.assertTrue(
            route["first_certified_geometric_group_authority"]
        )
        self.assertEqual(route["internal_lane_count"], 1)
        self.assertEqual(route["scip_call_count"], 0)
        self.assertTrue(route["external_lane_absent"])
        self.assertGreater(route["certified_candidate_count"], 0)
        self.assertEqual(
            route["deep_budget"],
            EXPECTED_DEEP_BUDGET,
        )
        self.assertFalse(route["budget_increased"])

    def test_r8_geometry_and_numeric_contract_remain_authoritative(
        self,
    ) -> None:
        inherited = self.preflight["inherited_r8_preflight"]
        strict = inherited["strict_subtractive_pipeline"]
        contract = self.preflight["r9_contract"]

        self.assertTrue(strict["all_operations_difference_only"])
        self.assertEqual(strict["flat_positive_volume_mm3"], 0.0)
        self.assertEqual(strict["flat_positive_body_count"], 0)
        self.assertEqual(strict["flat_positive_union_count"], 0)
        self.assertEqual(
            strict[
                "new_printable_body_count_attributed_to_flat_items"
            ],
            0,
        )
        self.assertTrue(
            contract[
                "functional_result_0179_remains_authoritative"
            ]
        )
        self.assertEqual(contract["product_grid_step_mm"], 0.1)
        self.assertEqual(contract["numeric_epsilon_mm"], 0.0001)
        self.assertTrue(
            contract["numeric_epsilon_is_not_product_resolution"]
        )
        self.assertFalse(contract["budget_increased"])
        self.assertFalse(contract["source_project_written"])
        self.assertFalse(contract["fusion_validated"])
        self.assertFalse(contract["print_validated"])

    def test_personal_replay_contract_pins_authoritative_inputs(
        self,
    ) -> None:
        replay = self.preflight["personal_project_replay_contract"]

        self.assertEqual(replay["effort_profile"], "deep")
        self.assertEqual(
            replay["placement_digest"],
            AUTHORITATIVE_PLACEMENT_DIGEST,
        )
        self.assertEqual(
            replay["source_sha256"],
            AUTHORITATIVE_PROJECT_SHA256,
        )
        self.assertFalse(replay["source_project_written"])
        self.assertFalse(replay["new_benchmark_or_corpus_created"])

    def test_authorized_suite_excludes_exactly_twelve_modules(
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
            "route": {"value": 7, "calculation_observed_ms": 12.5},
            "finalization_observed_ms": 10.0,
        }
        second = {
            "route": {"value": 7, "calculation_observed_ms": 99.9},
            "finalization_observed_ms": 88.8,
        }

        self.assertEqual(stable_digest(first), stable_digest(second))
        second["route"]["value"] = 8
        self.assertNotEqual(stable_digest(first), stable_digest(second))

    def test_manifest_preparer_and_human_recipe_pin_candidate(
        self,
    ) -> None:
        manifest = json.loads(
            (
                ROOT
                / "fusion_addin/BoardGameInsertGenerator/"
                "BoardGameInsertGenerator.manifest"
            ).read_text(encoding="utf-8")
        )
        preparer = (
            ROOT / "scripts/fusion/prepare_p64_l09u_r9v_gate.ps1"
        ).read_text(encoding="utf-8")
        recipe = (
            ROOT / "docs/P64_L09U_R9_V_0180_FUSION_GATE_RECIPE.md"
        ).read_text(encoding="utf-8")
        evidence = (
            ROOT / "docs/P64_L09U_R9_0180_PERFORMANCE_RECOVERY_EVIDENCE.md"
        ).read_text(encoding="utf-8")

        self.assertEqual(manifest["version"], "0.1.80")
        for marker in (
            'expectedVersion -ne "0.1.80"',
            "p64_l09u_r9v_preflight.py",
            "--case-id case02_plus",
            "--case-id case02_plus_plus",
            "--calculation-effort deep",
            "--include-diagnostics",
            AUTHORITATIVE_PLACEMENT_DIGEST,
            "source_sha256_before",
            "source_sha256_after",
            "p64-l09u-r9-c-v2",
            "bgig_installed_commit.txt",
            "fusion-validated=false",
            "print-validated=false",
        ):
            self.assertIn(marker, preparer)
        self.assertIn("pas la recette R8", recipe)
        self.assertIn("une seule fois `Calculer`", recipe)
        self.assertIn("Approfondi", recipe)
        self.assertIn("P64-L09U-R9-V Fusion OK 0.1.80", recipe)
        self.assertNotIn("PowerShell", recipe)
        self.assertIn("953", evidence)
        self.assertIn("3,727 s", evidence)
        self.assertIn("3,911 s", evidence)


if __name__ == "__main__":
    unittest.main()
