# 2026-07-06 - P6-M002 Fusion simple finger notch cuts

## Contexte

La validation humaine P6-M001V confirme que les cavites rectangulaires simples
sont visibles et mesurees correctement dans Fusion pour `examples/simple_tray.json`.
L'impression 3D reste non validee.

La gate P6-M002 autorise uniquement les encoches de doigts simples en Fusion,
sans fonds arrondis, fillets, booleans complexes, geometrie courbe reelle,
couvercles, exports STL/3MF ou recalcul metier dans Fusion.

## Travail realise

- Ajout d'un plan hors Fusion `FusionFingerNotchCutPlan`.
- Consommation des operations CAD IR `describe_cavity_feature` pour les encoches
  simples de paroi.
- Mapping des kinds `finger_notch`, `side_notch`, `center_notch` et
  `half_moon_notch` vers une coupe rectangulaire de bounding box.
- Conservation de `rounded_floor` comme intention non executee.
- Ajout de garde-fous hors Fusion : cavite inconnue, placement unsupported,
  debordement de cavite, hauteur excessive et epaisseur de paroi insuffisante.
- Ajout de l'execution Fusion par sketch XZ/YZ + `CutFeatureOperation` limite au
  body cible via `participantBodies`.
- Correctif apres premier KO partiel P6-M002V : conversion `modelToSketchSpace`
  pour les plans non XY, paroi/direction de cut explicites et compteurs
  planned/sketch/cut.
- Correctif apres second KO partiel P6-M002V : profil top-open qui depasse le
  haut du body pour eviter une fenetre fermee dans la paroi.
- Documentation de la procedure de smoke test manuel P6-M002.

## Statut de validation

- Code et tests hors Fusion : OK, 101 tests unitaires passes et CLI/export CAD IR valides.
- Validation Fusion manuelle : requise pour P6-M002V apres correction des KO partiels.
- Validation impression 3D : non realisee.

## Limites

Une `half_moon_notch` n'est pas encore une demi-lune courbe dans Fusion. P6-M002
cree uniquement une coupe rectangulaire de paroi top-open correspondant a sa bounding box.
Toute generation de courbe, fond arrondi ou fillet necessite une nouvelle gate
humaine.
