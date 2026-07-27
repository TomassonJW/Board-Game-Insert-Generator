# 2026-07-27 — P64-L09T-A recalcul explicite

## Décision appliquée

ADR-0093 supersède les deux réutilisations automatiques d'ADR-0075 et
ADR-0076 dans le parcours produit.

## Changement

- `validate_project` ne republie plus de plan minimal après une édition ;
- minimal, final et scène deviennent obsolètes ensemble ;
- les anciens statuts et messages de réutilisation disparaissent du bridge,
  de la palette et du journal courant ;
- cache certifié exact et witness restent disponibles seulement pendant
  l'action explicite `Calculer`.

## Preuves

- ciblés : `89/89` ;
- régressions historiques recadrées : `20/20` ;
- suite complète : `912/912` en `329.039 s`, un test SCIP natif ignoré ;
- benchmark/holdout solveur : aucun appel.

## Suite

P64-L09T-B devient prête après intégration de A. Aucun package Fusion n'est
installé avant G. `fusion-validated=false`, `print-validated=false`.
