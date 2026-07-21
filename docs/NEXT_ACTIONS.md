# Next Actions

Dernière mise à jour : 2026-07-21

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


## Trajectoire contractée P64-A02 — non ouverte

Le GO produit du 2026-07-21 accepte ADR-0071, ADR-0072 et les programmes
P64 de calcul étagé, finalisation et capacité réutilisable. Cette acceptation est
documentaire : elle ne remplace pas la gate P64-V2H03V et n'autorise pas encore
un changement du cycle réactif 0.1.55.

Ordre futur verrouillé après les gates déjà actives :

1. fermer P64-V2H03V, puis requalifier P44-V ;
2. cadrer P45-M001 sans lui transférer le solveur global ;
3. P64-L01 : états, digests, cache et invalidation incrémentale ;
4. P64-L02 : analyse locale, frontière progressive, score décomposé et résumé
   expert replié ; trois candidats visibles au plus, sans tronquer le moteur ;
5. P64-L03 puis P64-L03V : bouton de solve explicite, plan finalisable séparé,
   réponses obsolètes refusées et observation Fusion ;
6. P45/P46 selon leurs propres contrats ;
7. P64-F01 puis P64-F02 : finalisation simple, équilibrée et proportionnelle ;
8. P64-C01 puis C02 : carte de capacité en lecture seule, puis ajout local
   d'asset avec recertification et enveloppe monde inchangée ;
9. P64-F03 : cales explicites et confirmées, après retour physique pertinent ;
10. P64-C03 puis CV : conteneur autonome uniquement dans une baie de boîte
    explicitement réservée et certifiée.

P64-U01 et P64-X01 restent des trajectoires séparées. Aucun volume positif,
score élevé ou espace résiduel ne promet une disposition. Aucun asset,
séparateur, conteneur, corps ou cale n'est créé automatiquement.
