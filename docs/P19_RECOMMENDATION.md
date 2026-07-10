# P19 Recommendation

## Decision requested

Recommandation : `P19-BOX-FILL-MANUAL-MODULES-SPRINT` (option A).

## Why this first

Le risque principal n'est pas l'absence de widgets UI; c'est l'absence de `BoxFillPlan` executable. P19-A donne a l'utilisateur et au moteur un plan de boite complet minimal: modules manuels, positions, associations assets, reservations, collisions, volumes libres et warnings. Il fournit des fixtures et un contrat stable utilisables ensuite par palette/app, greedy et variantes.

## Scope proposed

- Entree additive CAD-agnostic pour modules manuels, positions et reservations.
- Validation Python pure des limites, collisions, couverture et volume libre.
- Rapport Markdown/JSON/CAD IR avec `BoxFillPlan` V0 explicable.
- Aucun solveur automatique, backtracking, palette, nouvelle geometrie Fusion, STL/3MF ni changement de tolerances.

## Alternatives deferred

- `P19-UX-PROTOTYPE-PERSISTENT-PALETTE-SPRINT`: deferree, car une UI sans plan de boite stabilise fabriquerait un modele parallele.
- `P19-BOX-FILL-SOLVER-V0-SPRINT`: refusee maintenant, car les contraintes, locks et layout manuel ne sont pas encore prouvables.

## Acceptance target

Une fixture avec 2-4 modules et une reservation doit produire un plan sans collision, un volume libre calcule et des erreurs actionnables pour collision, sortie de boite ou asset non couvert. Fusion ne consomme ce plan que dans une mission separee, sous gate si une nouvelle visualisation est necessaire.

## Human gate

Valider P19-A et accepter l'extension additive du modele/contrat `BoxFillPlan` avant implementation. La gate UX ADR-0036 reste ouverte pour toute palette/app.


## Outcome 2026-07-10

La gate P19-A a ete acceptee et le sprint est termine : ox_fill_plan.v0 est implemente, valide dans le moteur pur, expose dans Markdown/JSON et transporte sous metadata.box_fill_plan de la CAD IR. Le resultat ne lance aucun solveur, aucune palette/app ni materialisation Fusion. La suite recommandee est documentee dans docs/P20_RECOMMENDATION.md et reste gatee.
