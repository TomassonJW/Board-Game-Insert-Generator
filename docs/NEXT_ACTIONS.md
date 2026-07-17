# Next Actions

Dernière mise à jour : 2026-07-18

## Version active

V0.1 reste `mvp-accepted`, `fusion-validated: true` et
`print-validated: false`. P64-V2H02R demeure la dernière preuve Fusion.
P64-V2H03B est implémenté et validé automatiquement sans modifier la sélection
publique.

## Dernier état réel

- P44-M009H05 reste fusion-validated dans Fusion 0.1.36 ; le package initial
  P44-M007 0.1.37 est supersédé par ses correctifs.
- P44-VH02 conserve ses corrections de suppression et de nommage.
- P64-H01 reste fusion-validated par
  `P64-H01 Fusion OK 0.1.42 - commit 5865645`.
- P64-V2H02R reste fusion-validated par
  `P64-V2H02R Fusion OK 0.1.54 - commit 42e8993`.
- H03B ajoute canonique, relayouts rectangulaires, digests, certificats, Pareto
  et caps 24/48/96 dans une frontière Python interne.
- Les sorties de `derive_container_plan`, le schéma, les solveurs et l'UI
  restent inchangés.
- Le cas dense reste `no_solution_within_budget` ; le volume positif ne
  prouve pas une disposition.

## Prochaine action recommandée

### P64-V2H03C — Sélection globale paresseuse

P64-V2H03C est la seule mission `ready`.

Périmètre :

1. adapter les variantes certifiées aux participants free-3D ;
2. exécuter d'abord le portefeuille canonique complet inchangé ;
3. ouvrir le fallback multi-variantes seulement sans candidat canonique ;
4. développer paresseusement au plus 2/4/6 variantes par participant ;
5. préserver les lanes Rapide/Normal/Approfondi par préfixes ;
6. appliquer le certificat global après chaque plan complet ;
7. exposer budgets, digests, rejets et arrêt dans le diagnostic secondaire ;
8. activer les fixtures globales 4 à 10 sans changer schéma ou UI.

Interdits : produit cartésien, forme P45, contrôle Fusion, score public, valeur
physique, scène ou matérialisation automatique.

Validation : fallback canonique, cul-de-sac multi-cavités, monotonie, arrêt
borné, annulation/stale, non-régressions denses, suite complète, compileall,
frontière adsk et diff-check.

Modèle conseillé : `gpt-5.6-sol`, raisonnement `max`. Option économique :
`gpt-5.6-sol`, raisonnement `xhigh`, avec plus de risque sur les états
paresseux, la monotonie et les certificats globaux.

## Lots suivants, non ouverts

1. P64-V2H03V après C si le résultat visible change.
2. P44-V, puis P45/P46 selon leurs contrats et gates.
3. P64-F01 restant / P64-F02 après P46.
4. P64-U01 : progression non modale et annulable.
5. P64-X01 : moteur exact éventuel après benchmark, ADR et GO distinct.

## Séquence verrouillée

Une seule mission est active. P45 et ses formes restent hors scope. P44-V et
P46 restent bloquées ; P47-P50 restent bloquées jusqu'à P46 et P69 jusqu'à P50.

## Fin de chaque mission

Mettre à jour le pilotage, relire le diff, exécuter les preuves, committer puis
intégrer directement dans main. Une gate Fusion ne vaut jamais impression.
