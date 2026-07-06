# Layer and Stacking Model

## Objectif

Representer les etages, couches, supports et empilements dans la boite sans
pretendre encore a une validation physique.

## Etat actuel

- P8-M001 charge des layers declaratifs dans `volumetric_grid.layers`.
- Les modules peuvent declarer une occupation X/Y/Z par `module_placements`.
- Les boards, livrets et plateaux peuvent etre representes comme zones `reserved`, sans asset model complet.

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

1. `P8-M002 - Approfondir reservations, ordre de retrait et surfaces de support abstraites`.
2. `P8-M003 - Preparer une fixture multi-layer plus proche d'un jeu reel`.
3. `P8-M004 - Rapporter l'ordre de retrait et les surfaces de support`.

## Gates

- Gate impression reelle avant de valider une charge, un support ou une friction.
- Gate Fusion si les layers declenchent une vue CAD nouvelle.

## Convention P8-M001

Un `Layer` P8-M001 est une bande de Z discretisee par `z_start` et `z_count`. Il
porte un role documentaire comme `printable_modules` ou
`future_board_rulebook_reservations`. Les layers ne creent pas encore de regles
de support, de charge, de friction ou d'ordre de retrait.

Toute interpretation physique d'un empilement reste experimentale tant qu'une
impression et une mesure reelles n'ont pas ete faites.