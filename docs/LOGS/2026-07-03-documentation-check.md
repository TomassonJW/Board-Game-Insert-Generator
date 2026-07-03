# 2026-07-03 - Documentation check

## Contexte

La mission execute `P0-M002 - Ajouter une verification documentaire de base`.
Elle ajoute un garde-fou automatise pour detecter rapidement les fichiers de
pilotage critiques manquants ou les sections minimales absentes.

## Changements

- Ajout du test unitaire `tests/test_project_documents.py`.
- Verification de l'existence des fichiers critiques de pilotage.
- Verification de sections minimales dans les documents de controle projet.
- Mise a jour de `docs/QUALITY_RULES.md` pour documenter le controle automatise.
- Passage de `P0-M002` a `done` dans `docs/BACKLOG.md`.
- Mise a jour de `docs/NEXT_ACTIONS.md` pour recommander `P0-M005`.

## Verifications

- `$env:PYTHONPATH = "src"; python -m unittest discover -s tests` : OK, 9 tests
  passes.
- `$env:PYTHONPATH = "src"; python -m board_game_insert_generator
  examples\simple_box.json --format markdown` : OK, rapport Markdown genere.
- `git diff --check` : OK.

## Impact

Le depot dispose maintenant d'un controle automatise minimal du plan de pilotage.
Un futur agent ne devrait plus pouvoir supprimer ou vider un document critique
sans faire echouer la suite unitaire.

## Suivi

- Prochaine carte recommandee : `P0-M005 - Stabiliser le format des ADR`.
