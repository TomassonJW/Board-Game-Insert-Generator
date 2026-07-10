# Product Spec

## Produit cible

Board Game Insert Generator est un outil local de conception parametrique pour
produire des systemes d'inserts modulaires de jeux de societe imprimables en 3D
FDM.

Le produit doit partir d'une description structuree d'une boite, de ses assets et
des intentions de rangement, puis produire des propositions explicables :

- decomposition du volume de boite ;
- reservations pour boards, livrets, regles, plateaux ou couvercle ;
- modules imprimables ;
- cavites et features ergonomiques ;
- tolerances explicites ;
- rapport de validation ;
- CAD IR ;
- generation Fusion 360 inspectable ;
- exports imprimables dans une phase future.

## North Star operationnelle

Transformer les assets reels, contraintes de boite et intentions d'usage d'un jeu
de societe en systemes volumetriques modulaires imprimables, tolerancees,
inspectables et iterables, sans enfermer la logique de conception dans Fusion 360.

## Utilisateurs cibles

### Maker de jeux de societe

Veut ranger un jeu rapidement, avec peu de code. Il accepte de mesurer la boite
et les composants, mais attend des valeurs par defaut prudentes et des rapports
lisibles.

### Designer technique

Veut controler les tolerances, les parois, les cavites, les couvercles, les
layers, les exports et les variantes.

### Developpeur ou agent Codex

Veut etendre le moteur mission par mission, via capabilities, milestones, gates,
backlog et tests.

## Entrees produit

Entrees actuelles :

- fichier JSON local ;
- dimensions internes de boite ;
- hauteur utile ;
- tolerances et profils d'impression ;
- modules demandes ;
- cavites simples ;
- features ergonomiques abstraites de cavites ;
- strategie de layout ;
- exemples versionnes.

Entrees futures :

- assets a ranger avec dimensions exactes ou approximatives ; P9-M001 en decrit
  le schema cible sans encore l'activer dans le loader ;
- volumes de contenance attendus ;
- boards, livrets, regles et plateaux a reserver ;
- contraintes de layers et empilement ;
- preferences d'accessibilite et ordre de retrait ;
- preferences de nombre de modules, ergonomie et setup ;
- CSV, Google Sheets ou formulaire local ;
- assistant de conception.

## Sorties produit

Sorties actuelles :

- rapport Markdown ;
- rapport JSON ;
- cellules theoriques 2D ;
- corps imprimables rectangulaires simples ;
- CAD IR `cad_ir.v0` ;
- blanks rectangulaires Fusion valides manuellement.

Sorties futures :

- cavites Fusion reelles ;
- vues compactes et vues eclatees ;
- variantes de layout scorees ;
- fiches de fabrication ;
- exports STL/3MF ;
- documentation utilisateur par projet.

## Product Pillars et capabilities

La liste de reference vit dans `docs/CAPABILITY_MAP.md`. Les piliers actifs sont :

- Asset-first design ;
- Volumetric layout ;
- Modular printable bodies ;
- Cavities and ergonomic features ;
- CAD generation pipeline ;
- Human validation gates ;
- Design language and aesthetics.

## Principes UX

- Le mode simple doit rester rassurant pour un utilisateur non expert.
- Les options avancees doivent exister sans surcharger l'entree minimale.
- Les rapports doivent expliquer choix, dimensions, limites et validations.
- Une valeur de tolerance doit etre visible, modifiable et reliee a sa source.
- Le systeme ne doit pas pretendre qu'une impression sera parfaite sans test
  physique.
- L'accessibilite et l'ordre de retrait comptent autant que la compacite.

## Non-objectifs immediats

- Solveur 3D complet.
- Interface graphique complete.
- Dependances SaaS obligatoires.
- Export STL/3MF avant stabilisation CAD et gate.
- Fusion 360 comme dependance du coeur Python.
- Garantie d'impression sans prototype.
- Generation Fusion reelle de cavites, encoches ou fillets sans gate.

## Criteres de succes par maturite

### Fondation

Un agent peut reprendre le depot, comprendre la mission active, identifier la
capability servie, lancer les tests et proposer le prochain increment.

### Moteur pur

Une configuration locale produit des resultats valides, reproductibles et testes
hors Fusion 360.

### Produit volumetrique abstrait

Le moteur peut representer assets, modules, cavites, features, layers,
reservations, volumes libres et ordre de retrait sans generation CAD reelle.

### CAD inspectable

Une configuration valide produit des composants Fusion inspectables, nommes et
dimensionnes correctement, avec vue compacte puis vue eclatee.

### Produit imprimable

Un utilisateur peut imprimer des modules fonctionnels pour un jeu reel, ajuster
les tolerances et documenter les ecarts constates.

### Produit assiste

Le systeme propose plusieurs layouts, explique les arbitrages et aide a choisir
selon compacite, accessibilite, impression, setup et esthetique.

## Update P18 - Produit cible operationnel

Le produit cible est un BoxFillPlan editable: inventaire asset-first, intentions, reservations, layers, modules, volumes libres et variantes scorees. La commande Fusion actuelle reste une interface de developpement; la UX premium est decrite dans docs/UX_PRODUCT_VISION.md.

## P19 completion addendum

P19 est complet contre son contrat autorise : cellules libres AABB exactes (`exact_aabb_cells_v0`), conservation de volume, diagnostics structures, coverage par asset, CLI `validate-box-fill` / `report-box-fill` / `export-box-fill-plan`, fixtures valide et invalides, bridge explicite `derived_from_executable_asset_plan` et transport CAD IR metadata. Les cellules decrivent le residuel et ne constituent pas un placement automatique. P20 greedy reste bloque par gate humaine ; Fusion ne recalcule ni ne materialise ce plan.