# 2026-07-03 - ADR template

## Contexte

La mission execute `P0-M005 - Stabiliser le format des ADR`. Elle prepare les
futures decisions structurantes avant les missions produit de Phase 1.

## Changements

- Ajout de `docs/DECISIONS/ADR-TEMPLATE.md`.
- Mise a jour de `docs/DECISIONS/README.md` avec les criteres minimaux ADR.
- Ajout du template ADR au controle documentaire automatise.
- Passage de `P0-M005` a `done` dans `docs/BACKLOG.md`.
- Mise a jour de `docs/NEXT_ACTIONS.md` pour recommander `P1-M001`.

## Verifications

- `$env:PYTHONPATH = "src"; python -m unittest discover -s tests` : OK, 9 tests
  passes.
- `git diff --check` : OK.

## Impact

Les prochaines decisions structurantes ont maintenant un format cible explicite.
La boucle autonome peut quitter la Phase 0 documentaire et prioriser le moteur
Python pur.

## Suivi

- Prochaine carte recommandee : `P1-M001 - Consolidate core data models`.
