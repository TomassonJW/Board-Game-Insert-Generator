# Next Actions

Dernière mise à jour : 2026-07-21

## Version active

V0.1 reste `mvp-accepted`, `fusion-validated: true` et
`print-validated: false`. P64-V2H03V et P44-V sont fermées dans Fusion 0.1.55.
La réserve de charge P44 à environ cinquante conteneurs reste explicitement non
observée et ne constitue aucune preuve de performance.

P45-M001V est acceptée avec une interface conceptuelle unifiée `Pile` /
`Basculer` pour cartes et autres assets. Ce contrat est documentaire : aucun
schéma, runtime, calcul, UI ou comportement public correspondant n'est encore
implémenté.

## Dernier état réel

- P64-V2H03B/C/V fournit la frontière locale, la sélection globale paresseuse,
  les certificats et la preuve Fusion des variantes internes ;
- le mécanisme dense 11 × 34 reste `no_solution_within_budget` et n'est déclaré
  ni soluble ni impossible ;
- P44-V est `done-human-gate` pour la fondation UX 0.1.55 ;
- ADR-0071/0072 décrivent la future boucle locale, le solve global explicite,
  la finalisation et la capacité réutilisable, sans runtime correspondant ;
- P45-M001 et ADR-0073 sont `architecture-accepted` avec séparation stricte
  pile, pose, disposition locale et placement global.

## Prochaine action recommandée

### P64-L01 — États, digests et invalidation incrémentale

Objectif borné : représenter les états source, analyse locale, solve global,
finalisation et matérialisation, puis invalider uniquement les résultats
dépendant de l'entité modifiée.

Livrables attendus :

1. contrat runtime pur Python des états et transitions autorisées ;
2. identités et digests séparés pour asset, pile/pose P45, conteneur, boîte et
   paramètres globaux ;
3. graphe de dépendances et invalidation par asset, conteneur ou boîte ;
4. cache local borné et rejet fail-closed des réponses `stale` ;
5. fixtures déterministes prouvant qu'une modification locale ne déclenche pas
   implicitement un solve global ;
6. télémétrie lisible de fraîcheur, provenance et raison d'invalidation.

Frontières : aucun champ public P45, aucune UI `Pile` / `Basculer`, aucune forme
géométrique, aucune recalibration, aucun changement de solveur, aucune scène
Fusion et aucune matérialisation automatique. P45 reste propriétaire du sens
local ; P64 orchestre l'état et le placement global.

Sources : ADR-0071, ADR-0073, le contrat P45-M001 et les contrats P64-L01
référencés dans le backlog.

## Lots suivants, non ouverts

1. P64-L02 puis P64-L03/L03V selon ADR-0071 ;
2. futur runtime P45 par contrat de schéma et migration additive distincts ;
3. P46 seulement après formes et ergonomie réellement matérialisées ;
4. P64-F01/F02, C01-C03 et F03 selon leurs dépendances ;
5. P47-P50 restent bloqués par P46, P69 par P50.

## Séquence verrouillée

Une seule mission peut être exécutée à la fois. P64-L01 est la seule mission
`ready`. P45 ne possède pas le solveur global ; P64 ne définit pas les piles,
poses, intentions ou formes. Les jeux externes restent globaux, les valeurs
physiques inchangées et aucune scène n'est créée automatiquement.

## Fin de chaque mission

Mettre à jour le pilotage, relire le diff, exécuter les preuves, committer puis
intégrer directement dans main seulement lorsqu'aucune gate humaine n'est
ouverte. Une gate Fusion ne vaut jamais impression.
