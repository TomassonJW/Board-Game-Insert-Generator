# P64-L09U-R8-C — preuve de frontière minimale soustractive

Date : 2026-07-28.

Statut : `automated-validated`, `P64-L09U-R8-C-done`,
`P64-L09U-R8-D-ready`, `fusion-validated=false`,
`print-validated=false`.

## Résultat

Le calcul minimal publie maintenant
`bgig.minimal_flat_geometry_certificate.v1`.

Le certificat prouve :

```text
flat_positive_body_count = 0
flat_positive_union_count = 0
flat_positive_volume_mm3 = 0
positive_geometry_operation_count = 0
reservation_required_z_compensation_count = 0
support_count = 0
cut_count = 0
```

Tous les prismes réservés restent `printable=false`. Le plan minimal transporte
uniquement les poses, enveloppes, ordres, régions locales et volumes réservés.

Le certificat est présent :

- dans `top_inset_reservations` ;
- dans l'artefact `minimal_layout` ;
- dans le résumé et les invariants ;
- dans le certificat produit global par le contrôle
  `minimal_flat_geometry_strictly_non_positive`.

## Rejet de l'ancien contrat

Une `reservation_required_z_compensation_mm` positive bloque maintenant le
plan minimal avec :

```text
MINIMAL_FLAT_POSITIVE_Z_COMPENSATION_FORBIDDEN
```

La régression force un allongement de `6,8 mm` sur une enveloppe
`23,2 × 23,2 mm`. Le certificat mesure exactement :

```text
23,2 × 23,2 × 6,8 = 3 660,032 mm³
```

Le plan est rejeté au lieu de présenter cette matière comme un support ou une
simple métadonnée.

## Identité

La version du solveur minimal devient :

```text
p64-l09u-r8-c-v1
```

Ce changement invalide les artefacts dérivés sous l'ancien contrat sans
modifier la recherche, ses lanes, ses budgets ou ses critères.

## Fichiers produit

- `src/board_game_insert_generator/top_inset_reservation.py`
- `src/board_game_insert_generator/partition_solver.py`
- `src/board_game_insert_generator/free_3d_plan_adapter.py`
- `src/board_game_insert_generator/solver_contract.py`
- `src/board_game_insert_generator/minimal_layout_solver.py`

## Régressions

- réservation supérieure : `27/27` ;
- solveur minimal : `17/17` ;
- certificat commun : `6/6` ;
- solveur de partition : `17/17` ;
- total ciblé : `67/67` ;
- compilation Python : OK ;
- `git diff --check` : OK.

Aucun benchmark, holdout, corpus ou tournoi n'a été importé ou exécuté.

## Données personnelles

Les projets personnels n'ont pas été sauvegardés, normalisés ni versionnés.
Leurs SHA-256 restent :

- `CasLimite02+` :
  `5E84FE6F5C0B3E5F046201D442C414504DD95D4DB8E711169A2624485466D7DC`
- `CasLimite02++` :
  `83E9E90A6BFD86B18D3A157077A0E63DC2F543DDAB626ADB2151E269E01D9743`

## Limite et suite

R8-C ne change volontairement ni la finalisation, ni la CAD IR, ni Fusion.
R8-D doit maintenant remplacer le couple ambigu
`final_size_mm` / `cad_size_mm` par la géométrie positive explicite et figée
des conteneurs finalisés.

Décision :
`docs/DECISIONS/ADR-0105-conteneurs-finalises-et-encastrements-strictement-soustractifs.md`.
