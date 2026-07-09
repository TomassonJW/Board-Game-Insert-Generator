# P17 Preprint Check Protocol V0

## Objectif

Ce protocole prepare une premiere session preprint apres `export_printables`. Il ne cree pas de nouveau coupon Fusion et ne valide pas l'impression. Il encadre la collecte d'informations necessaires pour passer plus tard de `print_validated: false` a une validation physique locale documentee.

## Entrees requises

- Dossier export BGIG cree par `export_printables`.
- `bgig_export_manifest.json`.
- `bgig_export_manifest.md`.
- Fichiers STL exportes.
- Profil logiciel affiche par BGIG.
- Imprimante, filament, buse, hauteur de couche, slicer et profil slicer.

## Verification avant slicing

1. Ouvrir `bgig_export_manifest.json`.
2. Verifier `print_validated: false`.
3. Verifier `printability_validated_by_print: no`.
4. Verifier que `printability_export_allowed` n'est pas `false` pour le module vise.
5. Relever les `issues[]` et warnings printability.
6. Verifier que seuls les fichiers STL attendus sont presents.
7. Refuser la session si le manifeste signale un blocker non traite.

## Verification slicer

Pour chaque STL :

- importer sans reparation automatique silencieuse ;
- noter l'orientation ;
- noter temps estime, masse, couches, supports eventuels ;
- verifier visuellement murs, fond, cavites, encoches et parois internes ;
- ne pas modifier les tolerances logiciel dans le slicer sans noter l'override.

## Mesures apres impression

Mesurer au minimum :

- dimensions externes X/Y/Z du module ;
- epaisseur de mur externe la plus faible ;
- epaisseur de paroi interne la plus faible ;
- fond conserve ;
- largeur/profondeur des cavites principales ;
- largeur/profondeur des encoches ;
- insertion/retrait de chaque type d'asset teste.

## Statuts autorises

- `not_printed` : export prepare, aucune impression.
- `printed_unmeasured` : impression faite, mesures absentes.
- `measured_local_ok` : mesures locales OK pour ce couple imprimante/profil.
- `measured_local_ko` : au moins un point bloquant observe.
- `retest_required` : mesure ambigue ou protocole incomplet.

Aucun de ces statuts ne modifie les valeurs par defaut sans gate humaine separee.
