# 2026-07-28 — P64-L09U-R7-C2 parois et score utile

## Décision appliquée

Le placement automatique rejette désormais toute empreinte ou prise située à
moins de la paroi canonique du bord de boîte. Deux zones plates disjointes
doivent garder la même séparation. Le score des poses faisables privilégie la
couverture et le centrage utiles ainsi que le recouvrement sain.

Le centrage utile précède la marge excédentaire dans le score : la marge
canonique est déjà une contrainte dure, et son surplus ne doit pas éloigner une
encoche de la matière qu'elle doit servir.

## Validation

- tests ciblés : `62/62` ;
- `CasLimite02+` : replay réussi, SHA avant/après identiques ;
- `CasLimite02++` : replay réussi, SHA avant/après identiques ;
- aucune UI manuelle, aucun benchmark, holdout, corpus ou tournoi.

## Suite

R7-C3 doit recertifier les fragments produits sur les corps composites finaux,
sans déplacer silencieusement une pose déjà portée par le plan minimal.
