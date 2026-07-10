# ADR-0038 - BoxFill greedy 2D V0

## Statut

Accepted for P20 implementation.

## Decision

`box_fill_greedy_2d.v0` consume un `BoxFillSolveRequest` contenant un `BoxFillPlan` source et des candidats sans position. Il produit un nouveau plan resolu dans `BoxFillSolveResult`; le plan source n'est jamais mute.

Les modules existants, particulierement `locked` et `manual`, et les reservations sont des obstacles fixes. Les candidats sont tries de maniere stable par priorite, surface, cote maximal, hauteur et id. Chaque candidat essaie les layers autorises dans un ordre stable et les positions XY formees par les frontieres des obstacles. Seules les orientations native et 90 degres autour de Z sont autorisees, sans backtracking ni optimisation globale.

Un candidat impossible reste visible dans les diagnostics structures. Un resultat `partial` ou `blocked` ne pretend jamais etre un plan complet valide.

## Consequences

Le moteur reste pur, CAD-agnostic et sans `adsk`. Fusion, UI, preview et CAD IR consommeront le resultat mais ne recalculeront pas le placement.
