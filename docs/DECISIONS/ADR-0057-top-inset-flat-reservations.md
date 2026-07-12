# ADR-0057 - Reservations superieures encastrees pour plateaux et livrets

## Statut

Acceptee le 2026-07-12 par validation humaine explicite : `GO` pour avancer
vers le MVP. Elle remplace ADR-0050 pour la cible produit ; P63 portera son
implementation.

## Date

2026-07-12

## Cartes liees

- P60-R - Realignement produit apres revue Fusion
- P63 - Reservations superieures encastrees
- P64 - Solveur volumetrique multi-etages
- P66 - Acceptance V0.1 revisee

## Contexte

ADR-0050 reserve une pile globale de plateaux et livrets au-dessus de tous les
conteneurs, puis reduit uniformement leur hauteur. La revue P60 demande un autre
comportement : les conteneurs montent au plan superieur de conception et chaque
element plat creuse localement son empreinte depuis le dessus. Le plateau
affleure les zones hautes, les conteneurs peuvent le caler autour de son contour
et une prise permet son retrait.

## Options

1. Conserver la pile globale P40.
2. Calculer des conteneurs pleins puis les couper apres placement.
3. Introduire une reservation superieure localisee avant et pendant le solveur.

## Decision proposee

Retenir l option 3 et remplacer ADR-0050.

Chaque plateau ou livret produit une `top_inset_reservation` CAD-agnostic avec
empreinte XY, epaisseur, niveau, orientation, jeu, profondeur d encastrement,
ordre de retrait et zone de prise. Le solveur connait les intersections avec les
conteneurs avant de valider leurs cavites, leurs parois, leur support et leur
fabricabilite.

Les conteneurs restent au plan superieur de conception hors empreinte. Dans
l empreinte, une coupe locale de la profondeur requise est produite dans chaque
corps intersecte. Une reservation n est ni un asset, ni une cavite de contenu,
ni un corps imprimable.

Plusieurs elements plats peuvent etre empiles, partiellement superposes ou cote
a cote. L ordre est derive automatiquement quand il est evident ; l interface
demande un choix seulement en cas d ambiguite. Une zone de prise rectangulaire
minimale est requise en V0.1, sans promettre les formes ergonomiques V0.2.

## Consequences

- La hauteur reste disponible hors empreinte du plateau.
- Le plateau peut affleurer le sommet et participer au maintien local.
- Les appuis, retraits et conflits deviennent testables dans le coeur pur.
- Le placement des reservations et celui des conteneurs deviennent couples.
- La CAD IR doit supporter une operation de retrait par intersection.

## Alternatives refusees

- Coupe apres solveur : elle peut percer une cavite ou une paroi sans recalcul.
- Modeler le plateau comme couvercle : cela introduit un contrat fonctionnel non
  demande et brouille la V0.3.

## Validation attendue

- Invariants d intersection, de non-percement et d ordre de retrait.
- Coupes et vues de dessus/cote dans l apercu.
- Observation Fusion d un plateau affleurant avec prise visible.
