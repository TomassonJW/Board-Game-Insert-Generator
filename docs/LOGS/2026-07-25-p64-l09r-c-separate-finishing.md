# Journal P64-L09R-C — finition séparée

Date : 2026-07-25

## Décision exécutée

La finition devient une action produit distincte du calcul minimal. Son budget est indépendant, sa deadline est globale et son résultat remplace le minimal uniquement après recertification complète. Timeout, rejet et résultat obsolète laissent le plan minimal courant intact et matérialisable.

## Changements

- profils de finition 3/10/20/60/180 s et caps monotones ;
- token de requête lié aux digests source, artefact minimal et valeur minimale ;
- rejet stale avant cache et publication ;
- repli sur fermeture de base certifiée si seul objectif secondaire expire ;
- pont palette prêt à recevoir `finishing_effort` ;
- tests de budget indépendant, timeout non destructif, stale et sélection CAD minimale.

## Validation

- compilation Python : OK ;
- tests session : 17/17 ;
- tests palette : 29/29 ;
- tests fermeture continue : 5/5 ;
- suite complète : 859/859 en 240,829 s ; un test natif ignoré sous Python 3.10 ;
- `git diff --check` : OK.

## Limites

Les sélecteurs visibles et les trois actions permanentes appartiennent à P64-L09R-D. Le hors-thread UI et la jauge appartiennent à E. Aucun benchmark, package Fusion, observation Fusion ou fait impression produit.
