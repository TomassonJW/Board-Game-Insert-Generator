# 2026-07-08 - P13-M001 quick_asset_box UI V0

Mission : implementer le premier input asset-first depuis la commande Fusion.

Changements :

- Nouveau mode `quick_asset_box` distinct de `cad_ir_file`, `config_file` et `quick_parametric_box`.
- Champ UI editable `Assets (quick_asset_box)` persiste dans `bgig_ui_settings.json`.
- Format V0 : `asset_id,type,count,x_mm,y_mm,z_mm,fit`, separe par `;` ou saut de ligne.
- Types V0 : `tokens`, `dice`, `meeples`, `cards`, `sleeved_cards`, `generic`.
- Generation d'une config temporaire stricte et reuse du pipeline assets existant.
- Metadata CAD IR additive `metadata.quick_asset_box` pour le rapport Fusion.
- Script `scripts/fusion/prepare_quick_asset_test.ps1` pour preparer l'addin et les settings P13.

Limites : pas de palette HTML, pas de tableau assets avance, pas de solveur complexe, pas de geometrie Fusion nouvelle, pas d'export STL/3MF, pas de validation d'impression.

Statut : `implemented-fusion`. Gate humaine `P13-M001V` active.
