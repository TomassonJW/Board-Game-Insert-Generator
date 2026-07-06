# 2026-07-06 - P6-M002V KO partiel et correction encoche Fusion

## Retour de validation humaine

Thomas a teste l'add-in avec une CAD IR issue de
`examples/simple_finger_notch_tray.json`.

Resultat observe :

- add-in lance : OK ;
- CAD IR chargee : OK ;
- blank genere : OK ;
- cavite rectangulaire generee : OK ;
- body visible : OK ;
- geometrie liee a l'encoche visible : oui, mais seulement comme sketch 2D
  place incorrectement ;
- aucune coupe volumique d'encoche visible dans une paroi ;
- `front-half-moon-notch` non validee.

## Diagnostic

Le plan d'encoche etait bien cree hors Fusion, mais l'esquisse Fusion etait
construite sur un plan XZ avec des points traites comme des coordonnees de
sketch. Sur un plan non XY, les points modele doivent etre convertis vers
l'espace du sketch avant `addTwoPointRectangle`.

## Correction

- Le plan hors Fusion transporte maintenant explicitement la paroi cible, le
  plan de sketch, l'offset de plan, la direction d'extrusion, la profondeur et
  les deux points modele du profil.
- L'add-in convertit les points modele en points de sketch via
  `modelToSketchSpace`.
- Les messages Fusion distinguent features d'encoche planifiees, sketches crees
  et cuts executes.
- Les tests hors Fusion verrouillent les orientations `front`, `back`, `left` et
  `right`.

## Statut

Correction codee et testee hors Fusion : 101 tests unitaires passent, CLI et
export CAD IR passent sur `simple_tray` et `simple_finger_notch_tray`. Nouveau
smoke test manuel Fusion requis pour verifier qu'une vraie coupe volumique
apparait dans la paroi du tray.

`print-validated: false` reste inchangé.
