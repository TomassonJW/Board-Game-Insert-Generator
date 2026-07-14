# Next Actions

Derniere mise a jour : 2026-07-14

## Version active

V0.1 - MVP Fusion-only `mvp-accepted` par P66, package 0.1.20 au commit
`6e351bb`. `fusion-validated: true`, `print-validated: false`.

## Derniere mission terminee

P67-V - arbitrage humain de la trajectoire V0.2. Thomas accepte D67-01 a
D67-11, l option C et ADR-0062. Les precisions sur les jeux par objet et les
cartes Conteneurs sont capturees sans changement runtime.

## Derniere preuve

Retour humain du 2026-07-14 : option C, quatre onglets, composition
Conteneur/Elements, toolbar sans complements, X/Y, calcul hybride, cycle
document, separation gabarit/profil, accents semantiques et P44-M001 acceptes.
Les complements restent en quarantaine pour maintenant.

## Mission courante

Aucune implementation en cours. P67 est `done-human-gate`. P44-M001 est la
seule mission V0.2 `ready`.

## Prochaine action recommandee

P44-M001 - stabilite de saisie et d etat de la palette.

Statut : `ready`, `no-business-change`, `fusion-retest-required`.
Contrat : `docs/P44_M001_UI_STATE_STABILITY_CONTRACT.md`.
Package cible : palette Fusion `0.1.21`.

Objectif : conserver focus, caret, details ouverts, carte active et scroll
pendant chaque edition et reponse derivee asynchrone. Aucun changement de
schema, solveur, jeu, tolerance, geometrie, scene automatique, navigation ou
complement n est autorise dans cette mission.

## Missions suivantes bloquees

P44-M002 a P44-M007 restent bloquees par leur sequence. P44-M008 doit cadrer
les jeux herites et overrides X/Y/Z par objet, puis obtenir une gate humaine de
tolerance avant P44-M009. P45/P46 ne commencent pas avant P44-V ; P47-P50
restent bloques jusqu a P46 ; P69 reste bloque jusqu a P50.

P68 reste `planned-after-p66` et peut recueillir des observations reelles sans
modifier les defaults. `print-validated: false` reste obligatoire.

## Fin de chaque mission

Documenter chaque OK/KO sans extrapoler a l impression, mettre a jour le
pilotage, committer et integrer directement dans main quand les preuves
automatisees sont vertes.
