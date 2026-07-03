# 2026-07-03 - CLI diagnose

## Contexte

La mission execute `P1-M004 - Ajouter une commande CLI de diagnostic`. Elle
fournit une boucle courte pour verifier chargement de config, layout et
generation des rapports.

## Changements

- Ajout de la commande `diagnose` a la CLI existante.
- Conservation de l'usage historique `python -m board_game_insert_generator
  <config> --format markdown|json`.
- Diagnostic texte avec config chargee, strategie de layout, modules demandes,
  instances generees, corps imprimables, warnings et generation des rapports.
- Test CLI dedie pour le diagnostic OK.
- Documentation de la commande dans `README.md`.
- Passage de `P1-M004` a `done` et de `P2-M001` a `ready`.

## Verifications

- `$env:PYTHONPATH = "src"; python -m unittest discover -s tests` : OK, 24 tests
  passes.
- `$env:PYTHONPATH = "src"; python -m board_game_insert_generator diagnose
  examples\simple_box.json` : OK, diagnostic genere.
- `$env:PYTHONPATH = "src"; python -m board_game_insert_generator
  examples\simple_box.json --format markdown` : OK, rapport Markdown genere.
- `$env:PYTHONPATH = "src"; python -m board_game_insert_generator
  examples\simple_box.json --format json` : OK, rapport JSON genere.
- `git diff --check` : OK.

## Impact

Un utilisateur ou un agent peut maintenant verifier rapidement une configuration
sans inspecter manuellement un rapport complet. Cette verification reste
abstraite et ne valide ni Fusion 360 ni l'impression 3D.

## Suivi

- Prochaine carte recommandee : `P2-M001 - Formalize simple rectangular layout model`.
