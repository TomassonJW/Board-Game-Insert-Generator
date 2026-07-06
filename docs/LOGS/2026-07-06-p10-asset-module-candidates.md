# 2026-07-06 - P10-M004 asset module candidates

## Mission

`P10-M004 - Generer des candidats de modules depuis assets simples`.

## Changement

Le moteur expose une synthese `module_candidates` depuis les assets charges. Les
candidats restent des metadata explicables : `candidate_only`, `reservation_only`
ou `blocked`. Ils ne modifient pas `config.modules`, ne creent pas de layout et
ne declenchent aucune generation Fusion.

## Validation attendue

Tests unitaires, CLI Markdown/JSON/export CAD IR sur les exemples pertinents,
`git diff --check` et absence de `adsk` dans le coeur Python.
