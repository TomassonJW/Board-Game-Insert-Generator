# Log - 2026-07-04 - P5-M004 features ergonomiques abstraites

## Mission

`P5-M004 - Decrire les encoches de doigts et fonds arrondis comme features abstraites`.

Gate humaine validee pour un perimetre strictement CAD-agnostic : aucune coupe,
boolean, extrusion cut, fillet, conge, geometrie courbe reelle ou export
imprimable Fusion 360.

## Livré

- Ajout d'un contrat `FeatureKind` et `Feature` explicite dans le coeur Python.
- Association de features ergonomiques a `Cavity`.
- Chargement JSON strict via `modules[].cavities[].features`.
- Validation des positions, tailles, rayons, statuts abstraits et limites locales
  de cavite.
- Rapports Markdown/JSON enrichis avec un compteur et une section de features.
- CAD IR enrichie avec `body.cavities[].features` et operations abstraites
  `describe_cavity_feature`.
- Exemple `examples/simple_finger_notch_tray.json`.
- ADR-0011 pour fixer la frontiere abstraite.

## Limites

- Fusion ne genere pas ces features.
- Les features ne sont pas validees par impression reelle.
- Les placements restent des conventions abstraites jusqu'a une future mission
  Fusion validee par gate.

## Gate suivante

Toute mission qui execute vraiment `subtract_rectangular_cavity` ou
`describe_cavity_feature` dans Fusion, ou qui ajoute encoche reelle, demi-lune,
fond arrondi, fillet, boolean, extrusion cut ou geometrie courbe, doit repasser
par une gate humaine dediee.
