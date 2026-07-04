# Log - P6-M001 cavites rectangulaires Fusion

Date : 2026-07-04

## Mission

`P6-M001 - Generer les cavites rectangulaires simples dans Fusion`.

## Gate

Gate humaine validee pour une mission unique, limitee aux cavites rectangulaires
simples. Les features ergonomiques, fonds arrondis, fillets, couvercles, exports
STL/3MF et geometries courbes restent interdits.

## Travail realise

- Ajout d'un plan hors Fusion `FusionCavityCutPlan` depuis les operations CAD IR
  `subtract_rectangular_cavity`.
- Ajout de garde-fous hors Fusion : body cible, coordonnees locales, dimensions
  positives, debordement X/Y, profondeur inferieure a la hauteur du blank et
  plancher minimal conserve.
- Ajout dans l'add-in Fusion d'une extrusion cut rectangulaire descendante limitee
  au body cible via `participantBodies`.
- Les operations `describe_cavity_feature` restent non executees.
- Documentation de la convention top-open et du smoke test manuel P6-M001.

## Validation

Les tests automatises doivent couvrir le plan de coupe et la non-execution des
features ergonomiques. La generation Fusion P6-M001 reste `manual validation
required` tant que Thomas n'a pas lance et mesure le smoke test dans Fusion.

## Suite

Prochaine action humaine : `P6-M001V - Valider manuellement les cavites
rectangulaires Fusion` avec une CAD IR issue de `examples/simple_tray.json`.
