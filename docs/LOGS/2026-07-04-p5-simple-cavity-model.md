# 2026-07-04 - P5-M001 cavites simples abstraites

## Mission

`P5-M001 - Modeliser les cavites simples`.

## Contexte

La gate humaine du 2026-07-04 autorise la vague P5 cote moteur Python pur,
configuration, rapports et CAD IR. Elle n'autorise pas les coupes Fusion reelles.

## Resultat

- `modules[].cavities` est accepte dans le JSON V0.
- Une cavite simple porte id, type fonctionnel, origine locale, taille, clearance
  et commentaire.
- La validation refuse les cavites hors enveloppe, les parois X/Y trop fines, les
  fonds trop fins, les dimensions invalides et les clearances negatives.
- Les rapports Markdown/JSON exposent les cavites planifiees.
- La CAD IR ajoute `body.cavities` et l'operation abstraite
  `subtract_rectangular_cavity`.
- L'add-in Fusion reste limite aux blanks : les cavites sont `abstract_only` et
  `fusion_generation: not_implemented`.

## Validation attendue

Tests automatises et exports CLI. Aucune validation Fusion ou impression n'est
revendiquee pour les cavites.

## Gate suivante

Toute execution de cavite dans Fusion par sketch, extrusion cut ou boolean reste
soumise a une nouvelle gate humaine.