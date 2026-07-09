# 2026-07-09 - P15-M002 storage_orientation flat_tray V0

Mission : `P15-M002 - storage_orientation flat_tray V0`.

Changement : le modele assets accepte `storage_orientation` (`auto`, `flat_tray`, `vertical_stack`) et `max_stack_height_mm`. Pour tokens/dice/meeples/generic, `auto` est resolu en `flat_tray`, avec defaults de hauteur de pile : tokens `12.0`, dice `20.0`, meeples `24.0`, generic `16.0`. `vertical_stack` garde l'ancien comportement base sur la hauteur disponible.

Impact produit : les petits assets itemises ne deviennent plus automatiquement des tours hautes. Le sizing count-aware cree davantage de piles XY quand le count depasse la capacite de pile bornee. Les fixtures legacy avec tokens epais declarent explicitement `vertical_stack`.

Validation automatique : tests assets cibles OK. Validation Fusion et impression non realisees.

Suite : `P15-M003` doit exposer/persister `max_stack_height_mm` et le reporting `stack_height_policy`, `xy_expansion_used`, `z_expansion_used` dans `quick_asset_box`.