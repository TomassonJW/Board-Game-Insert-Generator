# 2026-07-09 - P14-USABLE-ASSET-TRAY-M001 layout multi-assets

Mission interne 1 du sprint `P14-USABLE-ASSET-TRAY-SPRINT`.

Preflight post-crash : `main` propre et aligne avec `origin/main`, `HEAD` attendu `8fd1b7a`, `P13-ASSET-M005V` enregistree comme `fusion-validated-v0`, `print-validated: false`, gate P13-M006 levee par decision utilisateur explicite de lancer P14.

Changement : le moteur de compartiments asset-specific essaie maintenant row, column, puis shelf layout deterministe. Les cas multi-assets compatibles peuvent creer 3 ou 4 compartiments dans un module count-aware unique avec parois internes reportees.

Refus : si aucun layout ne tient, `ASSET_COMPARTMENTS_DO_NOT_FIT` documente les tentatives. Le fallback vers une cavite globale est supprime quand les compartiments requis sont refuses.

Validation automatique : nouveaux tests assets pour 3 assets, 4 assets et rejet explicite ; suite unittest complete OK avant commit. Validation Fusion et impression restent non realisees.