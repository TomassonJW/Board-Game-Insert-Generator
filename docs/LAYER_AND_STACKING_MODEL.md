# Layer and Stacking Model

## Objectif

Representer les etages, couches, supports et empilements dans la boite sans
pretendre encore a une validation physique.

## Etat actuel

- Une seule hauteur utile est prise en compte.
- Les modules ont une hauteur, mais pas d'etage ni d'ordre vertical.
- Les boards, livrets et plateaux ne sont pas encore modelises comme reservations.

## Concepts cibles

- `Layer` : tranche verticale nommee avec hauteur et role.
- `StackGroup` : modules ou reservations empiles.
- `SupportSurface` : surface qui supporte une couche superieure.
- `ClearanceAbove` : jeu vertical au-dessus d'une couche ou d'un board.
- `TopReservation` : espace reserve au-dessus pour boards, regles ou livrets.

## Invariants

- La somme des layers et reservations doit rester sous `usable_height_mm`.
- Un module empile doit declarer ce qu'il supporte et ce qui le supporte.
- Les regles de support sont experimentales tant qu'elles ne sont pas imprimees.

## Prochaines missions possibles

1. `P8-M002 - Specifier les layers et reservations verticales`.
2. `P8-M003 - Charger une fixture multi-layer sans solveur`.
3. `P8-M004 - Rapporter l'ordre de retrait et les surfaces de support`.

## Gates

- Gate impression reelle avant de valider une charge, un support ou une friction.
- Gate Fusion si les layers declenchent une vue CAD nouvelle.
