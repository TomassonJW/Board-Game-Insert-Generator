# Next Actions

Derniere mise a jour : 2026-07-14

## Version active

V0.1 - MVP Fusion-only `mvp-accepted` par P66, package 0.1.20 au commit
`6e351bb`. `fusion-validated: true`, `print-validated: false`.

## Derniere mission terminee

P44-M002 - densite compacte et hierarchie de carte, package 0.1.22.

## Derniere preuve

Le mode Compact conserve les champs editables des cartes, avec des grilles
adaptees, des titres renforces et des actions de carte de 40 px minimum.
`Solidite` est visible en permanence ; `Details calcules` replie taille,
etage, appui, surplus et raisons de conteneur. Les 454 tests, la syntaxe JS,
l exemple CLI, `compileall`, le controle `adsk` et le diff-check passent ; la
validation Fusion reste a rejouer.

## Mission courante

Aucune implementation en cours. P44-M002 est `implemented`,
`automated-validated`, `fusion-retest-required` et integree dans `main`.

## Prochaine action recommandee

P44-M003 - quatre onglets, Boite et elements plats.

Statut : `ready-after-p44-m002-integration`, `no-business-change`,
`fusion-retest-required`.
Dependance : P44-M002 integree dans `main`.

Objectif : passer a quatre onglets, supprimer Precedent/Suivant, fusionner
Boite/plateaux/livrets, traduire l ordre de retrait et ajouter le bouton X/Y.
Aucun jeu par objet, schema, solveur, tolerance, geometrie, scene automatique
ou complement ne sera modifie.

## Missions suivantes bloquees

P44-M004 a P44-M007 restent bloquees par leur sequence. P44-M008 doit cadrer
les jeux herites et overrides X/Y/Z par objet, puis obtenir une gate humaine de
tolerance avant P44-M009. P45/P46 ne commencent pas avant P44-V ; P47-P50
restent bloques jusqu a P46 ; P69 reste bloque jusqu a P50.

P68 reste `planned-after-p66` et peut recueillir des observations reelles sans
modifier les defaults. `print-validated: false` reste obligatoire.

## Fin de chaque mission

Documenter chaque OK/KO sans extrapoler a l impression, mettre a jour le
pilotage, committer et integrer directement dans main quand les preuves
automatisees sont vertes.
