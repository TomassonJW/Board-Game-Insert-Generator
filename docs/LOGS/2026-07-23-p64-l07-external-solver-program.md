# 2026-07-23 — recadrage P64-L07 vers un vrai benchmark externe

## Contexte

Le premier Goal P64-L06 a produit un corpus, un petit oracle et un runner
reprenable, mais il n'a comparé aucun solveur externe mature. Les trois
hypothèses mesurées étaient des variantes mineures du solveur BGIG.

Thomas demande explicitement de comparer BGIG au meilleur de ce qui est
accessible et libre d'utilisation, puis d'intégrer le meilleur choix, avec la
possibilité de conserver jusqu'à trois moteurs complémentaires.

## Décision

- P64-L06 reste clôturé dans sa portée étroite.
- P64-L07 devient la prochaine campagne unique.
- ADR-0081 autorise la recherche externe, les téléchargements isolés, le
  benchmark d'au moins trois concurrents distincts et l'intégration
  conditionnelle d'un à trois gagnants.
- Le holdout L06 est consommé ; P64-L07 crée un corpus V2 et un nouveau holdout.
- Le `/goal` de la tâche de reprise vaut GO complet, sans seconde autorisation.

## Frontières

- T0/T1 seulement.
- Aucune installation globale ni service distant.
- Licence, redistribution, Windows hors ligne et packaging vérifiés.
- Toute sortie repasse par le certificat BGIG.
- `fusion-validated: false` et `print-validated: false`.

## Livrables

- `docs/DECISIONS/ADR-0081-open-external-solver-tournament.md`
- `docs/P64_L07_OPEN_SOLVER_TOURNAMENT_PROGRAM.md`
- `docs/P64_L07_AUTONOMOUS_GOAL_RUNBOOK.md`
- alignement de PILOTAGE_CURRENT, NEXT_ACTIONS, HUMAN_GATES, STATUS,
  CAPABILITY_MAP, ROADMAP, BACKLOG et du programme P64 multi-solveurs.

## Validation

- garde documentaire : 2/2 ;
- alignement Fusion-only : 6/6 ;
- suite complète : 715/715 en 225,888 s ;
- `git diff --check` : OK avant staging.
