# Next Actions

Dernière mise à jour : 2026-07-21

## Version active

V0.1 reste `mvp-accepted`, `fusion-validated: true` et
`print-validated: false` pour son périmètre historique. P64-V2H03V et P44-V
sont fermées dans Fusion 0.1.55.

P64-L01, P64-L02 et P64-L03 restent `automated-validated` pour l'état
incrémental, l'analyse locale et le retrait du solve global automatique.
P64-L03V est un KO contextuel sur Fusion 0.1.56 : la séparation des actions est
visible, mais le solve agrandit déjà les enveloppes et la finalisation ne
transforme rien. La mise à jour d'une scène existante peut aussi rester masquée
par un ancien digest.

ADR-0074 et P64-L03R-A sont `architecture-accepted`, sans changement runtime.

## Dernier état réel

- les dimensions et variantes locales restent réactives sans solve global ;
- le runtime 0.1.56 appelle encore les chemins de placement avec allocation de
  surplus X/Y/Z ;
- la finalisation de compatibilité conserve la partition reçue avec
  `geometry_changed: false` ;
- la matérialisation reste actuellement bloquée avant finalisation ;
- l'UI ne compare pas encore le digest de scène au digest exact de l'artefact
  courant ;
- le contrat cible distingue désormais `minimal_layout` et `finalized_plan` ;
- le plan minimal certifié sera matérialisable et exportable avant finition ;
- la recherche minimale utilisera un portfolio borné de graines, ancres et
  propagations ordonné par rareté de placement ;
- le cas dense 11 × 34 reste `no_solution_within_budget`.

## Prochaine action recommandée

### P64-L03R-B — Solveur minimal multi-graines

Implémenter uniquement le nouvel artefact `minimal_layout` dans le cœur Python :

1. consommer les variantes locales minimales ;
2. interdire toute allocation implicite de surplus X/Y/Z ;
3. comparer plusieurs graines, ancres coin/bord/centre/surface basse et
   propagations déterministes ;
4. favoriser le Z faisable le plus bas avec surfaces de support locales ;
5. conserver un beam diversifié, les budgets monotones et les statuts honnêtes ;
6. produire résiduel, provenance, sous-scores et certificat global ;
7. ne modifier ni bridge de matérialisation, ni scène Fusion, ni finition.

Contrat : `docs/P64_L03R_MINIMAL_LAYOUT_AND_MATERIALIZATION_CONTRACT.md`.

Acceptation : fixtures 1 à 10 et 16 à 18 du contrat, tests cœur ciblés, suite
complète, compileall, frontière adsk et diff-check. Aucun nouveau résultat dense
n'est exigé.

## Repères historiques conservés

- `P44-M009H05 Fusion OK 0.1.36 - commit 7c76ba0` ;
- P44-M007 a livré le package `0.1.37` ;
- `P64-H01 Fusion OK 0.1.42 - commit 5865645` ;
- P44-VH02 reste un retour contextuel supersédé, sans promotion
  `fusion-validated` ;
- `P64-V2H03V Fusion OK 0.1.55` ;
- `P44-V Fusion OK 0.1.55 - commit 70d45c6`.
## Lots suivants, non ouverts

1. P64-L03R-C après B : matérialisation minimale, digests exacts et remplacement
   sûr de la scène BGIG ;
2. P64-L03R-V après B/C : gate Fusion corrective ;
3. P64-F01A02 seulement après une L03R-V positive et ses dépendances ;
4. P64-F02A02, C01-C03 et F03 selon leurs dépendances ;
5. P45 runtime, P46 et P47-P50 restent séparés et verrouillés.

## Séquence verrouillée

Une seule mission peut être exécutée à la fois. P64-L03R-B est la seule mission
`ready`. P45 conserve les variantes/formes locales ; P64 conserve le placement
global. Aucune finition, valeur physique, scène ou migration de schéma n'est
ouverte par le contrat L03R-A.

## Fin de chaque mission

Mettre à jour le pilotage, relire le diff, exécuter les preuves, committer puis
intégrer directement dans main lorsqu'aucune vraie gate humaine n'est ouverte.
Une gate Fusion ne vaut jamais impression.
