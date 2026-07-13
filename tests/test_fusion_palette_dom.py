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

    def test_supports_dynamic_rows_progressive_disclosure_and_local_file_import(self) -> None:
        self.assertNotIn("expert-mode", self.dom.ids)
        for marker in ("import-file", "preset-import-file", "personal-presets", "lifecycle", "technical-drawer", "technical-detail"):
            self.assertIn(marker, self.dom.ids)
        for marker in ('data-density="compact"', 'data-density="detailed"', "local-details", "density-compact"):
            self.assertIn(marker, self.markup)
        for action in ("add-content", "add-content-preset", "duplicate-content", "delete-content", "add-flat", "delete-flat", "add-group", "delete-group", "add-complement", "add-complement-preset", "delete-complement"):
            self.assertIn(action, self.markup)

    def test_makes_presets_explicit_bodies_and_container_dimensions_obvious(self) -> None:
        for marker in (
            "Demarrage rapide",
            "bloc plein sert de cale ou de support",
            "Corps explicites",
            "Dimensionnement par axe",
            "group-mode", "group-target", "Auto", "Cible", "Fixe",
            "creation_presets", "Dimensions resolues", "Format de cartes", "Debout sur grand cote",
        ):
            self.assertIn(marker, self.markup)

    def test_exposes_non_mutating_container_estimation_without_a_new_bridge_action(self) -> None:
        for marker in (
            "estimate-groups-action",
            "Estimer les tailles",
            "Reestimer les tailles",
            "container_sizing",
            "Taille calculee",
            "Avant modification - A reestimer",
            "Estimation deja en cours.",
            "calculated?'Calculee '+dimText(calculated)+' | ':'')+status",
            "sendProject('solve_project')",
        ):
            self.assertIn(marker, self.markup)
        self.assertIn("estimate-groups", self.dom.actions)
        self.assertNotIn("estimate_project", self.dom.bridge_actions)
        self.assertIn("does_not_materialize_fusion", (ROOT / "src" / "board_game_insert_generator" / "container_sizing_view.py").read_text(encoding="utf-8"))
    def test_exposes_the_p61_lifecycle_and_keeps_healthy_inspection_out_of_global_messages(self) -> None:
        for marker in ("renderLifecycle", "scheduleDerived", "solvedStale", "Ancienne proposition", "technical_detail"):
            self.assertIn(marker, self.markup)
        self.assertIn("sendFusion('inspect',true)", self.markup)
        self.assertNotIn("Mode avance", self.markup)
        for malformed in ("Centr?", "Apr?s", "retrait n?", " ? encastrement"):
            self.assertNotIn(malformed, self.markup)

    def test_routes_validation_and_persistence_to_the_versioned_python_bridge(self) -> None:
        self.assertEqual(self.dom.bridge_actions, {"validate_project", "save_project", "export_project", "export_personal_presets", "solve_project", "materialize_project"})
        self.assertIn("bgig.palette.request.v1", self.markup)
        self.assertIn("bgig.palette.response.v1", self.markup)
        self.assertIn("bgig_palette_project", self.markup)
        self.assertIn("8000", self.markup)

    def test_exposes_xy_and_z_clearances_and_one_persistent_materialize_action(self) -> None:
        self.assertIn("Jeu entre conteneurs X-Y (total)", self.markup)
        self.assertIn("Jeu bac / boite X-Y (par cote)", self.markup)
        self.assertIn('data-path="layout.container_box_xy_clearance_mm"', self.markup)
        self.assertIn("Jeu entre conteneurs Z (total)", self.markup)
        self.assertIn("Jeu bac / boite Z (haut)", self.markup)
        self.assertEqual(self.markup.count("Jeu entre conteneurs X-Y (total)"), 1)
        self.assertEqual(self.markup.count("Jeu bac / boite X-Y (par cote)"), 1)
        self.assertEqual(self.markup.count("Jeu entre conteneurs Z (total)"), 1)
        self.assertEqual(self.markup.count("Jeu bac / boite Z (haut)"), 1)
        self.assertIn('data-path="layout.container_z_clearance_mm"', self.markup)
        self.assertEqual(self.markup.count('data-bridge="materialize_project"'), 1)
        self.assertIn('id="materialize-action"', self.markup)
        self.assertIn("renderPersistentActions", self.markup)
        self.assertLess(
            self.markup.index('data-bridge="solve_project">Recalculer</button><button id="materialize-action"'),
            self.markup.index('<div class="action-zone center">'),
        )
    def test_has_no_external_web_runtime_or_business_solver_in_javascript(self) -> None:
        for forbidden in ("localhost", "fetch(", "XMLHttpRequest", "npm ", "Vite", "solvePartition", "derive_expandable_envelope_contract"):
            self.assertNotIn(forbidden, self.markup)
        bridge = (ROOT / "fusion_addin" / "BoardGameInsertGenerator" / "palette_project.py").read_text(encoding="utf-8")
        self.assertNotIn("import adsk", bridge)
        self.assertIn("derive_expandable_envelope_contract", bridge)
        self.assertIn("derive_top_inset_reservations", bridge)
        self.assertIn("compatibility_flat_stack_payload", bridge)

    def test_installer_bundles_the_pure_engine_and_smoke_is_fusion_only(self) -> None:
        helpers = (ROOT / "scripts" / "fusion" / "_fusion_helpers.ps1").read_text(encoding="utf-8")
        smoke = (ROOT / "scripts" / "fusion" / "prepare_p56_palette_test.ps1").read_text(encoding="utf-8")
        self.assertIn("lib\\board_game_insert_generator", helpers)
        self.assertIn("top_inset_reservation.py", helpers)
        self.assertIn("volumetric_stage_solver.py", helpers)
        self.assertIn("Assert-BgigPaletteProjectRuntime", helpers)
        self.assertIn("Aucun navigateur", smoke)
        self.assertIn("P56 Fusion OK", smoke)


if __name__ == "__main__":
    unittest.main()
