# 2026-07-09 - P13-ASSET-M003 asset-fit cavity V0

## Mission

Implementer la premiere cavite asset-first V0 depuis l'enveloppe count-aware `asset_fit`, dans le flux `quick_asset_box`.

## Resultat

- Metadata `asset_fit_cavity` ajoutee aux modules `executable_asset_plan`.
- Politique `single_asset_fit_rectangular_cavity_v0`.
- Fusion convertit les cavites planifiees en coupes rectangulaires reelles via `subtract_rectangular_cavity`.
- Reporting ajoute : `asset_cavity_policy`, cavites planned/generated, dimensions, fond restant, murs attendus.
- Scripts Fusion prepares pour le smoke M003 count-aware + cavite.

## Limites

- Pas d'assets individuels visualises.
- Pas de cavites par pile ou par item.
- Pas de solveur global ni optimisation.
- Capacite heuristique non garantie physiquement.
- Aucune impression 3D validee.

## Gate suivante

`P13-ASSET-M003V` : validation humaine Fusion obligatoire avant mission produit suivante.

## Verifications

- `python -m unittest discover -s tests` : OK, 185 tests.
- `python -m py_compile fusion_addin/BoardGameInsertGenerator/BoardGameInsertGenerator.py fusion_addin/BoardGameInsertGenerator/fusion_skeleton.py` : OK.
- CLI Markdown/JSON/export CAD IR exemples P12/P13 : OK.
- `scripts/fusion/prepare_quick_asset_test.ps1 -DryRun` : OK.
- `scripts/fusion/prepare_quick_asset_test.ps1` : OK, add-in installe et settings ecrits.
- `scripts/fusion/check_installed_addin.ps1` : OK.
- `git diff --check` : OK.
- `rg -n "adsk" src/board_game_insert_generator` : aucune occurrence.
