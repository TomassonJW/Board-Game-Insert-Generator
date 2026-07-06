# 2026-07-06 - P10-M006 deterministic asset grouping

## Mission

`P10-M006 - Regrouper deterministiquement des assets compatibles`.

## Changement

Les assets compatibles peuvent produire un candidat groupe unique quand ils
partagent kind, containment intent et confiance de mesure, sans reservation ni
module hint. Le grouping reste report-only et reversible.

## Limites

Aucun solveur global, aucun grouping heterogene, aucune generation Fusion.
