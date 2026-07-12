from pathlib import Path
import unittest


class FrontendStudioContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        root = Path(__file__).resolve().parents[1]
        cls.source = (root / "frontend" / "src" / "App.tsx").read_text(encoding="utf-8")
        cls.types = (root / "frontend" / "src" / "project_v1.ts").read_text(encoding="utf-8")
        cls.validation = (root / "frontend" / "src" / "project_v1_validation.ts").read_text(encoding="utf-8")

    def test_primary_journey_is_user_first_and_not_a_technical_wizard(self) -> None:
        for label in (
            "Ma boîte",
            "Ce que tu veux ranger",
            "Plateaux et livrets",
            "Les bacs demandés",
            "Compléter l’espace",
            "Réglages de fabrication",
            "Construire mon insert",
        ):
            self.assertIn(label, self.source)
        self.assertNotIn("AppearanceEditor", self.source)
        self.assertNotIn("MechanismEditor", self.source)
        self.assertNotIn("studioSteps", self.source)

    def test_content_table_exposes_shape_quantity_and_target_container(self) -> None:
        for marker in ("shape_kind", "quantity", "container_group_id", "+ Créer un nouveau bac"):
            self.assertIn(marker, self.source)
        for shape in ("round", "square", "rectangle", "cards", "cube", "meeple", "custom"):
            self.assertIn(f"'{shape}'", self.types)

    def test_v1_import_and_save_are_available_without_legacy_editor_concepts(self) -> None:
        self.assertIn("loadProjectV1Starter", self.source)
        self.assertIn("normalizeProjectV1", self.source)
        self.assertIn("Importer un projet", self.source)
        self.assertIn("Sauvegarder", self.source)
        for legacy_concept in ("CandidateEditor", "ReservationEditor", "allowed_layers", "manual_modules"):
            self.assertNotIn(legacy_concept, self.source)

    def test_client_validation_covers_groups_flats_and_fill_elements(self) -> None:
        for marker in ("validateProjectV1", "container_groups", "flat_items", "fill_elements", "layout_clearance_mm"):
            self.assertIn(marker, self.validation)


if __name__ == "__main__":
    unittest.main()
