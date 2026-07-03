# 2026-07-03 - Config loading validation

## Contexte

La mission execute `P1-M002 - Harden config loading and validation`. Elle rend
le chargement JSON plus strict avant d'ameliorer les rapports CLI.

## Changements

- Refus des champs inconnus a la racine, dans `box`, `layout`, `tolerances`,
  `defaults`, `modules[]` et les dimensions.
- Parsing explicite des champs numeriques, entiers, booleens et chaines.
- Conversion des erreurs de type en `ConfigError` actionnables.
- Ajout de tests loader pour champs inconnus et types invalides.
- Documentation des regles de validation stricte dans `docs/CONFIG_SCHEMA.md`.
- Passage de `P1-M002` a `done` et de `P1-M003` a `ready`.

## Verifications

- `$env:PYTHONPATH = "src"; python -m unittest discover -s tests` : OK, 20 tests
  passes.
- `$env:PYTHONPATH = "src"; python -m board_game_insert_generator
  examples\simple_box.json --format markdown` : OK, rapport Markdown genere.
- `git diff --check` : OK.

## Impact

Le format JSON V0 est plus previsible. Les erreurs de chargement sont maintenant
plus proches de leur champ source, ce qui prepare un reporting CLI plus clair.

## Suivi

- Prochaine carte recommandee : `P1-M003 - Improve CLI reporting`.
