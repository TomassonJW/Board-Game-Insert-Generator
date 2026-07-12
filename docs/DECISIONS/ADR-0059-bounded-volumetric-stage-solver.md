# ADR-0059 - Solveur volumetrique borne par etages

## Statut

Proposee le 2026-07-12 apres la revue produit P60. Validation humaine requise
avant P64.

## Date

2026-07-12

## Cartes liees

- P60-R - Realignement produit apres revue Fusion
- P64 - Solveur volumetrique multi-etages
- P66 - Acceptance V0.1 revisee

## Contexte

Le solveur P57 construit des rangees XY, place tous les corps a Z = 0 et leur
impose la hauteur de stockage complete. Il echoue donc sur des contenus qui
tiendraient en plusieurs etages et repartit le surplus sans tenir compte de la
taille relative ou d une epaisseur de paroi desirable.

Le projet possede deja des contrats CAD-agnostic de grille, reservation,
support, ordre de retrait et enveloppe minimale/finale. Il faut les converger
sans introduire prematurement une dependance d optimisation lourde.

## Options

1. Etendre le shelf solver 2D avec quelques cas Z.
2. Construire un solveur 3D borne par etages, heuristique et deterministe.
3. Ajouter immediatement CP-SAT ou un solveur MIP externe.

## Decision proposee

Retenir l option 2.

Le solveur enumere un portefeuille borne d arrangements XY par etage, puis
compose des etages compatibles en Z selon hauteur, support, collisions et ordre
de retrait. Il integre les reservations superieures avant validation finale.

Le surplus est reparti par objectifs souples ponderes : volume ou empreinte
minimale, epaisseur de paroi desirable, alignement utile, accessibilite et
preferences `equilibre`, `compact`, `accessible` ou `matiere reduite`. Les
valeurs `Fixe` restent des contraintes dures ; `Cible` reste ajustable.

Le resultat distingue `complete`, `proposal_with_residuals` et `impossible`.
Une cale ou un separateur peut etre suggere avec une raison et des dimensions,
mais n est jamais ajoute sans confirmation. `automatic_body_count` reste zero.

## Consequences

- Les cas multi-etages deviennent un objectif explicite du MVP revise.
- Le solveur reste pur, deterministe et testable sans service externe.
- La combinatoire doit etre bornee et les budgets de recherche documentes.
- Une dependance CP-SAT/MIP demanderait une nouvelle ADR et des preuves.

## Alternatives refusees

- Accumuler des exceptions dans P57 : dette elevee et diagnostics fragiles.
- Ajouter un solveur externe maintenant : cout de packaging et de maintenance
  injustifie avant de stabiliser le contrat volumetrique.

## Validation attendue

- Fixtures un etage, plusieurs etages, rotations et retraits.
- Conservation de volume, non-collision, support et ordre de retrait.
- Tests des modes Auto/Cible/Fixe, surplus pondere et resultats partiels.
