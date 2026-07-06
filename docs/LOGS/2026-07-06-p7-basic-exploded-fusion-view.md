# Log - P7-M001 vue eclatee Fusion basique

Date : 2026-07-06

## Mission

`P7-M001 - Generer une vue eclatee Fusion basique`.

## Perimetre implemente

- Ajout du mode local `compact_and_exploded` par defaut.
- Ajout du repli `compact_only` via `exploded_view_mode.txt`.
- Plan hors Fusion de bodies `exploded` comme copies rectangulaires des blanks
  CAD IR et modules asset-first places.
- Placement exploded a droite de la boite avec marge et espacement fixes.
- Generation Fusion des copies rectangulaires dans le composant racine.

## Limites

- La vue compacte reste la seule a recevoir les coupes de cavites et encoches
  deja supportees.
- La vue eclatee basique ne cree pas de composants enfants, fillets, courbes,
  modules composites ou exports.
- Validation Fusion manuelle requise.
- `print-validated: false`.

## Gate suivante

Stop pour smoke test humain Fusion P7-M001V avant toute vue eclatee avancee,
export, module composite, solveur plus automatique ou geometrie supplementaire.
