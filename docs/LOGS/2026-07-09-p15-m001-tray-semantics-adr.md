# 2026-07-09 - P15-M001 tray semantics ADR

Contexte : P14 est techniquement fonctionnel mais non valide comme usable. Les modules issus de `quick_asset_box` peuvent devenir trop hauts car le sizing count-aware utilise implicitement presque toute la hauteur disponible.

Changement : ajout de `docs/DECISIONS/ADR-0033-tray-semantics-v0.md`.

Decision : conserver `z_mm` comme dimension unitaire pour tokens/dice/meeples/generic, mais introduire un defaut produit `flat_tray` avec `max_stack_height_mm`. `vertical_stack` devient explicite. La grid reste une lattice de placement/reservation, pas une taille physique de body.

Validation : mission documentaire, tests projet a lancer avant commit. Aucun changement moteur ni Fusion.
