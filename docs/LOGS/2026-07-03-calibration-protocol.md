# Log - P3-M004 calibration protocol

Date : 2026-07-03

## Mission

`P3-M004 - Ajouter un protocole de calibration physique`

## Changement

Ajout de `docs/CALIBRATION_PROTOCOL.md`.

Le protocole definit :

- preconditions de session de calibration ;
- coupons a preparer ;
- champs de tolerance concernes ;
- tableau de resultats ;
- regles d'interpretation ;
- sortie attendue d'une session ;
- gates futures preparees.

Le document est reference depuis les regles qualite, le modele de tolerance et le
README. Le garde-fou documentaire verifie son existence et ses sections
principales.

## Limites

- Aucun coupon imprimable n'est genere par le moteur actuel.
- Aucun STL/3MF et aucune integration Fusion 360 ne sont ajoutes.
- Aucune impression reelle n'a ete effectuee.
- Aucune valeur de tolerance par defaut n'est modifiee.

## Validation

- `python -m unittest discover -s tests` : OK, 44 tests passes.
- `python -m board_game_insert_generator examples/simple_box.json --format markdown` :
  OK, rapport Markdown genere.
- `git diff --check` : OK.

## Suite

`P4-M000 - Prepare Fusion 360 integration gate report` devient la prochaine
mission recommandee. Elle doit preparer la decision humaine sans commencer
l'integration Fusion 360 executable.