# 2026-07-14 — P44-M004V2 hybride C

## Fait déclencheur

La revue humaine du package 0.1.25 a jugé la composition fonctionnelle mais encore
trop verticale : faible utilisation de la largeur Fusion, bruit éditorial,
premier conteneur trop bas et comparaison parent/enfants insuffisante.

## Décision

Thomas valide l’hybride C : grilles techniques horizontales, largeur utile
augmentée, contrôles principaux visibles, actions et calculs secondaires
progressivement révélés, cibles de 40 px conservées.

## Effet

Le package passe à 0.1.26. La correction reste UI-only et n’altère ni modèle,
bridge, solveur, tolérance, géométrie, CAD IR, scène Fusion ou compléments.
P44-M004 n’est pas déclarée fusion-validated par le retour 0.1.25 ; une nouvelle
gate P44-M004V2 est ouverte avant P44-M005.
