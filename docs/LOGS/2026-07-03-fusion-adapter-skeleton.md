# Log - P4-M002 Fusion adapter skeleton

## Date

2026-07-03

## Mission

`P4-M002 - Creer un squelette d'adaptateur Fusion 360`

## Contexte

La gate humaine a autorise un squelette Fusion isole apres la livraison du
contrat CAD IR `P4-M001`.

## Changements

- Creation du dossier `fusion_addin/BoardGameInsertGenerator`.
- Ajout d'un manifeste d'add-in et d'un point d'entree `run(context)` /
  `stop(context)`.
- Ajout d'une couche `fusion_skeleton.py` testable hors Fusion.
- Anticipation du cas Fusion Zero Doc sans creation de document ou geometrie.
- Conversion de la CAD IR vers un plan d'operations `planned_only`.
- Documentation d'installation locale et de debug hors Fusion.
- ADR-0008 pour fixer la frontiere entre coeur Python et squelette Fusion.

## Validation attendue

Les tests Python doivent couvrir la partie hors Fusion. Une verification runtime
dans Fusion reste future et ne vaut pas validation de geometrie.

## Gate suivante

`P4-M003` doit recevoir une nouvelle validation humaine avant toute generation
reelle de blanks rectangulaires dans Fusion.
