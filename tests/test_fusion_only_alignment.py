from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class FusionOnlyAlignmentTests(unittest.TestCase):
    def read(self, relative: str) -> str:
        return (ROOT / relative).read_text(encoding="utf-8")

    def test_authoritative_contracts_make_fusion_the_only_product_surface(self) -> None:
        north = self.read("docs/NORTH_STAR.md")
        vision = self.read("docs/CANONICAL_PRODUCT_VISION.md")
        acceptance = self.read("docs/MVP_V01_ACCEPTANCE_CONTRACT.md")
        contract = self.read("docs/FUSION_ONLY_MVP_CONTRACT.md")

        for content in (north, vision, acceptance, contract):
            self.assertIn("Fusion", content)
        self.assertIn("add-in autonome", north)
        self.assertIn("palette HTML embarquee", vision)
        self.assertIn("sans navigateur externe", contract)
        self.assertNotIn("Le Studio est l'interface principale", vision)
        self.assertNotIn("conduit clairement au Studio", acceptance)

    def test_old_web_primary_decisions_are_superseded(self) -> None:
        for relative in (
            "docs/DECISIONS/ADR-0040-local-composer-loopback-adapter.md",
            "docs/DECISIONS/ADR-0041-local-composer-selection-cad-ir-bridge.md",
            "docs/DECISIONS/ADR-0042-studio-primary-fusion-palette-secondary.md",
        ):
            self.assertIn("Supersede", self.read(relative))
        adr = self.read("docs/DECISIONS/ADR-0055-fusion-only-mvp-product-surface.md")
        self.assertIn("Accepte", adr)
        self.assertIn("Aucun navigateur externe", adr)

    def test_active_p56_is_the_embedded_fusion_editor(self) -> None:
        backlog = self.read("docs/BACKLOG.md")
        start = backlog.index("### P56 - Editeur complet embarque dans Fusion")
        end = backlog.index("### P57 -", start)
        p56 = backlog[start:end]

        self.assertIn("palette P32", p56)
        self.assertIn("`implemented`", p56)
        self.assertIn("`fusion-validated: false`", p56)
        self.assertIn("aucune logique metier en JavaScript", p56)
        self.assertNotIn("interface responsive", p56)

    def test_current_palette_no_longer_redirects_to_a_web_studio(self) -> None:
        markup = self.read("fusion_addin/BoardGameInsertGenerator/palette.html")
        bridge = self.read("fusion_addin/BoardGameInsertGenerator/BoardGameInsertGenerator.py")

        self.assertNotIn("Studio", markup)
        self.assertNotIn("Studio", bridge)
        self.assertNotIn("localhost", markup)
        self.assertIn('class="eyebrow">BGIG</span>', markup)
        self.assertIn("bgig.palette.request.v1", markup)

    def test_next_action_records_p44_m007_without_promoting_print(self) -> None:
        actions = self.read("docs/NEXT_ACTIONS.md")
        decision = self.read("docs/DECISIONS/ADR-0064-global-container-clearances.md")
        contract = self.read("docs/P44_M007_ADAPTIVE_CALCULATION_CONTRACT.md")

        self.assertIn("mvp-accepted", actions)
        self.assertIn("P44-M009H05", actions)
        self.assertIn("0.1.36", actions)
        self.assertIn("P44-M007H02V", actions)
        self.assertIn("0.1.37", actions)
        self.assertIn("human-fusion-check-required", actions)
        self.assertIn("P44-M007H02 Fusion OK 0.1.39 - commit <sha>", actions)
        self.assertIn("350 ms", contract)
        self.assertIn("1 500 ms", contract)
        self.assertIn("annulation logique", contract)
        self.assertIn("exclusivement globaux", decision)
        self.assertIn("roundtrippables", decision)
        self.assertIn("print-validated: false", actions)
        self.assertNotIn("ready-for-explicit-go", actions)
        self.assertNotIn("data-bridge=\"validate_project\"", self.read("fusion_addin/BoardGameInsertGenerator/palette.html"))
    def test_french_ui_copy_requirement_is_bounded_and_testable(self) -> None:
        contract = self.read("docs/P44_FRENCH_UI_ORTHOTYPOGRAPHY_CONTRACT.md")
        backlog = self.read("docs/BACKLOG.md")

        for marker in (
            "Éléments du jeu",
            "Réglages",
            "Aperçu",
            "Épaisseur",
            "Quantité",
            "À plat",
            "Boîte",
            '<meta charset="utf-8">',
            "Éléments d’été — boîte à dés",
        ):
            self.assertIn(marker, contract)
        self.assertIn("P44-M003", contract)
        self.assertIn("P44-M006", contract)
        self.assertIn("identifiants stables", contract)
        self.assertIn("UTF-8 sans BOM", contract)
        self.assertIn("roundtrip d’un nom accentué", backlog)

if __name__ == "__main__":
    unittest.main()
