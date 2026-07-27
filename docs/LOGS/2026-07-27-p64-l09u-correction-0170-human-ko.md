# 2026-07-27 — P64-L09U correction du human-KO 0.1.70

## Décision

La candidate 0.1.70 est classée `human-KO` et `do-not-run`.

Le correctif 0.1.71 :

- supprime le démarrage sur le dernier projet ;
- désactive les témoins certifiés intersession ;
- rétablit le calcul frais des cas denses avec réservation supérieure ;
- groupe les unions et coupes rectangulaires par propriétaire dans Fusion ;
- prépare une nouvelle gate humaine chronométrée.

## Preuves

- 80 tests ciblés initiaux : OK ;
- 90 tests Fusion skeleton : OK ;
- 89 tests ciblés solveur, palette, CAD et release : OK ;
- replay local de six variantes, lecture seule : OK ;
- suite globale autorisée : `880/880` en `384.051 s` ;
- une intégration SCIP native ignorée sous Python 3.10 ;
- douze modules benchmark/corpus/tournoi exclus ;
- cavités figées et résiduel imprimable nul : OK ;
- validation Fusion 0.1.71 : en attente ;
- validation impression : en attente.

## Références

- `docs/P64_L09T_V_0170_HUMAN_KO_EVIDENCE.md`
- `docs/DECISIONS/ADR-0094-session-vierge-et-materialisation-fusion-par-lots.md`
- `docs/P64_L09U_RELEASE_GATE_EVIDENCE.md`
- `docs/P64_L09U_V_FUSION_GATE_RECIPE.md`
