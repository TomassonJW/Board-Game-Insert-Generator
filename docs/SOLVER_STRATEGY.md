# Solver Strategy

## Objectif

Le solveur futur doit proposer plusieurs organisations explicables. Il ne doit
pas devenir une boite noire ni remplacer les gates physiques.

## Etat actuel

- `row_fill` et `grid` sont deterministes.
- Le rapport contient un score simple de layout, non optimise.
- Aucun optimiseur global, heuristique complexe ou dependance lourde n'est present.
- P10-M002 expose une comparaison `variant_comparison` report-only entre strategies deterministes deja implementees.
- P10-M003 ajoute des raisons de rejet structurees et actionnables pour les variantes non generables.
- P10-M004 ajoute des `module_candidates` deterministes depuis les assets, sans solveur global.

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

## Raisons detaillees de rejet P10-M003

P10-M003 enrichit les variantes `rejected` avec `rejection_reasons`, en plus des
raisons textuelles deja presentes. Chaque raison contient : `code`, `category`,
`severity`, `message`, `constraint_ref` et `actionable`.

Codes de rejet documentes pour le reporting report-only :

| Code | Sens | Exemple de correction |
| --- | --- | --- |
| `DOES_NOT_FIT` | La variante ne rentre pas dans l'enveloppe disponible. | Reduire un module, changer de strategie deterministe ou agrandir la boite. |
| `DIMENSIONS_INCOMPATIBLE` | Une dimension de module/asset est incompatible avec la boite ou l'orientation. | Verifier les mesures et la rotation autorisee. |
| `COLLISION` | Des spans volumetriques declaratifs se chevauchent. | Deplacer ou redimensionner un placement ou une zone. |
| `LAYER_EXCEEDED` | Un layer sort de la grille ou chevauche un autre layer. | Corriger `z_start` / `z_count`. |
| `SUPPORT_INSUFFICIENT` | Une reference de support abstrait est absente ou incoherente. | Declarer une surface de support abstraite valide. |
| `REMOVAL_ORDER_IMPOSSIBLE` | L'ordre de retrait ou la direction d'acces est incoherent. | Donner un ordre unique et une direction explicite. |
| `RESERVATION_VIOLATED` | Une reservation attendue est absente ou violee. | Relier l'asset a une zone existante ou preserver le span reserve. |
| `CLEARANCE_INSUFFICIENT` | Un jeu de cavite est inferieur au profil actif. | Augmenter le clearance ou changer de profil. |
| `VARIANT_GENERATION_FAILED` | Rejet generique non classe. | Lire l'erreur source et corriger la configuration. |

Cette taxonomie ne cree pas de nouveau solveur. Elle classe les erreurs de
validation/layout deja disponibles pour rendre les refus exploitables.


## Candidats de modules P10-M004

Les `module_candidates` sont une entree de raisonnement pour les variantes futures.
Ils restent hors solveur : aucune recherche de placement, aucun backtracking et
aucune modification de `config.modules`.

Leur role est de rendre visible la transition `assets -> besoins de contenance` :
le rapport indique quels assets peuvent suggerer un module, lesquels restent de
simples reservations et quelles dimensions sont seulement indicatives.
