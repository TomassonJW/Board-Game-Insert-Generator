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

### P64-V2H03V — Préparation et observation Fusion

P64-V2H03V est la seule mission `ready`.

Périmètre :

1. créer une fixture Fusion déterministe du cul-de-sac multi-cavités résolu ;
2. préparer le package add-in suivant sans changer schéma, valeurs ou defaults ;
3. installer automatiquement l'add-in et les settings locaux ;
4. vérifier les marqueurs du commit installé ;
5. demander à Thomas uniquement l'observation du résultat variantes, du
   diagnostic secondaire, de la stabilité de palette et de l'absence de scène
   automatique ;
6. conserver un projet canonique simple comme non-régression visible ;
7. présenter tout cas dense non certifié comme `no_solution_within_budget`,
   jamais comme impossible.

Interdits : forme ou champ P45, nouveau solveur, valeur physique, tolérance,
default, corps automatique, scène automatique ou revendication d'impression.

Validation avant observation : tests ciblés, suite pertinente, compileall,
frontière `adsk`, diff-check, installation locale et SHA installé vérifié. La
gate humaine ne commence qu'après cette préparation.

Modèle conseillé : `gpt-5.6-sol`, raisonnement `xhigh`. La mission est surtout
une intégration Fusion et une préparation de preuve, avec un risque modéré sur
le packaging, les fixtures et la traçabilité. Option économique :
`gpt-5.6-terra`, raisonnement `high`, acceptable si le contrat H03V est suivi
strictement, avec davantage de risque de reprise sur les marqueurs et le
parcours de gate.

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
