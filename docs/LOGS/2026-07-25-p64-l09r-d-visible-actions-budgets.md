# Journal P64-L09R-D — actions et budgets visibles

Date : 2026-07-25

## Changement produit

La palette expose désormais trois actions permanentes. Leur activation dépend uniquement de état courant du plan et de opération active. Les budgets calcul et finition sont visibles, indépendants, persistants et accompagnés de leur limite réelle.

## Invalidation

Le budget du calcul reste une dépendance du plan minimal. Le budget de finition utilise une invalidation dédiée : il annule une finition en cours, marque seulement le plan final obsolète et conserve le plan minimal certifié ainsi que sa sélection CAD.

## Validation

- 18/18 tests cycle ;
- 29/29 tests pont ;
- 40/40 tests DOM ;
- 28/28 tests résultat, transport et synchro CAD ;
- JavaScript `node --check` OK ;
- suite complète 861/861 en 252,858 s, un test natif ignoré ;
- compilation et diff check OK.

## Suite

P64-L09R-E doit déplacer la zone activité juste au-dessus des boutons, la supprimer totalement au repos, rafraîchir environ chaque seconde et exécuter calcul et finition purs hors thread UI sans `adsk`.
