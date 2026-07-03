# Log - P3-M003 print profiles

Date : 2026-07-03

## Mission

`P3-M003 - Ajouter des profils d'impression`

## Changement

Le JSON V0 accepte maintenant un champ racine optionnel `print_profile`.

Profils reconnus :

- `default` ;
- `pla_standard` ;
- `petg_standard` ;
- `fast_draft` ;
- `fine_detail`.

Le loader resout le profil en `ToleranceProfile`, puis applique les champs
explicites de `tolerances` comme overrides champ par champ. Les rapports
Markdown/JSON exposent le profil choisi et la table des tolerances finales.

## Limites

- Les valeurs du profil `default` restent inchangees.
- Les profils opt-in sont des points de depart experimentaux, pas une validation
  physique.
- Aucune integration Fusion 360, aucun export STL/3MF et aucune impression reelle
  ne sont inclus dans cette mission.

## Decision

ADR ajoutee : `docs/DECISIONS/ADR-0006-explicit-print-profiles.md`.

## Validation

- `python -m unittest discover -s tests` : OK, 44 tests passes.
- `python -m board_game_insert_generator examples/simple_box.json --format markdown` :
  OK, rapport Markdown genere avec profil d'impression et tolerances appliquees.
- `python -m board_game_insert_generator examples/simple_grid.json --format markdown` :
  OK, rapport Markdown genere avec profil d'impression et tolerances appliquees.
- `python -m board_game_insert_generator examples/simple_box.json --format json` :
  OK, rapport JSON genere avec profil d'impression et tolerances appliquees.
- `git diff --check` : OK.

## Suite

`P3-M004 - Ajouter un protocole de calibration physique` est la prochaine mission
recommandee. Elle doit documenter la mesure physique sans declarer les profils
valides tant qu'aucune impression reelle n'a ete effectuee.