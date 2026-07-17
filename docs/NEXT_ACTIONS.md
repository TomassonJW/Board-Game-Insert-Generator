# Next Actions

Dernière mise à jour : 2026-07-18

## Version active

V0.1 reste `mvp-accepted` par P66, `fusion-validated: true` et
`print-validated: false`. P44 poursuit la fondation UX V0.2, mais P44-V reste en
KO contextuel. P64-V2H02R est maintenant fusion-validated, sans rouvrir automatiquement une mission runtime.

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
- P64-V2H02R est `fusion-validated` dans Fusion 0.1.54 par la preuve
  `P64-V2H02R Fusion OK 0.1.54 - commit 42e8993` ; la correction conserve
  la portée bornée : aucune preuve de solubilité du cas dense ni d'impression.
- Le cas de référence conserve environ 693,6 cm³ de marge volumique théorique,
  mais cette borne ne prouve pas une disposition orthogonale. Son statut reste
  honnêtement `no_solution_within_budget`.

## Prochaine action recommandée

### Arbitrage explicite avant toute nouvelle mission runtime

P64-V2H02R est `done-human-gate` et `fusion-validated` par la preuve
`P64-V2H02R Fusion OK 0.1.54 - commit 42e8993`.

Aucune mission n'est automatiquement prête : P64-V2H03 engage les variantes internes
et leur coordination avec P45. L'arbitrage humain doit choisir son périmètre avant
tout code. P44-V reste un KO contextuel à requalifier séparément.

## Lots suivants, non ouverts

1. Arbitrage explicite P64-V2H03 / P45 avant toute mission runtime.
2. P64-V2H03 : variantes internes bornées et sélection globale, à coordonner
   explicitement avec P45 avant tout code.
3. P44-V, puis P45/P46 selon leurs contrats et gates.
4. P64-F01 restant / P64-F02 après P46 : finition et harmonisation modulaire.
5. P64-U01 : progression de calcul non modale et annulable, sans vol de focus.
6. P64-X01 : éventuel moteur exact, seulement après benchmark, ADR de dépendance
   et GO distinct.

## Séquence verrouillée

Aucune action runtime n'est `ready` sans arbitrage. P44-V, P45 et P46
restent bloqués. P47-P50 restent bloqués jusqu'à P46 et P69 jusqu'à P50. P68
peut recueillir des faits réels sans recalibrer les defaults.

## Fin de chaque mission

Mettre à jour le pilotage, relire le diff, exécuter les preuves prévues, committer
puis intégrer directement dans `main` lorsqu'aucune gate humaine n'est ouverte.
Une gate Fusion ne devient jamais une validation d'impression.