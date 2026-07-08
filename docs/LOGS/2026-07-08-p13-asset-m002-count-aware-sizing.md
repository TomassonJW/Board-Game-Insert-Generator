# 2026-07-08 - P13-ASSET-M002 count-aware asset sizing

Contexte : P13-M001V a valide `quick_asset_box` comme V0 honnete mais non count-aware. Le module proxy ne devait plus suggerer une capacite non representee.

Changements :

- Sizing count-aware V0 pour `tokens`, `dice`, `meeples` et `generic`.
- `count` calcule capacite par pile, nombre de piles XY, enveloppe asset-fit et taille module.
- `cards` et `sleeved_cards` gardent `z_mm` comme hauteur totale de paquet/deck avec warning.
- Metadata additive `storage_sizing` sur candidats, modules generes et placements.
- Reporting Fusion `count_aware_storage_sizing`, diagnostics par asset/module, capacite declaree et garantie heuristique.
- Sketch Fusion debug non imprimable `asset-fit debug outline` sur les modules asset candidates.
- Script smoke quick asset prepare sur boite `130 x 50 x 60` et assets counts `40` / `23`.

Limites : pas d'assets individuels Fusion, pas de cavites/logements, pas de solveur global, pas de validation impression.

Gate suivante : `P13-ASSET-M002V` dans Fusion 360.