# Next Actions

Dernière mise à jour : 2026-07-17

## Version active

V0.1 reste `mvp-accepted` par P66, `fusion-validated: true` et
`print-validated: false`. P44 poursuit la fondation UX V0.2, mais P44-V reste en
KO contextuel tant que le solveur n'a pas passé la gate corrective P64-V2H02.

## Dernier état réel

- P44-M009H05 reste `fusion-validated` dans Fusion 0.1.36 par la preuve
  `P44-M009H05 Fusion OK 0.1.36 - commit 7c76ba0`.
- Le package initial P44-M007 0.1.37 est supersédé par ses correctifs.
- P44-M007H03 est `fusion-validated` dans Fusion 0.1.40 par la preuve
  `P44-M007H03 Fusion OK 0.1.40 - commit 92f07c8`.
- P44-VH02 a corrigé la suppression directe et le nommage incrémental ; ses faits
  UX restent acceptés contextuellement sans valider le solveur.
- P64-H01 est `fusion-validated` dans Fusion 0.1.42 par la preuve
  `P64-H01 Fusion OK 0.1.42 - commit 5865645`.
- P64-H03R conserve les gains de recherche dirigée ; ils n'ont pas été retirés.
- P64-H04 à H08 ont introduit résultats honnêtes, contrat commun, greedy 3D,
  beam, portefeuille et réglages Fusion.
- P64-V2 0.1.51 est un KO contextuel sur le cas dense réel.
- P64-V2H01 0.1.52 a certifié la fixture à 9 corps, mais le projet réel étendu à
  11 conteneurs et 34 contenus reste sans candidat : la gate 0.1.52 est
  supersédée et ne doit pas recevoir de preuve OK.
- P64-V2H02 0.1.53 est observée OK pour capacité, vérité, budgets, méthodes et occlusion ;
  seul le sens Y de la vue de dessus est encore inversé à l'écran. P64-V2H02R 0.1.54
  corrige ce repère visuel uniquement.
- Le cas de référence conserve environ 693,6 cm³ de marge volumique théorique,
  mais cette borne ne prouve pas une disposition orthogonale. Son statut reste
  honnêtement `no_solution_within_budget`.

## Prochaine action recommandée

### P64-V2H02R — Correctif de repère de la vue de dessus

Statut : ready-for-human-fusion-check après installation du package 0.1.54.

Préparation : `scripts/fusion/prepare_p64_v2h02_capacity_search_test.ps1`.

Objectif humain :

- vérifier que la capacité théorique apparaît sur résultat résolu et non résolu ;
- vérifier qu'un budget épuisé dit `non résolu` et non `impossible` ;
- vérifier que Rapide, Normal et Approfondi exposent 1, 2 et 4 priorités et des
  largeurs beam distinctes ;
- vérifier que des méthodes ou efforts peuvent légitimement conserver le même
  résultat tout en affichant leurs métriques propres ;
- vérifier que la vue de dessus masque les cavités situées sous un corps et représente Y dans le sens d'une observation depuis le dessus (miroir autour de l'axe X), sans modifier la coupe X/Z ;
- vérifier qu'aucune scène n'est matérialisée automatiquement.

Retour attendu : `P64-V2H02R Fusion OK 0.1.54 - commit <sha>`, ou KO contextuel
avec le projet laissé dans son état reproductible.

La gate ne revendique ni solution du cas dense, ni harmonisation modulaire,
ni calibration physique, ni impression.

## Lots suivants, non ouverts

1. P64-V2H02R : correctif de repère, puis arbitrage de P64-V2H03.
2. P64-V2H03 : variantes internes bornées et sélection globale, à coordonner
   explicitement avec P45 avant tout code.
3. P44-V, puis P45/P46 selon leurs contrats et gates.
4. P64-F01 restant / P64-F02 après P46 : finition et harmonisation modulaire.
5. P64-U01 : progression de calcul non modale et annulable, sans vol de focus.
6. P64-X01 : éventuel moteur exact, seulement après benchmark, ADR de dépendance
   et GO distinct.

## Séquence verrouillée

P64-V2H02R est la seule action `ready-for-human-fusion-check`. P44-V, P45 et P46
restent bloqués. P47-P50 restent bloqués jusqu'à P46 et P69 jusqu'à P50. P68
peut recueillir des faits réels sans recalibrer les defaults.

## Fin de chaque mission

Mettre à jour le pilotage, relire le diff, exécuter les preuves prévues, committer
puis intégrer directement dans `main` lorsqu'aucune gate humaine n'est ouverte.
Une gate Fusion ne devient jamais une validation d'impression.