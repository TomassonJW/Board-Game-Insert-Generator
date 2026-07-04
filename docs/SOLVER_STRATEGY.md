# Solver Strategy

## Objectif

Le solveur futur doit proposer plusieurs organisations explicables. Il ne doit
pas devenir une boite noire ni remplacer les gates physiques.

## Etat actuel

- `row_fill` et `grid` sont deterministes.
- Le rapport contient un score simple de layout, non optimise.
- Aucun optimiseur global, heuristique complexe ou dependance lourde n'est present.

## Strategie cible

1. Enumerer des variantes simples et reproductibles.
2. Filtrer les collisions et violations de contraintes.
3. Scorer selon compacite, accessibilite, hauteur, volumes libres, impression et setup.
4. Expliquer les arbitrages et hypothese par variante.
5. Laisser l'utilisateur choisir ou verrouiller certaines decisions.

## Invariants

- Le score doit rester explicable.
- Une variante rejetee doit donner une raison actionnable.
- Les dependances lourdes d'optimisation exigent ADR et validation humaine.
- Le solveur ne valide pas la faisabilite d'impression.

## Prochaines missions possibles

1. `P10-M001 - Definir les criteres de scoring volumetrique`.
2. `P10-M002 - Generer deux variantes deterministes depuis un meme projet`.
3. `P10-M003 - Rapporter les variantes refusees avec raisons`.

## Gates

- Gate architecture avant ajout d'un solveur externe ou d'une dependance lourde.
- Gate produit avant tout comportement automatique qui masque les hypotheses.
