# 2026-07-17 — Programme P64 multi-solveurs

## Contexte

P64-H01 est validé dans Fusion. P64-H02 puis un essai local P64-H03 ont amélioré
des cas réels sans éliminer les faux impossibles sur des projets denses disposant
encore de volume. Thomas a demandé une trajectoire complète, priorisée et assez
explicite pour être exécutée par des agents Terra ou Luna.

## Changements

- le solveur actuel est conservé comme baseline rapide `stage_stack` ;
- un placement 3D libre greedy, un beam robuste, un portefeuille Auto et un mode
  exact futur sont cadrés ;
- faisabilité, classement, effort et finition deviennent quatre concepts
  indépendants ;
- l'épuisement heuristique est distingué d'une impossibilité prouvée ;
- les finitions continue et modulaire sont planifiées après la gate V0.2 ;
- P64-H04 devient la seule mission `ready` ; P44-V et P45 restent bloqués jusqu'à
  P64-V2 puis reprise positive de P44-V.

## Vérifications

- lecture des contrats P44/P64, ADR 0054 à 0066 et documents de pilotage ;
- confrontation avec les structures actuelles de `partition_solver.py` et
  `volumetric_stage_solver.py` ;
- aucune modification du runtime, des valeurs physiques ou de la scène Fusion.

## Impact

Les prochains agents ne doivent plus prolonger P64-H03 par de nouveaux seeds sans
contrat. Ils commencent par observabilité et vérité des statuts, puis introduisent
les stratégies derrière une interface et un validateur communs.

## Suivi

- exécuter `P64-H04` selon `docs/P64_MULTI_SOLVER_PORTFOLIO_PROGRAM.md` ;
- ne préparer `P64-V2` qu'après P64-H08 ;
- conserver `print-validated: false`.
