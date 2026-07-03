# Log - P3-M001 face classification

Date : 2026-07-03

## Mission

`P3-M001 - Classify exposed, internal and functional faces`

## Gate

Gate humaine `Changement du modele de tolerance` validee avec autorisation
limitee : preparation de la classification dans le coeur Python pur, sans
modification des valeurs de tolerance par defaut et sans changement des dimensions
imprimables des exemples existants.

## Changement

Le moteur represente maintenant explicitement les faces rectangulaires simples :

- noms de faces : `x_min`, `x_max`, `y_min`, `y_max`, `z_min`, `z_max` ;
- roles : `peripheral`, `neighbor`, `exposed`, `functional`, `internal`,
  `welded` ;
- raison textuelle de classification ;
- voisin touche quand une face est classee `neighbor`.

Les classifications sont attachees aux `PrintableBody` et exposees comme
metadonnees dans les rapports Markdown/JSON. Le calcul d'offsets reste
numeriquement equivalent aux versions precedentes.

## Validation

- `python -m unittest discover -s tests` : OK, 40 tests passes.
- Les exemples `simple_box.json` et `simple_grid.json` gardent leurs dimensions
  imprimables attendues par tests unitaires.
- `python -m board_game_insert_generator examples/simple_box.json --format markdown` :
  OK, rapport Markdown genere avec classifications de faces.
- `python -m board_game_insert_generator examples/simple_grid.json --format markdown` :
  OK, rapport Markdown genere avec classifications de faces.
- `python -m board_game_insert_generator examples/simple_box.json --format json` :
  OK, rapport JSON genere avec classifications de faces.
- `git diff --check` : OK.

## Suite

`P3-M002 - Apply tolerance rules from face classification` necessite une nouvelle
gate humaine si la mission modifie le calcul dimensionnel des offsets ou les
valeurs de tolerance appliquees.
