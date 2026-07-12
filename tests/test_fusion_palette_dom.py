from html.parser import HTMLParser
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PALETTE = ROOT / "fusion_addin" / "BoardGameInsertGenerator" / "palette.html"


class PaletteDomParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.panels: set[str] = set()
        self.views: set[str] = set()
        self.ids: set[str] = set()
        self.actions: set[str] = set()
        self.bridge_actions: set[str] = set()

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if values.get("data-panel"):
            self.panels.add(str(values["data-panel"]))
        if values.get("data-view"):
            self.views.add(str(values["data-view"]))
        if values.get("id"):
            self.ids.add(str(values["id"]))
        if values.get("data-action"):
            self.actions.add(str(values["data-action"]))
        if values.get("data-bridge"):
            self.bridge_actions.add(str(values["data-bridge"]))


class FusionPaletteDomTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.markup = PALETTE.read_text(encoding="utf-8")
        cls.dom = PaletteDomParser()
        cls.dom.feed(cls.markup)

    def test_exposes_the_six_p56_views_in_one_embedded_surface(self) -> None:
        expected = {"box", "contents", "flats", "groups", "manufacturing", "result"}
        self.assertEqual(self.dom.views, expected)
        self.assertEqual(self.dom.panels, expected)

    def test_supports_dynamic_rows_simple_advanced_and_local_file_import(self) -> None:
        self.assertIn("expert-mode", self.dom.ids)
        self.assertIn("import-file", self.dom.ids)
        for action in ("add-content", "duplicate-content", "delete-content", "add-flat", "delete-flat", "add-group", "delete-group", "add-complement", "delete-complement"):
            self.assertIn(action, self.markup)

    def test_routes_validation_and_persistence_to_the_versioned_python_bridge(self) -> None:
        self.assertEqual(self.dom.bridge_actions, {"validate_project", "save_project", "export_project", "solve_project"})
        self.assertIn("bgig.palette.request.v1", self.markup)
        self.assertIn("bgig.palette.response.v1", self.markup)
        self.assertIn("bgig_palette_project", self.markup)
        self.assertIn("8000", self.markup)

    def test_has_no_external_web_runtime_or_business_solver_in_javascript(self) -> None:
        for forbidden in ("localhost", "fetch(", "XMLHttpRequest", "npm ", "Vite", "solvePartition", "derive_expandable_envelope_contract"):
            self.assertNotIn(forbidden, self.markup)
        bridge = (ROOT / "fusion_addin" / "BoardGameInsertGenerator" / "palette_project.py").read_text(encoding="utf-8")
        self.assertNotIn("import adsk", bridge)
        self.assertIn("derive_expandable_envelope_contract", bridge)
        self.assertIn("derive_flat_stack_reservation", bridge)

    def test_installer_bundles_the_pure_engine_and_smoke_is_fusion_only(self) -> None:
        helpers = (ROOT / "scripts" / "fusion" / "_fusion_helpers.ps1").read_text(encoding="utf-8")
        smoke = (ROOT / "scripts" / "fusion" / "prepare_p56_palette_test.ps1").read_text(encoding="utf-8")
        self.assertIn("lib\\board_game_insert_generator", helpers)
        self.assertIn("Assert-BgigPaletteProjectRuntime", helpers)
        self.assertIn("Aucun navigateur", smoke)
        self.assertIn("P56 Fusion OK", smoke)


if __name__ == "__main__":
    unittest.main()
