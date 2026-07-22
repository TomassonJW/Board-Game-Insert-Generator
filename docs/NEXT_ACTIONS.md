# Next Actions

Dernière mise à jour : 2026-07-22

## Version active

V0.1 reste `mvp-accepted`, `fusion-validated: true` pour son périmètre
historique et `print-validated: false`. La surface MVP reste exclusivement
l’add-in Fusion 360.

P64-L04A, P64-L04B et P64-L04C sont automated-validated. L04A fournit
la réutilisation locale à enveloppe fixe dans le package 0.1.58. L04B rend
Approfondi anytime. L04C ajoute l'activité honnête sans modifier le manifest
Fusion, qui reste à 0.1.58. fusion-validated: false et
print-validated: false pour P64-L04.

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
- analyse, calcul, finalisation et matérialisation exposent désormais identité,
  étape et temps écoulé sans pourcentage ni ETA inventés ;
- un second lancement du même type est bloqué ; aucune annulation décorative
  n'est exposée ;
- le cas dense 11 × 34 ne reçoit aucune nouvelle revendication.

Preuves :
`docs/P64_L04A_INCREMENTAL_LOCAL_REUSE_EVIDENCE.md` et
[P64-L04B](P64_L04B_DEEP_ANYTIME_EVIDENCE.md) et
[P64-L04C](P64_L04C_OPERATION_ACTIVITY_EVIDENCE.md).

## Prochaine action recommandée

### P64-L04V — Gate Fusion du parcours incrémental et des opérations longues

Type : gate humaine distincte. Aucun développement runtime supplémentaire ne doit
être ouvert avant son retour formel.

Préparation attendue dans une mission dédiée :

1. installer le package Fusion courant seulement après vérification du commit ;
2. vérifier l'activité immédiate, l'étape et le temps écoulé sur les opérations
   longues, sans pourcentage ni bouton Annuler décoratif ;
3. observer insertion locale sans mouvement monde ni solve global, puis fallback
   explicite ;
4. vérifier scène désynchronisée puis remplacée sans doublon ;
5. conserver provenance, méthode, budgets, phases, incumbent et raison d'arrêt ;
6. enregistrer un retour Fusion formel, sans revendication d'impression.

État d'entrée : L04A/B/C sont automated-validated ; package 0.1.58 ;
fusion-validated: false et print-validated: false pour P64-L04.


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

## Mise a jour P64-L04V preparation (2026-07-22)

Le preparateur versionne scripts/fusion/prepare_p64_l04v_gate.ps1, le fixture portable et la checklist sont prets. Executer le preparateur depuis le commit integre, puis collecter le retour humain defini par docs/P64_L04V_FUSION_GATE_CHECKLIST.md.
Aucune promotion fusion-validated ne precede cette observation ; print-validated: false.
