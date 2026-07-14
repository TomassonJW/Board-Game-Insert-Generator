# Next Actions

Derniere mise a jour : 2026-07-14

## Version active

V0.1 - MVP Fusion-only `mvp-accepted` par P66, package 0.1.20 au commit
`6e351bb`. `fusion-validated: true`, `print-validated: false`.

## Derniere mission terminee

P44-M001 - stabilite de saisie et d etat de la palette, package 0.1.21.

## Derniere preuve

La palette restaure focus, caret, details, carte active et scroll a partir des
identifiants stables des objets. Les reponses derivees `validate_project` et
`solve_project` dont la revision source est obsolete sont ignorees. Les tests
DOM/bridge ciblent aussi cinquante conteneurs. Les 453 tests, la syntaxe JS,
l exemple CLI, `compileall`, le controle `adsk` et le diff-check passent ; la
validation Fusion reste a rejouer.

## Mission courante

Aucune implementation en cours. P44-M001 est `implemented`,
`automated-validated`, `fusion-retest-required` et attend son integration dans
`main`.

## Prochaine action recommandee

P44-M002 - densite compacte et hierarchie de carte.

Statut : `ready-after-p44-m001-integration`, `no-business-change`,
`fusion-retest-required`.
Dependance : P44-M001 integree dans `main`.

Objectif : compacter champs et labels, rendre les titres lisibles et conserver
les cibles accessibles. `Solidite` sera visible ; les tailles calculees, etages,
appuis, surplus et raisons resteront des details secondaires replies. Aucun
schema, solveur, jeu, tolerance, geometrie, scene automatique ou complement ne
sera modifie.

## Missions suivantes bloquees

P44-M003 a P44-M007 restent bloquees par leur sequence. P44-M008 doit cadrer
les jeux herites et overrides X/Y/Z par objet, puis obtenir une gate humaine de
tolerance avant P44-M009. P45/P46 ne commencent pas avant P44-V ; P47-P50
restent bloques jusqu a P46 ; P69 reste bloque jusqu a P50.

P68 reste `planned-after-p66` et peut recueillir des observations reelles sans
modifier les defaults. `print-validated: false` reste obligatoire.

## Fin de chaque mission

Documenter chaque OK/KO sans extrapoler a l impression, mettre a jour le
pilotage, committer et integrer directement dans main quand les preuves
automatisees sont vertes.
