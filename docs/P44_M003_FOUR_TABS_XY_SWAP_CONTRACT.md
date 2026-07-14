# P44-M003 - Quatre onglets et interversion X/Y

Date : 2026-07-14
Statut : `done`, `implemented`, `automated-validated`, `human-fusion-gate-required`, `no-business-change`
Package cible : palette Fusion `0.1.24`
Capabilities : `C-FUSION-UI`, `C-QUALITY`
Dépendance : P44-M002V acceptée, package 0.1.23 observé dans Fusion.

## But

Rendre la navigation principale plus lisible avant la composition parent/enfant :

1. `Boîte et plateaux` ;
2. `Conteneurs et éléments` ;
3. `Réglages` ;
4. `Aperçu`.

`Précédent` et `Suivant` disparaissent. Boîte, plateaux et livrets partagent le
premier espace. Conteneurs et éléments partagent le deuxième espace, mais restent deux
listes plates : la projection parent/enfant est strictement réservée à P44-M004.

## Interversion X/Y

Un bouton accessible `Intervertir X et Y` échange atomiquement :

- les dimensions intérieures de la boîte ;
- les dimensions source d’un élément ;
- les dimensions d’un plateau ou livret ;
- le contrat complet X/Y d’un conteneur : mode, cible, fixe et expansion.

Il ne modifie jamais une origine X/Y, une position résolue, Z, le solveur ou la géométrie.
Pour un élément Cartes, l’interversion revient à une mesure explicite et retire le
catalogue actif, comme une édition directe existante.

`rotation_deg_z` est conservé dans le schéma et les projets historiques. Il sort du parcours
normal et reste accessible dans `Orientation historique` pour revenir à `Automatique` sans
migration destructive.

## Clarification plateau/livret

`Retrait calculé` devient `Ordre de retrait` avec une valeur compréhensible : `À retirer en 1er` ou `À retirer en 2e`, puis `À calculer après estimation`. La phrase de placement distingue la position, la taille
du logement encastré et le côté de la zone de prise.

## Exclusions

Aucun changement de schéma, loader, bridge Python, solveur, score, tolérance, réservation,
géométrie, CAD IR, scène Fusion automatique ou complément. Les jeux par objet restent
bloqués jusqu’à P44-M008 puis P44-M009.

## Preuves attendues

- DOM : quatre onglets, absence de navigation séquentielle, sections fusionnées et contrôles X/Y ;
- bridge : aucune nouvelle action métier ni mutation hors projet local ;
- roundtrip UTF-8 d’un nom `Éléments d’été — boîte à dés` ;
- suite complète, compilation, frontière `adsk` et `git diff --check` ;
- observation humaine Fusion du package 0.1.24 avant P44-M004.
