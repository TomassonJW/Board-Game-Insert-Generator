# 2026-07-06 - P6-M003 taxonomie des encoches et aides de prise

## Mission

Formaliser les types d'encoches et aides de prise sans generer de nouvelle
geometrie Fusion.

## Changements

- Ajout d'une taxonomie CAD-agnostic des features de cavites.
- Ajout du champ optionnel `taxonomy` dans la configuration V0.
- Validation des couples `kind` / `taxonomy` incoherents.
- Enrichissement des rapports Markdown/JSON et de la CAD IR avec la taxonomie
  resolue, le profil, le statut Fusion, le fallback et `print_validated: false`.
- Documentation de `top_open_rectangular_notch`, `top_open_half_moon_notch`,
  `through_wall_window`, `blind_internal_thumb_scoop`, `side_relief_notch`,
  `dual_side_card_access` et `rounded_floor_intent`.

## Limites

- Aucune demi-lune courbe Fusion.
- Aucun scoop interne non traversant Fusion.
- Aucun fillet, conge, fond arrondi, boolean avance, STL/3MF ou module composite.
- `top_open_half_moon_notch` garde un fallback rectangulaire top-open.
- `print-validated: false` reste inchange pour toutes les aides de prise.

## Gate suivante

Toute mission de generation Fusion reelle pour demi-lune courbe, scoop interne,
fillet/conge, fond arrondi, geometrie courbe, grille 3D ou module composite doit
faire l'objet d'une nouvelle validation humaine.
