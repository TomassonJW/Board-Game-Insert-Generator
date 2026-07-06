# 2026-07-06 - P10-M002 deterministic variant comparison

## Mission

Implementer `P10-M002 - Enumerer quelques variantes simples hors solveur complet`.

## Livrables

- `variant_comparison` dans les rapports JSON.
- Section Markdown `Variant comparison`.
- Sous-scores explicables : compacite, accessibilite, reservations, simplicite
  d'impression, setup et confiance de mesure.
- Tests unitaires.

## Limites

- Compare seulement `row_fill` et `grid`, deja implementes.
- Aucun nouveau placement automatique.
- Aucun optimiseur global.
- Aucune generation Fusion.