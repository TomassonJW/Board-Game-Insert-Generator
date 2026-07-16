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

    def test_exposes_four_primary_p44_m003_views_in_one_embedded_surface(self) -> None:
        expected = {"box", "contents", "manufacturing", "result"}
        self.assertEqual(self.dom.views, expected)
        self.assertEqual(self.dom.panels, expected)
        for marker in (">1. Boîte et plateaux<", ">2. Conteneurs et éléments<", ">3. Réglages<", ">4. Aperçu<"):
            self.assertIn(marker, self.markup)
        self.assertNotIn("previous-view", self.markup)
        self.assertNotIn("next-view", self.markup)
        self.assertIn('data-panel="box"', self.markup)
        self.assertIn('id="flats-section-title"', self.markup)
        self.assertIn('data-panel="contents"', self.markup)
        self.assertIn('id="groups-section-title"', self.markup)

    def test_interverts_xy_without_new_bridge_or_origin_mutation(self) -> None:
        for marker in (
            "swapBoxXY", "swapContentXY", "swapFlatXY", "swapGroupXY",
            "swapPair(group[key])", "data-action=\"swap-box-xy\"",
            "data-action=\"swap-content-xy\"", "data-action=\"swap-flat-xy\"",
            "data-action=\"swap-group-xy\"", "Orientation historique",
        ):
            self.assertIn(marker, self.markup)
        self.assertIn("['dimension_modes','target_outer_dimensions_mm','locked_outer_dimensions_mm','expansion_axes']", self.markup)
        self.assertNotIn('data-bridge="swap_', self.markup)
        self.assertIn("project.flat_items[index].origin_mm=values.x==null||values.y==null", self.markup)
        self.assertIn("rotation_deg_z", self.markup)

    def test_uses_utf8_french_copy_without_mojibake(self) -> None:
        for marker in ("Boîte", "éléments", "Réglages", "Aperçu", "Épaisseur", "Tolérance", "À plat"):
            self.assertIn(marker, self.markup)
        for forbidden in ("Ã", "Â", "�"):
            self.assertNotIn(forbidden, self.markup)

    def test_supports_dynamic_rows_progressive_disclosure_and_local_file_import(self) -> None:
        self.assertNotIn("expert-mode", self.dom.ids)
        for marker in ("import-file", "preset-import-file", "personal-presets", "lifecycle", "technical-drawer", "technical-detail"):
            self.assertIn(marker, self.dom.ids)
        for marker in ('data-density="compact"', 'data-density="detailed"', "local-details", "density-compact"):
            self.assertIn(marker, self.markup)
        for action in ("add-selected-content", "duplicate-content", "delete-content", "add-flat", "delete-flat", "add-group", "delete-group", "delete-complement"):
            self.assertIn(action, self.markup)
        self.assertNotIn('data-action="add-complement"', self.markup)
        self.assertNotIn('data-action="add-complement-preset"', self.markup)
        self.assertNotIn('id="complement-presets"', self.markup)

    def test_compacts_cards_as_dense_responsive_technical_rows(self) -> None:
        self.assertNotIn(".density-compact .row-details{display:none}", self.markup)
        for marker in (
            ".shell{max-width:1180px",
            ".app-status-line{display:flex",
            ".workspace-toolbar{display:flex",
            "main>.message.show{position:fixed",
            ".box-inline-grid{display:grid",
            ".asset-primary-grid{display:grid",
            ".flat-primary-grid{display:grid",
            ".container-primary-grid{display:grid",
            'class="card row-card technical-card content-card child-card"',
            'class="card row-card technical-card flat-card"',
            'class="card row-card technical-card group-card"',
            'class="card technical-card box-card"',
            'class="flat-secondary-grid"',
            'class="content-children"',
            "@media(max-width:1020px)",
            "@media(max-width:760px)",
            "@media(max-width:559px)",
        ):
            self.assertIn(marker, self.markup)
        self.assertEqual(self.markup.count('aria-label="Densité des listes"'), 1)
        self.assertNotIn("<h2>Démarrage rapide</h2>", self.markup)
        self.assertNotIn("<h4>Éléments contenus</h4>", self.markup)
        self.assertIn('.workspace-toolbar,.view[data-panel="box"] .section-command-bar{position:sticky', self.markup)
        self.assertIn("top:var(--bgig-sticky-controls-top,102px)", self.markup)
        self.assertIn("function syncStickyControlsOffset()", self.markup)
        self.assertIn("new ResizeObserver(syncStickyControlsOffset)", self.markup)
        self.assertIn("kind==='ok'?3000:6000", self.markup)
        self.assertIn("messageTimer=setTimeout", self.markup)
        self.assertIn("main>.message.show{position:fixed;top:8px", self.markup)
        self.assertIn('<div class="row-details">${targetControls}${customDetails}${clearanceControls}${children}</div>', self.markup)

    def test_collapses_unit_clearances_and_edits_one_xy_value_plus_z(self) -> None:
        for forbidden in (
            "<h4>Prise et tolérances</h4>",
            "<h4>Placement et ordre</h4>",
            "<h4>Solidité</h4>",
        ):
            self.assertNotIn(forbidden, self.markup)
        for marker in (
            "function sharedXYClearanceState",
            "function clearanceVectorFields",
            'class="clearance-details local-details"',
            "Tolérance cavité",
            "Jeu d’encastrement",
            "Jeu externe",
            "Entre deux conteneurs voisins, BGIG retient la plus grande demande des deux.",
            "Cette valeur ne se copie pas dans les autres cartes.",
            'data-key="xy"',
            "key==='xy'?{...current,x:value,y:value}",
            "axis==='xy'?{...current,x:value,y:value}",
            "Les valeurs X et Y diffèrent dans ce projet.",
            "<label>Pile<input",
            "<label>Paroi<input",
            "<label>Fond<input",
            "document.createElement('details')",
            "section.className='container-sizing local-details calculated-details'",
            "summary.textContent='Détails calculés'",
        ):
            self.assertIn(marker, self.markup)
        self.assertIn(
            "</div>${clearanceVectorFields(item,index,'content-clearance','Tolérance cavité',derived)}",
            self.markup,
        )
        self.assertIn(
            "</div>${clearanceVectorFields(item,index,'flat-clearance','Jeu d’encastrement',derived)}",
            self.markup,
        )
        self.assertNotIn("['x','y','z'].map(axis=>input('between_mm'", self.markup)

    def test_synchronizes_role_defaults_and_reads_latest_derived_values(self) -> None:
        for marker in (
            "GLOBAL_CLEARANCE_DEFAULT_BINDINGS",
            "function synchronizeGlobalClearanceDefault(path,value)",
            "function globalClearanceDefaultValue(path)",
            "Valeurs mixtes",
            "['container_between_mm','x']",
            "['container_between_mm','z']",
            "['container_box_per_side_xy_mm','x']",
            "['asset_cavity_mm','z']",
            "[axis]:'project_default'",
            "function derivedProjectItem(collection,idValue)",
            "derivedGroup(group.id)||group",
            "resolvedItem.clearance_effective_v1",
            "resolvedGroup.clearance_effective_v1",
            "#design-height[readonly]",
        ):
            self.assertIn(marker, self.markup)

    def test_creates_one_selected_preset_in_an_explicit_destination_without_new_bridge(self) -> None:
        for marker in (
            'id="creation-preset"', 'id="creation-destination"',
            'data-action="add-selected-content"', "Nouveau conteneur lié",
            "selectedCreationPreset", "selectedCreationDestination",
            "function selectedCreationTemplate()", "function addContent(groupId=null)",
            "addContent(button.dataset.groupId)",
            "Preset sélectionné", "Supprimer ce preset",
        ):
            self.assertIn(marker, self.markup)
        self.assertIn("add-selected-content", self.dom.actions)
        self.assertNotIn("add-content-preset", self.dom.actions)
        self.assertNotIn("add-personal-preset", self.dom.actions)
        self.assertNotIn('data-action="add-complement"', self.markup)
        self.assertNotIn('data-action="add-complement-preset"', self.markup)
        self.assertNotIn('data-bridge="add_', self.markup)

    def test_makes_presets_and_historical_complement_compatibility_obvious(self) -> None:
        for marker in (
            "workspace-toolbar",
            "Mes presets",
            "Compléments historiques",
            "historic-complements",
            "renderComplements",
            "group-unified-mode",
            "Personnalisé",
            "group-mode",
            "group-target",
            "Auto",
            "Cible",
            "Fixe",
            "creation_presets",
            "Résolu",
            "Format",
            "Orientation",
        ):
            self.assertIn(marker, self.markup)

    def test_projects_contents_inside_their_parent_container_without_schema_or_bridge_change(self) -> None:
        for marker in (
            "renderContentCard", "content-children", "child-card",
            "data-record-kind=\"content\"", "data-record-kind=\"group\"",
            'data-row="content-move"', "add-content-to-group",
            "Déplacer vers…", "setUnifiedGroupMode", "applyGroupModeToAll",
            "group-unified-mode", "Compatibilité historique par axe",
            "Personnalisé", "container-batch-controls",
        ):
            self.assertIn(marker, self.markup)
        persistent_target = 'data-row="content" data-index="' + chr(36) + '{index}" data-key="container_group_id"'
        self.assertNotIn(persistent_target, self.markup)
        self.assertNotIn('data-bridge="move_', self.markup)
        self.assertIn("project.contents[index].container_group_id=input.value", self.markup)
        self.assertIn("group.dimension_modes={x:mode,y:mode,z:mode}", self.markup)
        self.assertIn("data-record-kind][data-record-id]", self.markup)

    def test_exposes_non_mutating_container_estimation_without_a_new_bridge_action(self) -> None:
        for marker in (
            "estimate-groups-action",
            ">Réestimer</button>",
            "container_sizing",
            "Taille calculée",
            "Avant modification - A reestimer",
            "Estimation deja en cours.",
            "calculated?'Calculée '+dimText(calculated)+' | ':'')+status",
            "sendProject('solve_project')",
        ):
            self.assertIn(marker, self.markup)
        self.assertIn("estimate-groups", self.dom.actions)
        self.assertNotIn("estimate_project", self.dom.bridge_actions)
        self.assertIn("does_not_materialize_fusion", (ROOT / "src" / "board_game_insert_generator" / "container_sizing_view.py").read_text(encoding="utf-8"))

    def test_translates_preview_explanations_without_solver_codes(self) -> None:
        for marker in (
            "view.presentation", "preview-explanations", "Indice de comparaison",
            "Ordre de retrait", "previewRemoval", "Exporter les imprimables",
        ):
            self.assertIn(marker, self.markup)
        self.assertNotIn("supported_by_requested_bodies", self.markup)
        self.assertNotIn("data-bridge=\"solve_project\"", self.markup[self.markup.index("function renderResult"):self.markup.index("function renderPersistentActions")])
    def test_exposes_the_p61_lifecycle_and_keeps_healthy_inspection_out_of_global_messages(self) -> None:
        for marker in ("renderLifecycle", "scheduleDerived", "solvedStale", "Ancienne proposition", "technical_detail"):
            self.assertIn(marker, self.markup)
        self.assertIn("sendFusion('inspect',true)", self.markup)
        self.assertNotIn("Mode avance", self.markup)
        for malformed in ("Centr?", "Apr?s", "retrait n?", " ? encastrement"):
            self.assertNotIn(malformed, self.markup)

    def test_routes_validation_persistence_and_native_documents_to_the_versioned_bridge(self) -> None:
        self.assertEqual(self.dom.bridge_actions, {"validate_project", "save_document", "export_project", "export_personal_presets", "solve_project", "materialize_project"})
        for marker in ("bgig.palette.request.v1", "bgig.palette.response.v1", "bgig_palette_project", "bgig_palette_document", "DOCUMENT_ACTION", "sendDocument", "8000"):
            self.assertIn(marker, self.markup)

    def test_exposes_clear_design_settings_and_one_persistent_materialize_action(self) -> None:
        for marker in (
            "Épaisseur minimale des parois", "Épaisseur minimale du fond",
            "Jeu entre conteneurs", "Jeu conteneur-boîte",
            "Jeu entre conteneurs en hauteur", "Jeu élément-cavité",
            "Priorité de la proposition", "Jeu sous le couvercle",
            'data-path="layout.container_box_xy_clearance_mm"',
            'data-path="layout.container_z_clearance_mm"',
        ):
            self.assertIn(marker, self.markup)
        self.assertNotIn("Jeux et preferences", self.markup)
        self.assertNotIn('data-path="box.usable_height_mm"', self.markup)
        self.assertEqual(self.markup.count('data-bridge="materialize_project"'), 1)
        self.assertIn('id="materialize-action"', self.markup)
        self.assertIn("renderPersistentActions", self.markup)
        self.assertLess(
            self.markup.index('data-bridge="solve_project">Recalculer</button><button id="materialize-action"'),
            self.markup.index('<div class="action-zone center">'),
        )
    def test_preserves_interaction_state_with_stable_identifiers_and_rejects_stale_derivations(self) -> None:
        for marker in (
            "sourceRevision", "stampUiIdentifiers", "captureUiState", "restoreUiState",
            "data-object-id", "uiField", "uiDetails", "selectionStart",
            "scrollTop", "requestAnimationFrame", "data-ui-active-card",
        ):
            self.assertIn(marker, self.markup)
        self.assertIn("item?.id", self.markup)
        self.assertIn("pendingRequest?.derived&&pendingRequest.sourceRevision!==sourceRevision", self.markup)
        self.assertIn("derived:quiet||['validate_project','solve_project'].includes(action),sourceRevision", self.markup)
        self.assertIn("renderAll({preserve:!(['load_project','import_project','new_project','open_project_file','open_recent_project'].includes(action)||bootstrap)})", self.markup)
        self.assertIn("if(['load_project','import_project','new_project','open_project_file','open_recent_project'].includes(action)||bootstrap)sourceRevision+=1", self.markup)
        self.assertIn("if(action==='autosave_project')state('Modifications non sauvegardées - récupération enregistrée','ok')", self.markup)
        self.assertNotIn("renderPresets();renderContents();renderFlats();renderGroups();renderContainerSizing();renderLifecycle();return", self.markup)

    def test_supports_p44_m006_named_documents_recovery_and_discrete_diagnostics(self) -> None:
        for marker in (
            'data-action="new-project"', 'data-action="open-project"',
            'data-action="save-project-as"', 'id="save-document-action"',
            'id="document-status"', 'id="document-description"',
            'id="recent-documents"', 'id="design-height"',
            'id="diagnostic-tools"', 'data-confirm="Effacer uniquement les corps BGIG',
            "scheduleRecovery", "autosave_project", "open_recent_project",
            "save_project_as", "save_document", "new_project",
        ):
            self.assertIn(marker, self.markup)
        self.assertIn("Hauteur de conception", self.markup)
        self.assertIn("Diagnostic et scène Fusion", self.markup)
        self.assertNotIn('data-path="box.usable_height_mm"', self.markup)
        self.assertNotIn("<summary>Jeux et preferences</summary>", self.markup)

    def test_p44_m006_h01_guards_fusion_state_and_unsaved_document_transitions(self) -> None:
        for marker in (
            "function hasUnsavedEdition()",
            "documentInfo?.recovery_available",
            "function confirmDiscardUnsavedEdition(actionLabel)",
            "confirmDiscardUnsavedEdition('Créer un nouveau projet')",
            "confirmDiscardUnsavedEdition('Ouvrir un autre projet')",
            "const sceneSummary=$('#scene-summary'),sceneStatus=$('#scene-status');",
            "if(sceneSummary)sceneSummary.textContent=detail||'Inspection disponible.'",
            "if(sceneStatus)sceneStatus.textContent=payload.scene_status||'Scène inspectée'",
            "state('Réponse Fusion illisible','error')",
        ):
            self.assertIn(marker, self.markup)
        self.assertNotIn("$('#scene-status').textContent=", self.markup)

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
        for marker in ("$paletteMarkers", "workspace-toolbar", "container-primary-grid", "historic-complements", "[char]0x00EE", "[char]0x00E9", "[char]0x00E7"):
            self.assertIn(marker, helpers)
        self.assertNotIn('\"1. Boite\", \"6. Apercu\"', helpers)
        self.assertIn("Aucun navigateur", smoke)
        self.assertIn("P56 Fusion OK", smoke)
        p44_smoke = (ROOT / "scripts" / "fusion" / "prepare_p44_m005_creation_presets_test.ps1").read_text(encoding="utf-8")
        for marker in ("0.1.28", "creation-preset", "creation-destination", "Nouveau conteneur li", "P44-M005 Fusion OK"):
            self.assertIn(marker, p44_smoke)


    def test_prepares_the_p44_m006_fusion_document_cycle_gate(self) -> None:
        script = (ROOT / "scripts" / "fusion" / "prepare_p44_m006_document_cycle_test.ps1").read_text(encoding="utf-8")
        for marker in (
            "0.1.30", "document-status", "save-document-action",
            "open-project", "save-project-as", "design-height",
            "diagnostic-tools", "createFileDialog", "P44-M006 Fusion OK",
        ):
            self.assertIn(marker, script)


if __name__ == "__main__":
    unittest.main()
