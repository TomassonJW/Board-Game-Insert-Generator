# 2026-07-03 - Autonomy bootstrap

## Contexte

La mission cree la couche d'autonomie operatoire du projet. L'objectif est de
permettre a Codex d'avancer ensuite mission par mission avec un maximum
d'autonomie locale, tout en respectant des gates humaines strictes.

## Changements

- Ajout du protocole d'autonomie.
- Ajout de la boucle d'execution standard.
- Ajout des gates humaines obligatoires.
- Ajout d'une matrice de validation.
- Ajout des roles logiques d'agents.
- Ajout d'un plan de sprint 2 a 4 semaines.
- Ajout d'un runbook humain.
- Mise a jour du pilotage projet pour recommander `P0-M004`.

## Verifications

- `$env:PYTHONPATH = "src"; python -m unittest discover -s tests` : OK, 7 tests
  passes.
- `$env:PYTHONPATH = "src"; python -m board_game_insert_generator
  examples\simple_box.json --format markdown` : OK, rapport Markdown genere.
- `git diff --check` : OK.

## Impact

Le depot dispose d'un plan de controle plus explicite : Codex peut selectionner
une mission `ready`, l'executer seule, tester, documenter, committer et s'arreter
si une gate humaine est rencontree.

## Suivi

- Prochaine mission recommandee : `P0-M004` - Dry-run autonomous mission
  selection.
