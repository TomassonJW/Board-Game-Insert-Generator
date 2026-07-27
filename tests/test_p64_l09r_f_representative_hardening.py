from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PREPARER = ROOT / "scripts" / "fusion" / "prepare_p64_l09rv_gate.ps1"
RECIPE = ROOT / "docs" / "P64_L09R_V_FUSION_GATE_RECIPE.md"
EVIDENCE = ROOT / "docs" / "P64_L09R_V_0165_HUMAN_KO_EVIDENCE.md"
MANIFEST = ROOT / "fusion_addin" / "BoardGameInsertGenerator" / "BoardGameInsertGenerator.manifest"
HISTORICAL_PREPARER = ROOT / "scripts" / "fusion" / "prepare_p64_l09v_combined_gate.ps1"


class P64L09RFRepresentativeHardeningTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.evidence = EVIDENCE.read_text(encoding="utf-8")
        cls.recipe = RECIPE.read_text(encoding="utf-8")
        cls.preparer = PREPARER.read_text(encoding="utf-8")
        cls.historical = HISTORICAL_PREPARER.read_text(encoding="utf-8")
        cls.manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))

    def test_0165_is_human_ko_and_suspended(self) -> None:
        self.assertIn("human-KO", self.evidence)
        self.assertIn("suspended", self.evidence)
        self.assertIn("print-validated=false", self.evidence)

    def test_0165_artificial_growth_is_preserved_as_ko_evidence(self) -> None:
        for marker in ("31,6", "38,4", "6,8", "0,75"):
            self.assertIn(marker, self.evidence)

    def test_0165_false_success_is_preserved_as_ko_evidence(self) -> None:
        self.assertIn("printable_residual_remains", self.evidence)
        self.assertIn("finalized_plan_ready", self.evidence)
        self.assertIn("Projet accept", self.evidence)

    def test_recipe_remains_explicitly_retired(self) -> None:
        self.assertIn("human-KO", self.recipe)
        self.assertIn("do-not-run", self.recipe)
        self.assertIn("print-validated=false", self.recipe)

    def test_current_manifest_preserves_the_historical_preparer(self) -> None:
        self.assertEqual(self.manifest["version"], "0.1.74")
        self.assertIn('expectedVersion -ne "0.1.65"', self.preparer)

    def test_older_combined_gate_stays_distinct(self) -> None:
        self.assertIn('expectedVersion -ne "0.1.63"', self.historical)
        self.assertNotIn("p64_l09rv_preflight.py", self.historical)


if __name__ == "__main__":
    unittest.main()
