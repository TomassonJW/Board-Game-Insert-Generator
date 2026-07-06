# ADR-0020 - Fusion basic exploded view

## Statut

Remplace par ADR-0021 apres KO partiel P7-M001V.

## Date

2026-07-06

## Carte liee

- `P7-M001 - Generer une vue eclatee Fusion basique`

## Contexte

P11-M001 a valide manuellement la vue compacte Fusion depuis les placements grille
X/Y/Z. La gate humaine suivante autorise une premiere vue eclatee basique, sans
solveur, sans modules composites, sans export STL/3MF et sans nouvelle geometrie
ergonomique.

La vue eclatee doit aider l'inspection. Elle ne doit pas devenir un second moteur
de placement.

## Options

1. Ajouter des positions exploded dans la CAD IR et ne rien generer dans Fusion.
2. Generer dans Fusion une duplication rectangulaire simple a cote de la boite.
3. Creer une vraie vue eclatee avec composants enfants Fusion et transformations.

## Decision

Choisir l'option 2 pour P7-M001.

L'add-in Fusion conserve la vue compacte, puis cree des copies rectangulaires
`exploded` des blanks CAD IR et modules asset-first deja planifies. Ces copies
sont placees a droite de la boite sur une grille 2D deterministe, avec marge et
espacement fixes.

Le mode local par defaut est `compact_and_exploded`. Un fichier optionnel
`exploded_view_mode.txt` peut contenir `compact_only` pour repli. Toute autre
valeur est refusee avant generation.

Fusion ne recalcule ni solveur, ni clearances, ni tolerances, ni positions
compactes. Les dimensions des copies viennent des solides deja derives de la CAD
IR.

## Consequences

Effets positifs :

- la vue compacte P11 reste intacte ;
- la vue eclatee est visible et testable manuellement sans schema CAD IR
  incompatible ;
- le coeur Python reste sans `adsk` ;
- les tests hors Fusion couvrent mode, placement, nommage et garde-fous.

Effets negatifs et risques :

- la vue eclatee ne duplique pas encore les cavites et features comme operations
  soustractives ;
- la disposition exploded est une aide visuelle, pas une preuve de packaging ;
- la generation reelle doit etre inspectee dans Fusion avant statut
  `fusion-validated`.

## Alternatives refusees

Les composants enfants Fusion sont reportes pour rester compatible avec les
documents Part Design deja observes.

Une CAD IR de positions exploded est reportee : P7-M001 autorise une disposition
visuelle simple locale a l'add-in, tant qu'elle ne modifie pas le layout metier.

## Suivi

- Le smoke test humain P7-M001V a refuse partiellement les copies independantes de bodies.
- ADR-0021 remplace cette strategie par des occurrences liees.
- Smoke test humain P7-M001V2 requis.
- Nouvelle gate avant vue eclatee avancee, exports, modules composites ou
  transformations Fusion plus ambitieuses.
