# P64-L09T-A — preuve de recalcul explicite

## Statut

- Mission : P64-L09T-A.
- Date : 2026-07-27.
- Statut : `implemented-product`, `automated-validated`.
- `fusion-validated=false`.
- `print-validated=false`.

## Comportement livré

Après toute édition géométrique :

- le plan minimal devient obsolète ;
- le plan final devient obsolète ;
- l'identité de scène devient désynchronisée ;
- aucun placement monde n'est republié ;
- `Calculer` est la seule action capable de republier un plan minimal.

Le calcul explicite conserve :

- les dépendances et digests exacts ;
- l'invalidation et le rejet des résultats obsolètes ;
- le cache positif d'un plan certifié strictement identique ;
- le witness compatible, recertifié avant usage.

## Retrait des réutilisations automatiques

L'inventaire a identifié deux intégrations produit :

1. réutilisation locale à enveloppe fixe ;
2. insertion d'un nouveau conteneur dans le vide global.

Leurs appels ont été retirés de
`StagedCalculationSession.synchronize`. Le bridge ne republie plus de
partition pendant `validate_project`. La palette et le journal courant ne
transportent plus `local_reuse`, `global_void_reuse`, leurs statuts ni les
messages « intégré localement ».

Les producteurs algorithmiques historiques restent isolés pour leurs preuves
directes et anciens préflights. Ils ne sont plus importés ni appelés par le
cycle produit. Les anciens préflights L04V/L05V prouvent désormais la
supersession fail-closed : plan obsolète et prochaine action `calculate_layout`.

## Matrice de preuve

Les tests couvrent :

- ajout ou modification d'un contenu ;
- ajout d'un conteneur ;
- modification de la boîte ;
- modification d'un jeu ;
- ajout d'une réservation supérieure ;
- invalidation simultanée du minimal, du final et de la scène ;
- absence des anciens statuts dans le bridge, le journal et la palette ;
- cache certifié exact lors de deux appels explicites identiques à
  `Calculer` ;
- witness conservé comme incumbent recertifié, sans revendication de cache.

## Validations

- tests ciblés staged, bridge et palette : `89/89` en `2.147 s` ;
- régressions historiques L04/L05 recadrées : `20/20` en `1.029 s` ;
- syntaxe JavaScript extraite de la palette : `node --check`, OK ;
- suite complète : `912/912` en `329.039 s` ;
- test SCIP natif ignoré sous Python 3.10 : `1` ;
- benchmark ou holdout solveur invoqué : `0`.

La première tentative de suite complète a été interrompue par le timeout de
l'appel outil à 30 secondes, alors que le wrapper gardé était encore actif.
Le processus a été vérifié arrêté avant une relance unique. Cette première
tentative n'est pas comptée comme validation.

## Limites et suite

- Les diagnostics détaillés des arrêts anticipés ne sont pas modifiés par A ;
  ils appartiennent à P64-L09T-B.
- Les origines X/Y historiques des réservations restent présentes jusqu'à C.
- Aucun package Fusion n'est fabriqué ou installé avant G.
- 0.1.69 reste `human-KO`, `do-not-run`.

Prochaine mission : P64-L09T-B — rendre chaque arrêt anticipé immédiatement
compréhensible sans transformer une recherche bornée en preuve d'impossibilité.
