# 2026-07-25 — Préparation du Goal P64-L09S

## Contexte

La gate P64-L09R-V sur 0.1.65 est KO. Le calcul avec plateau allonge un petit
conteneur de 6,8 mm afin d'en faire un support à 0,75 % de couverture. La
finalisation laisse un résiduel important et l'interface annonce pourtant un
succès.

## Décision

- proposer ADR-0089 ;
- ne plus créer de support de plateau pendant le calcul minimal ;
- conserver SCIP pour la faisabilité 3D complexe ;
- remplacer la fermeture gloutonne comme autorité par une partition globale
  exacte et équilibrée ;
- autoriser en repli des annexes XY soudées, bornées et certifiées ;
- rendre les résultats UI strictement fidèles ;
- préparer un Goal P64-L09S en six lots automatisés puis une gate Fusion.

## Effet

- P64-L09R-V devient `human-KO`, non acceptée ;
- P64-L09S est `ready-for-user-goal-launch` ;
- aucune modification runtime, benchmark, installation Fusion, tolérance ou
  valeur physique n'est réalisée par cette préparation ;
- le lancement explicite du Goal par Thomas acceptera ADR-0089 ;
- aucune intervention humaine ne sera requise entre A et F ;
- P64-L09S-V restera obligatoire.

## Validation

- garde documentaire : 2/2 ;
- garde de recette L09R-F mise à jour : 6/6 ;
- suite complète : 875/875 en 287,519 s, un test natif SCIP ignoré sous Python 3.10 ;
- `git diff --check` : OK ;
- aucun benchmark, holdout, package ou test Fusion exécuté.
