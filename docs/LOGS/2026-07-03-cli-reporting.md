# 2026-07-03 - CLI reporting

## Contexte

La mission execute `P1-M003 - Improve CLI reporting`. Elle rend les sorties
Markdown et JSON plus utiles pour diagnostiquer une configuration, un layout et
les tolerances appliquees.

## Changements

- Ajout d'un bloc `Summary` dans le rapport Markdown.
- Ajout d'un bloc `Tolerance profile` dans le rapport Markdown.
- Enrichissement du rapport JSON avec `layout`, `defaults`, `module_requests` et
  un `summary` plus exploitable.
- Categories d'erreur CLI : configuration, validation, layout et tolerance.
- Ajout de tests unitaires pour le rapport et les erreurs CLI.
- Mise a jour du README sur le contenu des rapports.
- Passage de `P1-M003` a `done` et de `P1-M004` a `ready`.

## Verifications

- `$env:PYTHONPATH = "src"; python -m unittest discover -s tests` : OK, 23 tests
  passes.
- `$env:PYTHONPATH = "src"; python -m board_game_insert_generator
  examples\simple_box.json --format markdown` : OK, rapport Markdown genere.
- `$env:PYTHONPATH = "src"; python -m board_game_insert_generator
  examples\simple_box.json --format json` : OK, rapport JSON genere.
- `git diff --check` : OK.

## Impact

La CLI expose plus de contexte de diagnostic sans changer le calcul du moteur.
Les rapports restent une validation abstraite, pas une validation Fusion 360 ou
impression 3D.

## Suivi

- Prochaine carte recommandee : `P1-M004 - Ajouter une commande CLI de diagnostic`.
