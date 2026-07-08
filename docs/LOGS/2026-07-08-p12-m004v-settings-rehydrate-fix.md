# Log - P12-M004V KO settings non rehydrates

Date : 2026-07-08

## Observation

Le smoke test humain P12-M004V a ete refuse : apres preparation par
`scripts/fusion/prepare_quick_parametric_test.ps1`, la commande Fusion ne
montrait pas les valeurs attendues dans `quick_parametric_box`.

## Cause racine

Le script PowerShell ecrivait `bgig_ui_settings.json` avec `Set-Content -Encoding
UTF8`. Dans Windows PowerShell, cet encodage ajoute un BOM UTF-8. Le loader Python
lisait ensuite le fichier avec `encoding="utf-8"`, puis `json.loads()` refusait le
BOM. `load_fusion_ui_settings()` retournait alors `{}` silencieusement, ce qui
faisait retomber l'UI sur les defaults auto-detectes.

## Correction

- Lecture settings rendue robuste via `utf-8-sig`.
- Ecriture settings PowerShell faite en UTF-8 sans BOM via
  `[System.Text.UTF8Encoding]::new($false)`.
- Ajout d'un bloc visible dans la commande Fusion : chemin settings, loaded
  yes/no, input mode, action, generation mode et valeurs quick box chargees.
- Ajout d'un test de regression avec fichier settings UTF-8 BOM.

## Verification locale

Apres reexecution de `scripts/fusion/prepare_quick_parametric_test.ps1` :

- settings ecrit dans
  `C:\Users\janko\AppData\Roaming\Autodesk\Autodesk Fusion 360\API\AddIns\BoardGameInsertGenerator\bgig_ui_settings.json` ;
- BOM UTF-8 absent ;
- `default_fusion_ui_settings()` lit `settings_loaded: yes` ;
- `default_fusion_command_values()` produit `input_mode = quick_parametric_box`,
  `action = generate`, `generation_mode = compact_only` et les valeurs
  `120 x 80 x 30`, `4 x 4 x 3`, `1.2`, `0.4 / 0.3`, `draft`.

## Statut

Correction codee et preparee localement. P12-M004V reste a revalider dans Fusion.
`print-validated: false`.
