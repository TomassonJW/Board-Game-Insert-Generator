# 2026-07-04 - Strategic product realignment

## Mission

`P0-M009 - Realigner North Star, capabilities et roadmap volumetrique`.

## Contexte

Le projet a atteint un socle P5 : moteur Python pur, layout 2D, tolerances par
faces, profils d'impression, CAD IR, add-in Fusion, blanks Fusion valides
manuellement, export CAD IR, cavites simples abstraites et features ergonomiques
abstraites.

La demande humaine du 2026-07-04 valide le changement de North Star vers un
generateur intelligent de systemes volumetriques modulaires asset-first pour
inserts de jeux de societe.

## Changements

- Refonte documentaire de la North Star, spec produit et roadmap 0-14.
- Ajout de `docs/CAPABILITY_MAP.md` comme pont entre piliers, capabilities,
  milestones, gates et validations.
- Ajout de strategies cible pour asset model, volumetric layout, layers,
  accessibilite, solveur et vues eclatees.
- Mise a jour des protocoles d'autonomie pour choisir les missions par
  capability et milestone.
- Reorganisation du backlog autour des phases 0-14.
- Creation d'ADR-0012 pour le pilotage par capabilities.

## Limites

- Aucun solveur 3D n'est implemente.
- Aucun champ `assets`, `layers` ou `reservations` n'est accepte par le loader V0.
- Aucune nouvelle geometrie Fusion n'est generee.
- Les cavites/features restent abstraites dans Fusion tant qu'une gate P6 n'est
  pas validee.

## Gate suivante

Gate active : `P6-M001 - Generer les cavites rectangulaires simples dans Fusion`,
si l'humain veut autoriser les premieres operations soustractives Fusion.

Alternative non gated si Fusion est reportee : `P8-M001 - Specifier la grille
volumetrique 3D et les layers`.