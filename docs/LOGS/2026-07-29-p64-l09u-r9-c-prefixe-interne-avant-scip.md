# 2026-07-29 — P64-L09U-R9-C préfixe interne avant SCIP

## Décision

Pour le profil Approfondi, les projets avec éléments plats et moins de douze
groupes exécutent d'abord la première lane interne exacte. Une solution
certifiée de cette lane devient l'autorité du run.

Normal et Long gardent leurs propres budgets et comportements. SCIP reste le
repli après un échec borné du préfixe ; cet échec et sa télémétrie ne sont pas
masqués.

## Mesures

Replays orchestrés avec runtime natif livré :

- `CasLimite02+` : `10,013 s`, 1 lane, 0 SCIP ;
- `CasLimite02++` : `9,791 s`, 1 lane, 0 SCIP ;
- digest de placement : `a3ef…bc46` dans les deux cas ;
- SHA personnels : identiques avant/après.

Le chemin précédent mesurait `90,991 s` et `87,192 s`. Le gain est d'environ
89 %.

## Tests ciblés

- solveur minimal : 19 tests, OK ;
- solveur SCIP : 19 tests, OK, 1 skip de runtime optionnel ;
- calcul étagé : 21 tests, OK.

Les tests couvrent l'absence d'appel SCIP après certification interne et la
présence du repli SCIP après un échec honnête du préfixe.
