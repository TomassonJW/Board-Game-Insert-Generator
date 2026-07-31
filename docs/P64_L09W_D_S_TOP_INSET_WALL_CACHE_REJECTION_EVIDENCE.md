# P64-L09W-D-S — cache des contrôles de paroi rejeté

Date : 2026-07-31.

Statut : `increment-rejected`, `performance-hard-stop`,
`no-product-change-retained`, `holdout-sealed`.

## Résultat

Le deuxième levier causal testé n'est pas retenu.

Il réduisait le coût répété des contrôles de paroi pendant la recherche
automatique des réservations supérieures. Un cas causal public passait bien de
`bounded_unknown` à `certified_solution` dans le même budget public. Le panel
sentinelle a toutefois révélé une régression de temps dure sur
`p64-l09w-tuning-388-a020715e35`.

La campagne a été arrêtée immédiatement à `13/16`. Les 48 cas et les 400 cas
ouverts ne sont pas exécutés. Le code candidat et son test ont été retirés.

## Classification des 68 cas bornés de C

Le checkpoint public C, lu sans modification, donne :

- 16 cas sans élément plat déjà couverts par D-Q ;
- 24 cas `common` avec élément plat :
  - 21 rejets SCIP `MINIMAL_ENVELOPE_EXPANDED` ;
  - 3 rejets SCIP `TOP_INSET_AUTOMATIC_PLACEMENT_NOT_FOUND` ;
- 28 cas `stress` arrêtés par la deadline :
  - 15 avec témoin projeté recertifié et accepté ;
  - 9 avec témoin projeté refusé ;
  - 4 sans témoin initial disponible avant la recherche externe.

Le levier D-S ciblait uniquement le premier sous-groupe `stress` de 15 cas.

## Attribution causale

Sur `p64-l09w-tuning-338-f5347d13f7`, le témoin projeté est accepté, mais la
recertification des réservations supérieures répète des contrôles statiques de
boîte et de cavités jusqu'à épuiser le délai.

Le profil de diagnostic observe notamment :

- `97 896` appels à `_reservation_wall_certificate` ;
- `11 357 042` appels à `_rect_distance` ;
- le coût dominant dans `certify_top_inset_reservation_prisms`.

Ces compteurs viennent d'un profil instrumenté et ne servent pas de baseline de
temps.

Le candidat mettait en cache, dans un seul calcul, la partie statique exacte de
ces contrôles. Les contraintes entre éléments plats restaient recalculées. Il
ne changeait ni la grille `0,1 mm`, ni l'epsilon `0,0001 mm`, ni les valeurs
physiques, ni les limites publiques.

## Gain causal isolé

Sur le cas causal public :

- avant le candidat :
  - `bounded_unknown` ;
  - calcul `23 290,096 ms` ;
- avec le candidat :
  - `certified_solution` ;
  - calcul `13 825,920 ms` ;
  - témoin recertifié sélectionné ;
  - placement
    `042a9200a9d8c134622bd1a6fc0a5346fd8c421b94eb3a34f0f564ef5371c2ba`.

Les 66 tests ciblés du solveur minimal, des réservations supérieures, des
panels et des seuils passent avant la campagne sentinelle.

## Arrêt sentinelle

Les 13 premiers cas passent leurs gates fonctionnelles. Aucun ancien résultat
certifié ne perd son statut, son identité produit ou son placement.

La sentinelle `p64-l09w-tuning-388-a020715e35` conserve un résultat certifié
stable sur cinq répétitions, mais sa médiane de calcul vaut :

- observé : `37 814,985 ms` ;
- limite gelée : `23 070,369 ms`.

Les cinq placements sont identiques :
`5fc726469bb0568b611a7506c64f60bb424683c3731d88742b9a070206a340b0`.

La régression est expliquée : le témoin refusé termine plus vite, ce qui laisse
commencer une voie supplémentaire ; sa recertification commune non
interruptible franchit ensuite la deadline et porte la durée totale entre
`37 483,018 ms` et `39 723,146 ms`.

Le processus est arrêté avant la fin de
`p64-l09w-tuning-360-c8628c8c54`. Le checkpoint local interrompu engage :

- `13/16` cas complets ;
- `active_case_id=p64-l09w-tuning-360-c8628c8c54` ;
- digest du bundle candidat :
  `4f95348e14bb382151844983b534a356bc09884689114c6ac324086d60cea102` ;
- digest du checkpoint :
  `9e9883da3bb5846ac0e9fc7fe0b2310b3e05b130cee7891102515d6cb0d41574`.

Ce checkpoint n'est pas reprenable : il prouve uniquement l'arrêt anticipé du
candidat rejeté.

## Décision

Le cache D-S est rejeté et n'est pas intégré au produit.

La prochaine mission atomique doit choisir un autre levier. Elle peut
diagnostiquer la recertification supérieure non interruptible, mais ne doit ni
réintroduire ce cache tel quel, ni accepter une solution terminée après la
deadline, ni relever les budgets.

E reste bloquée. Le holdout n'a été ni lu, ni ouvert, ni invoqué :

- `holdout_file_read=false` ;
- `opening_count=0` ;
- `solver_invocation_count=0`.
