# P64-L09W-D-N — Preuve de déterminisme du résultat sélectionné

Date : 2026-07-30.

Statut : `diagnostic-complete`, `selected-product-contract-implemented`,
`holdout-sealed`.

## Verdict

Le cas public `p64-l09w-tuning-360-c8628c8c54` ne démontre pas trois
géométries différentes. Les quatre observations historiques C/D ont :

- le statut `certified_solution` ;
- la route `portfolio_lane` / `historical_bridge_edge` ;
- le même digest de placement
  `8906fd298e360b0a9b124b64fdf18f3e46b6cc4c8d9a5f009f24335344d490ea`.

Le champ historique `functional_digest` couvrait aussi la provenance de
recherche. Sous la limite de temps globale, une voie non retenue peut certifier
un nombre variable de propositions avant l'arrêt. Les observations historiques
diffèrent sur ces compteurs non retenus, pas sur le placement sélectionné.

## Reproduction

Cinq relectures exactes ont été exécutées avec :

- le même cas public ;
- le même `request_id` historique ;
- Python Fusion 3.14 ;
- SCIP 10.0.2 ;
- les budgets produit inchangés ;
- aucun accès au holdout.

Résultat :

- `5/5` plans complets produits ;
- `0` différence champ par champ entre le premier plan et chacun des quatre
  autres ;
- un seul digest produit sélectionné :
  `2704194d28b01489fc9147d3140efbf48b84561b679d1a73c7a78edaf2c14458` ;
- un seul digest de trace complète :
  `0d5576290638d1c1124062e8575f8a07b3708604a8cebbea0a405c992f0f3f12` ;
- un seul digest de placement :
  `8906fd298e360b0a9b124b64fdf18f3e46b6cc4c8d9a5f009f24335344d490ea`.

Temps de calcul observés : `21,994 s` à `22,772 s`.

## Correction de contrat

ADR-0109 sépare désormais :

- `selected_product_digest`, identité stable de la géométrie retenue et de ses
  contrats produit aval ;
- `execution_trace_digest`, identité stricte de la trace complète ;
- `deterministic`, stabilité du résultat produit ;
- `execution_trace_deterministic`, stabilité de la trace.

La baseline sentinelle a ensuite durci ce contrat :

- copie profonde du plan minimal avant toute finalisation aval ;
- identité produit v2 excluant le `candidate_digest` du certificat global,
  tout en conservant ses checks ;
- `execution_route_deterministic` distinct, car deux voies peuvent certifier le
  même produit.

Les anciens checkpoints restent lisibles. Leur champ historique
`functional_digest` n'est pas réécrit.

## Vérifications

- tests ciblés identité, runner C et runner D : `17/17`, OK ;
- cinq relectures exactes : `5/5`, OK ;
- comparaison complète des plans : `4/4` comparaisons à zéro différence, OK ;
- suite complète : aucun échec observé avant la borne, mais timeout gardé à
  `600 s`, donc verdict global `timeout`, non compté comme vert ;
- suite complète finale après clôture des panels :
  `1093/1093`, `1` skip prévu, OK en `622,557 s` avec la commande canonique ;
- `git diff --check` : OK ;
- holdout : aucune lecture, ouverture ou invocation.

## Limites

Cette preuve ferme la confusion entre résultat sélectionné et trace de
recherche. Elle ne transforme pas le correctif de finalisation D en amélioration
du taux de solutions minimales : le plafond ouvert reste `332/400`.

La prochaine étape n'est pas de reprendre `run_d_batch.ps1`. Elle consiste à
construire les panels permanents de 12–16 et 48 cas, puis à mesurer leur variance
avant de fixer des seuils de performance.
