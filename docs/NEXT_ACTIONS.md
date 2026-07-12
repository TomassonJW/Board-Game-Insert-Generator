# Next Actions

Derniere mise a jour : 2026-07-12

## Version active

V0.1 - vrai MVP Fusion-only selon ADR-0055 et rebase P60-R accepte.

## Derniere mission terminee

P61 - etat reactif et architecture de palette, package 0.1.10.

## Derniere preuve automatisee

La palette distingue saisie, minima, proposition et scene Fusion. Une edition
recalcule les derives, conserve l ancien Apercu comme obsolete et bloque sa
materialisation. Le rapport inspect complet reste dans Details techniques.
Les tests palette/bridge et la suite complete sont verts ; aucune validation
Fusion ou impression n est revendiquee.

## Mission courante

Aucune mission en cours. P61 est integree avant selection de la suite.

## Prochaine action prete

P62 - catalogue d elements et orientations de rangement.

Scope borne :

1. formats de cartes locaux et dimensions resolues visibles ;
2. sleevees / non sleevees ;
3. orientations a plat, debout grand cote, debout petit cote et automatique ;
4. presets personnels locaux, versionnes et exportables ;
5. migration additive et tests coeur/palette.

## Mission suivante apres P62

P63 - reservations superieures encastrees, selon ADR-0057 acceptee.

## Releases bloquees

P63 depend de P62 ; P64 depend de P63 ; P65 depend de P64. P44 a P50 restent
bloques jusqu a l acceptation humaine P66. P47 a P50 restent aussi bloques
jusqu a l acceptation de P46.

## Gate humaine active

Aucune gate avant P66 tant que P62-P65 restent dans les ADR acceptees et
n introduisent ni dependance lourde ni changement de tolerance. P66 demandera
une observation Fusion preparee automatiquement.

## Fin de chaque mission

Documenter chaque OK/KO sans extrapoler a l impression, mettre a jour le
pilotage, committer et integrer directement dans main quand les preuves
automatisees sont vertes. print-validated: false reste obligatoire.
