# 2026-07-09 - P13-ASSET-M005 per-compartment access notches V0

Contexte : P13-ASSET-M004V a valide les compartiments asset-specific. La gate produit M005 autorise une premiere ergonomie d'acces simple, sans courbes, scoops, fillets, solveur global ni export imprimable.

Changements :

- Nouvelle policy `per_compartment_top_open_rectangular_notch_v0`.
- Chaque compartiment asset-specific peut porter `asset_access_notch` avec asset id, compartment id, mur cible, position, largeur, profondeur depuis le haut, bbox de coupe et raison de generation/refus.
- Regle conservatrice : encoche seulement sur le mur avant externe, refusee si le compartiment n'est pas adjacent, trop etroit ou trop bas.
- Fusion convertit les notches planifiees en `FusionFingerNotchCutPlan` avec `source_feature_kind = asset_access_notch` et reutilise la coupe rectangulaire top-open existante.
- Reporting quick_asset_box et message Fusion ajoutent les compteurs `asset_access_*`.

Validation : suite unitaire complete OK pendant implementation. Validation Fusion humaine `P13-ASSET-M005V` requise avant de marquer fusion-validated. `print-validated: false`.