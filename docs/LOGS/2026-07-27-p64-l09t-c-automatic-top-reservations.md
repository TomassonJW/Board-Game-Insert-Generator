# Journal — P64-L09T-C réservations supérieures automatiques

Date : 2026-07-27.

## Décision appliquée

Les plateaux et livrets restent des réservations virtuelles supérieures. Leur
pose XY devient une décision automatique, bornée et déterministe du calcul. La
pose résolue est figée dans le plan minimal et transmise sans divergence à la
finition.

Les origines X/Y manuelles sont retirées de la palette. Les anciens projets sont
normalisés en mémoire et ne sont réécrits qu'après une sauvegarde explicite.

## Invariants protégés

- aucune nouvelle valeur physique ;
- paroi minimale issue du groupe ou du default projet existant ;
- réservation prioritaire au sommet en Z ;
- aucun corps, support ou cale artificiel ;
- aucune réduction, translation ou réorientation de cavité ;
- blocage explicite lorsqu'aucune pose ne peut être certifiée.

## Validation

Les suites ciblées passent `135/135`, `17/17`, `47/47` et `10/10` pour les
contrats documentaires. La syntaxe JavaScript embarquée passe `node --check`.
La gate globale autorisée hors onze modules benchmark/corpus/tournoi passe
`859/859` en `282.881 s`, avec un test SCIP natif ignoré.

Statut : `P64-L09T-C-automated-validated`.

`fusion-validated=false`, `print-validated=false`.

Prochaine mission : P64-L09T-D, priorité lexicographique « plancher d'abord ».
