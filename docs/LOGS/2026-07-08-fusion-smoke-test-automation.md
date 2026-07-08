# Log - automatisation preparation smoke tests Fusion

Date : 2026-07-08

## Gate

Gate humaine validee pour automatiser la preparation locale des smoke tests
Fusion. Cette mission ne change pas la geometrie, les tolerances, le solveur, le
contrat CAD IR ni le coeur Python pur.

## Implementation

- Ajout de `scripts/fusion/install_addin.ps1` pour copier l'add-in courant dans
  `%APPDATA%\Autodesk\Autodesk Fusion 360\API\AddIns\BoardGameInsertGenerator`.
- Ajout de `scripts/fusion/check_installed_addin.ps1` pour verifier les marqueurs
  de l'add-in installe.
- Ajout de `scripts/fusion/prepare_smoke_test.ps1` pour exporter une CAD IR de
  smoke test depuis config, installer l'add-in et precharger les settings UI.
- Ajout de `scripts/fusion/prepare_quick_parametric_test.ps1` pour preparer
  P12-M004V avec les valeurs `quick_parametric_box` recommandees.
- Tous les scripts de preparation supportent `-DryRun`.

## Regle operationnelle

Pour toute future gate Fusion, Codex prepare le smoke test avec ces scripts et
ne fournit a Thomas que les actions restantes dans Fusion, sauf blocage
d'infrastructure. Si l'ecriture AppData est bloquee, le rapport doit indiquer :
`Local AppData write blocked. Use Local/Handoff or approve filesystem write.`

## Validation attendue

P12-M004V reste une validation humaine dans Fusion : rehydratation des champs,
modification `box_inner_x_mm = 160`, `regenerate` sans doublon, reouverture avec
`160` conserve, puis `clear_bgig_scene` avec preservation non-BGIG.
