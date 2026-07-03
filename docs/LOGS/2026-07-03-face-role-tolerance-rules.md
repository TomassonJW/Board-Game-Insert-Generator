# Log - P3-M002 face-role tolerance rules

Date : 2026-07-03

## Mission

`P3-M002 - Apply tolerance rules from face classification`

## Gate

Gate humaine `Changement du modele de tolerance` validee explicitement pour une
mission unique. Perimetre autorise : appliquer les regles de tolerance depuis les
roles de faces existants, sans changer les valeurs de tolerance par defaut, sans
Fusion 360, sans export imprimable et sans modules composites complets.

## Changement

Le moteur de tolerance transforme maintenant chaque `FaceClassification` en
`FaceToleranceApplication`.

Chaque application expose :

- face ;
- role ;
- offset applique ;
- source de tolerance ;
- identifiant de regle ;
- indicateur `receives_clearance` ;
- raison textuelle.

Regles principales :

- `peripheral` recoit `peripheral_clearance_mm + printer_compensation_mm` ;
- `neighbor` recoit `module_gap_mm / 2 + printer_compensation_mm` ;
- `exposed` ne recoit aucun jeu, seulement la compensation imprimante si elle
  existe ;
- `functional` en `z_min` ne recoit aucun jeu ;
- `functional` en `z_max` recoit `vertical_lid_clearance_mm` ;
- `internal` et `welded` ne recoivent aucun jeu.

Les rapports Markdown/JSON exposent maintenant les tolerances appliquees. Les
dimensions imprimables de `simple_box.json` et `simple_grid.json` restent
inchangees et verrouillees par tests.

## Decision

ADR ajoutee : `docs/DECISIONS/ADR-0005-face-role-tolerance-rules.md`.

## Validation

- `python -m unittest discover -s tests` : OK, 42 tests passes.
- `python -m board_game_insert_generator examples/simple_box.json --format markdown` :
  OK, rapport Markdown genere avec tolerances appliquees.
- `python -m board_game_insert_generator examples/simple_grid.json --format markdown` :
  OK, rapport Markdown genere avec tolerances appliquees.
- `python -m board_game_insert_generator examples/simple_box.json --format json` :
  OK, rapport JSON genere avec tolerances appliquees.
- `git diff --check` : OK.

## Suite

`P3-M003 - Ajouter des profils d'impression` est la prochaine mission
recommandee. Toute modification des valeurs de tolerance par defaut reste une
gate humaine separee. Les roles `internal` et `welded` sont couverts par les
regles, mais leur detection automatique dans de vrais modules composites reste
future.