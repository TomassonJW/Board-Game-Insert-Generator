# 2026-07-12 - Realignement produit apres revue P60

## Contexte

La revue humaine dans Fusion confirme le fonctionnement du parcours jusqu a la
materialisation et la valeur de l Apercu, mais refuse P60 comme acceptance
produit. La mission demandee est strictement documentaire : comprendre,
challenger et replanifier avant toute reprise de production.

## Changements

- P60 est classe `product-review-ko` et `technical-baseline-useful`.
- Le rapport `docs/P60_PRODUCT_FEEDBACK_REALIGNMENT.md` relie chaque retour aux
  limites actuelles de la palette, de P40 et de P57.
- Le parcours cible devient Boite, Plateaux et livrets, Elements du jeu,
  Conteneurs, Reglages, Apercu.
- ADR-0056 a ADR-0060 proposent respectivement l etat reactif, les reservations
  superieures encastrees, le catalogue/orientations, le solveur volumetrique par
  etages et la divulgation progressive Fusion.
- Le chemin critique devient P61-P66 ; P66 remplace P60 comme gate de sortie
  V0.1 et P44-P50 restent bloques.
- Aucune valeur de tolerance, dependance, schema, logique moteur ou geometrie
  Fusion n est modifiee.

## Verifications

- Lecture des documents de pilotage obligatoires et des ADR-0047 a ADR-0055.
- Confrontation au code de palette, reservation plate et solveur P57.
- `python -m unittest discover -s tests -p 'test_project_documents.py'` : 2 tests OK.
- `python -m unittest discover -s tests -p 'test_fusion_only_alignment.py'` : 5 tests OK.
- `python -m unittest discover -s tests` : 387 tests OK.
- `git diff --check` : OK.

## Impact

Le prochain agent ne doit pas reprendre l ancienne carte P61 comme simple
nombre de bacs en hauteur. Il doit attendre la revue des ADR-0056 a ADR-0060,
puis commencer uniquement par P61 si les decisions correspondantes sont
acceptees.

## Suivi

- Gate active : revue humaine des ADR-0056 a ADR-0060.
- Prochaine mission apres validation : P61 - etat reactif et architecture de
  palette.
