# 2026-07-28 — P64-L09U-R5 accès partiel hors plateau

## Déclencheur

Thomas observe dans Fusion 0.1.75 que les cavités sous plateau sont correctement
placées et ouvertes sous la découpe, mais que leur portion hors plateau reste
presque fermée par le volume supérieur du conteneur.

## Verdict

- P64-L09U-R4-V : `human-KO`.
- 0.1.75 : `do-not-run`.
- `fusion-validated=false`.
- `print-validated=false`.

## Cause

Une intersection partielle avec un plateau abaissait toute la cavité. Les
accès verticaux hors plateau, présents dans le modèle CAD antérieur, avaient été
neutralisés lors de la correction d'ancrage local.

## Décision

ADR-0101 conserve l'ancrage et la profondeur, puis ouvre la cavité par régions
XY jusqu'au dessous de la découpe ou jusqu'au sommet fonctionnel local. Les
coupes restent bornées à l'empreinte de la cavité.

## État

Le code, la CAD IR, le plan Fusion et les tests partiels sont corrigés sur la
branche de mission. La suite autorisée, les replays personnels, l'intégration,
l'installation 0.1.76 et la gate R5-V restent à terminer.
