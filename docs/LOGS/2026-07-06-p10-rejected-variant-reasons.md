# 2026-07-06 - P10-M003 rejected variant reasons

## Mission

`P10-M003 - Rapporter les variantes refusees avec raisons detaillees`.

## Changement

Les variantes `rejected` exposees par `variant_comparison` transportent maintenant
une liste `rejection_reasons` structuree : code, categorie, severite, message
source, reference de contrainte et action corrective.

## Limites

- Report-only : aucune nouvelle strategie de placement.
- Aucun solveur global, aucun backtracking, aucune dependance lourde.
- Aucune generation Fusion nouvelle.

## Validation attendue

Tests unitaires, CLI Markdown/JSON/export CAD IR, `git diff --check` et absence de
`adsk` dans le coeur Python.