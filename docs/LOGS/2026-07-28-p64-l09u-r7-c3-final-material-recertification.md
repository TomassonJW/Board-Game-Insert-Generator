# 2026-07-28 — P64-L09U-R7-C3 recertification finale

## Résultat

La frontière de boîte additionne désormais le jeu externe et la paroi minimale.
Le solveur et la finalisation partagent un certificat de bandes résiduelles et
de composantes de coupe. La finalisation bloque sans déplacer la pose si une
dimension positive tombe sous le minimum.

Les coutures XY d'une réservation ne subdivisent plus un corps dont
l'intervalle Z ne rencontre pas la coupe. Sur `CasLimite02++`, cela supprime les
`14` prismes de `0,8 mm`, réduit les prismes de `118` à `56` et les coupes
supérieures de `45` à `18`.

## Validation

- tests ciblés : `66/66` ;
- deux replays personnels réussis, SHA inchangés ;
- zéro prisme ou coupe supérieure sous `1,2 mm` ;
- certificat final présent dans le plan Fusion.

La gate Fusion reste humaine.
