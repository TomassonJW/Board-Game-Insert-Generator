# P64-L09W-D — handoff Git propre

Date : 2026-07-30.

Statut : `handoff-committed`, `working-tree-clean-tracked`,
`campaign-partial-39`, `holdout-sealed`.

## Clôture Git de la passation

Thomas a levé l’exclusion du worktree uniquement pour sauvegarder le travail et
permettre une reprise dans un nouveau clavardage et une nouvelle branche.

L’incrément technique, ses tests et l’état de pause sont sauvegardés dans :

- commit : `2de5959d4363e63e45b943ffff712b0de53e51f5` ;
- branche source : `codex/p64-l09w-d-xy-residual-owner`.

Les artefacts `.codex-work/p64-l09w-d/` restent volontairement locaux et
ignorés. Ils ne contiennent aucun résultat de holdout et ne sont pas promus
dans Git.

La prochaine reprise doit créer une branche successeure depuis ce commit dans
un nouveau worktree, puis recadrer D à F avant toute nouvelle campagne.
Les sections historiques ci-dessous décrivent l’état antérieur au commit ;
cette clôture Git est désormais autoritaire.

## Décision de Thomas

La campagne D est interrompue volontairement pour reprendre le contrôle des
worktrees et réduire le coût de D à F.

Ordre imposé :

1. ce document clôt le clavardage courant sans commit D ;
2. un clavardage séparé audite, committe et unifie les autres worktrees BGIG,
   sans toucher au worktree courant ;
3. un troisième clavardage reprend ensuite dans le même worktree courant,
   recadre le protocole D à F, puis seulement poursuit la mission.

Le GO autonome P64-L09W reste acquis. Ne pas créer un nouveau GO normal.

## Identité Git autoritaire

- dépôt et worktree exclusif :
  `C:\Users\janko\.codex\worktrees\930b\BGIG` ;
- branche : `codex/p64-l09w-d-xy-residual-owner` ;
- base et upstream au moment de la pause : `origin/main` ;
- HEAD : `7a09c5c25eb70eae2f97de2e3da69e574032f129` ;
- ce commit est P64-L09W-C et est déjà poussé directement dans `origin/main` ;
- commit de passation : `2de5959d4363e63e45b943ffff712b0de53e51f5` ;
- P64-L09W-D n’est pas terminé ; son incrément courant possède désormais un
  commit de sauvegarde dédié.

Fichiers techniques sauvegardés :

- `src/board_game_insert_generator/xy_composite_closure.py` ;
- `tests/test_xy_composite_closure.py`.

Les documents de pilotage et ce handoff sont sauvegardés avec le même commit.

## Incrément D sauvegardé

Cause mesurée en C :

- 237 pertes `xy_composite_residual_owner_not_found`.

Diagnostic causal :

- `_consume_pending_residuals` fusionne les cellules restantes ;
- cette fusion peut effacer les frontières XY qui provenaient pourtant des
  faces des propriétaires et des réservations ;
- une grande cellule remélangée ne peut alors plus recevoir un propriétaire
  entier, même si ses sous-cellules sont certifiables.

Changement courant :

- lorsque toutes les voies existantes échouent, restaurer uniquement les
  frontières X/Y déjà portées par les prismes propriétaires et les zones
  d’encastrement ;
- rester sous `max_closure_candidates` ;
- ne poursuivre que si au moins une sous-cellule produit une extension ou une
  attache déjà certifiée ;
- ne changer aucun budget, solveur minimal, grille, epsilon ou valeur physique.

Aucun support vertical descendant, fallback arbitraire ou nouveau moteur n’est
présent dans le diff final.

## Tests et diagnostics observés

Tests verts :

- `tests/test_xy_composite_closure.py` : `19/19` ;
- `test_finalization_stop_diagnostics.py` : `9/9` ;
- `test_p64_l09s_f_end_to_end_hardening.py` : `5/5` ;
- `test_p64_l09t_f_composite_cad.py` : `8/8` ;
- `test_p64_l09u_r3_depth_local_insets.py` : `21/21` ;
- `test_staged_calculation.py` : `21/21`.

Deux cas causaux exacts passent désormais à résiduel nul et finalisation
`solution_found` :

- common `p64-l09w-discovery-001-55d8459fc2` ;
- stress `p64-l09w-tuning-240-ea12ccc81d`.

Sur six cas rapides supplémentaires anciennement
`xy_composite_residual_owner_not_found` :

- deux deviennent prêts ;
- trois ferment le résiduel mais restent refusés par un contrat CAD ou un
  certificat final, donc ne sont pas comptés comme gains ;
- un conserve `xy_composite_residual_owner_not_found`.

Trois cas déjà prêts ont été rejoués et restent certifiés et matérialisables.

## Campagne D partielle autoritaire

Artefacts locaux ignorés :

- `.codex-work\p64-l09w-d\reference-checkpoint.json` ;
- `.codex-work\p64-l09w-d\reference-report.json` ;
- `.codex-work\p64-l09w-d\compare_d_to_c.py` ;
- `.codex-work\p64-l09w-d\run_d_batch.ps1`.

État :

- terminés : `39/400` ;
- restants : `361` ;
- `active_case_id=None` ;
- aucun processus Python de campagne ;
- prêts baseline C sur ces 39 cas : `8` ;
- prêts candidat D sur ces 39 cas : `18` ;
- régressions d’un cas déjà prêt : `0` ;
- holdout lu : `false` ;
- ouvertures holdout : `0` ;
- invocations solveur holdout : `0`.

Digests :

- binding :
  `ccd846fab0322135d5dc2f706e921083451146bde5154443e2fde844bf1bd6dc` ;
- code bundle :
  `29cceb8e20b490f364cbac548d6fcacab05e65e8d5b3d008b7e9e17c6091c029` ;
- checkpoint :
  `7a65dad456ee39bc455592e9f373dcbff4e1b9241f60ed42bd6be5d000ec2639` ;
- ensemble de résultats :
  `6647e0c26e207607e45cea72eccbb9433ee8e22bfefe2e0ec4371a6871bed736` ;
- rapport :
  `1dd3f842f4d4cd6bfa06d2d79e49b1d7bbf79f82ebaad7c0158b750f039f7cb6`.

La campagne partielle est prometteuse, mais elle ne valide pas D et ne justifie
aucune revendication générale.

## Mission séparée 1 — nettoyage des worktrees

Le nouveau clavardage doit :

1. commencer dans le dépôt BGIG principal choisi par Thomas ;
2. exécuter un inventaire en lecture seule de tous les worktrees ;
3. relever pour chacun chemin, branche, HEAD, upstream, statut, diff et commits
   absents de `main` ;
4. regrouper les worktrees qui portent la même mission avant de décider quoi
   intégrer ;
5. committer les changements intentionnels et intégrer les branches autant que
   possible ;
6. ne supprimer qu’un worktree propre, intégré et explicitement vérifié ;
7. ne jamais toucher au worktree `930b`, à sa branche D, à son checkpoint ou à
   ses fichiers non committés ;
8. terminer avec `main` local/distant vérifié et la liste exacte des worktrees
   conservés, intégrés ou encore bloqués.

Un conflit réel, un secret, un travail non attribuable ou un risque de perte
doit rester bloquant pour le worktree concerné, pas pour tout l’audit.

## Mission séparée 2 — reprise légère de D à F

Reprendre exclusivement dans
`C:\Users\janko\.codex\worktrees\930b\BGIG`.

Avant toute mutation ou campagne :

1. relire ce handoff et `AGENTS.md` ;
2. appliquer `$windows-command-resilience` ;
3. vérifier branche, HEAD, statut et éventuelle avance de `origin/main` après
   le nettoyage des autres worktrees ;
4. préserver le diff D et ne pas le rebaser tant que sa sauvegarde et son
   contenu exact ne sont pas prouvés ;
5. comparer le contrat de campagne complète à un protocole allégé, stratifié et
   honnête ;
6. définir les cas causaux obligatoires, la non-régression des résultats prêts,
   les échantillons common/stress, les règles d’arrêt et les validations
   exceptionnelles ;
7. décider explicitement si les 361 replays ouverts restants sont encore
   nécessaires, peuvent être réduits ou doivent être remplacés par une preuve
   plus ciblée ;
8. conserver l’ouverture unique du holdout pour E seulement ;
9. garder F conditionnel au changement produit réellement retenu.

Ne pas reprendre automatiquement `run_d_batch.ps1` avant ce recadrage.
