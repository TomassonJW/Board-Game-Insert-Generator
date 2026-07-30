# 2026-07-30 — P64-L09W-C campagne de référence

P64-L09W-C exécute la candidate 0.1.80 sur les 400 positifs ouverts du corpus
produit B, deux fois par cas, sans ouvrir le holdout privé.

La campagne se termine à 400/400 : 332 solutions certifiées, 68 résultats
`bounded_unknown`, 368 replays fonctionnellement identiques, zéro faux
impossible et zéro solution non certifiée publiée. Seulement 61 cas sont prêts
hors Fusion.

La strate `stress` mesure un calcul p50 de 24,943 s, p95 de 77,117 s et p99 de
121,761 s. SCIP reste marginal sur les cas certifiés, avec un p95 de
16,775 ms. La perte dominante est aval : 271 solutions minimales certifiées ne
sont pas finalisées, dont 237 avec
`xy_composite_residual_owner_not_found`.

Décision : P64-L09W-D devient la prochaine mission. Son premier et unique
incrément sélectionné cible une résolution déterministe de la propriété des
cellules résiduelles XY. Aucun budget, valeur physique, grille, epsilon ou
holdout ne change. Toute règle arbitraire ou perte de solution est interdite.

Preuve :
`docs/P64_L09W_C_REFERENCE_CAMPAIGN_EVIDENCE.md`.

Validation : runner `7/7`, contrat documentaire `11/11`, suite P64-L09W
`29/29` après ajout du verrou documentaire final, compilation Python `OK`,
puis suite complète autorisée avant ce verrou `1061/1061` en `582,188 s` avec
une intégration SCIP native ignorée. `ruff` n'est pas disponible dans
l'environnement et n'est donc pas revendiqué comme vert.
