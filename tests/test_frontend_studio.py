from pathlib import Path
import unittest


class FrontendStudioContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.source = (Path(__file__).resolve().parents[1] / "frontend" / "src" / "App.tsx").read_text(encoding="utf-8")

    def test_primary_journey_has_five_progressive_steps(self) -> None:
        for step_id in ("box", "contents", "organisation", "proposals", "prepare"):
            self.assertIn(f"id: '{step_id}'", self.source)

    def test_live_box_preview_does_not_pretend_to_be_printable(self) -> None:
        self.assertIn("Vue vivante", self.source)
        self.assertIn("Aperçu vivant", self.source)
        self.assertIn("Elle ne représente pas encore des bacs imprimables.", self.source)

    def test_manufacturing_statuses_are_explicit(self) -> None:
        for label in ("À explorer", "À vérifier dans Fusion", "À imprimer et mesurer"):
            self.assertIn(label, self.source)

    def test_p33_appearance_controls_are_live_but_not_presented_as_printed_geometry(self) -> None:
        for label in (
            "Finition vivante",
            "Aperçu uniquement",
            "Rayon d aperçu",
            "Biseau d aperçu",
            "Prise visuelle",
            "Le plan, les tolérances, les murs et le fond ne bougent pas.",
        ):
            self.assertIn(label, self.source)
        self.assertIn("appearance-${draft.appearance.visual.theme}", self.source)
        self.assertIn("PreviewModule", self.source)

    def test_technical_export_stays_in_expert_mode_and_describes_p31_honestly(self) -> None:
        self.assertIn("Mode expert : télécharger le dossier de préparation", self.source)
        self.assertIn("bacs ouverts à vérifier dans Fusion", self.source)


if __name__ == "__main__":
    unittest.main()
