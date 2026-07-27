# P64-L09T-G — preuve de durcissement et candidate 0.1.70

Date : 2026-07-27.

## Verdict

P64-L09T-G est `automated-validated`.

- Candidate source : `0.1.70`.
- Gate suivante : P64-L09T-V, observation humaine dans Fusion.
- Statut : `prepared-not-human-observed`.
- `fusion-validated=false`.
- `print-validated=false`.
- Aucun benchmark ou holdout solveur n'a été ouvert ou exécuté.

## Correctifs de robustesse découverts en G

Deux défauts réels ont été trouvés pendant le rejeu exact :

1. un witness certifié antérieur au rang « plancher d'abord » portait sept axes
   et provoquait une erreur lors de sa lecture avec les douze axes courants ;
2. sur les compositions avec au moins douze corps et une réservation haute,
   l'attribution cellule par cellule consommait le budget avant d'essayer la
   partition rectangulaire déjà certifiable avec découpe de réservation
   différée.

Le correctif reste borné :

- le witness ancien est accepté uniquement comme incumbent à recertifier ;
- la recherche continue toujours et aucun cache hit n'est revendiqué ;
- le witness est réécrit au format de rang courant après un calcul frais ;
- pour une composition réservée de douze corps ou plus, la fermeture essaie
  d'abord la partition rectangulaire, puis transmet uniquement le temps restant
  au repli par annexes ;
- les cavités et les paramètres physiques ne sont jamais déplacés ou modifiés.

Le seuil `12` est une bifurcation de stratégie de recherche, pas une dimension
physique ni une preuve de capacité.

## Matrice publique reproductible

`tests/test_p64_l09t_g_release_gate.py` couvre :

- un équivalent public dense de `CasLimite01+` avec douze corps, plusieurs
  familles de contenus, ajouts et réservation supérieure ;
- un équivalent anonymisé de `CasLimite02` ;
- ajout de contenus à jeux constants ;
- jeux seuls à contenus constants ;
- combinaison contenus + jeux ;
- calcul, finalisation, CAD IR et plan Fusion pur ;
- certificat final, cavités figées, paroi minimale et résiduel nul ;
- absence de chemin ou d'identité personnelle dans le reçu public.

Les tests ciblés existants complètent la matrice pour :

- smoke public ;
- plateau automatiquement décentré et plateau proche d'une cavité ;
- plan tout au sol et pile nécessaire ;
- fermeture rectangulaire et fermeture par annexes ;
- rejets, résultats stale et arrêts anticipés explicables.

## Rejeux locaux exacts

`scripts/fusion/p64_l09t_local_replay.py` a relu, sans les écrire :

- `case01` ;
- `case01_plus` ;
- `case02` ;
- `case02_content_only` ;
- `case02_clearance_only` ;
- `case02_combined`.

Les six parcours ont produit :

- `calculation_status=solution_found` ;
- `finalization_status=solution_found` ;
- `cad_status=ready_for_fusion` ;
- `cavities_frozen=true` ;
- `printable_residual_volume_mm3=0.0`.

Le reçu local confirme `source_projects_unchanged=true`. Il reste hors dépôt et
ne contient aucune donnée projet versionnée.

## Validations

- Tests ciblés G et frontières concernées : `158/158` en `109.834 s`.
- Suite globale autorisée : `873/873` en `374.311 s`.
- Test ignoré : `1`, intégration SCIP native indisponible sous Python 3.10.
- Modules exécutés : `111`.
- Modules benchmark/holdout explicitement exclus : `12`.
- Import `adsk` dans `src/board_game_insert_generator/` : aucun.
- Preflight public :
  `f78017e31ff18ad81d0a2aef6e9e1e7d52e624372779f56482ad472ec069fa65`.
- Preflight public : `13` contrôles, `41` unions, `13` coupes.

Une première invocation globale non canonique a chargé les tests comme package
et produit uniquement des erreurs d'import de helpers historiques. Le lanceur
temporaire a été corrigé pour reproduire `unittest discover -s tests`; la
relance canonique ci-dessus est entièrement verte.

## Package et préparation

- Manifeste source : `0.1.70`.
- Fixture publique :
  `p64-l09tv-01-explicit-composite.bgig.json`.
- Preflight : `scripts/fusion/p64_l09tv_preflight.py`.
- Préparateur : `scripts/fusion/prepare_p64_l09tv_gate.ps1`.
- Rejeu local : `scripts/fusion/p64_l09t_local_replay.py`.
- Le préparateur vérifie runtime, version, marqueurs, réglages, fixtures,
  reçus et commit installé avant de remettre la recette à Thomas.

## Limites et risques

- La validation automatisée prouve les contrats Python, CAD IR et adaptateur
  pur, pas l'exécution réelle de Fusion.
- Le witness historique est une amorce recertifiée, jamais une réutilisation
  automatique d'un résultat publié.
- L'impression, les dimensions obtenues sur machine et les trois familles
  P64-F03 restent hors de cette mission.
- Toute observation Fusion divergente vaut KO et doit conserver les
  diagnostics exacts.

## Prochaine action

Thomas exécute uniquement
`docs/P64_L09T_V_FUSION_GATE_RECIPE.md`. Codex ne promeut aucun statut humain.
