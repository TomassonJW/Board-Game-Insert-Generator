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

ADR-0074 et P64-L03R-A sont `architecture-accepted`. P64-L03R-B et
P64-L03R-C sont `implemented-core` et `automated-validated`. C branche le plan
minimal sur la CAD IR, la palette et le remplacement borné de scène ; aucune
observation Fusion n'est encore revendiquée.

## Dernier état réel

- les dimensions et variantes locales restent réactives sans solve global ;
- `Calculer` consomme désormais le `minimal_layout` certifié de L03R-B ;
- la CAD IR minimale conserve les enveloppes exactes et le résiduel non
  distribué ;
- `minimal_layout` est matérialisable avant toute finalisation ;
- aucune méthode réelle de finition n'est livrée dans C ;
- l'identité de scène compare `artifact_kind`, les digests du plan, de
  l'artefact et de la CAD IR, ainsi que `source_revision` ;
- une scène ambiguë est refusée avant suppression, et une scène détenue par BGIG
  peut être remplacée sans viser les objets utilisateur ;
- le package de gate corrective est 0.1.57 ;
- le cas dense 11 × 34 reste `no_solution_within_budget`.

## Prochaine action recommandée

### P64-L03R-V — Gate Fusion corrective 0.1.57

Aucun nouveau lot de code n'est ouvert avant cette observation humaine. Le
package doit être préparé par
`scripts/fusion/prepare_p64_l03r_v_corrective_test.ps1`, puis Thomas vérifie dans
Fusion :

1. une édition locale ne lance aucun solve global et ne modifie aucune scène ;
2. `Calculer l'agencement minimal` conserve les dimensions minimales et montre
   le résiduel non imprimé ;
3. `Matérialiser les volumes minimaux` fonctionne sans finalisation ;
4. une nouvelle édition laisse l'ancienne scène visible mais désynchronisée ;
5. le nouveau calcul expose `Mettre à jour la scène` ;
6. la mise à jour conserve exactement une racine BGIG et un objet utilisateur
   témoin non tagué ;
7. l'identité technique contient les cinq champs contractuels exacts.

Retour attendu : `P64-L03R-V Fusion OK 0.1.57 - commit <sha>`, ou KO contextuel
avec projet, étape, statut visible et diagnostic. Cette gate ne valide ni valeur
physique ni impression.

Contrat :
`docs/P64_L03R_MINIMAL_LAYOUT_AND_MATERIALIZATION_CONTRACT.md`.
Preuve automatisée d'entrée :
`docs/P64_L03R_C_DUAL_MATERIALIZATION_EVIDENCE.md`.

## Repères historiques conservés

- `P44-M009H05 Fusion OK 0.1.36 - commit 7c76ba0` ;
- P44-M007 a livré le package `0.1.37` ;
- `P64-H01 Fusion OK 0.1.42 - commit 5865645` ;
- P44-VH02 reste un retour contextuel supersédé, sans promotion
  `fusion-validated` ;
- `P64-V2H03V Fusion OK 0.1.55` ;
- `P44-V Fusion OK 0.1.55 - commit 70d45c6`.

## Lots suivants, non ouverts

1. P64-L03R-V : gate Fusion corrective active ;
2. P64-F01A02 seulement après une L03R-V positive et ses dépendances ;
3. P64-F02A02, C01-C03 et F03 selon leurs dépendances ;
4. P45 runtime, P46 et P47-P50 restent séparés et verrouillés.

## Séquence verrouillée

Une seule étape est active : P64-L03R-V, gate humaine sans nouvelle mission de
code. P45 conserve les variantes/formes locales ; P64 conserve le placement
global. Aucune transformation de finition, valeur physique ou migration de
schéma n'est ouverte avant le retour de gate.

## Fin de chaque mission

Mettre à jour le pilotage, relire le diff, exécuter les preuves, committer puis
intégrer directement dans main lorsqu'aucune vraie gate humaine n'est ouverte.
Une gate Fusion ne vaut jamais impression.
