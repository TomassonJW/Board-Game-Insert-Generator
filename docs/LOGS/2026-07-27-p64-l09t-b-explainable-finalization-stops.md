# 2026-07-27 — P64-L09T-B

## Décision

Les arrêts de finition utilisent désormais un diagnostic produit versionné,
distinct de la raison technique brute. Une recherche bornée inconnue ne vaut
jamais preuve d'impossibilité.

## Effet

- phase, temps, plafond, candidats, rejets et nature du verdict sont
  transportés jusqu'à la palette ;
- les détails techniques restent repliés ;
- un prérequis absent devient un résultat explicable ;
- aucun algorithme de placement ou de finition ne change.

## Validation

Tests ciblés : `99/99`. Syntaxe JavaScript : `OK`.
Suite complète : `922/922` en `299.3 s`, un test SCIP natif ignoré.
Aucun benchmark ou holdout solveur invoqué.

## Suite

Après intégration, P64-L09T-C automatise les poses X/Y des réservations hautes
et certifie la paroi minimale existante.
