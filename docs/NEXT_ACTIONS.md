# Next Actions

Dernière mise à jour : 2026-07-14

## Version active

V0.1 - MVP Fusion-only `mvp-accepted` par P66, package 0.1.20 au commit
`6e351bb`. `fusion-validated: true`, `print-validated: false`.

## Dernière gate humaine fermée

P44-M002V est acceptée par le retour :
`P44-M002V Fusion OK 0.1.23 - commit 2f78a99`.

La densité hybride A+B du package 0.1.23 est donc `fusion-validated`.
Cette validation porte sur la compacité et la lisibilité des cartes, pas sur
l’impression.

## Exigence transversale ajoutée

Les textes utilisateur doivent désormais employer un français correctement
accentué. Tout nouveau texte P44 applique cette règle ; P44-M006 portera la
passe exhaustive sur l’historique. Contrat :
`docs/P44_FRENCH_UI_ORTHOTYPOGRAPHY_CONTRACT.md`.

## Mission courante

Aucune implémentation en cours. La gate P44-M002V est fermée et intégrée au
pilotage.

## Prochaine action recommandee

P44-M003 - quatre onglets, Boîte et éléments plats.

Statut : `ready-after-p44-m002v`, `no-business-change`,
`fusion-retest-required`.
Dépendance : P44-M002V acceptée.

Objectif : passer à quatre onglets, supprimer Précédent/Suivant, fusionner
Boîte/plateaux/livrets, traduire l’ordre de retrait et ajouter le bouton X/Y.
Les nouveaux libellés doivent respecter le contrat de français accentué.
Aucun jeu par objet, schéma, solveur, tolérance, géométrie, scène automatique
ou complément ne sera modifié.

## Missions suivantes bloquées

P44-M004 à P44-M007 restent bloquées par leur séquence. P44-M008 doit cadrer
les jeux hérités et overrides X/Y/Z par objet, puis obtenir une gate humaine de
tolérance avant P44-M009. P45/P46 ne commencent pas avant P44-V ; P47-P50
restent bloqués jusqu’à P46 ; P69 reste bloqué jusqu’à P50.

P68 reste `planned-after-p66` et peut recueillir des observations réelles sans
modifier les defaults. `print-validated: false` reste obligatoire.

## Fin de chaque mission

Documenter chaque OK/KO sans extrapoler à l’impression, mettre à jour le
pilotage, committer et intégrer directement dans main quand les preuves
automatisées sont vertes.
