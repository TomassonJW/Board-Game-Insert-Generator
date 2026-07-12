# ADR-0050 - Reservation de pile superieure avant placement global

## Statut

Supersedee le 2026-07-12 par ADR-0057 acceptee. Cette ADR reste le
contrat historique implemente par P40, pas la cible produit P63.

## Date

2026-07-12

## Carte liee

- `P40 - Pile superieure plateaux et livrets`.

## Contexte

Les plateaux et livrets sont des volumes non imprimables poses au-dessus des
bacs. Les ignorer pendant le dimensionnement P39 permettrait de calculer des
bacs plus hauts que la place restante. Les placer completement ici serait
premature : cela exige le solveur X/Y/Z et le traitement du volume restant P41.

## Options

1. Laisser P41 decouvrir la pile de plateaux en meme temps que tout le volume.
2. Conserver les dimensions P39 et couper les bacs apres coup.
3. Reserver la pile maintenant, puis recalculer P39 sous la hauteur restante.

## Decision

Retenir l option 3 avec `bgig.flat_stack_reservation.v1`.

P40 trie les lignes ayant un `stack_order` explicite avant les autres, additionne
les epaisseurs par quantite, et reserve :

- une empreinte maximale XY des plateaux/livrets, avec jeu de layout sur les
  cotes ;
- leur hauteur totale, plus le jeu entre pile et bacs ;
- la hauteur de stockage restante en dessous.

Les bacs P39 sont ensuite recalcules sous cette hauteur. Un debordement XY ou Z
est bloque explicitement. P40 calcule aussi le budget de surface superieure des
bacs : il peut indiquer qu il suffit en aire, ou qu un support supplementaire
sera necessaire. Il ne pretend jamais que le support est continu avant P41.

## Consequences

- Les tailles de bacs tiennent compte des plateaux et livrets avant P41.
- Le Studio montre la hauteur qui reste aux bacs et le statut de support.
- P41 doit encore choisir les positions, prouver le support continu et ajouter
  des bacs/volumes de remplissage si necessaire.
- La pile est une `Reservation`, jamais un bac imprimable ou une geometrie CAD.

## Alternatives refusees

- Ajuster les bacs seulement dans Fusion : Fusion ne doit pas devenir le moteur
  de decision.
- Declares le support valide a partir de la seule somme des aires : les surfaces
  doivent etre continues apres placement.
- Ajouter une encoche ou un logement de plateau en P40 : cela appartient a P42
  ou, pour l ergonomie, a V0.2.
