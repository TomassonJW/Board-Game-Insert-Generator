# 2026-07-03 - Governance bootstrap

## Contexte

Le depot disposait deja d'un moteur Python experimental et de quelques documents
de conception, mais pas encore d'un systeme complet permettant a Codex de
travailler mission par mission avec statut, backlog, ADR, logs et templates.

## Changements

- Ajout de `AGENTS.md` comme protocole racine pour les agents.
- Ajout d'une specification produit et d'une roadmap phasee de 0 a 10.
- Ajout d'un backlog actionnable par missions courtes.
- Ajout de `docs/STATUS.md` et `docs/NEXT_ACTIONS.md`.
- Ajout des index `docs/DECISIONS/README.md` et `docs/LOGS/README.md`.
- Ajout d'une ADR sur la documentation comme plan de controle projet.
- Ajout de templates GitHub pour missions, bugs, decisions et pull requests.

## Verifications

Verifications lancees pendant la mission :

```powershell
$env:PYTHONPATH = "src"
python -m unittest discover -s tests
python -m board_game_insert_generator examples/simple_box.json --format markdown
```

Resultat :

- suite unitaire : OK, 7 tests passes ;
- exemple CLI : OK, rapport Markdown genere ;
- `git diff --check` : OK sur le diff suivi avant staging.

## Impact

Le prochain agent doit commencer par lire `AGENTS.md`, `docs/STATUS.md`,
`docs/ROADMAP.md`, `docs/BACKLOG.md` et `docs/NEXT_ACTIONS.md`. Le projet peut
maintenant avancer par petites missions documentees, testees et commitees.

## Suivi

- Prochaine mission recommandee : `P0-M002 - Ajouter une verification
  documentaire de base`.
