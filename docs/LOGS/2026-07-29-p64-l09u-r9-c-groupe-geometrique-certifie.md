# 2026-07-29 — P64-L09U-R9-C groupe géométrique certifié

## Décision

La première lane Approfondie produit toujours ses douze complétions sous les
mêmes plafonds. Elles sont regroupées par rang géométrique exact.

Tous les membres du premier groupe qui contient une solution certifiée sont
certifiés. Le classement produit complet choisit ensuite à l'intérieur de ce
groupe. Les groupes géométriquement moins bons ne déclenchent plus de
résolution plate.

## Contre-preuve utile

Certifier un seul membre atteignait environ 3,2–3,4 s, mais choisissait
`cab1…9878` sur `CasLimite02+`. Cette variante est rejetée.

Le meilleur groupe contient deux symétries. Leur certification complète
conserve `a3ef…bc46` sur les deux projets.

## Mesures

- `CasLimite02+` : `3,874 s` ;
- `CasLimite02++` : `4,052 s` ;
- 12 complétions beam inchangées ;
- 2 candidats du groupe certifiés, puis revalidation finale ;
- une lane, zéro SCIP ;
- SHA personnels inchangés.

## Tests ciblés

- solveur minimal : 19 tests, OK ;
- calcul étagé : 21 tests, OK ;
- SCIP : 19 tests, OK, 1 skip optionnel ;
- témoin certifié : 5 tests, OK ;
- portfolio : 5 tests, OK en 61,401 s.
