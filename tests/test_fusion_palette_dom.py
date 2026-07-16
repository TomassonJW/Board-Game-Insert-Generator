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
        self.assertIn("local-details", self.markup)
        for marker in ('data-density="compact"', 'data-density="detailed"', "density-compact", "setDensity(", "bgig-list-density", "compact-summary"):
            self.assertNotIn(marker, self.markup)
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
            ".container-primary-grid{display:flex",
            'class="card row-card technical-card content-card child-card"',
            'class="card row-card technical-card flat-card"',
            "group-card ${collapsed?'is-collapsed':''}",
            'class="card technical-card box-card"',
            'class="flat-secondary-grid"',
            'class="content-children"',
            "@media(max-width:1020px)",
            "@media(max-width:760px)",
            "@media(max-width:559px)",
        ):
            self.assertIn(marker, self.markup)
        self.assertNotIn('aria-label="Densité des listes"', self.markup)
        self.assertNotIn(">Compact</button>", self.markup)
        self.assertNotIn(">Détaillé</button>", self.markup)
        self.assertNotIn("<h2>Démarrage rapide</h2>", self.markup)
        self.assertNotIn("<h4>Éléments contenus</h4>", self.markup)
        self.assertIn('.workspace-toolbar,.view[data-panel="box"] .section-command-bar{position:sticky', self.markup)
        self.assertIn("top:var(--bgig-sticky-controls-top,102px)", self.markup)
        self.assertIn("function syncStickyControlsOffset()", self.markup)
        self.assertIn("new ResizeObserver(syncStickyControlsOffset)", self.markup)
        self.assertIn("kind==='ok'?3000:6000", self.markup)
        self.assertIn("messageTimer=setTimeout", self.markup)
        self.assertIn("main>.message.show{position:fixed;top:8px", self.markup)
        self.assertIn('<div class="row-details">${customDetails}${children}</div>', self.markup)
        for marker in (
            ".container-summary{display:flex",
            ".container-controls{display:flex",
            'class="container-identity"',
            'class="group-mode-control"',
            'class="group-target-field"',
            "const targetControls=sizedMode?",
            '''targetField('x')}<button type="button" class="xy-swap-button"''',
            "${targetField('y')}${targetField('z')}",
            "Épaisseur paroi", "Épaisseur fond",
        ):
            self.assertIn(marker, self.markup)
        self.assertNotIn("container-target-grid", self.markup)

    def test_collapses_unit_clearances_and_edits_one_xy_value_plus_z(self) -> None:
        for forbidden in (
            "<h4>Prise et tolérances</h4>",
            "<h4>Placement et ordre</h4>",
            "<h4>Solidité</h4>",
            "Jeu externe",
            "Voisinage total",
            "function groupClearanceFields",
            'data-row="group-clearance"',
            "resolvedGroup.clearance_effective_v1",
        ):
            self.assertNotIn(forbidden, self.markup)
        for marker in (
            "function sharedXYClearanceState",
            "function clearanceVectorFields",
            'class="clearance-details local-details"',
            "Tolérance cavité",
            "Jeu d’encastrement",
            'data-key="xy"',
            "key==='xy'?{...current,x:value,y:value}",
            "Les valeurs X et Y diffèrent dans ce projet.",
            "<label>Pile<input",
            'Épaisseur paroi<input',
            'Épaisseur fond<input',
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

    def test_synchronizes_role_defaults_and_reads_latest_derived_values(self) -> None:
        for marker in (
            "GLOBAL_CLEARANCE_BINDINGS",
            "function setGlobalClearance(name,value)",
            "function globalClearanceValue(name)",
            "Valeurs mixtes",
            "container_between_xy",
            "container_between_z",
            "container_box_xy",
            "container_box_z",
            "asset_cavity_xy",
            "asset_cavity_z",
            "[axis]:'project_default'",
            "function derivedProjectItem(collection,idValue)",
            "resolvedItem.clearance_effective_v1",
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

    def test_aligns_container_identity_left_and_controls_right_with_a_truthful_global_mode(self) -> None:
        for marker in (
            'id="group-batch-controls"',
            'class="container-section-actions"',
            'class="container-summary"',
            'class="container-controls"',
            '.container-controls{display:flex;align-items:flex-end;justify-content:flex-end',
            'const modes=groups.map(uniformGroupMode),batchMode=',
            '>Mixte</option>',
            'groups.forEach(group=>setUnifiedGroupMode(group,mode))',
        ):
            self.assertIn(marker, self.markup)
        self.assertNotIn("Renseigne", self.markup)
        self.assertNotIn("confirm(`Appliquer le mode", self.markup)


    def test_exposes_non_mutating_container_estimation_without_a_new_bridge_action(self) -> None:
        for marker in (
            "estimate-groups-action",
            ">Réestimer</button>",
            "container_sizing",
            "Taille calculée",
            "Avant modification - A reestimer",
            "Estimation deja en cours.",
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
    def test_runs_adaptive_calculation_and_ignores_obsolete_responses(self) -> None:
        for marker in (
            "DERIVE_DEBOUNCE_MS=350", "AUTO_SOLVE_STABILITY_MS=1500",
            "scheduleAdaptiveSolve", "cancelAdaptiveSolve", "autoSolveTimer",
            "latestDerivedRequest", "adaptiveStatus", "Recalculer maintenant",
            "sendProject('validate_project',{},true,'adaptive')",
            "sendProject('solve_project',{},true,'adaptive')",
            "latestDerivedRequest[pendingRequest.derivedKey]!==payload.request_id",
        ):
            self.assertIn(marker, self.markup)
        self.assertNotIn('data-bridge="validate_project"', self.markup)
        self.assertEqual(self.markup.count('data-bridge="materialize_project"'), 1)
        self.assertLess(self.markup.index('id="preview-status"'), self.markup.index('id="preview-explanations"'))
        self.assertLess(self.markup.index('class="plan-grid"', self.markup.index("function renderResult")), self.markup.index('id="preview-explanations"'))
        self.assertIn('Calculée automatiquement', self.markup)
        self.assertIn('id="design-height" readonly aria-readonly="true" tabindex="-1"', self.markup)

    def test_keeps_background_updates_out_of_editable_dom_and_defers_layout_paint(self) -> None:
        quiet_start = self.markup.index("if(pendingRequest?.quiet)")
        quiet_end = self.markup.index("if(payload.partition)", quiet_start)
        quiet_branch = self.markup[quiet_start:quiet_end]
        self.assertIn("renderBackgroundUpdate(action)", quiet_branch)
        self.assertNotIn("renderAll()", quiet_branch)
        for marker in (
            "function renderBackgroundUpdate(action)",
            "function editableFieldActive()",
            "deferredDerivedPaint=true",
            "function flushDeferredDerivedPaint()",
            "document.addEventListener('focusout'",
            "function renderDerivedFacts()",
            "derivedStale=true",
            "markCardFactsPending()",
        ):
            self.assertIn(marker, self.markup)
        change_start = self.markup.index("document.addEventListener('change'")
        change_end = self.markup.index("window.fusionJavaScriptHandler=", change_start)
        change_handler = self.markup[change_start:change_end]
        self.assertIn("if(structural)renderAll()", change_handler)
        self.assertNotIn("markDirty();renderAll()", change_handler)

    def test_switches_card_measure_fields_and_exposes_explicit_sleeve_deltas(self) -> None:
        for marker in (
            "M\u00e9thode de mesure",
            "\u00c9paisseur paquet",
            "\u00c9paisseur carte \u00d7 nb",
            "counted?'':dimensionField('z')",
            "const quantityField=!isCards||counted?",
            "const thicknessField=counted?",
            "sleeve_extra_xy_mm",
            "sleeve_extra_z_mm_per_card",
            "DEFAULT_SLEEVE_EXTRA_XY_MM=3",
            "DEFAULT_SLEEVE_EXTRA_Z_MM_PER_CARD=.19",
            "ESTIMATED_CARD_THICKNESS_MM=.31",
            "Nb cartes",
            "card_stack_declared_thickness_mm",
            "card_declared_xy_mm",
            "function estimatedCardCount",
            "function markCardFactsPending",
            "À recalculer",
            'placeholder="Catalogue"',
        ):
            self.assertIn(marker, self.markup)

        self.assertIn(
            "${dimensions}${quantityField}${thicknessField}${methodField}${moveAction}",
            self.markup,
        )
        self.assertNotIn("${methodField}${dimensions}", self.markup)
        sleeve_start = self.markup.index("const sleeveFields=")
        sleeve_end = self.markup.index("const cardFields=", sleeve_start)
        self.assertNotIn("counted?", self.markup[sleeve_start:sleeve_end])
        self.assertIn(
            'class="card-estimated-count" title="Épaisseur paquet divisée par 0,31 mm',
            self.markup,
        )
        self.assertIn(">Nb cartes<input type=\"number\"", self.markup)
        self.assertNotIn("Nombre de cartes estimées", self.markup)
        for marker in ("card-sleeve-toggle", "card-orientation-field", "card-sleeve-xy", "card-sleeve-z", ".card-resolved-fact{flex:"):
            self.assertIn(marker, self.markup)

    def test_collapses_and_expands_each_container_without_hiding_its_primary_line(self) -> None:
        for marker in (
            "collapsedGroups=new Set()",
            'data-action="toggle-group"',
            "function toggleGroup(groupId)",
            ".group-card.is-collapsed .row-details{display:none}",
            'aria-expanded="${String(!collapsed)}"',
            '<div class="container-primary-grid">',
            '<div class="row-details">${customDetails}${children}</div>',
        ):
            self.assertIn(marker, self.markup)
        for marker in (
            'id="toggle-all-groups"', 'data-action="toggle-all-groups"',
            "function toggleAllGroups()", "function renderToggleAllGroups()",
            "Tout replier", "Tout déplier", 'placeholder="Défaut"',
        ):
            self.assertIn(marker, self.markup)
        self.assertEqual(self.markup.count('placeholder="Défaut"'), 2)

    def test_exposes_the_p61_lifecycle_and_keeps_healthy_inspection_out_of_global_messages(self) -> None:
        for marker in ("renderLifecycle", "scheduleDerived", "solvedStale", "Ancienne proposition", "technical_detail"):
            self.assertIn(marker, self.markup)
        self.assertIn("sendFusion('inspect',true)", self.markup)
        self.assertNotIn("Mode avance", self.markup)
        for malformed in ("Centr?", "Apr?s", "retrait n?", " ? encastrement"):
            self.assertNotIn(malformed, self.markup)

    def test_routes_validation_persistence_and_native_documents_to_the_versioned_bridge(self) -> None:
        self.assertEqual(self.dom.bridge_actions, {"save_document", "export_project", "export_personal_presets", "solve_project", "materialize_project"})
        for marker in ("bgig.palette.request.v1", "bgig.palette.response.v1", "bgig_palette_project", "bgig_palette_document", "DOCUMENT_ACTION", "sendDocument", "8000"):
            self.assertIn(marker, self.markup)

    def test_exposes_clear_design_settings_and_one_persistent_materialize_action(self) -> None:
        for marker in (
            "Réglages de conception", "Épaisseurs minimales", "Parois", "Fond",
            "Jeux (tolérances)", "Jeu entre conteneurs", "Jeu conteneur-boîte",
            "Jeu élément-cavité (par défaut)", "Priorité de la proposition",
            'class="settings-clearance-table"',
            '.settings-card{width:min(100%,760px)',
            '.settings-clearance-table{display:grid;gap:4px;width:min(100%,590px)',
            'grid-template-columns:minmax(270px,1fr) 104px 104px',
            '.settings-band-title{display:flex;align-items:baseline;justify-content:flex-start',
            'data-global-clearance="container_between_xy"',
            'data-global-clearance="container_between_z"',
            'data-global-clearance="container_box_xy"',
            'data-global-clearance="container_box_z"',
            'data-global-clearance="asset_cavity_xy"',
            'data-global-clearance="asset_cavity_z"',
        ):
            self.assertIn(marker, self.markup)
        self.assertEqual(self.markup.count('data-global-clearance="'), 6)
        self.assertNotIn("Jeux et preferences", self.markup)
        self.assertNotIn("Jeu entre conteneurs en hauteur", self.markup)
        self.assertNotIn("Jeu sous le couvercle", self.markup)
        self.assertNotIn('data-path="layout.container_box_xy_clearance_mm"', self.markup)
        self.assertNotIn('data-path="layout.container_z_clearance_mm"', self.markup)
        self.assertNotIn('data-path="box.usable_height_mm"', self.markup)
        self.assertEqual(self.markup.count('data-bridge="materialize_project"'), 1)
        self.assertIn('id="materialize-action"', self.markup)
        self.assertIn("renderPersistentActions", self.markup)
        self.assertLess(
            self.markup.index('data-bridge="solve_project">Recalculer maintenant</button><button id="materialize-action"'),
            self.markup.index('<div class="action-zone center">'),
        )

    def test_keeps_solver_usable_height_synced_with_the_visible_design_height(self) -> None:
        for marker in (
            "function designHeightValue()",
            "function syncDesignHeight()",
            "project.box.usable_height_mm=Math.max(0.0001,designHeightValue())",
            "if(path===\'box.inner_dimensions_mm.z\')syncDesignHeight()",
            "if(name===\'container_box_z\')syncDesignHeight()",
        ):
            self.assertIn(marker, self.markup)
        self.assertGreaterEqual(self.markup.count("if(project)syncDesignHeight();"), 2)
        self.assertNotIn("design=Math.max(0,z-lid)", self.markup)

    def test_preserves_interaction_state_with_stable_identifiers_and_rejects_stale_derivations(self) -> None:
        for marker in (
            "sourceRevision", "stampUiIdentifiers", "captureUiState", "restoreUiState",
            "data-object-id", "uiField", "uiDetails", "selectionStart",
            "scrollTop", "requestAnimationFrame", "data-ui-active-card",
        ):
            self.assertIn(marker, self.markup)
        self.assertIn("item?.id", self.markup)
        self.assertIn("pendingRequest?.derived&&(pendingRequest.sourceRevision!==sourceRevision", self.markup)
        self.assertIn("payload.envelopes&&payload.flat_stack&&(bootstrap||pendingRequest?.sourceRevision===sourceRevision)", self.markup)
        self.assertIn("derived:quiet||Boolean(derivedKey),derivedKey,sourceRevision", self.markup)
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


    def test_prepares_the_p44_m007_adaptive_preview_gate(self) -> None:
        script = (ROOT / "scripts" / "fusion" / "prepare_p44_m007_adaptive_preview_test.ps1").read_text(encoding="utf-8")
        for marker in (
            "0.1.40", "DERIVE_DEBOUNCE_MS=350", "AUTO_SOLVE_STABILITY_MS=1500",
            "latestDerivedRequest", "renderBackgroundUpdate(action)", "deferredDerivedPaint",
            "derivedStale=true", "markCardFactsPending",
            "DEFAULT_SLEEVE_EXTRA_XY_MM=3", "DEFAULT_SLEEVE_EXTRA_Z_MM_PER_CARD=.19",
            "ESTIMATED_CARD_THICKNESS_MM=.31", "card_stack_declared_thickness_mm",
            "card_declared_xy_mm", "Nb cartes", "sleeve_extra_xy_mm",
            "sleeve_extra_z_mm_per_card", "toggle-group", "toggle-all-groups",
            "data-density=", "bgig-list-density", "compact-summary", "Recalculer maintenant",
            "preview-status", "preview-explanations", "[char]0x00E9",
            "exactly one explicit materialize action", "P44-M007H03 Fusion OK 0.1.40",
        ):
            self.assertIn(marker, script)

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
