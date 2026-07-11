# P34 - Smoke Fusion du coupon coulissant

## Statut

`fusion-smoke-required`, `print-validated: false`.

## Ce qui est prepare automatiquement

Le script `scripts/fusion/prepare_p34_sliding_lid_coupon_test.ps1` exporte le
starter choisi avec `sliding_lid`, installe l'add-in, ecrit les reglages locaux
et pointe Fusion vers la CAD IR temporaire.

Le coupon est volontairement place a cote de la boite. Il ne modifie pas les
bacs selectionnes ni leur placement P21.

## Ce que Fusion doit montrer

- les bacs ouverts existants ;
- un bac de coupon et un capot de coupon ;
- le capot comme une piece unique avec deux glissieres laterales descendantes ;
- le rapport avec `Joined cap rails: 2` ;
- `Print validation: false` toujours visible.

## Retour humain attendu

Repondre `P34 Fusion OK` si les deux glissieres sont visiblement jointes au
capot et si aucune piece n'est libre ou dupliquee. Repondre `P34 Fusion KO`
avec ce qui est observe sinon.

## Limites

Le smoke ne prouve ni le frottement, ni le jeu reel, ni la resistance, ni la
qualite d'impression. Le prochain vrai test est un coupon imprime et mesure.
