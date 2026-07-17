# P64-H06 — Placement 3D libre greedy EP/EMS

Statut : `implemented`, `automated-validated` dans le package 0.1.49.

## Objectif borné

P64-H06 livre une seconde famille interne, `free_3d_greedy`, réellement
distincte de `stage_stack`. Elle reçoit une enveloppe canonique déjà dérivée par
conteneur, place les minima en 3D libre et ne modifie ni assets, ni cavités, ni
valeurs physiques, ni tolérances, ni réservations, ni schéma projet.

Le chemin public `solve_partition_plan` reste la baseline `stage_stack`. Le
routage entre familles, le beam, les profils d'effort et `portfolio_auto`
appartiennent exclusivement à P64-H07.

## Moteur livré

`free_3d_greedy_solver.py` maintient :

- des espaces maximaux vides orthogonaux, divisés après chaque placement puis
  dédupliqués par inclusion ;
- des points extrêmes issus des faces positives placées et des origines EMS ;
- une trajectoire greedy unique et déterministe ;
- un choix « plus contraint d'abord » selon le nombre d'options courantes, les
  axes fixes, le volume minimal et l'identifiant stable ;
- les rotations globales X/Y limitées à 0/90 degrés ;
- une couverture d'appui calculée par union de rectangles, donc sans double
  comptage lorsqu'un corps supérieur repose sur plusieurs corps ;
- des bornes nécessaires simples sur le volume minimal et les axes ;
- des limites dures sur états, essais de placement, EMS et points extrêmes.

Un participant momentanément sans option n'est pas déclaré impossible tant
qu'un autre participant plaçable peut ouvrir une surface ou un espace. Un
cul-de-sac greedy ou un budget atteint produit toujours
`no_solution_within_budget`, jamais `proven_impossible`.

## Contrat et validation

La stratégie réutilise directement `SolverStrategy`, `SolverBudget`,
`SolverCandidate`, `PlacementSnapshot` et `ValidationCheck` du contrat H05.
Chaque solution géométrique repasse par
`solver_contract.validate_placement_geometry` pour la boîte, les jeux et les
collisions, puis ajoute les appuis et l'interdiction des corps automatiques.

Cette admission `bgig.free_3d_geometry_validation.v1` est volontairement
distincte du certificat produit complet
`bgig.solver_candidate_certificate.v1`. P64-H07 devra reconstruire le plan
complet, restaurer enveloppes, cavités, fonds, parois, réservations, retrait et
conservation, puis obtenir ce certificat complet avant toute exposition comme
matérialisable. Une admission H06 seule n'autorise donc ni scène ni
matérialisation.

## Budget et télémétrie

Aucun budget produit par défaut n'est créé dans H06. L'appelant doit fournir un
`SolverBudget` explicite contenant :

- `max_search_states` ;
- `max_placement_trials` ;
- `max_empty_spaces` ;
- `max_extreme_points`.

La télémétrie déterministe compte états, essais, options faisables, EMS/points
générés, dédupliqués et maximums retenus. Le benchmark automatisé initial
exécute les huit cas H06, dont les trois fixtures H04, en moins d'une seconde
sur l'environnement de développement observé ; ce fait ne devient ni SLA ni
seuil produit.

## Acceptation automatisée

- corpus H04 simple, dense H01 et réservations H02 placé avec une enveloppe
  canonique par conteneur ;
- un corps franchit un plan Z local d'un voisin sans couche globale ;
- un corps supérieur est accepté avec deux supports valides ;
- validation commune : boîte, jeux, non-collision, appui et zéro corps
  automatique ;
- EMS et points extrêmes dédupliqués ;
- digest et exécution déterministes ;
- budget dur honnête ;
- impossibilité prouvée limitée aux bornes nécessaires explicites ;
- axes `fixed` résolus sur leur cible explicite ;
- parité H05 et régressions stage-stack inchangées.

## Hors scope et limites connues

- pas de beam, retour arrière multi-états ou portefeuille Auto ;
- pas de budget Rapide/Normal/Approfondi ni réglage Fusion ;
- pas de variantes internes P45, grille dense, finition, cale ou solveur exact ;
- pas de candidat matérialisable H06 avant certification produit dans H07 ;
- le greedy reste sensible aux choix précoces : un échec est un épuisement de
  cette trajectoire, pas une preuve ;
- aucun recalibrage physique et aucune preuve Fusion ou impression nouvelle.

`fusion-validated` reste P64-H01 0.1.42. `print-validated: false`.
