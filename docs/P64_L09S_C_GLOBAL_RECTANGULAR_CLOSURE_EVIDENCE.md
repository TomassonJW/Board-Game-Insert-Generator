# P64-L09S-C - preuve de fermeture rectangulaire globale

mission: P64-L09S-C
status: implemented-and-tested
date: 2026-07-25

## Construction globale

- Partition BSP 3D bornee.
- Chaque feuille porte un proprietaire rectangulaire ou une reservation fixe.
- `partition_complete_by_construction=true`.
- `global_rectangular_partition_by_construction=true`.
- `printable_residual_volume_mm3=0`.
- Chaque corps final est possede exactement une fois.
- Les jeux deviennent des vides techniques certifies.
- Les prismes reserves sont exclus du volume imprimable.
- `composite_annexes_used=false`.

## Equilibre

- La recherche compare les partitions completes selon la dispersion du volume ajoute.
- Elle departage ensuite selon la dispersion des ratios expansion.
- Aucune baseline gloutonne complete ne constitue plus un prealable.
- `global_resolve_invocation_count=1`.

## Frontiere vers D

Un corps unique centre avec une reservation de coin ne peut pas couvrir le domaine par un seul rectangle. C retourne `global_rectangular_partition_not_found`, conserve exactement le plan minimal et ne publie aucun plan final. D couvrira ce cas par annexe XY bornee.

## Verifications

- Noyau global : 4/4.
- Bridge palette : 29/29.
- Cycle staged : 19/19.
- Fermeture locale historique : 5/5.
- Cache et invalidation : 9/9.
- CAD de partition : 14/14.
- Garde DOM et package Fusion : 41/41.
- `authorized_suite: 812/812`, 1 test natif SCIP ignore.
- 72 tests benchmark, holdout, tournament ou replay de corpus exclus selon le Goal.

## Limites

- Annexes composites : D.
- Unions CAD et encoches exactes : E.
- Aucun package Fusion installe.
- `fusion-validated=false`.
- `print-validated=false`.
