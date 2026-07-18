# Next Actions

Dernière mise à jour : 2026-07-18

## Version active

V0.1 reste `mvp-accepted`, `fusion-validated: true` et
`print-validated: false`. P64-V2H02R demeure la dernière preuve Fusion.
P64-V2H03B et C sont implémentés et validés automatiquement ; aucune preuve
Fusion H03 n'est encore acquise.

## Dernier état réel

- P44-M009H05 reste fusion-validated dans Fusion 0.1.36 ; le package initial
  P44-M007 0.1.37 est supersédé par ses correctifs.
- P44-VH02 conserve ses corrections de suppression et de nommage.
- P64-H01 reste fusion-validated par
  `P64-H01 Fusion OK 0.1.42 - commit 5865645`.
- P64-V2H02R reste fusion-validated par
  `P64-V2H02R Fusion OK 0.1.54 - commit 42e8993`.
- H03B fournit canonique, relayouts rectangulaires, digests, certificats, Pareto
  et caps 24/48/96 dans une frontière Python interne.
- H03C branche cette frontière en fallback après le portefeuille canonique
  complet, sans produit cartésien et sans nouveau contrôle de palette.
- Le cul-de-sac multi-cavités minimal est résolu en Rapide ; la réservation
  localisée est résolue en Normal.
- Le mécanisme dense anonymisé 11 × 34 reste `no_solution_within_budget` jusque
  dans la lane Deep. Ce résultat ne prouve ni solubilité ni impossibilité.
- Suite complète H03C : 566/566 OK. Preuve :
  `docs/P64_V2H03C_GLOBAL_SELECTION_EVIDENCE.md`.

## Prochaine action recommandée

### P64-V2H03V — Observation humaine Fusion

P64-V2H03V est `ready-for-human-fusion-check`. Le package 0.1.55, la fixture du
cul-de-sac multi-cavités, le contrôle canonique simple, les réglages
`Auto intelligent + Rapide` et le diagnostic secondaire replié sont préparés.

Action restante pour Thomas :

1. recharger l'add-in 0.1.55 et ouvrir BGIG ;
2. confirmer que la fixture affiche une solution avec deux variantes internes
   non canoniques et un certificat global ;
3. ouvrir `Diagnostic du calcul > Variantes internes` et vérifier voie, budgets,
   compteurs, ordre canonique-first et absence de produit cartésien ;
4. ouvrir le contrôle récent `p64-v2h03v-simple-control.bgig.json` et confirmer
   `Étages et piles`, sans diagnostic variantes ;
5. confirmer la stabilité de la palette et l'absence de scène avant
   `Matérialiser dans Fusion`.

Retour attendu :
`P64-V2H03V Fusion OK 0.1.55 - commit <sha>`, ou un KO contextuel avec projet,
méthode, effort, statut visible et diagnostic.

Aucun agent n'est requis pendant cette gate humaine. Après retour explicite, la
clôture documentaire peut utiliser `gpt-5.6-terra`, raisonnement `medium` ; le
compromis est acceptable car elle ne doit modifier aucun runtime. Un modèle plus
puissant n'est utile qu'en cas de KO nécessitant une nouvelle analyse du solveur
ou de la palette.

## Lots suivants, non ouverts

1. clôture documentaire P64-V2H03 après retour Fusion explicite ;
2. P44-V, puis P45/P46 selon leurs contrats et gates ;
3. P64-F01 restant / P64-F02 après P46 ;
4. P64-U01 : progression non modale et annulable ;
5. P64-X01 : moteur exact éventuel après benchmark, ADR et GO distinct.

## Séquence verrouillée

Une seule mission est active. P45 et ses formes restent hors scope. P44-V et
P46 restent bloquées ; P47-P50 restent bloquées jusqu'à P46 et P69 jusqu'à P50.

## Fin de chaque mission

Mettre à jour le pilotage, relire le diff, exécuter les preuves, committer puis
intégrer directement dans main. Une gate Fusion ne vaut jamais impression.
