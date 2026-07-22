# P64-L04B — Preuve Approfondi anytime et borné

Date : 2026-07-22
Statut : `implemented-core`, `automated-validated`
Fusion validated : false
Print validated : false

## Résultat

L’effort `deep` n’est plus une réexécution de neuf lanes sous les caps les plus
larges. Il exécute d’abord le préfixe Normal exact avec ses six lanes et leurs
budgets historiques, conserve son meilleur plan certifié comme incumbent, puis
n’exécute que les trois lanes supplémentaires d’Approfondi.

Ces trois lanes partagent une deadline de 30 000 ms. Chaque beam reçoit le
minimum entre son garde-temps historique et le temps restant. À expiration, le
solveur renvoie l’incumbent Normal certifié ; il ne transforme plus cette
solution en `no_solution_within_budget`.

## Contrat livré

- `quick` reste préfixe de `normal`, lui-même préfixe de `deep` ;
- caps par lane inchangés : 5 000 / 12 000 / 30 000 ms ;
- nouveau cap de portfolio
  `max_deep_extension_elapsed_ms = 30_000` ;
- remplacement de l’incumbent seulement par un tuple de classement nommé
  strictement meilleur ;
- égalité : incumbent Normal conservé ;
- expiration avec incumbent : `solution_found` ;
- expiration sans incumbent : `no_solution_within_budget` ;
- annulation de validité : `stale_or_cancelled`, fail-closed ;
- aucune frontière Pareto moteur limitée au top 3 ;
- aucune finalisation, CAD IR, scène ou matérialisation automatique.

Le contrat exécutable est
`docs/P64_L04B_DEEP_ANYTIME_CONTRACT.md`.

## Observabilité

La provenance `bgig.minimal_layout_portfolio.v1` expose :

- budgets Normal et Deep ;
- deadline et temps écoulé de l’extension ;
- lanes prévues, tentées et terminées ;
- statut, arrêt, candidats et frontière Pareto de chaque phase ;
- digest, profil et axes de rang de l’incumbent initial ;
- phase sélectionnée, amélioration ou conservation ;
- sources et digests des frontières locales ;
- raison d’arrêt finale.

Les exécutions Deep limitées par horloge portent
`solver.deterministic = false`. Le plan sélectionné repasse intégralement par le
certificat minimal commun avant retour.

## Validation automatisée

Résultats observés :

- 14/14 tests ciblés `test_minimal_layout_solver.py` ;
- 10/10 tests staged ;
- 9/9 tests de réutilisation locale ;
- 14/14 tests CAD de partition ;
- 22/22 tests palette/projet, dont l’effort Deep ;
- 639/639 tests de la suite complète en 154,896 s ;
- Ruff ciblé sur les fichiers modifiés : OK ;
- `py_compile` ciblé : OK ;
- `compileall` sur `src`, `fusion_addin` et `tests` : OK ;
- frontière `adsk` du cœur pur : OK ;
- `git diff --check` : OK avant clôture.

Le Ruff global reste hors preuve : il signale 41 dettes préexistantes dans des
fichiers non modifiés par L04B. Aucun de ces diagnostics ne touche le diff de la
mission.

## Limites

- La deadline de 30 s borne l’extension Deep après le préfixe Normal ; elle ne
  réduit pas les caps historiques du calcul Normal préalable.
- L’arrêt est coopératif : une certification atomique déjà commencée se termine
  avant que le résultat soit publié.
- L04B ne fournit pas encore d’activité visuelle, d’étape courante ni de temps
  écoulé dans la palette ; ces éléments appartiennent à L04C.
- Aucune nouvelle solution n’est revendiquée pour le cas dense 11 × 34.
- Le manifest Fusion reste à 0.1.58 : aucune installation ni gate humaine n’est
  requise pour ce lot cœur.
- `fusion-validated: false`, `print-validated: false`.

## Suite

P64-L04C est la prochaine mission : rendre l’attente visible pendant analyse,
calcul, finalisation et matérialisation, sans faux pourcentage et sans ouvrir de
nouvelle sémantique d’annulation. L04V restera la gate Fusion combinée après
validation automatisée de L04C.
