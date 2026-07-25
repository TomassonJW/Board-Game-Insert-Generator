# P64-L09R-B — Preuve du calcul minimal fiable et des budgets globaux

Date : 2026-07-25

Statut : `implemented-product`, `automated-validated`.

## Portée livrée

- Le support dur de faisabilité est de nouveau l'enveloppe extérieure XY. Les ouvertures et la matière réellement porteuse restent disponibles comme diagnostic, mais ne rejettent plus un plan dont les enveloppes se portent correctement.
- Les réservations supérieures restent transmises au solveur SCIP. Après un placement minimal complet, une compensation Z strictement nécessaire peut étendre un conteneur non fixe jusqu'au sommet uniquement s'il recouvre la réservation et si aucun corps ne se trouve au-dessus.
- Le plan minimal certifié, y compris avec plateau ou livret, est directement matérialisable. Le garde CAD accepte X/Y minimaux et seulement l'écart Z explicitement certifié comme compensation de réservation.
- L'ordre petits-dessous/grands-dessus est une préférence secondaire. Il ne devient jamais une contrainte dure et une inversion nécessaire reste admissible.
- Les cinq profils appliquent une seule deadline totale depuis l'entrée publique : Rapide 3 s, Court 10 s, Normal 20 s, Long 60 s, Approfondi 180 s. Préparation, SCIP, repli interne et première certification partagent ce budget.
- Une échéance atteinte produit `no_solution_within_budget`, jamais une preuve d'impossibilité.

## Preuves fonctionnelles

- Le cas P66 complet avec huit conteneurs et deux éléments plats produit un plan minimal `constructed`, certifié et matérialisable sans finition ; la construction CAD est `ready_for_fusion`.
- Le cas de réservation localisée précédemment borné sans solution passe à `solution_found` avec une compensation Z explicite et sans corps automatique.
- Le cas contextuel P64-V2H01 admet les plans `free_3d` et `auto` par support d'enveloppe ; le diagnostic matière reste honnêtement `unsupported`.
- Le corpus CI conserve ses cinq préfixes attendus et améliore `localized-reservation-normal` de `no_solution_within_budget` à `solution_found` sans perte fonctionnelle.
- Les tests couvrent les cinq budgets, leur monotonie, la deadline totale, le timeout honnête, les réservations SCIP, l'inversion nécessaire, le déterminisme, le garde CAD et le cas public 28x30.

## Validation

- Tests documentaires : 2/2 OK.
- Suite complète : 856/856 en 238,361 s ; un test natif ignoré sous Python 3.10.
- Compilation Python : `python -m compileall -q src tests` OK.
- Contrôles ciblés : calcul minimal, P66, CAD, SCIP, support, witness, corpus et timeout OK.
- `git diff --check` : OK.

## Limites et non-objectifs

- Aucun benchmark de performance n'a été lancé.
- Aucun package ni réglage Fusion n'a été installé ou modifié.
- Aucune observation Fusion, impression, tolérance ou valeur physique n'est validée.
- La finition séparée, les boutons visibles et la progression appartiennent respectivement à P64-L09R-C, D et E.
- La gate humaine P64-L09R-V reste inactive jusqu'à l'intégration de B à F.
