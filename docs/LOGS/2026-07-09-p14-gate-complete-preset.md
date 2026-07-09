# 2026-07-09 - P14 gate smoke preset correction

Contexte : `P14-USABLE-ASSET-TRAY-SPRINT-V` n'est pas invalidee cote generation. Le smoke prepare apres `3062443` utilisait le preset `tokens`, trop proche du scenario P13-ASSET-M005 pour valider les apports P14.

Correction : ajout du preset `p14_complete` et passage du script `scripts/fusion/prepare_quick_asset_test.ps1` sur ce preset par defaut.

Scenario gate : box `220 x 160 x 96`, grid `8 x 5 x 4`, assets `coin-tokens,tokens,36,18,16,2,loose; status-tokens,tokens,24,12,18,2,loose; damage-tokens,tokens,18,20,20,2,loose; dice-set,dice,12,16,16,16,loose; wood-meeples,meeples,20,12,12,18,loose`.

Objectif de validation Fusion : 5 assets lus, 3 candidats/modules asset-first, groupe tokens a 3 compartiments avec `deterministic_shelf_by_source_asset_v0`, printability report V0, aide inline quick_asset_box, presets de preparation, regenerate sans doublon et clear preserve non-BGIG. Impression 3D non validee.
