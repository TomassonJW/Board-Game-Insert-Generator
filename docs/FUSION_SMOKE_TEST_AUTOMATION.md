# Fusion Smoke Test Automation

Derniere mise a jour : 2026-07-08

## Objectif

Les validations Fusion restent humaines, mais leur preparation ne doit plus etre
un travail manuel PowerShell pour Thomas.

Pour toute future gate Fusion, Codex doit preparer le smoke test depuis le depot
autant que l'environnement local le permet :

- verifier le commit courant ;
- generer les CAD IR temporaires quand le test en a besoin ;
- installer l'add-in courant dans le dossier Fusion AddIns ;
- ecrire les settings UI locaux utiles ;
- verifier que l'add-in installe contient les marqueurs attendus ;
- fournir seulement les actions restantes a realiser dans Fusion.

Thomas ne doit recevoir de blocs PowerShell a executer manuellement que si
l'infrastructure bloque Codex.

## Scripts

Les scripts vivent dans `scripts/fusion/`.

### `install_addin.ps1`

Installe l'add-in courant depuis le repo vers :

```text
%APPDATA%\Autodesk\Autodesk Fusion 360\API\AddIns\BoardGameInsertGenerator
```

Le script resout le repo root, verifie `fusion_addin/BoardGameInsertGenerator`,
supprime l'ancienne copie installee, copie l'add-in courant, affiche le commit
courant et verifie les marqueurs de commande UI attendus.

### `check_installed_addin.ps1`

Verifie que l'add-in installe existe et contient les marqueurs attendus.

### `prepare_smoke_test.ps1`

Prepare un smoke test CAD IR depuis une configuration exemple :

```powershell
scripts/fusion/prepare_smoke_test.ps1 `
  -ConfigPath examples/simple_asset_product_scene.json `
  -GenerationMode compact_only
```

Le script exporte une CAD IR dans `%TEMP%`, installe l'add-in, ecrit
`bgig_ui_settings.json` avec `input_mode = cad_ir_file`, puis affiche les actions
Fusion restantes.

### `prepare_quick_parametric_test.ps1`

Prepare le smoke test P12-M004V sans JSON source :

```powershell
scripts/fusion/prepare_quick_parametric_test.ps1
```

Le script installe l'add-in, ecrit `bgig_ui_settings.json` en
`quick_parametric_box`, puis precharge les valeurs :

- box `120 x 80 x 30` ;
- grid `4 x 4 x 3` ;
- wall/floor `1.2` ;
- clearances `0.4` / `0.3` ;
- print profile `draft`.

## Dry run

Tous les scripts de preparation acceptent `-DryRun`.

`-DryRun` doit etre utilise pour verifier la syntaxe, les chemins et le resume
sans modifier `%APPDATA%`.

## Permissions AppData

Si Codex ne peut pas ecrire dans `%APPDATA%`, il doit s'arreter et rapporter :

```text
Local AppData write blocked. Use Local/Handoff or approve filesystem write.
```

Dans ce cas, Codex ne doit pas pretendre que l'add-in est installe et ne doit pas
continuer vers une validation Fusion.

Les settings UI doivent etre ecrits en UTF-8 sans BOM. Le loader Python accepte aussi les fichiers UTF-8 avec BOM via `utf-8-sig`, mais les scripts doivent rester sans BOM pour eviter les regressions Windows PowerShell.

## P12-M004V

Le smoke test courant se prepare par :

```powershell
scripts/fusion/prepare_quick_parametric_test.ps1
```

Actions restantes dans Fusion :

1. Ouvrir Fusion 360 et un document Assembly-compatible.
2. Lancer `BoardGameInsertGenerator` ou cliquer `Generate Board Game Insert`.
3. Verifier dans le bloc `UI settings` : `UI settings loaded: yes`, `Loaded input mode: quick_parametric_box`, `Loaded generation mode: compact_only` et les valeurs quick box `120 x 80 x 30`, `4 x 4 x 3`, `1.2`, `0.4 / 0.3`, `draft`.
4. Verifier `Input mode = quick_parametric_box` et `Action = generate` ou `regenerate` si une scene BGIG existe deja.
5. Generer, rouvrir BGIG, verifier que toutes les valeurs sont restaurees.
6. Changer `box_inner_x_mm` a `160`, passer en `Action = regenerate`, lancer.
7. Verifier que la scene est remplacee sans doublon.
8. Rouvrir BGIG et verifier que `160` est toujours present.
9. Lancer `clear_bgig_scene`.
10. Verifier que les objets non BGIG sont preserves.

Statut attendu apres preparation : `manual_validation_required`, car seule
l'execution dans Fusion valide le comportement reel.

## P14-USABLE-ASSET-TRAY-SPRINT-V

La gate P14 se prepare avec le preset riche par defaut :

```powershell
scripts/fusion/prepare_quick_asset_test.ps1 -Preset p14_complete
```

Le script installe l'add-in courant et ecrit `bgig_ui_settings.json` avec `input_mode = quick_asset_box`, generation `compact_only`, box `220 x 160 x 96`, grid `8 x 5 x 4` et assets :

- `coin-tokens,tokens,36,18,16,2,loose` ;
- `status-tokens,tokens,24,12,18,2,loose` ;
- `damage-tokens,tokens,18,20,20,2,loose` ;
- `dice-set,dice,12,16,16,16,loose` ;
- `wood-meeples,meeples,20,12,12,18,loose`.

Ce scenario doit valider les apports P14 : 5 assets lus, plusieurs candidats modules, groupe tokens a 3 sources avec layout `deterministic_shelf_by_source_asset_v0`, rapports `printability_report_v0`, aide inline `quick_asset_box`, presets de smoke, regeneration sans doublon, clear preserve non-BGIG. Il ne valide toujours pas l'impression 3D.

## P15-TRAY-SEMANTICS-ALIGNMENT-SPRINT-V

La gate P15 se prepare avec le preset par defaut `p15_tray_semantics` :

```powershell
scripts/fusion/prepare_quick_asset_test.ps1 -Preset p15_tray_semantics
```

Le script installe l'add-in courant et ecrit `bgig_ui_settings.json` avec `input_mode = quick_asset_box`, generation `compact_only`, box `220 x 160 x 60`, grid `8 x 5 x 3`, `quick_asset_box_max_stack_height_mm = 18` et assets :

- `coin-tokens,tokens,40,18,16,2,loose` ;
- `status-tokens,tokens,24,12,18,2,loose` ;
- `dice-set,dice,8,16,16,16,loose` ;
- `wood-meeples,meeples,18,12,12,8,loose` ;
- `cubes,generic,24,8,8,8,loose`.

Ce scenario doit valider les apports P15 : modules bas en `flat_tray`, `max_stack_height_mm` visible et persiste, sizing qui s'etale en XY avant Z, semantique grid explicite (`placement_reservation_lattice_v0`, `body_snap_to_grid: no`), compartiments/encoches V0, printability report, regenerate sans doublon et clear preserve non-BGIG. Il ne valide toujours pas l'impression 3D.

## P16-ERGONOMIC-2D-TRAY-PACKING-SPRINT-V

La gate P16 se prepare avec le preset par defaut `p16_ergonomic_tray_packing` :

```powershell
scripts/fusion/prepare_quick_asset_test.ps1 -Preset p16_ergonomic_tray_packing
```

Le script installe l'add-in courant et ecrit `bgig_ui_settings.json` avec `input_mode = quick_asset_box`, generation `compact_only`, box `240 x 170 x 60`, grid `8 x 5 x 3`, `quick_asset_box_max_stack_height_mm = 18`, `quick_asset_box_target_aspect_ratio = 1.4`, `quick_asset_box_max_module_length_mm = 70` et assets :

- `coin-tokens,tokens,48,10,10,2,loose` ;
- `status-tokens,tokens,36,10,10,2,loose` ;
- `damage-tokens,tokens,24,14,12,2,loose` ;
- `dice-set,dice,8,16,16,16,loose` ;
- `wood-meeples,meeples,18,12,12,8,loose`.

Ce scenario doit valider les apports P16 : `tray_packing_policy: flat_tray_2d_v0`, `pile_grid_columns`, `pile_grid_rows`, `target_aspect_ratio`, `max_module_length_mm`, `linear_layout_avoided`, compartiments et encoches V0 conserves, regenerate sans doublon et clear preserve non-BGIG. Il ne valide toujours pas l'impression 3D.


## P17-PRINTABLE-EXPORT-AND-PREPRINT-SPRINT-V

La gate P17 se prepare avec le preset dedie `p17_printable_export` :

```powershell
scripts/fusion/prepare_quick_asset_test.ps1 -Preset p17_printable_export
```

Le script installe l'add-in courant et ecrit `bgig_ui_settings.json` avec `input_mode = quick_asset_box`, action initiale `generate`, generation `compact_only`, box `240 x 170 x 60`, grid `8 x 5 x 3`, `quick_asset_box_max_stack_height_mm = 18`, `quick_asset_box_target_aspect_ratio = 1.4`, `quick_asset_box_max_module_length_mm = 70` et assets :

- `coin-tokens,tokens,48,10,10,2,loose` ;
- `status-tokens,tokens,36,10,10,2,loose` ;
- `damage-tokens,tokens,24,14,12,2,loose` ;
- `dice-set,dice,8,16,16,16,loose` ;
- `wood-meeples,meeples,18,12,12,8,loose`.

Smoke cible :

1. Ouvrir Fusion 360 et un document Assembly-compatible.
2. Ouvrir BGIG et confirmer `UI settings loaded: yes`, `Input mode = quick_asset_box`, preset P17 et champs persistants.
3. Lancer `generate` et verifier scene riche P16/P17 : 5 assets, `flat_tray_2d_v0`, compartments, access notches, `printability_checked: yes`, `printability_export_allowed`, `Registry validation: ok`, `Print validation: false`.
4. Rouvrir BGIG, choisir `Action = export_printables`, lancer.
5. Verifier `export_policy: fusion_only_stl_per_printable_module_v0`, STL exportes, `printable_modules_exported`, `refused_modules`, `bgig_export_manifest.json`, `bgig_export_manifest.md` et `print_validated: false`.
6. Verifier que references, outlines, sketches debug, helpers, source occurrences, vues eclatees et objets non-BGIG ne sont pas exportes comme STL imprimables.
7. Ouvrir le manifeste JSON et verifier `schema_version: bgig.export_manifest.v0`, assets/modules, fichiers exportes, warnings/issues et `printability_validated_by_print: no`.
8. Lancer `clear_bgig_scene` et verifier que les objets non-BGIG sont preserves.

Cette gate ne valide pas l'impression physique.