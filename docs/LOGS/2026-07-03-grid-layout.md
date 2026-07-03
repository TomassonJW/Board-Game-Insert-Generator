# Log - P2-M003 grid layout

Date : 2026-07-03

## Mission

`P2-M003 - Ajouter une strategie grille explicite`

## Changement

La strategie `grid` est maintenant executable dans le moteur Python pur.

Contrat implemente :

- les instances sont triees comme `row_fill` : priorite descendante puis ordre
  source ;
- la cellule reguliere XY est calculee depuis la plus grande empreinte de module
  orientee ;
- les instances sont placees ligne par ligne dans cette grille ;
- la configuration est refusee si les cellules regulieres depassent la profondeur
  disponible de la boite ;
- `columns` reste reserve et non executable.

Un exemple reproductible est ajoute dans `examples/simple_grid.json`.

## Validation

- `python -m unittest discover -s tests` : OK, 34 tests passes.
- `python -m board_game_insert_generator examples/simple_box.json --format markdown` :
  OK, rapport Markdown genere.
- `python -m board_game_insert_generator examples/simple_grid.json --format markdown` :
  OK, rapport Markdown genere.
- `git diff --check` : OK.

## Suite

La prochaine mission recommandee est `P2-M004 - Exporter un resume de layout
comparatif`.
