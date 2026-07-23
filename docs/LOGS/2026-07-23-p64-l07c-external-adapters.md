# 2026-07-23 — P64-L07C adapters externes

## Décision appliquée

Quatre moteurs réels sont encapsulés hors processus sous une entrée sol 2D
commune : OR-Tools CP-SAT, HiGHS, SCIP/PySCIPOpt et LAFF.

SCIP et LAFF restent `benchmark-only` après découverte de dépendances natives
ou de licences transitives qui interdisent de conclure sur la redistribution
produit dans ce lot.

## Preuve

- 32 artefacts verrouillés avant exécution ;
- quatre familles externes ;
- 12/12 contrôles réels conformes ;
- huit placements BGIG recertifiés ;
- trois impossibilités prouvées par moteurs exacts ;
- LAFF conserve `bounded_unknown` ;
- aucun holdout lu ;
- aucun routage produit modifié.

## Correction de pilotage

Les quatre `small_exact_controls` sélectionnés en L07B ne correspondent pas au
modèle exact sol après matérialisation. L07C ajoute trois contrôles explicites
sans modifier le manifest V2 ni le reçu du holdout scellé.

## Suite

P64-L07D doit exécuter les régressions, discovery, tuning puis une sélection
scellée avant l'ouverture unique du holdout.
