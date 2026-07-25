from __future__ import annotations

from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PREFLIGHT = ROOT / "scripts" / "fusion" / "p64_l09rv_preflight.py"
PREPARER = ROOT / "scripts" / "fusion" / "prepare_p64_l09rv_gate.ps1"
RECIPE = ROOT / "docs" / "P64_L09R_V_FUSION_GATE_RECIPE.md"
EVIDENCE = ROOT / "docs" / "P64_L09R_F_REPRESENTATIVE_HARDENING_EVIDENCE.md"
MANIFEST = ROOT / "fusion_addin" / "BoardGameInsertGenerator" / "BoardGameInsertGenerator.manifest"
HISTORICAL_PREPARER = ROOT / "scripts" / "fusion" / "prepare_p64_l09v_combined_gate.ps1"


def load_preflight_module() -> object:
    spec = importlib.util.spec_from_file_location("p64_l09rv_preflight", PREFLIGHT)
    if spec is None or spec.loader is None:
        raise AssertionError("Le préflight P64-L09R-V ne peut pas être importé.")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class P64L09RFRepresentativeHardeningTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = load_preflight_module()
        cls.projects, cls.summary = cls.module.build_preflight()

    def test_preflight_covers_public_28x30_without_holdout_or_benchmark(self) -> None:
        control = self.summary["public_28x30"]

        self.assertEqual(control["status"], "solution_found")
        self.assertEqual(control["placement_count"], 28)
        self.assertTrue(control["external_recertified"])
        self.assertFalse(control["holdout_read"])
        self.assertFalse(self.summary["holdout_opened"])
        self.assertFalse(self.summary["benchmark_executed"])
        self.assertFalse(self.summary["fusion_validated"])
        self.assertFalse(self.summary["print_validated"])

    def test_preference_fixture_observes_soft_small_below_large_order(self) -> None:
        flow = self.summary["fixtures"]["preference"]["flow"]
        placements = {
            item["container_group_id"]: item for item in flow["placements"]
        }
        large_z = placements["large"]["origin_mm"]["z"]

        self.assertGreater(large_z, placements["small-a"]["origin_mm"]["z"])
        self.assertGreater(large_z, placements["small-b"]["origin_mm"]["z"])
        self.assertTrue(flow["minimal"]["materializable"])
        self.assertEqual(flow["minimal"]["cad_status"], "ready_for_fusion")
        self.assertEqual(flow["minimal"]["budget_ms"], 20_000)
        self.assertGreaterEqual(flow["minimal"]["observed_ms"], 0.0)

    def test_tray_fixture_materializes_minimal_then_final_with_separate_measurements(self) -> None:
        flow = self.summary["fixtures"]["tray_flow"]["flow"]
        minimal = flow["minimal"]
        finishing = flow["finishing"]

        self.assertGreaterEqual(flow["reservation_count"], 1)
        self.assertTrue(minimal["materializable"])
        self.assertTrue(finishing["materializable"])
        self.assertEqual(minimal["cad_status"], "ready_for_fusion")
        self.assertEqual(finishing["cad_status"], "ready_for_fusion")
        self.assertEqual(minimal["budget_ms"], 20_000)
        self.assertEqual(finishing["budget_ms"], 3_000)
        self.assertGreaterEqual(minimal["observed_ms"], 0.0)
        self.assertGreaterEqual(finishing["observed_ms"], 0.0)
        self.assertEqual(
            finishing["source_minimal_artifact_digest"],
            minimal["artifact_digest"],
        )
        self.assertNotEqual(finishing["artifact_digest"], minimal["artifact_digest"])
        self.assertTrue(self.summary["separate_measurements"])

    def test_receipt_digest_ignores_only_observed_machine_durations(self) -> None:
        repeated = deepcopy(self.summary)
        for fixture in repeated["fixtures"].values():
            fixture["flow"]["minimal"]["observed_ms"] = 999_001.0
            fixture["flow"]["finishing"]["observed_ms"] = 999_002.0

        self.assertEqual(
            self.summary["preflight_digest"],
            self.module._preflight_digest(repeated),
        )
        self.assertEqual(
            set(self.summary["fixtures"]),
            {"preference", "tray_flow"},
        )
        self.assertEqual(
            self.summary["expected_ui"]["calculation_budgets_seconds"],
            [3, 10, 20, 60, 180],
        )
        self.assertEqual(
            self.summary["expected_ui"]["finishing_budgets_seconds"],
            [3, 10, 20, 60, 180],
        )
        self.assertEqual(self.summary["expected_ui"]["activity_refresh_ms"], 1_000)
        self.assertTrue(self.summary["expected_ui"]["activity_absent_at_rest"])
    def test_new_gate_is_unambiguously_versioned_and_old_gate_stays_superseded(self) -> None:
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        preparer = PREPARER.read_text(encoding="utf-8")
        historical = HISTORICAL_PREPARER.read_text(encoding="utf-8")

        self.assertEqual(manifest["version"], "0.1.64")
        self.assertEqual(self.summary["addin_version"], "0.1.64")
        self.assertIn('expectedVersion -ne "0.1.64"', preparer)
        self.assertIn("p64_l09rv_preflight.py", preparer)
        self.assertIn("p64-l09rv-01-preference-envelope.bgig.json", preparer)
        self.assertIn("p64-l09rv-02-tray-separated-flow.bgig.json", preparer)
        self.assertIn("worker imports adsk", preparer)
        self.assertIn("P64-L09R-V", preparer)
        self.assertIn('expectedVersion -ne "0.1.63"', historical)
        self.assertNotIn("p64_l09rv_preflight.py", historical)

    def test_gate_recipe_is_complete_and_never_promotes_print_validation(self) -> None:
        recipe = RECIPE.read_text(encoding="utf-8")
        evidence = EVIDENCE.read_text(encoding="utf-8")

        for marker in (
            "prepared-not-installed",
            "prepare_p64_l09rv_gate.ps1",
            "Local AppData write blocked. Use Local/Handoff or approve filesystem write.",
            "Observation au repos",
            "Fixture 01",
            "Fixture 02",
            "Matérialisation minimale avant finition",
            "Finition séparée et plan final",
            "Résultat à me renvoyer",
            "print-validated=false",
        ):
            self.assertIn(marker, recipe)
        self.assertIn("Aucune installation Fusion n’est exécutée dans F", evidence)
        self.assertNotIn("fusion-validated=true", recipe)
        self.assertNotIn("print-validated=true", recipe)


if __name__ == "__main__":
    unittest.main()