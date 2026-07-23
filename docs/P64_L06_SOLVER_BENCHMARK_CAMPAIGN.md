# P64-L06 — Programme de benchmark et d'amélioration du solveur

## 1. Statut et objectif

Statut : `designed`, `execution-authorized-by-ADR-0080`.

Ce programme transforme les cas réels, synthétiques et adversariaux en preuves
comparables afin d'améliorer la capacité puis la vitesse du solveur P64. Il
prolonge P64-L05D1 et ADR-0079 ; il ne remplace ni leur corpus, ni leur gate A/B.

L'objectif n'est pas de promettre un solveur parfait. Le placement orthogonal 3D
est combinatoire et les futures formes irrégulières constituent un autre niveau
de problème. L'objectif raisonnable est :

- retrouver davantage de plans certifiés sur les cas réellement faisables ;
- expliquer les échecs bornés sans les présenter comme des impossibilités ;
- comparer plusieurs familles d'algorithmes sous les mêmes entrées et caps ;
- améliorer une hypothèse à la fois avec non-régression ;
- préparer des interfaces compatibles avec de futures formes sans les simuler
  prématurément.

P64-L06A et P64-L06B sont terminées : 13/13 bundles classés, un cas réel anonymisé, puis 192 cas T0/T1 générés.
P64-L06C est la prochaine mission runtime.
Le lancement autonome, ses ressources, checkpoints, splits et arrêts sont normés par
`docs/P64_L06_AUTONOMOUS_GOAL_RUNBOOK.md`.

## 2. Réponse au besoin d'auto-amélioration

Codex peut exécuter une campagne autonome longue en mode goal si l'objectif, les
budgets, les artefacts et les arrêts sont explicites. Cette autonomie couvre :

1. génération ou import revu de cas ;
2. exécution reproductible des solveurs ;
3. comparaison, classification et visualisation des résultats ;
4. proposition d'une modification algorithmique bornée ;
5. implémentation et gate A/B dans une mission suivante autorisée.

Le runtime BGIG ne s'auto-modifie pas. Un clic DEV ne réécrit pas l'algorithme et
un modèle d'apprentissage n'est pas entraîné silencieusement. Le flux accepté
reste :

`journal ou cas local -> validation -> anonymisation éventuelle -> replay -> diagnostic -> changement relu -> A/B -> validation`.

Le chemin utilisateur est une provenance utile, pas une preuve géométrique. Une
solution humaine connue ne devient un oracle que si ses placements normalisés
sont reconstruits et certifiés par le cœur pur.

## 3. Familles de problèmes

| Tier | Famille | Représentation | Usage |
| --- | --- | --- | --- |
| T0 | contrat P64 actuel | parallélépipèdes, rotations Z autorisées, étages, réservations, support et retrait | gate fonctionnelle actuelle |
| T1 | stress P64 actuel | T0 avec forte cardinalité, remplissage serré, voisinages trompeurs et warm start | campagne de capacité et vitesse |
| T2 | poses globales enrichies | parallélépipèdes avec poses 3D discrètes et conteneurs fermés | futur après contrat mécanisme |
| T3 | formes 2D extrudées et composites | cercle, polygone, contour, union orthogonale | futur P45/C-COMPOSITE |
| T4 | formes 3D arbitraires | voxel, maillage ou décomposition convexe | recherche V4+, hors solveur courant |

Seuls T0 et T1 participent à l'acceptation P64-L06 initiale. T2 à T4 servent à
qualifier l'architecture et les candidats futurs ; ils ne doivent pas produire
de faux échecs sur une capacité non implémentée.

## 4. Matrice de scénarios T0/T1

Le corpus étendu doit couvrir au minimum :

- cas simples de référence et impossibilités géométriques prouvables ;
- volume total compatible mais disposition impossible ;
- disposition faisable avec très peu de marge ;
- longs conteneurs minces, empreintes presque égales et permutations adverses ;
- plusieurs étages avec hauteurs hétérogènes ;
- conteneurs traversant plusieurs intervalles Z ;
- réservations supérieures localisées et appuis minimaux ;
- ordre de retrait contraint ;
- grande cardinalité et nombreux doublons dimensionnels ;
- ajout incrémental d'un asset dans une enveloppe existante ;
- ajout incrémental d'un conteneur dans le vide global ;
- reconstruction froide, witness compatible et witness incompatible ;
- même géométrie sous plusieurs ordres de déclaration lorsque le contrat
  n'impose pas cet ordre ;
- cas réels anonymisés avec échec borné et, lorsque disponible, plan certifié
  connu.

Une marge volumique positive n'est jamais une preuve de faisabilité. À l'inverse,
un `no_solution_within_budget` n'est jamais une preuve d'impossibilité.

La matrice sépare explicitement les axes locaux P45 et globaux P64. Elle couvre
les familles nombreux conteneurs/un contenu, peu de conteneurs/nombreux
contenus, nombreux/nombreux, mélange hétérogène et modification incrémentale
suivie d'une reconstruction froide. Les valeurs et la stratégie de couverture
par paires sont fixées dans le runbook ; aucun produit cartésien exhaustif n'est
requis.

## 5. Sources de vérité et oracles

### Validateur commun

Tout plan, interne ou externe, repasse par le certificat BGIG : limites de boîte,
collisions, jeux, enveloppes P45, réservations, appuis, retrait, quantités,
absence de corps automatique et digests. La sortie d'un solveur tiers n'est
jamais crue directement.

### Témoin certifié connu

Un plan produit par BGIG et recertifié reste le meilleur oracle de faisabilité
courant. Le witness P64-L05C peut initialiser une recherche compatible, mais il
ne couvre pas un projet modifié.

### Témoin humain assisté futur

Un futur artefact de développement pourra enregistrer des placements
normalisés fournis ou aidés par l'humain, puis les certifier hors Fusion. Il ne
capturera pas seulement une suite de clics et ne lira pas la scène Fusion comme
source de vérité. Son schéma et sa provenance exigeront un contrat puis, si le
comportement public change, une ADR.

### Petit oracle exact

Les petites instances T0 pourront être énumérées ou modélisées par contraintes
pour distinguer :

- faisable connu ;
- impossible prouvé dans le modèle exact ;
- inconnu après budget.

Cet oracle reste un outil de développement séparé du portefeuille produit.

## 6. Candidats externes à comparer, pas à adopter

| Candidat | Portée vérifiée | Intérêt pour BGIG | Limite ou coût |
| --- | --- | --- | --- |
| [PackingSolver](https://github.com/fontanf/packingsolver) | solveur `box` pour parallélépipèdes 3D ; solveur `irregular` séparé pour polygones 2D ; MIT | premier comparateur offline T0/T1, rotations et limite de temps | C++/CMake, adaptation des contraintes BGIG, aucune confiance sans recertification |
| [3d-bin-container-packing](https://github.com/skjolber/3d-bin-container-packing) | LAFF, heuristiques et brute force pour petit nombre de boîtes rectangulaires ; Apache-2.0 | comparator rapide, deadline et oracle partiel sur petites cardinalités | runtime Java, contraintes BGIG non natives, brute force exponentiel |
| [OR-Tools CP-SAT](https://developers.google.com/optimization/cp) | solveur de contraintes général ; primitive officielle `NoOverlap2D` | petit oracle exact ou recherche hybride après modèle BGIG explicite | dépendance lourde ; le 3D nécessite un modèle disjonctif dédié |
| [libnest2d](https://github.com/tamasmeszaros/libnest2d) | nesting de polygones 2D, LGPL-3.0 | recherche T3 pour formes locales extrudées | pas un solveur 3D global ; intégration C++ et licence à auditer |
| Approches voxel/maillage | recherche sur formes 3D irrégulières | veille T4 et futurs benchmarks | coût mémoire, collisions, robustesse et pipeline très différents |

Le fait qu'un moteur soit open source et testé ne signifie pas qu'il respecte les
réservations, supports, retraits, tolérances, identités ou certificats BGIG.
ADR-0068 continue d'interdire son ajout direct au produit sans benchmark,
analyse de licence/packaging, ADR de dépendance et GO humain.

L'ordre d'exécution évite de bloquer la campagne sur un outil tiers : petit
oracle exact interne sans dépendance, solveurs BGIG existants, puis au plus un
adapter externe déjà autorisé. PackingSolver, Java/LAFF et CP-SAT ne sont jamais
installés silencieusement et leur indisponibilité n'empêche pas L06D/L06E.

## 7. Mesures obligatoires

La comparaison est lexicographique : la vérité fonctionnelle précède toujours
la vitesse.

1. statut exact et raison d'arrêt ;
2. certificat commun et invariants violés ;
3. taux de cas faisables connus retrouvés ;
4. pertes de solutions connues, éliminatoires ;
5. qualité du plan selon les axes P64 nommés ;
6. temps jusqu'au premier plan certifié ;
7. temps et gain de chaque incumbent suivant ;
8. états, candidats, branches, déduplications et recertifications ;
9. mémoire maximale et temps CPU lorsque mesurables ;
10. stabilité des digests sur répétitions ;
11. bénéfice ou coût du warm start ;
12. résultat froid et chaud séparés.

Les temps mur sont descriptifs. Une campagne doit conserver machine, version,
nombre de workers, seed, budget et température de cache. Elle ne mélange pas les
résultats Windows, CI et autres machines dans une même revendication de vitesse.

## 8. Tiers d'exécution autonome

| Tier | Cible initiale | Budget de campagne | Usage |
| --- | --- | --- | --- |
| `ci` | 12 à 20 cas stables | moins de 60 s au total | non-régression quotidienne |
| `extended` | 100 à 300 cas générés et réels anonymisés | cap explicite, jusqu'à 2 h | comparaison de variantes |
| `soak` | 500 à 2 000 seeds ou matrices ciblées | cap explicite, jusqu'à 8 h | exploration autonome ponctuelle |

Ces nombres sont des enveloppes de départ, à réviser après mesure. Chaque run est
reprenable et écrit atomiquement :

- manifest et digest de corpus ;
- configuration machine et solveurs ;
- résultats par cas ;
- checkpoint de reprise ;
- synthèse fonctionnelle ;
- distributions de temps séparées ;
- liste des cas nouveaux ou instables.

Une campagne ne reste jamais « en cours » sans heartbeat ni timeout métier. Elle
s'arrête sur perte fonctionnelle, corruption, dérive de corpus, budget global ou
demande utilisateur.

Les cas versionnés sont séparés en `regression`, `discovery`, `tuning` et
`holdout`. Le holdout reste fermé jusqu'au choix d'une seule hypothèse. La
comparaison suit un tournoi progressif : CI, découverte, trois hypothèses
maximum, réglage, choix unique, holdout, puis soak seulement si une incertitude
précise subsiste.

## 9. Découpage de livraison

### P64-L06A — inventaire des cas réels

- valider en lecture seule les bundles et journaux locaux disponibles ;
- anonymiser et rejouer uniquement un cas cohérent s'il existe ;
- classifier les autres observations comme preuves complémentaires non promues ;
- produire un rapport d'inventaire même sans cas réel promouvable ;
- ne modifier aucun solveur.

Statut : `done`, `automated-validated`. Treize bundles classés, un seul cas anonymisé et rejoué ; aucun solveur modifié.

### P64-L06B — oracles et générateur T0/T1

- étendre le manifest L05D1 sans casser ses digests historiques ;
- produire cas faisables par construction, cas négatifs prouvables et variantes
  adversariales ;
- définir le futur témoin humain assisté sans scène Fusion autoritaire.

Statut : `done`, `automated-validated`. Huit régressions et 192 recettes ; holdout fermé, aucun solveur modifié.

### P64-L06C — adapters comparatifs offline

- normaliser l'entrée/sortie de deux candidats au maximum ;
- commencer par PackingSolver et un petit oracle interne ou CP-SAT ;
- recertifier chaque sortie par BGIG ;
- garder toute dépendance hors runtime Fusion.

Statut : `ready-after-L06B-integration`. Le petit oracle interne sans dépendance est prioritaire ; toute installation reste soumise aux gates.

### P64-L06D — campagne autonome

- exécuter `ci`, puis `extended`, puis éventuellement `soak` ;
- publier couverture, qualité, coûts et familles de lacunes ;
- sélectionner une seule hypothèse algorithmique suivante.

Statut : `planned-after-L06B/L06C`.

### P64-L06E — amélioration ciblée

- changer une lane, un ordre, une borne ou une représentation à la fois ;
- conserver caps publics et certificat sauf contrat explicitement amendé ;
- passer la gate A/B L05D1 et le corpus L06.

Statut : `planned-after-L06D`.

### P64-L06V — confirmation réelle

- rejouer dans Fusion les cas humains retenus ;
- distinguer capacité, UX, temps et matérialisation ;
- ne revendiquer aucune généralisation depuis une fixture triviale.

Statut : `future-human-gate`.

## 10. Protocole goal pour Codex

Le runbook canonique est
`docs/P64_L06_AUTONOMOUS_GOAL_RUNBOOK.md`. Le premier Goal est plafonné à 36 h,
2 Gio d'artefacts temporaires, deux workers fonctionnels et une seule
amélioration intégrée. Il reste reprenable après une pause sûre.

Un goal autonome de campagne doit nommer :

- tier et corpus exacts ;
- adapters autorisés ;
- durée maximale et budgets par cas ;
- nombre de workers ;
- espace disque maximal ;
- conditions d'arrêt ;
- livrables attendus ;
- autorisation ou non d'implémenter ensuite une amélioration.

La campagne peut tourner plusieurs heures, reprendre ses checkpoints et produire
un diagnostic sans intervention. Elle ne peut pas :

- garantir l'optimalité universelle ;
- installer silencieusement un moteur ou un service ;
- modifier plusieurs stratégies à la fois ;
- augmenter les budgets pour masquer un échec ;
- promouvoir automatiquement un projet personnel ;
- intégrer du code auto-généré sans tests et revue du diff ;
- élargir T0/T1 aux formes futures pendant le même goal.

## 11. Critères d'acceptation du programme

Le programme est considéré opérationnel seulement lorsque :

- L06A inventorie les cas réels et ne promeut que les entrées valides et anonymisées ;
- le corpus distingue faisable, impossible prouvé et inconnu borné ;
- au moins un oracle indépendant ou comparateur est recertifié par BGIG ;
- les tiers CI/extended sont reprenables et déterministes fonctionnellement ;
- les splits tuning/holdout sont séparés et le holdout reste fermé avant choix ;
- les métriques de capacité précèdent les métriques de vitesse ;
- chaque évolution du solveur est une mission atomique passée par A/B ;
- les futures formes restent reliées à
  `docs/FUTURE_PRODUCT_HORIZONS.md` sans devenir des promesses actuelles.

## 12. Hors scope absolu

- auto-apprentissage ou auto-édition dans l'add-in Fusion ;
- réseau, SaaS ou télémétrie utilisateur ;
- import automatique de projets personnels ;
- scène Fusion comme oracle ;
- faux pourcentage, ETA ou optimalité ;
- changement silencieux de schéma, tolérance, budget ou deadline ;
- implémentation de formes, couvercles, preview ou compositeur manuel ;
- nouvelle revendication sur le cas dense 11 × 34 sans preuve représentative.
