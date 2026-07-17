# ADR-0070 — Propriété des variantes internes de conteneur

## Statut

Acceptée le 2026-07-18 dans le cadre du GO explicite de reprise
P64-V2H03 / P45. Ce GO délègue l'arbitrage borné tout en maintenant P45 bloquée
par ses dépendances produit et interdit d'anticiper ses formes futures.

## Date

2026-07-18

## Cartes liées

- `P64-V2H03A — Arbitrage et contrat des variantes internes`
- `P64-V2H03B — Frontière locale, certificats et fixtures`
- `P64-V2H03C — Sélection globale paresseuse et budgets`
- `P45-M001 — Contrat de disposition des assets non-cartes`

## Contexte

P64-V2H02R est `fusion-validated` pour la capacité informative, la vérité des
statuts, les budgets, les méthodes et la vue de dessus. Le projet dense de
référence reste toutefois `no_solution_within_budget`. Une relaxation exacte de
diagnostic hors produit a montré que la combinaison des enveloppes canoniques
actuelles est infaisable ; augmenter seulement le temps de recherche ne suffit
donc pas.

La dérivation P39/P55 calcule aujourd'hui une seule disposition locale par
conteneur. P64 reçoit ensuite cette enveloppe et cherche son placement global.
Pour un conteneur multi-cavités, plusieurs dispositions locales peuvent être
valides et produire des enveloppes différentes. Choisir localement une seule
disposition avant le solveur peut créer un cul-de-sac global alors qu'une autre
combinaison tient dans la boîte.

P45 reste néanmoins propriétaire des futures intentions fonctionnelles
`standard/auto`, `rangée` et `colonne verticale`, ainsi que des profils de
cavité et géométries ergonomiques. Laisser P64 inventer ces sémantiques
mélangerait recherche globale et conception locale. Attendre toute P45 avant de
corriger le solveur bloquerait inversement une frontière technique déjà
nécessaire, alors que P44-V et les formes V0.2 ne sont pas encore acceptées.

Contraintes non négociables :

- cœur Python pur, sans import `adsk` ;
- aucune modification de valeur physique, jeu, tolérance ou default ;
- jeux externes des conteneurs exclusivement globaux selon ADR-0064 ;
- aucune migration de `bgig.project.v1` et aucune nouvelle option novice ;
- cavités, contenus, quantités et provenance des jeux conservés ;
- baseline dirigée, EMS historique, greedy, beam et profils d'effort préservés ;
- aucun produit cartésien des variantes ;
- aucun statut `proven_impossible` issu d'un budget heuristique ;
- aucune revendication Fusion ou impression sans preuve correspondante.

## Options

### Option A — P64 possède et génère toutes les variantes

- Principe : le solveur global construit lui-même les dispositions internes et
  choisit simultanément cavités et placements.
- Avantages : intégration algorithmique directe et surface de code initiale
  réduite.
- Inconvénients : P64 absorberait la sémantique P45, les règles locales et les
  futures formes.
- Risques : duplication du validateur, couplage fort, modes utilisateur
  décoratifs ou incohérents.
- Coût de maintenance : élevé.
- Compatibilité MVP : mauvaise, car les frontières P39/P45/P64 disparaissent.
- Facilité de test : faible ; causes locales et globales deviennent difficiles à
  isoler.

### Option B — Attendre l'implémentation complète de P45

- Principe : aucune variante n'est exposée à P64 avant les modes et géométries
  V0.2.
- Avantages : propriété P45 évidente et aucune frontière transitoire.
- Inconvénients : le cul-de-sac du solveur bloque P44-V/P45 et P45 dépendrait
  elle-même d'une recherche globale non corrigée.
- Risques : dépendance circulaire et gros lot monolithique.
- Coût de maintenance : moyen, mais coût de délai élevé.
- Compatibilité MVP : correcte à long terme, inactionnable maintenant.
- Facilité de test : tardive et mêlée aux formes ergonomiques.

### Option C — Frontière locale certifiée, consommation globale paresseuse

- Principe : une frontière pure produit une petite frontière de variantes
  locales certifiées. P64 les consomme sans les interpréter et choisit
  paresseusement variante et placement sous un budget commun.
- Avantages : responsabilités nettes, certification à deux niveaux, intégration
  progressive et compatibilité avec les futurs producteurs P45.
- Inconvénients : types, digests et télémétrie internes supplémentaires.
- Risques : explosion combinatoire si la génération ou les lanes ne sont pas
  strictement bornées.
- Coût de maintenance : modéré et localisé.
- Compatibilité MVP : bonne ; aucun schéma projet ni contrôle novice requis.
- Facilité de test : forte, avec fixtures locales puis culs-de-sac globaux.

## Décision

Retenir l'option C.

### Propriété normative

| Sujet | Propriétaire | Règle |
| --- | --- | --- |
| Intentions utilisateur, modes de disposition et futures formes | P45 / `C-GEOMETRY` | P64 ne crée aucun mode ni libellé fonctionnel. |
| Représentation immuable d'une variante locale | frontière cœur commune | Contrat CAD-agnostic réutilisable par les producteurs P45 et P64-V2H03. |
| Génération corrective V2H03 | producteur technique borné de la frontière locale | Seulement des relayouts rectangulaires des cavités existantes ; aucune sémantique P45 revendiquée. |
| Certification locale | frontière géométrique, propriété fonctionnelle P45 | P64 refuse toute variante non certifiée et ne duplique pas ces règles. |
| Budgets, recherche paresseuse et sélection globale | P64 / `C-SOLVER` | Les variantes deviennent des options de placement, jamais un produit cartésien préconstruit. |
| Certification du plan complet | validateur commun P64 | Boîte, jeux globaux, collisions, réservations, appuis, retrait, fermeture et conservation restent autoritaires. |

La frontière locale distingue au minimum :

- `canonical_v1`, exactement équivalente à la dérivation courante ;
- `bounded_rectangular_relayout_v1`, producteur correctif interne fondé
  uniquement sur les cavités rectangulaires, murs, fonds et jeux déjà résolus ;
- les futurs producteurs P45, qui pourront apporter une sémantique acceptée sans
  modifier l'orchestrateur P64.

Le producteur correctif ne peut pas employer les noms `standard/auto`, `rangée`
ou `colonne verticale` comme s'ils étaient implémentés. Il ne modifie ni la
taille d'une cavité, ni son jeu, ni la quantité, ni la forme source. Il ne crée
aucun corps, aucune feature et aucune réservation.

### Identité et déduplication

Une variante est identifiée par un digest canonique de sa géométrie locale :
conteneur, enveloppe minimale, murs/fond, repère local, multiensemble des
cavités, origines, dimensions, quantités et provenance des jeux. L'ordre
d'énumération et les libellés humains ne participent pas au digest.

Une rotation globale X/Y de 90 degrés est une option de placement P64, pas une
nouvelle variante locale. Les miroirs ne sont pas dédupliqués sans équivalence
sémantique explicitement certifiée. Les doublons géométriques d'un même
conteneur sont fusionnés ; leurs producteurs et raisons restent traçables.

### Deux certificats obligatoires

Le certificat local vérifie la couverture des contenus, l'immuabilité des
cavités et jeux, le non-recouvrement local, les parois/cloisons/fonds minimaux,
le repère et l'absence de corps automatique. Il ne certifie ni placement dans la
boîte, ni réservations supérieures, ni support, ni retrait global.

Le certificat global P64 choisit exactement une variante locale certifiée par
conteneur, puis réapplique toutes les règles produit. Une solution n'est
matérialisable que si les deux niveaux sont valides.

### Coût, budgets et monotonie

Le coût local est un vecteur explicable servant uniquement à ordonner et élaguer
la frontière : priorité canonique, enveloppe, aspect, complexité du layout et
identifiant stable. Il ne revendique ni accessibilité, ni facilité d'impression,
ni économie de matière sans métrique dédiée. Le classement public final reste
celui des plans complets certifiés.

La voie canonique complète reste exécutée en premier avec ses budgets inchangés.
Dans P64-V2H03 initial, la voie multi-variantes est corrective : elle ne démarre
que si aucune solution canonique admissible n'a été trouvée. Les profils plus
profonds réexécutent et conservent les lanes moins profondes avant d'ajouter une
lane ; une recherche élargie ne peut donc pas évincer une solution déjà trouvée.

Les limites numériques ne sont pas inventées dans ce lot documentaire.
P64-V2H03B doit mesurer les fixtures et figer, dans le code et les tests, les
caps `générées`, `certifiées`, `retenues`, `options par expansion`, `états
d'affectation` et `essais de placement`. Rapide ⊆ Normal ⊆ Approfondi est une
condition d'acceptation. Une limite atteinte reste
`no_solution_within_budget`.

### Traçabilité et UX

Chaque run multi-variantes doit permettre de retrouver les variantes générées,
rejetées, dédupliquées, retenues et sélectionnées, leur producteur, leur digest,
leur certificat, les caps consommés et le motif d'arrêt. Cette information reste
dans le diagnostic secondaire ; aucun nouveau contrôle n'encombre le parcours
normal et aucun champ n'est ajouté au projet utilisateur.

## Conséquences

### Positives

- P64 peut corriger les culs-de-sac de dérivation sans définir les formes P45.
- P45 pourra ajouter des sémantiques locales derrière une frontière stable.
- La voie canonique et ses preuves restent observables et non évincées.
- Les échecs locaux, globaux et budgétaires deviennent séparables.

### Négatives

- Le pipeline doit porter deux niveaux de certificat et une provenance de
  variante.
- Les tests devront couvrir les équivalences géométriques et les lanes de
  budget, pas seulement le plan final.

### Risques

- Explosion combinatoire : mitigée par frontière de Pareto, caps, expansion
  paresseuse et absence de produit cartésien.
- Dérive sémantique : mitigée par des producteurs nommés et l'interdiction
  d'exposer le producteur correctif comme mode P45.
- Régression dense : mitigée par la lane canonique complète et des fixtures
  déterministes avant intégration globale.

## Alternatives refusées

- Option A : refusée car P64 absorberait conception locale et futures formes.
- Option B : refusée car elle crée une dépendance circulaire et retarde une
  correction technique déjà nécessaire.
- Pré-sélectionner la meilleure variante de chaque conteneur avant P64 : refusé,
  car le meilleur choix local peut former la pire combinaison globale.
- Construire toutes les combinaisons : refusé pour coût exponentiel et absence
  de budget honnête.

## Suivi

- Contrat normatif :
  `docs/P64_V2H03_INTERNAL_VARIANT_COORDINATION_CONTRACT.md`.
- P64-V2H03B implémente la frontière locale, les certificats et les fixtures,
  sans modifier la sélection publique.
- P64-V2H03C branche la sélection globale paresseuse, les lanes et la
  télémétrie, puis prépare une gate Fusion distincte si le résultat visible
  change.
- P45-M001 reste bloquée par P44-V et conserve ses propres décisions de formes
  et d'UX.
- `fusion-validated: false` et `print-validated: false` pour P64-V2H03.
