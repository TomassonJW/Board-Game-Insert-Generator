# Log - P2-M004 layout comparison

Date : 2026-07-03

## Mission

`P2-M004 - Exporter un resume de layout comparatif`

## Changement

Les rapports Markdown et JSON exposent maintenant une comparaison simple des
strategies de layout implementees.

Champs compares :

- strategie ;
- statut ;
- empreinte de layout ;
- occupation XY de la boite ;
- nombre de warnings ;
- score simple.

Le score privilegie une empreinte XY plus compacte et moins de warnings. Il est
documente comme indicateur basique, pas comme preuve d'optimisation globale.

## Validation

- `python -m unittest discover -s tests` : OK, 34 tests passes.
- `python -m board_game_insert_generator examples/simple_box.json --format markdown` :
  OK, rapport Markdown genere.
- `python -m board_game_insert_generator examples/simple_grid.json --format markdown` :
  OK, rapport Markdown genere.
- `python -m board_game_insert_generator examples/simple_box.json --format json` :
  OK, rapport JSON genere.
- `git diff --check` : OK.

## Gate suivante

`P3-M001 - Classify exposed, internal and functional faces` touche au modele de
tolerance. La gate humaine `Changement du modele de tolerance` doit etre validee
avant execution.
