# Next Actions

Dernière mise à jour : 2026-07-22

## Version active

V0.1 reste `mvp-accepted`, `fusion-validated: true` pour son périmètre
historique et `print-validated: false`. La surface MVP reste exclusivement
l’add-in Fusion 360.

P64-L04A et P64-L04B sont `automated-validated`. L04A fournit la réutilisation
locale à enveloppe fixe dans le package 0.1.58. L04B rend Approfondi anytime
dans le cœur sans modifier le manifest Fusion, qui reste à 0.1.58.
`fusion-validated: false` et `print-validated: false` pour P64-L04.

## Dernier état réel

- une édition continue de recalculer uniquement ses dérivations locales ;
- une insertion interne admissible peut republier un `minimal_layout` courant
  sans solve global ni déplacement monde ;
- le fallback global reste explicite et aucune scène n’est modifiée
  automatiquement ;
- Rapide reste préfixe de Normal, Normal devient le préfixe et l’incumbent
  d’Approfondi ;
- les six lanes Normal gardent leurs caps historiques ;
- seules les trois lanes supplémentaires Deep partagent ensuite une deadline de
  30 000 ms ;
- une expiration Deep conserve l’incumbent certifié et ne le transforme plus en
  `no_solution_within_budget` ;
- sans incumbent, l’échec reste honnête ; une annulation stale reste
  `stale_or_cancelled` ;
- budgets, temps, lanes, phases, incumbent et raison d’arrêt sont observables ;
- l’indication d’attente pendant calcul et matérialisation reste absente ;
- le cas dense 11 × 34 ne reçoit aucune nouvelle revendication.

Preuves :
`docs/P64_L04A_INCREMENTAL_LOCAL_REUSE_EVIDENCE.md` et
`docs/P64_L04B_DEEP_ANYTIME_EVIDENCE.md`.

## Prochaine action recommandée

### P64-L04C — Attente et progression UX honnêtes

Objectif : rendre immédiatement visibles les opérations longues dans la palette
Fusion sans inventer une précision que le moteur ne possède pas.

Lot borné :

1. afficher une activité dès le lancement d’une analyse, d’un calcul, d’une
   finalisation ou d’une matérialisation ;
2. exposer l’étape courante et le temps écoulé, sans faux pourcentage ;
3. bloquer les doubles lancements d’une même opération ;
4. conserver les actions, focus, autosave et détails repliés existants ;
5. n’afficher Annuler que lorsqu’une opération possède une vraie sémantique
   coopérative et sûre ; `stale_or_cancelled` ne devient pas une annulation
   utilisateur générique ;
6. tester le producteur pur d’état d’activité, le bridge et le DOM ;
7. ne modifier ni solveur, budgets, schéma, géométrie, finalisation, scène ou
   valeur physique.

Autorité :
`docs/DECISIONS/ADR-0075-pre-final-local-layout-reuse.md`,
`docs/P64_L04_INCREMENTAL_LOCAL_REUSE_CONTRACT.md` et
`docs/P64_L04B_DEEP_ANYTIME_CONTRACT.md`.

Aucune revue humaine n’est requise entre L04B et L04C.

## Gate humaine différée

### P64-L04V — Parcours incrémental et opérations longues

La prochaine revue Fusion reste regroupée après L04C automatisé. Elle devra
observer le plan minimal, l’insertion locale sans mouvement monde ni solve
global, le fallback explicite, la scène désynchronisée puis remplacée sans
doublon, et le retour d’activité des opérations longues.

Le retour formel futur sera défini par le préparateur L04V. D’ici là, ne
revendiquer ni `fusion-validated` pour P64-L04, ni impression réelle.

## Lots verrouillés

- P64-F01A02 et F02A02 restent séparés : ils possèdent la finalisation du volume ;
- P64-C01/C02 restent post-finalisation et ne doivent pas absorber L04A ;
- P45 conserve formes, intentions et certificat local ;
- P46, P47-P50, P67-P69 et les valeurs physiques restent hors scope ;
- aucune résolution du cas dense n’est implicite.

## Fin de chaque mission

Mettre à jour le pilotage, relire le diff, exécuter les preuves, committer puis
intégrer directement dans `main` lorsqu’aucune vraie gate humaine n’est active.
Une gate Fusion ne vaut jamais impression.

## Repères historiques conservés

- `P44-M009H05 Fusion OK 0.1.36 - commit 7c76ba0` ;
- P44-M007 a livré le package `0.1.37` ;
- `P64-H01 Fusion OK 0.1.42 - commit 5865645` ;
- P44-VH02 reste un retour contextuel supersédé, sans promotion
  `fusion-validated` ;
- `P64-V2H03V Fusion OK 0.1.55` ;
- `P44-V Fusion OK 0.1.55 - commit 70d45c6`.
