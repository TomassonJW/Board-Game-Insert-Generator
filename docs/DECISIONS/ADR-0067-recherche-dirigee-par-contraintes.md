# ADR-0067 — Recherche dirigée par contraintes avant diversification hash

## Statut

Acceptée le 2026-07-17 par le GO explicite de corriger les faux `Calcul impossible`
restants sur le projet Fusion dense.

## Contexte

ADR-0065 introduit les piles volumétriques et ADR-0066 une reprise hash bornée.
Le cas réel montre toutefois qu’un changement minime d’enveloppe peut éliminer
les bons ordres. Le rejet final fournit déjà une information exploitable : quelles
cavités percent une réservation supérieure et de combien leur corps manque de
hauteur. Une reprise aveugle par hash ne garantit pas de conserver la bonne
composition verticale ni le bon placement XY.

## Options

1. Augmenter fortement le nombre de seeds hash.
2. Assouplir les validations des cavités sous les plateaux.
3. Utiliser les contraintes de rejet pour guider un faisceau déterministe borné,
   puis conserver le hash en dernier recours.
4. Introduire immédiatement CP-SAT, MIP ou une dépendance externe équivalente.

## Décision

Retenir l’option 3.

Le chemin canonique reste prioritaire et inchangé. Après un cul-de-sac, des
portefeuilles structurés classent les participants par risque de réservation. Le
portefeuille spécialisé explore un faisceau de piles non contiguës, conserve des
états pour plusieurs nombres de piles, évalue des ordres XY géométriques et peut
redistribuer le surplus Z à l’intérieur d’une pile expansible lorsque la position
XY finale le nécessite.

La redistribution conserve la hauteur totale, les jeux et tous les minima. Elle
ne touche jamais une dimension fixe. Les rectangles de cavité et de réservation
servent uniquement à guider la recherche ; `apply_top_inset_reservations` et les
validateurs existants restent l’autorité d’acceptation.

Les budgets spécialisés sont bornés à 128 partitions de piles et 32 ordres XY.
Les six seeds hash d’ADR-0066 restent disponibles seulement si les stratégies
dirigées échouent.

## Conséquences

- les faux impossibles liés à l’élagage vertical et XY disposent d’une reprise
  explicable et reproductible ;
- les projets simples conservent leur coût canonique ;
- un cas réellement difficile peut prendre plusieurs secondes, mais le travail
  est borné et les requêtes obsolètes restent gérées par P44-M007 ;
- l’algorithme reste heuristique et ne revendique pas l’optimalité globale ;
- une future adoption d’un optimiseur externe exige une nouvelle ADR et une
  mesure démontrant que cette recherche bornée ne suffit plus.

## Validation

Autosauvegarde Fusion exacte, stress assets et conteneurs, régressions de
redistribution Z, déterminisme, suite complète, digest P66, compilation,
frontière `adsk`, diff-check et gate Fusion 0.1.45.