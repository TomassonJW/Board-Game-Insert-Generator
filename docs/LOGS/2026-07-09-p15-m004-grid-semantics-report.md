# 2026-07-09 - P15-M004 grid semantics report

Mission : `P15-M004 - Grid semantics report V0`.

Changements : metadata additive sur placements asset-first et plan Fusion pour clarifier que la grid est une lattice de placement/reservation, pas une taille physique de body. Champs ajoutes : `grid_semantics: placement_reservation_lattice_v0`, `body_snap_to_grid: no`, `grid_span_is_reserved_space: yes`, `body_size_may_be_smaller_than_grid_span: yes`.

Reporting : `quick_asset_box_summary`, `Module source mapping` et `Body sizing report` exposent la distinction entre `theoretical_grid_extent_mm` et `printable_body_size_mm`. Aucune nouvelle geometrie, aucun solveur et aucune tolerance ne sont ajoutes.
