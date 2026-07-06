# 2026-07-06 - P11-M002 Fusion multi-layer grid scene

## Mission

Coder `P11-M002 - Generer une scene Fusion multi-layer depuis placements grille X/Y/Z`.

## Livrables

- Exemple `examples/simple_multilayer_grid_scene.json`.
- Plan asset-first avec un module bas `3 x 3 x 1` a `origin_units (1, 0, 0)`.
- Plan asset-first avec un module plus haut `2 x 2 x 2` a `origin_units (0, 0, 1)`.
- Compteurs `multi_layer_module_count`, `z_placed_module_count` et `height_variant_count` dans les rapports JSON/Markdown.
- Transport hors Fusion de `grid_origin_units` et `grid_size_units` sur les blanks generes par grille.
- Message Fusion enrichi avec modules multi-layer, modules avec placement Z et variantes de hauteur.
- Tests hors Fusion pour plan, export CAD IR et occurrences compactes/eclatees liees.

## Limites

- Generation codee mais non encore validee manuellement dans Fusion.
- Fusion consomme la CAD IR et ne recalcule ni solveur, ni tolerance, ni support.
- Pas de modules composites, fillets, geometrie courbe ou export STL/3MF.
- Aucune validation d'impression 3D ou de portance.