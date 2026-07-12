from __future__ import annotations

from html.parser import HTMLParser
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SPEC_PATH = ROOT / "docs" / "P54_PREMIUM_EDITOR_UX.md"
PROTOTYPE_PATH = ROOT / "docs" / "prototypes" / "p54_premium_editor_wireframe.html"


class _PrototypeParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.ids: set[str] = set()
        self.lang = ""

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if tag == "html":
            self.lang = values.get("lang") or ""
        element_id = values.get("id")
        if element_id:
            self.ids.add(element_id)


class P54PremiumEditorReferenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.spec = SPEC_PATH.read_text(encoding="utf-8")
        cls.prototype = PROTOTYPE_PATH.read_text(encoding="utf-8")
        cls.parser = _PrototypeParser()
        cls.parser.feed(cls.prototype)

    def test_reference_covers_the_complete_v01_editor(self) -> None:
        for marker in (
            "Ecran Boite",
            "Ecran Assets",
            "Ecran Plateaux et livrets",
            "Ecran Bacs",
            "Ecran Fabrication",
            "Ecran Resultat",
            "Complements explicites",
            "Etats obligatoires",
            "Accessibilite",
        ):
            self.assertIn(marker, self.spec)

    def test_reference_preserves_fixed_cavities_and_forbids_automatic_bodies(self) -> None:
        self.assertIn("Les cavites gardent leurs mesures", self.spec)
        self.assertIn("BGIG n en ajoute jamais", self.spec)
        self.assertIn("0 corps automatique", self.spec)
        self.assertIn("Aucun corps automatique ne sera cree", self.prototype)

    def test_prototype_exposes_all_primary_sections_and_responsive_rules(self) -> None:
        self.assertEqual(self.parser.lang, "fr")
        self.assertEqual(
            self.parser.ids,
            {"box", "assets", "flats", "containers", "settings"},
        )
        self.assertIn("@media (max-width: 1180px)", self.prototype)
        self.assertIn("@media (max-width: 760px)", self.prototype)
        self.assertIn("min-height: 40px", self.prototype)

    def test_reference_does_not_contain_known_mojibake_sequences(self) -> None:
        for marker in ("Ã", "Â", "â€"):
            self.assertNotIn(marker, self.spec)
            self.assertNotIn(marker, self.prototype)


if __name__ == "__main__":
    unittest.main()
