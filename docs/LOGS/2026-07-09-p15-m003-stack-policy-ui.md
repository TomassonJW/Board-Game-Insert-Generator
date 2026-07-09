# 2026-07-09 - P15-M003 stack policy UI

Mission : `P15-M003 - max_stack_height_mm et reporting stack policy`.

Changements : ajout d'un champ Fusion classique optionnel `Max stack height mm (quick_asset_box, optional)`, persistance `quick_asset_box_max_stack_height_mm`, application a la config temporaire `quick_asset_box` via `assets[].max_stack_height_mm`, et reporting explicite `storage_orientation`, `stack_height_policy`, `max_stack_height_mm`, `stack_height_used_mm`, `xy_expansion_used`, `z_expansion_used`.

Validation automatique ciblee : tests Fusion skeleton pour rehydratation settings, sauvegarde, override `6 mm`, regression constantes UI et resume stack policy. Validation Fusion P15 reste a preparer en fin de sprint.
