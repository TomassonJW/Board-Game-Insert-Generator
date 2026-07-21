# 2026-07-21 — P64-L03R-C matérialisation duale

## Mission

Brancher le `minimal_layout` certifié de L03R-B sur le cycle staged, la CAD IR et
la scène Fusion sans ouvrir une méthode de finition, modifier le solveur public
ou distribuer le résiduel.

## Changements

- calcul global staged redirigé vers `solve_minimal_layout` et les digests L01/L02 ;
- artefacts `minimal_layout` et `finalized_plan` distincts et sélectionnables ;
- matérialisation minimale autorisée avant toute finalisation ;
- CAD IR construite depuis l'artefact exact, avec digest de géométrie revalidé ;
- identité de scène complète et comparaison stricte ;
- remplacement borné à une scène BGIG possédée, refus fail-closed des ambiguïtés ;
- UX à deux branches, avec `Mettre à jour la scène` après recalcul ;
- package de gate corrective porté à 0.1.57.

## Preuve

La preuve détaillée est
`docs/P64_L03R_C_DUAL_MATERIALIZATION_EVIDENCE.md`. Les fixtures 11 à 18 et les
tests cœur/CAD/bridge/DOM/registre sont automatisés. La suite complète et les
contrôles statiques sont exécutés avant intégration.

## Frontières préservées

Aucune méthode de finition réelle, cale, réserve utile, modification P45,
valeur physique, tolérance, default, schéma projet ou nouveau résultat dense.
Le cas 11 × 34 reste `no_solution_within_budget`.
La fixture P66 historique à huit bacs avec réservations hautes échoue aussi
honnêtement sur le chemin minimal Normal (`TOP_INSET_WITHOUT_SUPPORTING_BODY`)
et n'émet aucune CAD ; C ne modifie pas le solveur pour contourner ce certificat.

`fusion-validated: false`, `print-validated: false`.

## Suite

P64-L03R-V devient la gate humaine active sur Fusion 0.1.57. P64-F01A02 reste
verrouillé jusqu'à un retour positif et ses autres dépendances.
