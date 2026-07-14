# Log - P44-M002V2 densite technique corrective

Date : 2026-07-14
Mission : P44-M002V2
Package : 0.1.23

## Declencheur

Thomas a teste le package 0.1.22 et a conclu que les cartes restaient trop
grandes. Les tests DOM validaient la presence de grilles, pas la densite
visuelle attendue. P44-M002 est donc conserve comme implementation automatisee
mais requalifie `human-ux-ko` pour la compacite.

## Decision

L hybride A+B est retenu : bandes semantiques pour la lecture et grille
technique dense pour les valeurs courtes. Les champs numeriques sont bornes,
les cibles restent a 40 px et les sections essentielles restent ouvertes.
Les explications et calculs secondaires peuvent etre replies.

## Frontieres

Aucun changement de schema, loader, coeur, bridge metier, solveur, tolerance,
geometrie, CAD IR, scene Fusion ou complement. P44-M003 reste bloque jusqu a la
gate humaine P44-M002V.

## Validation

455 tests, syntaxe JavaScript, exemple CLI, compileall et frontiere `adsk`
passent. Le package installe ne sera pas qualifie `fusion-validated` avant
le retour humain explicite.
