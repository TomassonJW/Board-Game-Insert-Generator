# 2026-07-06 - P8-M001 socle de grille volumetrique 3D

## Mission

Gate humaine validee pour `P8-M001 - Specifier et implementer le socle de grille
volumetrique 3D et layers` dans le coeur Python pur, configuration, validation,
rapports et CAD IR abstraite.

## Livrables

- Bloc config optionnel `volumetric_grid`.
- Modeles Python purs pour unites de grille, layers, placements et zones.
- Validation de couverture du volume utile, spans, collisions et dimensions de
  placements.
- Exemple `examples/simple_3d_grid.json`.
- Rapports Markdown/JSON avec occupation et volume libre.
- Metadata CAD IR additive `metadata.volumetric_grid`.
- ADR-0016.

## Limites

- Aucun solveur automatique.
- Aucune generation Fusion volumetrique.
- Aucun changement des tolerances par defaut.
- Aucun export STL/3MF.
- Aucun statut `print-validated`.

## Gate suivante

Toute generation Fusion reelle basee sur la grille 3D, les layers, une vue
eclatee ou des modules multi-hauteurs reste sous gate humaine.