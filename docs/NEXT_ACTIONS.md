# Next Actions

Derniere mise a jour : 2026-07-14

## Version active

V0.1 - MVP Fusion-only `mvp-accepted` par P66, package 0.1.20 au commit
`6e351bb`. `fusion-validated: true`, `print-validated: false`.

## Requalification humaine

P44-M002, package 0.1.22, est `implemented` et `automated-validated`, mais
`human-ux-ko` sur la compacite reelle. Les garanties de focus, bridge et coeur
restent valides ; sa densite est remplacee par P44-M002V2.

## Derniere mission implementee

P44-M002V2 - correction de densite technique hybride A+B, package 0.1.23.

## Derniere preuve

Les cartes utilisent des bandes semantiques et une grille dense : dimensions
bornees, seuils 760/560 px, cibles de 40 px, sections essentielles visibles et
calculs secondaires replies. Les 455 tests, la syntaxe JavaScript, l exemple
CLI, `compileall`, la frontiere `adsk` et le diff-check passent. La validation
Fusion humaine n est pas acquise.

## Mission courante

P44-M002V - gate humaine de densite du package 0.1.23.

Statut : `human-gate`, `blocks-p44-m003`.
Action Codex : installer et verifier le package local.
Action humaine : observer les cartes a largeur normale et etroite dans Fusion.

## Prochaine action recommandee

Retour attendu :
`P44-M002V Fusion OK 0.1.23 - commit <sha>`

En cas de KO, indiquer la carte, la largeur approximative et le probleme.
P44-M003 ne doit pas commencer avant ce retour OK.

## Missions suivantes bloquees

P44-M003 est `blocked-by-p44-m002v`. P44-M004 a P44-M007 restent bloquees par
leur sequence. P44-M008 doit cadrer les jeux herites et overrides X/Y/Z par
objet, puis obtenir une gate humaine de tolerance avant P44-M009. P45/P46 ne
commencent pas avant P44-V ; P47-P50 restent bloques jusqu a P46 ; P69 reste
bloque jusqu a P50.

P68 reste `planned-after-p66` et peut recueillir des observations reelles sans
modifier les defaults. `print-validated: false` reste obligatoire.

## Fin de chaque mission

Documenter chaque OK/KO sans extrapoler a l impression, mettre a jour le
pilotage, committer et integrer directement dans main quand les preuves
automatisees sont vertes.
