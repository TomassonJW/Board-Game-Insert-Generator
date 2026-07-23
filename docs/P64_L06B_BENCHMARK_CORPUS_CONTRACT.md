# P64-L06B — Contrat du corpus T0/T1 généré

## Statut et portée

P64-L06B est `implemented-core` et `automated-validated`. Il ajoute un corpus de
benchmark déterministe sans modifier le solveur P64, ses lanes, ses budgets, ses
deadlines, son classement, son certificat, le schéma projet, Fusion, la CAD IR ou
la finalisation.

Le corpus reste strictement limité aux parallélépipèdes T0/T1 du contrat actuel.
Aucune forme, pose ou mécanique T2 à T4 n'est simulée.

## Artefacts versionnés

- manifest : `bgig.solver_benchmark_manifest.v1` ;
- recette compacte : `bgig.solver_benchmark_recipe.v1` ;
- sélection avant ouverture : `bgig.solver_benchmark_holdout_selection.v1` ;
- fixture canonique : `tests/fixtures/p64_l06_solver_benchmark.v1.json` ;
- constructeur : `scripts/solver/build_solver_benchmark_manifest.py`.

Le manifest embarque les corpus de régression validés sans modifier leur contenu
ni leur digest. Il ajoute des recettes générées, leur seed, les digests des
projets matérialisés, les digests des oracles et les caractéristiques utiles. Une
reconstruction complète doit être identique octet pour octet.

## Splits

Le manifest contient huit cas de régression existants, puis trois splits de
64 cas chacun :

- `discovery` sert à trouver et classer les lacunes ;
- `tuning` sert uniquement à départager les réglages d'une hypothèse ;
- `holdout` accepte ou refuse l'unique candidat retenu.

Le holdout est `sealed` par défaut. Son accès exige un enregistrement signé par
digest indiquant exactement un candidat, choisi avant l'ouverture. Après
ouverture, aucun réglage supplémentaire n'est autorisé ; une nouvelle itération
exige un nouveau manifest versionné.

Les tests de L06B vérifient la fermeture et la structure du holdout. Aucun solveur
n'est exécuté sur ses cas avant le choix unique de L06D.

## Oracles

### Faisable par construction

Chaque cas `feasible_by_construction` possède :

1. un agencement local canonique P45, avec cavités, murs et plancher vérifiés ;
2. un placement global AABB construit séparément de P64 ;
3. un contrôle de boîte, non-chevauchement, réservation, support des étages et
   ordre de retrait ;
4. un digest d'oracle distinct du projet.

Le placement oracle n'est jamais fourni comme point de départ au solveur testé.
Un petit cas est néanmoins rejoué par le solveur courant afin de vérifier que la
chaîne de certificat BGIG reste utilisable.

### Impossible prouvé

Chaque cas `proven_impossible_small_exact` porte une preuve exacte et vérifiée :

- somme des volumes extérieurs fixes strictement supérieure au volume disponible ;
- ou hauteur minimale d'un corps strictement supérieure à la hauteur disponible.

Ces preuves sont des bornes nécessaires. Elles ne transforment jamais un simple
échec de recherche en preuve d'impossibilité.

## Matrice et familles

Chaque split généré couvre les cinq familles :

- nombreux conteneurs avec un contenu chacun ;
- peu de conteneurs avec de nombreux contenus ;
- nombreux conteneurs avec de nombreux contenus ;
- mélange simple, dense et hétérogène ;
- modification incrémentale puis reconstruction froide.

Les recettes couvrent les cardinalités P45 `1, 2, 4, 8, 16, 32`, les cibles de
frontière `1, 2, 4, 8`, les cardinalités P64 `2, 4, 8, 12, 18, 30, 50`, un à
trois étages, trois profils de dimensions, trois densités, réservations absentes
ou contraignantes, ordres naturels ou adversariaux et arrangements évidents ou
concurrents. La génération combine ces axes ; elle ne réalise pas leur produit
cartésien.

Les valeurs `1, 2, 4, 8` de variantes sont aussi observées sur des frontières P45
réellement certifiées. Le champ `retained_variant_target` reste une cible de
construction par cas, pas une fausse promesse que chaque cas produit exactement
ce nombre.

## Rotations

Le benchmark distingue `permitted` et `forbidden_by_benchmark`. Un témoin interdit
reste à zéro degré ; un témoin permis peut utiliser une rotation Z.

Le schéma `bgig.project.v1` ne permet pas aujourd'hui d'interdire la rotation
globale d'un conteneur. Cette contrainte reste donc dans le contrat du benchmark,
sans changement silencieux du schéma public. Un adapter qui ne sait pas la
respecter doit répondre `unsupported` ; il ne peut pas ignorer la contrainte.

## Séquences incrémentales

Chaque split contient six paires. Les deux membres d'une paire ont exactement le
même projet courant et le même projet précédent, mais des modes d'exécution
`incremental` et `cold` distincts. Les changements couvrent modification interne,
nouveau conteneur et reconstruction complète. Cette identité permet une
comparaison sans changer l'entrée entre les deux parcours.

## Témoin humain futur

Un futur cas réel peut compléter la régression seulement après validation,
anonymisation, renormalisation et revue. La scène Fusion, un journal local ou un
projet personnel ne deviennent jamais un oracle autoritaire et ne sont jamais
promus automatiquement.

## Invariants et limites

- aucune dépendance externe ;
- aucun réseau, apprentissage ou auto-modification ;
- aucun chemin local, contexte client ou secret dans le manifest ;
- aucun solveur lancé pendant la génération des recettes ;
- aucun warm start obtenu depuis les témoins ;
- aucune revendication nouvelle sur le cas dense 11 × 34 ;
- `fusion-validated: false` ;
- `print-validated: false`.

Le petit oracle exact exhaustif et l'interface commune des comparateurs restent
le lot P64-L06C. L06B fournit déjà les vérités construites et les bornes négatives
nécessaires pour les tester.
