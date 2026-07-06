# Solver Strategy

## Objectif

Le solveur futur doit proposer plusieurs organisations explicables. Il ne doit
pas devenir une boite noire ni remplacer les gates physiques.

## Etat actuel

- `row_fill` et `grid` sont deterministes.
- Le rapport contient un score simple de layout, non optimise.
- Aucun optimiseur global, heuristique complexe ou dependance lourde n'est present.
- P10-M002 expose une comparaison `variant_comparison` report-only entre strategies deterministes deja implementees.

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

## Criteres de scoring P10-M001

P10-M001 definit un contrat de scoring, pas un solveur. Un futur score de variante
doit rester decomposable en sous-scores lisibles :

| Critere | Role | Exemple de mesure future |
| --- | --- | --- |
| Compacite XY/Z | Eviter le gaspillage de volume utile. | occupation, free cells, hauteur utilisee |
| Accessibilite | Favoriser les retraits simples. | `removal_order`, `access_direction`, grip features |
| Respect des reservations | Preserver boards, livrets, regles et zones interdites. | collisions refusees, reservations intactes |
| Simplicite d'impression | Eviter trop de corps ou formes complexes. | nombre de modules, hauteurs, operations abstraites |
| Setup table | Limiter les manipulations pendant la mise en place. | assets `access_first`, ordre de retrait |
| Robustesse de mesure | Penaliser les dimensions approximatives critiques. | `dimension_confidence` |

Format cible d'un score explicable :

```json
{
  "variant_id": "variant-a",
  "total_score": 82.5,
  "subscores": {
    "compactness": 20,
    "accessibility": 18,
    "reservation_integrity": 20,
    "print_simplicity": 14,
    "setup": 7,
    "measurement_confidence": 3.5
  },
  "reasons": [
    "Top board reservation is removed before card modules.",
    "Two assets use approximate dimensions, so confidence is reduced."
  ],
  "status": "explain_only"
}
```

Invariants P10-M001 :

- aucun optimiseur global ;
- aucune generation de variantes ;
- aucune dependance lourde ;
- un score futur doit etre auditables par raisons, pas seulement par nombre ;
- une variante refusee devra exposer des raisons avant toute comparaison.
## Comparaison report-only P10-M002

P10-M002 ajoute une comparaison de variantes dans les rapports Markdown/JSON. Les
variantes sont uniquement les strategies deterministes deja implementees :
`layout:row_fill` et `layout:grid`.

Le moteur ne cherche pas de nouvelles positions. Il regenere les layouts connus,
calcule des sous-scores explicables et expose des raisons. Le statut des entrees
est `explain_only` ou `rejected`.

Ce n'est pas un solveur complet : aucune optimisation globale, aucun backtracking,
aucune dependance externe et aucune generation Fusion ne sont ajoutes.