# 2026-07-09 - P16-M002 flat_tray_2d engine

P16-M002 implemente le packing 2D local des piles pour `flat_tray`.

Changements : remplacement du row packing interne par `flat_tray_2d_v0`, diagnostics `tray_packing_policy`, `pile_grid_columns`, `pile_grid_rows`, `target_aspect_ratio`, `max_module_length_mm`, `linear_layout_avoided`, propagation aux compartiments et diagnostics asset.

Exemples verifies par tests : 30 tokens en `3 x 2`, override `max_stack_height_mm = 6` en `5 x 3`, 8 des en `4 x 2`, 12 piles de cubes en `4 x 3`. `vertical_stack` conserve le comportement lineaire legacy.

Limites : pas de solveur global, pas de backtracking, pas de cavites par item/pile, pas de validation Fusion ou impression dans cette mission.
