# Horizons produit BGIG après V0.3

## 1. Statut et règle de lecture

Ce document est un registre de vision différée. Il conserve les directions
produit exprimées après le POC Fusion sans les rendre `ready`, sans modifier la
North Star et sans déplacer l'ordre canonique :

1. V0.1 fonctionnelle acceptée ;
2. V0.2 formes et ergonomie ;
3. V0.3 couvercles ;
4. revue P69 ;
5. lots P70+ priorisés humainement.

Les horizons V1.x, V2, V3 et V4 ci-dessous sont indicatifs. Ils servent à éviter
la perte d'idées et à préparer des frontières compatibles. Ils ne constituent ni
une promesse de version, ni une autorisation de runtime, ni des critères
d'acceptation du solveur P64 actuel.

## 2. Couverture déjà présente

| Direction produit | Couverture actuelle | Écart restant |
| --- | --- | --- |
| Coins extérieurs droits, arrondis ou chanfreinés | V0.2, P45 et `CANONICAL_PRODUCT_VISION.md` | choix par coin, rayons locaux et validation physique |
| Aides de prise, fonds arrondis, labels et finitions | V0.2, C-FEATURE et C-AESTHETIC | géométries Fusion complètes, presets et impression |
| Couvercle encastré et coulissant intérieur | V0.3, P47-P50 | autres familles de fermeture et rôles multiples |
| Grille, couches, réservations et volumes libres | C-GRID-3D, C-LAYERS, P63/P64 | surface d'édition manuelle 3D absente |
| Modules composites en L/T | C-COMPOSITE et phase 11 | unions réelles, cavités, solveur et gates physiques |
| Orientation à plat ou basculée des cartes et tuiles | P62 et P45-M001V | angles inclinés discrets et supports dédiés absents |
| Épaisseur des parois de conteneur | P45 et modèle de tolérance | rôle de cloison et surcharge locale distincte absents |

## 3. Registre des capacités futures

| ID de vision | Capacité | Horizon indicatif | Propriétaire principal | Prérequis avant activation |
| --- | --- | --- | --- | --- |
| F-SHAPE-PRIMITIVES | Conteneurs et logements extrudés circulaires, polygonaux réguliers, rectangulaires arrondis ou chanfreinés | V1.x / V2 | P45, C-GEOMETRY | contrat de forme, collision 2D, CAD IR, Fusion et coupons |
| F-SHAPE-COMPOSITE | Formes soudées, scindées ou adaptatives, par exemple un rectangle qui contourne un cercle | V2 / V3 | C-COMPOSITE puis P45 | primitives certifiées, unions, épaisseurs et accessibilité |
| F-SHAPE-ARBITRARY-3D | Maillages ou solides 3D irréguliers avec orientations libres | V4+ recherche | futur moteur géométrique | représentation, collision robuste, discrétisation et ADR majeure |
| F-ANGLED-HOLDERS | Rangeurs de cartes ou tuiles inclinés selon une liste d'angles explicites | V1.x / V2 | P45 | pose, hauteur, appui, retrait, accès et impression |
| F-CLOSED-CONTAINER-POSE | Réorientation d'un conteneur fermé dans la boîte | V2 | P64 après certificat mécanisme | fermeture retenue, rétention, six poses, stabilité et accès |
| F-DIVIDER-PROFILES | Épaisseur distincte pour cloisons internes, éventuellement par séparateur | V1.x / V2 | P45 / géométrie | modèle additif, résistance, migration et preuve physique |
| F-LID-FAMILIES | Coulissant en rainures, encastré affleurant, sommet rétreint, appuis ou grips de coins | V1.x / V2 | P47-P50 puis P70+ | tolérances locales, friction, insertion, coupons et impression |
| F-DUAL-ROLE-TRAY-LID | Plateau ou livret rigide employé comme couvercle et élément de retrait | V2 / V3 | mécanismes, P63 et P64 | rôle double, rainures, support, ordre de retrait et certificat |
| F-PER-CORNER-FINISH | Arrondi ou chanfrein choisi par coin intérieur ou extérieur | V1.x / V2 | P45 / C-AESTHETIC | topologie stable, rayons bornés, contrôles Fusion |
| F-SURFACE-FINISH | Ajourage, texte embossé ou gravé et autres finitions paramétriques | V2 | C-AESTHETIC | résistance minimale, police/licence, CAD et impression |
| F-SEMANTIC-COLORS | Couleurs par boîte, conteneur, plateau, livret et asset, avec presets accessibles | V1.x / V2 | P69 puis P70+ / UI | identités stables, contraste, thème et persistance locale |
| F-LIGHTWEIGHT-3D-PREVIEW | Aperçu 3D primitif et peu coûteux avant matérialisation Fusion | V1.x / V2 | P69 puis P70+ / renderer | lecture seule du plan, badge approximatif et aucun recalcul métier |
| F-MANUAL-3D-COMPOSER | Mode parallèle de composition sur grille 3D, avec placements, verrous et aides manuelles | V3 / V4 | P70+ / nouvelle surface d'édition | même projet, même validateur, mêmes certificats et ADR d'interface |

## 4. Frontières de responsabilité

### P45 — formes, poses et composition locale

P45 possède la forme locale d'un asset ou d'un conteneur, les cavités, les
cloisons, les poses d'assets et les futurs rangeurs inclinés. Une variante locale
doit être certifiée avant d'être offerte à P64.

Les formes sont introduites par paliers :

1. primitives 2D extrudées simples ;
2. unions ou soustractions composites bornées ;
3. formes 3D arbitraires seulement après décision architecturale dédiée.

### P64 — placement global certifié

P64 place des enveloppes et des poses déjà admissibles. Il ne dessine pas une
forme locale et ne décide pas comment fabriquer un couvercle. La réorientation
d'un conteneur fermé ne pourra devenir une pose globale que si le mécanisme
certifie sa rétention, son volume fermé et ses directions de retrait.

### P47-P50 et suites — mécanismes

Les couvercles, rainures, grips, sommets rétreints et plateaux à double rôle
changent la géométrie, les tolérances, l'ordre d'assemblage et souvent le volume
global. Ils restent un axe mécanisme distinct du solveur.

### P69/P70+ — expérience et visualisation

Les couleurs, thèmes, personnalisation, aperçu 3D et compositeur manuel sont des
capacités d'interface. L'aperçu lit un plan ; il ne le rend pas vrai. Le
compositeur manuel peut fournir plus tard des placements verrouillés ou un
incumbent, mais il ne devient jamais une seconde source de vérité géométrique.

## 5. Ce qui devient un critère solveur

Une idée devient un critère de benchmark P64 seulement lorsqu'elle modifie une
entrée ou un invariant de placement global :

- enveloppe et ensemble de poses autorisées ;
- non-chevauchement et jeux ;
- support, stabilité et retrait ;
- réservations et directions d'insertion ;
- qualité d'un plan certifié ;
- temps jusqu'au premier incumbent et aux améliorations.

Les couleurs, thèmes, textes, ajourages et style visuel ne sont pas des critères
du solveur. Les finitions peuvent seulement modifier plus tard l'enveloppe, la
résistance ou la fabricabilité transportées au solveur.

Les formes non encore supportées alimentent des familles de scénarios futurs,
pas la gate fonctionnelle du solveur rectangulaire actuel. Exiger dès maintenant
qu'un algorithme accepte toutes les formes possibles disperserait le projet et
rendrait les comparaisons incohérentes.

## 6. Mode manuel 3D différé

Le mode de grille 3D est conservé comme une future surface produit distincte,
probablement V3 ou V4. Son contrat minimal devra imposer :

- le même format de projet et les mêmes identités stables que le mode assisté ;
- des placements manuels explicites, verrouillables et annulables ;
- le validateur commun avant toute matérialisation ;
- une distinction visible entre intention, plan certifié et scène Fusion ;
- la possibilité de proposer un placement comme témoin de faisabilité, sans
  importer silencieusement la scène Fusion comme vérité ;
- une UX dédiée, sans surcharger le parcours novice actuel.

Une ADR sera requise avant de choisir son architecture d'interface et son modèle
d'édition. Aucun prototype de ce mode n'est autorisé par ce registre.

## 7. Activation et preuves

Avant de rendre une capacité de ce registre `ready`, le lot qui l'active doit :

1. confirmer sa place après P69 ou justifier explicitement une dépendance plus
   précoce ;
2. nommer son propriétaire P45, P64, mécanisme, UI ou CAD ;
3. définir le format de données et la migration ;
4. séparer preuve automatisée, observation Fusion et impression réelle ;
5. ajouter une ADR si l'architecture, une dépendance majeure ou le comportement
   public change ;
6. créer des fixtures représentatives, jamais seulement un cas à volume libre
   évident.

Le programme de mesure algorithmique associé est
`docs/P64_L06_SOLVER_BENCHMARK_CAMPAIGN.md`.
