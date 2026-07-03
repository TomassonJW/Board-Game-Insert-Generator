# 2026-07-03 - Core model contract

## Contexte

La mission execute `P1-M001 - Consolidate core data models`. Elle consolide le
contrat interne des dataclasses avant le durcissement du loader et de la
validation.

## Changements

- Ajout de `tests/test_model_contract.py`.
- Tests de contrat pour configuration valide, dimensions invalides, hauteur
  utile incoherente, ids dupliques, quantites invalides et tolerances negatives.
- Test de distinction entre `Cell` theorique et `PrintableBody` imprimable.
- Documentation dans `docs/GEOMETRY_MODEL.md` du role des dataclasses comme
  objets de valeur legers en millimetres.
- Passage de `P1-M001` a `done` et de `P1-M002` a `ready`.

## Verifications

- `$env:PYTHONPATH = "src"; python -m unittest discover -s tests` : OK, 14 tests
  passes.
- `$env:PYTHONPATH = "src"; python -m board_game_insert_generator
  examples\simple_box.json --format markdown` : OK, rapport Markdown genere.
- `git diff --check` : OK.

## Impact

Le contrat Phase 1 des modeles est explicite sans changer l'API publique ni
introduire de validation dans tous les constructeurs. La prochaine mission peut
durcir le chargement JSON et les messages d'erreur.

## Suivi

- Prochaine carte recommandee : `P1-M002 - Harden config loading and validation`.
