from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]

class FusionPaletteResultTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.markup = (ROOT / "fusion_addin" / "BoardGameInsertGenerator" / "palette.html").read_text(encoding="utf-8")
        cls.bridge = (ROOT / "fusion_addin" / "BoardGameInsertGenerator" / "palette_project.py").read_text(encoding="utf-8")

    def test_renders_both_projections_from_the_python_result_view(self) -> None:
        for marker in ("response.result_view", "view.top_view", "view.section_xz", "svgPlan(view", "viewBox=", "Vue dessus", "Coupe X / Z"):
            self.assertIn(marker, self.markup)

    def test_result_exposes_user_facing_evidence_without_engine_codes(self) -> None:
        for marker in ("final_body_count", "stage_count", "automatic_body_count", "minimum_outer_envelope_mm", "final_outer_dimensions_mm", "surplus_distribution_mm", "cavity_count", "view.presentation", "preview-explanations", "stageExplanation.coverage_label", "flatExplanation.coverage_label", "Ordre de retrait"):
            self.assertIn(marker, self.markup)
        for marker in ("Indice de comparaison", "Appui des etages", "Comment lire cet indice ?", "presentation.score"):
            self.assertIn(marker, self.markup)
        self.assertNotIn("Les deux vues ci-dessous utilisent exclusivement les placements P57", self.markup)
        self.assertNotIn("Plan ${esc(view.source_plan_digest", self.markup)
        self.assertNotIn("supported_by_requested_bodies", self.markup)

    def test_preview_actions_are_clear_without_duplicating_the_persistent_calculation_actions(self) -> None:
        start = self.markup.index("function renderResult")
        result_block = self.markup[start:self.markup.index("function renderPersistentActions", start)]

        self.assertIn('data-fusion="export"', result_block)
        self.assertIn("Exporter les imprimables", result_block)
        self.assertNotIn('data-bridge="solve_project"', result_block)
        self.assertNotIn('data-bridge="materialize_project"', result_block)
    def test_impossible_and_obsolete_states_never_show_a_fake_solution(self) -> None:
        self.assertIn("Aucune fausse solution n est affichee", self.markup)
        self.assertIn("Ancienne proposition", self.markup)
        self.assertIn("solvedStale=Boolean(lastSolved)", self.markup)
        self.assertIn("lastSolved=payload", self.markup)
        self.assertIn("if(!complete&&!partial)", self.markup)
        self.assertIn("proposal_with_residuals", self.markup)
        self.assertIn("materializable=complete", self.markup)
        self.assertIn('data-bridge="materialize_project"', self.markup)
        self.assertIn('data-bridge="regenerate_project"', self.markup)
        self.assertIn("Une proposition complète et à jour est requise", self.markup)
        self.assertIn("Volume residuel a decider", self.markup)

    def test_p59_exposes_owned_scene_actions_without_raw_cad_codes(self) -> None:
        for marker in (
            "response.cad_build", "materializedDigest", "component_count",
            'data-fusion="inspect"', 'data-fusion="clear"', 'data-fusion="export"',
            "scene_status==='synchronized'", "technicalDetail(payload.scene_result",
        ):
            self.assertIn(marker, self.markup)
        self.assertNotIn("cad_ir_digest", self.markup)
        self.assertIn("build_partition_cad", self.bridge)
        self.assertIn('"cad_build": deepcopy(cad_build)', self.bridge)

    def test_geometry_projection_is_owned_by_python_not_recomputed_by_javascript(self) -> None:
        self.assertIn("build_partition_result_view", self.bridge)
        self.assertIn('"result_view": deepcopy(result_view)', self.bridge)
        for forbidden in ("deriveCavity", "solvePartition", "packBodies", "localhost", "fetch("):
            self.assertNotIn(forbidden, self.markup)

if __name__ == "__main__":
    unittest.main()
