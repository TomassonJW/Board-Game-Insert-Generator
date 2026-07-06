# 2026-07-06 - P8-M002 reservation, removal and support abstractions

## Mission

Implementer `P8-M002 - Approfondir reservations, ordre de retrait et surfaces de
support abstraites` dans le coeur Python pur.

## Livrables

- Extension additive de `volumetric_grid` avec `support_surfaces`,
  `removal_order`, `access_direction`, `reservation_kind`, `asset_kind` et
  `support_surface_id`.
- Validation des references, directions d'acces, ordres de retrait et surfaces
  bornees dans la grille.
- Rapports Markdown/JSON enrichis avec surfaces de support et sequence de retrait.
- CAD IR enrichie via `metadata.volumetric_grid`, sans nouvelle operation Fusion.
- Exemple `examples/simple_3d_reservations.json`.
- ADR-0017.

## Limites

- Aucun solveur automatique.
- Aucune generation Fusion nouvelle.
- Aucun support physique valide par impression.
- Les assets restent encore implicites ; P9 doit les modeliser explicitement.

## Validation attendue

Tests unitaires, CLI Markdown/JSON/export CAD IR sur les exemples existants et le
nouvel exemple, `git diff --check`, absence de `adsk` dans le coeur Python.