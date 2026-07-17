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
- P10-M005 expose une variante `asset-candidates:row_fill` recommandee si elle rentre, toujours report-only.
- P10-M006 groupe des assets compatibles avant generation de candidats, sans solveur complexe.
- P10-M008 convertit la variante asset recommandee en `executable_asset_plan` avec placement grille greedy borne, sans backtracking ni optimisation globale.

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


## Variante recommandee P10-M005

P10-M005 ajoute une variante determinee depuis les `module_candidates` :
`asset-candidates:row_fill`. Elle utilise une heuristique row-fill bornee avec
rotation XY simple si necessaire.

La variante est `recommended` seulement si tous les candidats imprimables tiennent
dans la boite. En cas d'echec, elle est `rejected` avec `rejection_reasons`. Elle
ne cree aucun `ModuleRequest`, aucune cellule de layout reelle et aucune
geometrie Fusion.


## Grouping borne P10-M006

Le grouping P10-M006 est une preparation de candidats, pas une optimisation. Il
regroupe seulement des assets strictement compatibles et laisse les reservations,
assets avec `module_hint` et dimensions Z inconnues hors regroupement.


## Rejet asset-candidate P10-M007

P10-M007 ajoute un exemple ou la variante `asset-candidates:row_fill` est
`rejected` parce que le candidat derive d'asset ne rentre pas dans la boite. Le
rapport conserve `rejection_reasons` structurees et aucune recommandation n'est
produite.

## Plan executable borne P10-M008

`P10-M008` fait passer la boucle asset-first de report-only a un premier plan
concret, mais toujours deterministe et borne :

1. lire la variante recommandee `asset-candidates:row_fill` ;
2. creer des modules generes abstraits depuis les candidats imprimables ;
3. si une `volumetric_grid` existe, convertir les dimensions millimetres en
   unites par arrondi superieur ;
4. placer chaque module par balayage greedy `z/y/x` sur le premier span libre ;
5. refuser explicitement les modules sans grille ou sans span libre.

Ce n'est pas un solveur global : il n'y a pas de backtracking, pas de recherche
de meilleure permutation, pas de dependance externe et pas de generation Fusion.
Le resultat est expose comme `executable_asset_plan` dans les rapports et la CAD
IR metadata.

## P13-M001 - Reuse quick_asset_box

`quick_asset_box` ne change pas la strategie solveur. Il transforme une saisie UI en config temporaire, puis reutilise le pipeline borne existant : `module_candidates`, variante recommandee deterministe et `executable_asset_plan` greedy grille X/Y/Z. Aucun backtracking, aucune optimisation globale et aucun nouveau score ne sont ajoutes.

## P13-ASSET-M002 - Heuristique count-aware bornee

Le sizing count-aware n'introduit pas de solveur global. L'algorithme est volontairement borne : hauteur maximale derivee de la boite et de la plus grande plage Z libre de la grille, capacite par pile par division entiere, nombre de piles par plafond, puis row-packing XY deterministe des piles. Si l'enveloppe issue de cette heuristique ne rentre pas dans la boite/grille, la variante est refusee avec diagnostic au lieu de promettre une capacite.

Aucun backtracking, optimisation globale, score multi-variante lourd ou generation de cavites n'est ajoute en P13-ASSET-M002.

## P16-M001 - Heuristique flat_tray_2d V0

P16 autorise une heuristique locale de packing 2D des piles, sans changer la nature du solveur BGIG.

Ce qui est autorise :

- calcul deterministe de `items_per_pile` depuis `max_stack_height_mm` et `z_mm` ;
- calcul de `pile_count` depuis `count` ;
- choix local de `pile_grid_columns` et `pile_grid_rows` pour approcher `target_aspect_ratio` ;
- preference pour une organisation 2D quand elle reduit une longue ligne X ;
- refus ou warning si `max_module_length_mm` ou la boite/grille rendent le resultat impossible.

Ce qui reste interdit : solveur global, backtracking, permutation optimale de modules, dependance d'optimisation, cavites par item, visualisation de chaque asset individuel.

## P16-M002 - Implementation flat_tray_2d V0

L'heuristique `flat_tray_2d_v0` est locale au sizing d'un asset ou groupe d'assets. Elle choisit une grille de piles deterministe en enumerant les colonnes possibles, en minimisant d'abord les cases vides puis l'ecart au `target_aspect_ratio`.

Cette implementation ne change pas le placement global des modules dans la grille volumetrique : le `executable_asset_plan` continue d'utiliser le placement greedy borne existant. Il n'y a toujours pas de backtracking ni d'optimisation globale.

## Stratégie acceptée après P64-A01

Le solveur cible est un portefeuille, pas un algorithme universel. Le baseline
`stage_stack` sert les projets simples et réguliers. `free_3d_greedy` exploite
points extrêmes et espaces maximaux vides. `free_3d_beam` conserve plusieurs
états pour les projets denses. `portfolio_auto` distribue un budget et retient
le meilleur candidat certifié. `exact_proof` reste futur et sous gate.

La génération de variantes internes par conteneur sera une frontière de Pareto
bornée, jamais le produit cartésien global. P45 en définit la sémantique. Les
grilles uniformes restent des seeds/labs ; les plans de coupe adaptatifs et
espaces résiduels sont l'état principal du moteur 3D.

La faisabilité précède toujours la finition. Fermeture continue et harmonisation
modulaire ne peuvent modifier les contraintes physiques ni invalider la solution
de base. Voir `P64_MULTI_SOLVER_PORTFOLIO_PROGRAM.md`.

## Frontière acceptée P64-V2H03 / P45

ADR-0070 interdit de présélectionner une seule disposition locale avant la
recherche globale lorsque plusieurs enveloppes multi-cavités sont certifiées.
P45 conserve la sémantique des modes et formes ; une frontière géométrique pure
produit les variantes et leur certificat local ; P64 choisit paresseusement
variante et placement puis applique le certificat global.

Le premier runtime est un fallback correctif. Le portefeuille canonique complet
reste prioritaire et inchangé. Les recherches multi-variantes sont exécutées par
lanes préservées, sans produit cartésien et avec des caps monotones. Une limite
atteinte reste `no_solution_within_budget`. Les valeurs numériques des caps ne
seront fixées qu'après les fixtures et mesures de P64-V2H03B.

Contrat : `docs/P64_V2H03_INTERNAL_VARIANT_COORDINATION_CONTRACT.md`.

## État P64-V2H03B

La frontière locale est implémentée, mais aucun solveur public ne la consomme.
Le portefeuille canonique, greedy, EMS historique et beam reste inchangé.

H03C devra adapter les références aux états free-3D, conserver les lanes avant
le fallback et appliquer le certificat global. Les caps globaux sont présents
mais non consommés dans H03B.
