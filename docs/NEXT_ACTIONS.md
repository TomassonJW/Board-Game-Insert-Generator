# Next Actions

Dernière mise à jour : 2026-07-21

## Version active

V0.1 reste `mvp-accepted`, `fusion-validated: true` et
`print-validated: false`. P64-V2H03V et P44-V sont fermées dans Fusion 0.1.55.
La réserve de charge P44 à environ cinquante conteneurs reste explicitement non
observée et ne constitue aucune preuve de performance Fusion.

P45-M001V est `architecture-accepted` sans runtime. P64-L01 et P64-L02 sont
`implemented-core` et `automated-validated`. Le bridge et la palette exposent
désormais l’analyse locale progressive, sans changement de schéma, solveur,
valeur physique ou scène.

## Dernier état réel

- les clés complètes L01 distinguent source asset, pose, defaults hérités,
  frontière de conteneur, contexte boîte, solve global et finalisation ;
- une édition d’asset recalcule seulement sa frontière et son contexte ;
- une édition de boîte réutilise les géométries intrinsèques et renouvelle les
  annotations contextuelles ;
- les statuts `compatible`, `conditional`, `incompatible` et `unknown`
  restent séparés du certificat global ; `unknown` n’est jamais compatible ;
- efficacité d’enveloppe, volume, empreinte, aspect, hauteur et complexité sont
  publiés séparément, sans score total opaque ;
- la frontière moteur reste plus large que les représentants `Compact`,
  `Équilibré` et `Bas` visibles dans un volet replié ;
- les bornes globales réactives n’effectuent aucun placement et ne prouvent
  aucune solution ;
- `validate_project` ne lance aucun solve global dans le bridge L02 ;
- le mécanisme dense 11 × 34 reste honnêtement
  `no_solution_within_budget`, sans nouvelle revendication.

## Prochaine action recommandée

### P64-L03 — Solvage explicite et finalisation staged

Objectif borné : remplacer l’orchestration globale automatique P44-M007 par une
action visible `Calculer l’agencement`, conserver l’ancien résultat comme
obsolète, puis séparer placement, finalisation et matérialisation.

Livrables attendus :

1. aucune édition ordinaire ne lance le portefeuille global ;
2. action primaire contextuelle `Calculer l’agencement`, puis
   `Finaliser le volume`, puis `Matérialiser dans Fusion` ;
3. progressive widening sur la frontière moteur complète, jamais sur les trois
   cartes visibles seulement ;
4. annulation, requêtes tardives et mutations pendant run traitées
   `stale_or_cancelled` ;
5. placement certifié distinct d’un plan final certifié et matérialisable ;
6. ancien aperçu grisé, focus stable, détails techniques repliés ;
7. tests cœur, bridge et DOM, puis gate Fusion P64-L03V distincte.

Frontières : préserver baseline, EMS historique, greedy, beam, Auto, budgets
Rapide/Normal/Approfondi et statuts ADR-0068. Aucun runtime P45, aucune
recalibration, aucune forme, aucun corps automatique, aucune cale et aucune
harmonisation F01/F02 implicite.

Sources : ADR-0056, ADR-0068, ADR-0069, ADR-0070, ADR-0071,
`P64_STAGED_CALCULATION_AND_FINISHING_PROGRAM.md` et la preuve P64-L02.

## Repères historiques conservés

- `P44-M009H05 Fusion OK 0.1.36 - commit 7c76ba0` ;
- P44-M007 a livré le package `0.1.37` ;
- `P64-H01 Fusion OK 0.1.42 - commit 5865645` ;
- P44-VH02 reste un retour contextuel supersédé, sans promotion
  `fusion-validated` ;
- `P64-V2H03V Fusion OK 0.1.55` ;
- `P44-V Fusion OK 0.1.55 - commit 70d45c6`.

## Lots suivants, non ouverts

1. P64-L03V après L03 automated-validated ;
2. futur runtime P45 par contrat de schéma et migration additive distincts ;
3. P46 seulement après formes et ergonomie matérialisées ;
4. P64-F01/F02, C01-C03 et F03 selon leurs dépendances ;
5. P47-P50 restent bloqués par P46, P69 par P50.

## Séquence verrouillée

Une seule mission peut être exécutée à la fois. P64-L03 est la seule mission
`ready`. P45 ne possède pas le solveur global ; P64 ne définit pas les piles,
poses, intentions ou formes. Les jeux externes restent globaux, les valeurs
physiques inchangées et aucune scène n’est créée automatiquement.

## Fin de chaque mission

Mettre à jour le pilotage, relire le diff, exécuter les preuves, committer puis
intégrer directement dans main seulement lorsqu’aucune gate humaine n’est
ouverte. Une gate Fusion ne vaut jamais impression.
