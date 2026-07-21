# Architecture

## Principe directeur

Le moteur pur decide. Les adaptateurs exportent.

Le projet separe volontairement les calculs metier de la cible Fusion 360. Cette
separation evite de rendre les tests dependants d'un environnement CAD, facilite
le debug et prepare d'autres sorties futures comme STL, 3MF, Markdown, JSON, CSV
ou Google Sheets.

## Frontieres non negociables

- Le coeur `src/board_game_insert_generator/` ne depend pas de Fusion 360.
- L'adaptateur Fusion 360 ne decide ni du layout ni des tolerances.
- Le JSON n'est pas le modele interne.
- Les cellules theoriques ne sont pas des dimensions d'impression.
- Les modules composites ne recoivent pas de jeu entre primitives internes
  soudees.
- Les dimensions metier sont en millimetres.

## Plan de controle projet

L'architecture technique est pilotee avec :

- `AGENTS.md` pour le protocole agent ;
- `docs/STATUS.md` pour l'etat reel ;
- `docs/NORTH_STAR.md` pour la direction produit long terme ;
- `docs/CAPABILITY_MAP.md` pour relier piliers, capabilities, milestones, gates et validations ;
- `docs/ROADMAP.md` pour les phases macro ;
- `docs/BACKLOG.md` pour les missions ;
- `docs/DECISIONS/` pour les ADR ;
- `docs/LOGS/` pour les jalons et changements d'orientation.

## Architecture Tracks

La trajectoire produit est decoupee en tracks qui peuvent avancer par missions
atomiques, sans melanger les niveaux de maturite :

- `Product control plane` : North Star, capability map, roadmap, backlog, gates,
  validation matrix, ADR et logs.
- `Pure engine` : configuration, validation, layout, tolerances, cavites,
  features, assets futurs et solveur futur.
- `Volumetric model` : grille X/Y/Z, layers, reservations, volumes libres,
  empilement, ordre de retrait et support.
- `CAD IR` : contrat CAD-agnostic serialisable qui transporte les decisions du
  moteur vers des adaptateurs.
- `Fusion adapter` : sortie Fusion inspectable, sans recalcul metier.
- `Physical validation` : calibration, smoke tests Fusion, impression reelle et
  retours ergonomiques.

Un track peut etre `designed` sans etre implemente. Le statut precis vit dans
`docs/CAPABILITY_MAP.md`.

## Couches logicielles

### 1. Configuration

Responsabilite : charger une description utilisateur depuis JSON V0.

Fichiers actuels :

- `src/board_game_insert_generator/config_loader.py`
- `docs/CONFIG_SCHEMA.md`
- `examples/*.json`

La configuration ne doit contenir aucun secret et toutes les dimensions sont en
millimetres. Le champ optionnel `print_profile` choisit un preset de tolerance
local et explicite ; les champs `tolerances` restent les valeurs finales ou les
overrides visibles.

### 2. Modele metier

Responsabilite : definir les concepts stables du domaine.

Fichier actuel :

- `src/board_game_insert_generator/models.py`

Concepts principaux :

- `BoxSpec`
- `ModuleRequest`
- `ToleranceProfile`
- `Cell`
- `PrimitiveVolume`
- `CompositeModule`
- `PrintableBody`
- `Cavity`
- `Feature`
- futurs `Asset`, `Layer`, `Reservation`, `VolumetricCell` et `RemovalOrder`

### 3. Validation

Responsabilite : refuser les configurations incoherentes avant layout.

Fichier actuel :

- `src/board_game_insert_generator/validation.py`

La validation couvre deja les dimensions positives, les unites, les hauteurs
utiles, les quantites et les contraintes simples de taille. Elle devra evoluer
vers un rapport structure stable.

### 4. Layout

Responsabilite : produire des cellules theoriques dans l'espace de la boite.

Fichier actuel :

- `src/board_game_insert_generator/layout.py`

Le layout actuel est volontairement simple : les modules sont tries par priorite
et places par lignes avec `row_fill`. Cette strategie donne une base
reproductible sans pretendre resoudre l'optimisation.

Contrat Phase 2 :

- `row_fill` et `grid` sont les strategies implementees ;
- `columns` est un identifiant reserve pour mission future, pas un comportement
  executable ;
- le layout produit uniquement des `Cell` theoriques, sans appliquer de
  tolerance et sans creer de geometrie CAD ;
- le tri de `row_fill` reste deterministe : priorite descendante, puis ordre de
  declaration dans la configuration ;
- `grid` calcule une cellule reguliere XY depuis la plus grande empreinte de
  module orientee, puis place les instances en lignes et colonnes ;
- une extension de strategie doit rester dans le coeur Python pur et recevoir
  ses tests avant tout adaptateur Fusion 360.

### 5. Tolerances

Responsabilite : transformer les cellules theoriques en corps imprimables.

Fichier actuel :

- `src/board_game_insert_generator/tolerance.py`

Le moteur applique des jeux selon les faces : contre la boite, contre un voisin,
libre, ou sous couvercle. Depuis `P3-M002`, ces faces portent une classification
explicite et une application de tolerance indiquant offset, source et regle. Les
valeurs par defaut ne changent pas. Depuis `P3-M003`, un profil d'impression
opt-in peut resoudre des valeurs de tolerance experimentales, toujours visibles
dans les rapports. Les volumes internes soudes d'un meme futur module composite
ne doivent pas recevoir de jeu entre eux.

### 6. Geometrie abstraite

Responsabilite : produire une representation intermediaire claire, independante
de Fusion.

Etat actuel :

- dataclasses Python ;
- rapport JSON ;
- rapport Markdown ;
- comparaison simple de strategies de layout dans les rapports ;
- concepts de primitives et cavites deja nommes ;
- features ergonomiques abstraites associees aux cavites ;
- contrat CAD IR V0 dans `src/board_game_insert_generator/cad_ir.py`, documente
  dans `docs/CAD_IR_CONTRACT.md`.

Etat cible :

- operations geometriques abstraites ;
- metadata de layers, reservations, ordre de retrait et vues compactes/eclatees ;
- booleens conceptuels : union, cut, shell, fillet, chamfer ;
- metadata de nommage ;
- mapping vers Fusion 360.

### 7. Adaptateur Fusion 360

Responsabilite : convertir la geometrie abstraite en composants Fusion 360, sans
recalculer le layout ni les tolerances.

Etat actuel :

- add-in isole dans `fusion_addin/BoardGameInsertGenerator` ;
- point d'entree `run(context)` / `stop(context)` ;
- detection du cas Zero Doc ;
- chargement d'une CAD IR JSON locale ;
- plan de generation hors Fusion ;
- premiere generation minimale de blanks rectangulaires par esquisse + extrusion ;
- validation Fusion reelle encore manuelle.

Cette couche doit recevoir une CAD IR deja resolue. Les futurs `PrintableBody`,
`Cavity` et `Feature` doivent etre calcules dans le coeur Python pur avant d'etre
convertis par l'adaptateur. L'adaptateur ne doit pas recalculer layout, offsets
ou tolerances.

### 8. Interface utilisateur Fusion-only

Responsabilite : porter le parcours produit dans la palette HTML embarquee de
l add-in Fusion 360.

La palette edite un projet versionne, affiche les validations et le plan moteur,
puis demande explicitement la materialisation. Elle communique avec le coeur par
un bridge JSON et ne contient aucun solveur. CommandInputs reste un mode expert.

Le frontend web P23, le serveur loopback et les autres interfaces sont des
prototypes ou outils de developpement hors MVP. Ils ne sont pas requis par le
runtime utilisateur.

## Flux actuel

1. Lire un fichier JSON.
2. Construire `InsertConfig`.
3. Valider la configuration.
4. Generer des `Cell`.
5. Appliquer les tolerances pour produire des `PrintableBody`.
6. Generer un rapport Markdown ou JSON.
7. Exporter une CAD IR JSON si demande par la CLI.

## Flux cible Fusion

1. Lire une configuration ou un projet deja resolu.
2. Executer le moteur pur.
3. Recevoir une representation CAD-agnostic.
4. Creer une boite de reference Fusion.
5. Creer un composant par module.
6. Appliquer esquisses, extrusions, shells, cuts, fillets et chamfers.
7. Exporter ou laisser inspecter les composants.

Le flux P4-M003 atteint les etapes 4 et 5 pour des blanks rectangulaires simples,
mais il reste hors cavites, couvercles, fillets, exports et validation physique.
La verification dans Fusion 360 reste manuelle.

## Documents de strategie lies

- `docs/CAPABILITY_MAP.md` : lecture de pilotage par capabilities.
- `docs/VOLUMETRIC_LAYOUT_STRATEGY.md` : future grille X/Y/Z et layers.
- `docs/ASSET_MODEL_STRATEGY.md` : passage asset-first.
- `docs/SOLVER_STRATEGY.md` : solveur semi-automatique futur.
- `docs/LAYER_AND_STACKING_MODEL.md` : empilement et etages.
- `docs/ACCESSIBILITY_MODEL.md` : ordre de retrait et ergonomie.
- `docs/EXPLODED_VIEW_STRATEGY.md` : vues compactes et eclatees.

## Decisions structurantes connues

- ADR-0001 : moteur Python pur avant Fusion 360.
- ADR-0002 : separation cellule theorique / corps imprimable.
- ADR-0003 : JSON d'abord, CSV/Sheets plus tard.
- ADR-0004 : documentation comme plan de controle projet.
- ADR-0005 : regles de tolerance par role de face.
- ADR-0006 : profils d'impression explicites et surchargeables.
- ADR-0007 : representation intermediaire CAD-agnostic.
- ADR-0008 : frontiere du squelette d'adaptateur Fusion 360.
- ADR-0009 : generation Fusion minimale par esquisse et extrusion.
- ADR-0010 : cavites abstraites avant coupes Fusion.
- ADR-0011 : features ergonomiques abstraites de cavites.

## P19 completion addendum

P19 est complet contre son contrat autorise : cellules libres AABB exactes (`exact_aabb_cells_v0`), conservation de volume, diagnostics structures, coverage par asset, CLI `validate-box-fill` / `report-box-fill` / `export-box-fill-plan`, fixtures valide et invalides, bridge explicite `derived_from_executable_asset_plan` et transport CAD IR metadata. Les cellules decrivent le residuel et ne constituent pas un placement automatique. P20 greedy reste bloque par gate humaine ; Fusion ne recalcule ni ne materialise ce plan.

## P20 completion - 2026-07-10

Statut : `done`, `implemented-core`, `implemented-cli`, `implemented-cad-ir-metadata`. Le moteur `box_fill_greedy_2d.v0` produit un nouveau BoxFillPlan sans muter la source, respecte locks, modules manuels, reservations et layers, supporte la rotation XY 90 degres et expose diagnostics, digest, metrics, rapports JSON/Markdown, preview SVG et metadata CAD IR. Aucun backtracking, solveur global, UI persistante, geometrie Fusion ou validation d impression n est ajoute. P21 reste gate et recommande les variantes/scoring.

## P39 - Plan de bacs derive

Le flux V0.1 est maintenant : `bgig.project.v1` ->
`bgig.container_derivation.v1` -> reservation des plateaux P40 -> solveur global
P41 -> CAD IR/Fusion P42. `container_derivation.py` est un module Python pur :
il dimensionne les bacs et logements requis, mais ne les place pas dans la boite
et n importe aucune API Fusion. ADR-0049 fixe cette frontiere.

## P40 - Reservation de pile superieure

`flat_stack_reservation.py` est un module pur entre P39 et P41. Il reserve les
plateaux/livrets, derive la hauteur restante et demande a P39 des bacs sous cette
contrainte. Il transmet une exigence de support a P41 sans produire de geometrie
ni declarer un support physique valide. ADR-0050 fixe ce contrat.

## P41 historique et remplacement P57

`volume_closure.py` reste une fondation experimentale historique : sa
classification de regions libres ne constitue plus le plan produit. P57 le
remplace par `partition_solver.py`, module pur qui produit
`bgig.partition_plan.v1` depuis P40/P55. Le solveur choisit dimensions finales,
rotations et positions des seuls corps demandes, revalide P55 et conserve les
jeux comme vides. Il est borne et deterministe, sans pretendre etre globalement
optimal.

## P42 historique et remplacement P59

`volume_cad.py` materialise encore le plan P41 historique, y compris ses
remplissages retenus. Cette route reste testee comme fondation experimentale mais
est `superseded-for-product`. P59 produira la CAD IR exclusivement depuis
`bgig.partition_plan.v1`, sans region libre materialisee. ADR-0052 continue
d interdire toute logique de solveur ou de dimensionnement dans Fusion.

## Pipeline V0.1 corrige par ADR-0054

Le pipeline de decision est strictement sequentiel :

`projet utilisateur -> cavites calibrees -> enveloppes minimales -> reservation
plateaux/livrets -> partition et enveloppes finales -> palette Fusion -> CAD IR ->
scene Fusion`.

Le solveur de partition est la seule couche qui peut choisir les dimensions
exterieures finales. L editeur ne dessine pas les bacs a la main, la CAD IR ne
complete pas le plan et Fusion ne cree aucun remplissage. Les anciennes regions
libres P41 restent des donnees de diagnostic et de conservation, jamais une liste
de corps a imprimer.

## P58 - Projection de resultat

`partition_result_view.py` est une couche pure et en lecture seule entre
`bgig.partition_plan.v1` et la palette. Elle projette les placements reels en
vue dessus et en coupe X/Z, transforme les cavites locales P55 selon la rotation
P57 et transporte details, pile et supports. Elle ne genere pas de CAD IR et ne
peut pas dessiner une partition non construite. Le JavaScript applique seulement
les primitives SVG deja exprimees en millimetres.
## P59 - CAD IR de partition et scene Fusion

`partition_cad.py` remplace la route produit P42 historique. Il verifie que le
plan fourni correspond encore au projet normalise, transforme chaque placement
P57 en un composant `cad_ir.v0` et exprime les cavites P55 dans le repere local
du body final. Le digest CAD est deterministe et les metadata transportent le
digest P57, le nombre de composants et l invariant `automatic_body_count = 0`.

Le bridge de palette orchestre seulement ce flux. L entrypoint ecrit l IR
atomiquement puis appelle l adaptateur adsk en `compact_only`. La regeneration
supprime la scene BGIG possedee avant remplacement ; les objets non-BGIG restent
hors scope. Les routes P41/P42 de remplissage automatique restent testees mais
`superseded-for-product`.

## Portefeuille de stratégies P64

ADR-0068 remplace le solveur monolithique comme trajectoire par quatre composants
internes purs : `SolverStrategy`, `SolverCandidate`, `ValidationCertificate` et
`SolverRunTelemetry`. `stage_stack` encapsule le comportement actuel ; les
familles 3D libres utilisent le même contrat.

Les stratégies proposent, le validateur commun certifie. Une stratégie ne peut
ni recalculer les cavités, ni assouplir support/réservation, ni produire de CAD.
L'orchestrateur compare seulement des candidats certifiés et la palette projette
le résultat sans déplacer la logique dans JavaScript ou `adsk`.

La finition ADR-0069 est une couche postérieure au certificat de faisabilité.
Elle transforme les seules enveloppes extensibles, puis demande un nouveau
certificat. Son échec restitue le candidat de base. Les assets, cavités, minima,
jeux, tolérances et réservations demeurent immuables.

## Frontière des variantes internes P64-V2H03

ADR-0070 ajoute une frontière interne entre dérivation géométrique et placement
global, sans modifier le projet utilisateur. Une variante locale immuable porte
une enveloppe minimale, un layout de cavités, un digest, une provenance, un coût
local et un certificat local. P45 reste propriétaire des sémantiques et futures
formes ; P64 reçoit seulement des variantes certifiées.

Le solveur n'énumère pas leur produit cartésien. Il choisit paresseusement une
variante lorsqu'il développe un participant, puis le validateur commun certifie
le plan complet avec boîte, jeux globaux, réservations, appuis, retrait,
fermeture et conservation. La voie canonique est exécutée en premier et reste
inchangée. Ce contrat reste Python pur, sans `adsk`, nouvelle forme, schéma
projet ou matérialisation automatique.

Contrat d'exécution :
`docs/P64_V2H03_INTERNAL_VARIANT_COORDINATION_CONTRACT.md`.

## Implémentation de la frontière locale P64-V2H03B

`container_internal_variants.py` est une couche cœur pure après la dérivation
canonique et avant tout solveur global. Aucun chemin public ne l'importe dans
H03B. Elle porte snapshots immuables, producteurs, digest, certificat local et
Pareto. Le producteur canonique reste primaire ; les doublons correctifs
deviennent des alias de provenance. Le cœur reste sans `adsk`.


## Pipeline cible P64-A02 — calcul étagé

ADR-0071 ajoute une machine d'état au pipeline produit sans déplacer la logique
dans Fusion :

projet source -> analyses locales certifiées -> agencement global certifié ->
plan finalisé certifié -> CAD IR -> scène Fusion.

Les analyses locales sont indexées par digest d'asset, de conteneur et de
contraintes pertinentes. Elles sont réutilisables tant que leurs dépendances ne
changent pas. Le plan global cite chaque variante locale retenue ; la
finalisation cite le plan global ; la CAD IR cite la finalisation. Une réponse
dont le digest source n'est plus courant est rejetée à chaque frontière.

Le solve global reste l'unique propriétaire des poses monde et des jeux externes.
La finalisation peut étendre des faces autorisées ou préserver une réserve, mais
elle ne modifie ni cavités, ni minima, ni topologie fonctionnelle. Fusion reste
un adaptateur de projection et de matérialisation explicite.

## Carte de capacité dérivée P64-A02

ADR-0072 place CapacityOpportunityMap après la finalisation. Une
InternalOpportunityZone décrit de la matière potentiellement reconvertible à
l'intérieur d'un corps existant ; une BoxReserveBay décrit un volume monde
intentionnellement préservé. Ni l'une ni l'autre n'est un corps, une cavité, un
EMS autoritaire ou une source projet.

La carte est éphémère, liée aux digests source/global/final. Une insertion locale
crée une nouvelle révision de projet puis traverse à nouveau dérivation locale,
certificat global et finalisation. Le chemin accéléré évite seulement la
recherche de nouvelles poses ; il n'évite jamais la validation.
