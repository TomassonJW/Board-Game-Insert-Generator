# ADR-0017 - Volumetric reservation, removal and support contract

## Statut

Accepted - 2026-07-06.

## Contexte

P8-M001 a introduit une grille X/Y/Z declarative, des layers, des placements de
modules et des zones reservees/interdites. La mission P8-M002 doit enrichir ce
modele avec reservations plus explicites, ordre de retrait et surfaces de
support, sans solveur automatique et sans generation Fusion reelle.

## Options

1. Ajouter un modele de support/retrait separe au niveau racine.
2. Etendre `volumetric_grid` avec des champs additifs sur placements/zones et une
   liste `support_surfaces`.
3. Attendre le modele asset-first avant de representer ces notions.

## Decision

P8-M002 etend `volumetric_grid` de maniere additive :

- `module_placements[]` et `zones[]` peuvent porter `removal_order`,
  `access_direction` et `support_surface_id` ;
- `zones[]` ajoutent `reservation_kind` et `asset_kind` ;
- `support_surfaces[]` decrit une surface abstraite portee par `grid_floor`, un
  `module_placement` ou une `zone` ;
- les rapports et `metadata.volumetric_grid` CAD IR exposent aussi
  `removal_sequence`.

## Consequences

Le coeur Python peut expliquer une sequence de retrait et des intentions de
support sans creer de geometrie. La CAD IR reste `cad_ir.v0`, car l'extension est
metadata-only et additive. Les surfaces de support restent `abstract_only` et
`physical_validation: not_validated`.

## Alternatives refusees

- Modele racine separe : premature avant P9 asset-first.
- Solveur de support/empilement : hors perimetre P8-M002.
- Generation Fusion de surfaces ou vues : gate humaine obligatoire.

## Suivi

P9 devra relier assets plats, boards, regles et reservations. Une gate impression
reste necessaire avant de valider une portance ou une ergonomie comme confortable.