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
        self.assertIn("BGIG dans Fusion 360", markup)
        self.assertIn("bgig.palette.request.v1", markup)

    def test_next_action_advances_the_accepted_post_mvp_fusion_path(self) -> None:
        actions = self.read("docs/NEXT_ACTIONS.md")
        framing = self.read("docs/P44_M002_COMPACT_ACCESSIBLE_CARDS_CONTRACT.md")

        self.assertIn("P44-M002", actions)
        self.assertIn("implemented", actions)
        self.assertIn("P44-M003", actions)
        self.assertIn("mvp-accepted", actions)
        self.assertIn("Statut : `ready-after-p44-m002-integration`, `no-business-change`,", actions)
        self.assertIn("Package cible : palette Fusion `0.1.22`", framing)
        self.assertIn("mode Compact", framing)
        self.assertIn("Solidite", framing)
        self.assertIn("Details calcules", framing)
        self.assertIn("Aucun calcul metier n est ajoute au JavaScript", framing)
        self.assertIn("solveur, score, jeu, tolerance", framing)
        self.assertNotIn("codex/p56-premium-editor", actions)
        self.assertNotIn("inspection visuelle runtime du frontend reel", actions)


if __name__ == "__main__":
    unittest.main()
