# 2026-07-09 - P14-USABLE-ASSET-TRAY-M004 quick_asset_box presets

Mission : rendre la preparation des smoke tests `quick_asset_box` plus rapide avec des scenarios V0 sans ajouter de palette ni de nouvelle geometrie.

Changement : ajout du catalogue `scripts/fusion/quick_asset_presets.json` et du parametre `-Preset` dans `scripts/fusion/prepare_quick_asset_test.ps1`.

Presets : `tokens` conserve le cas P13/P14 existant, `dice_meeples_generic` couvre des objets mixtes simples, `cards_tokens` documente la semantique cartes ou `z_mm` est une hauteur totale de deck.

Validation : presets verifies par test automatise via parsing `quick_asset_box` et generation de config temporaire. Validation Fusion sprint P14 encore requise. Impression 3D non validee.
