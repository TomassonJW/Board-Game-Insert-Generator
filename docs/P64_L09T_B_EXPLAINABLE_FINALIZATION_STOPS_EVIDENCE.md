# P64-L09T-B — Preuve des arrêts de finition explicables

Date : 2026-07-27.

Statut : `automated-validated`, `fusion-validated=false`,
`print-validated=false`.

## Périmètre

Cette mission explique les sorties de la finition bornée sans modifier ses
placements, ses stratégies, ses budgets ou ses paramètres physiques.

Le contrat `bgig.finalization_stop_diagnostics.v1` transporte :

- la nature du verdict ;
- la phase atteinte ;
- la raison technique stable ;
- le temps écoulé et le plafond contractuel ;
- le fait que l'arrêt précède ou atteint le plafond ;
- les nombres de candidats et de rejets ;
- les codes de rejet et compteurs techniques utiles ;
- un drapeau explicite de preuve d'impossibilité.

## Nature des verdicts

Les valeurs admises sont :

- `success` ;
- `prerequisite_missing` ;
- `certificate_rejected` ;
- `strategy_exhausted` ;
- `deadline_reached` ;
- `proven_impossible` ;
- `stale`.

Une stratégie bornée épuisée reste `inconnu, pas impossible`. Le moteur et la
palette ne peuvent employer la présentation d'impossibilité que si
`proof_of_impossibility=true`.

## Transport produit

Le même diagnostic est disponible :

1. dans `finalized_plan.last_attempt` ;
2. dans `solver_result.stop_diagnostics` lors d'un arrêt sans plan final ;
3. dans la télémétrie solveur ;
4. dans `operation_activity.result_timing` de la palette.

L'interface affiche immédiatement le titre, la phase et le temps face au
plafond. Le volet technique replié conserve la raison brute, les codes de rejet
et les compteurs.

Une demande `Finaliser` sans plan minimal courant retourne maintenant un
résultat produit structuré `prerequisite_missing` au lieu d'une erreur
générique du bridge.

## Preuves automatisées

- diagnostics unitaires et familles rectangulaire, continue, composite et
  certificat ;
- prérequis absent ;
- deadline distincte d'un arrêt précoce ;
- rejet de certificat ;
- stratégie bornée épuisée ;
- impossibilité explicitement prouvée ;
- résultat stale ;
- succès ;
- transport staged, bridge et activité ;
- garde DOM contre une impossibilité sans preuve ;
- syntaxe JavaScript embarquée validée par Node.

Résultats ciblés :

- `99/99` tests en `2.201 s` ;
- `node --check` : `OK`.

La suite complète finale passe :

- `922/922` en `299.3 s` ;
- aucun échec ni erreur ;
- un test SCIP natif ignoré sous Python 3.10 ;
- aucun benchmark ou holdout solveur invoqué.

La première exécution complète avait correctement révélé deux attentes
historiques à réaligner : la garde de pilotage attendait encore le lancement du
Goal et la fixture P66 attendait l'ancienne erreur générique de finition. Les
deux contrats couvrent maintenant l'état explicable courant.

## Frontières

- aucun benchmark ou holdout solveur lancé ;
- aucune fixture personnelle lue ou modifiée ;
- aucune installation Fusion ;
- aucune valeur physique inventée ;
- aucune promotion `fusion-validated` ou `print-validated`.
