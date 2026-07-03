# Product Spec

## Produit cible

Board Game Insert Generator est un outil local de conception parametrique pour
produire des modules d'inserts de jeux de societe imprimables en 3D FDM.

Le produit doit partir d'une description structuree d'une boite, de ses assets et
des intentions de rangement, puis produire des propositions explicables :

- layout theorique ;
- modules imprimables ;
- tolerances explicites ;
- rapport de validation ;
- generation Fusion 360 dans une phase ulterieure ;
- exports exploitables a terme pour impression.

## North Star operationnelle

Transformer des contraintes de rangement mesurees en geometries imprimables,
modulaires, tolerancees, comprehensibles et iterables, sans enfermer la logique de
conception dans Fusion 360.

## Utilisateurs cibles

### Maker de jeux de societe

Veut ranger un jeu rapidement, avec peu de code. Il accepte de mesurer la boite
et les composants, mais attend des valeurs par defaut prudentes.

### Designer technique

Veut controler les tolerances, les parois, les cavites, les couvercles et les
exports. Il attend des rapports precis et des parametres reproductibles.

### Developpeur ou agent Codex

Veut etendre le moteur mission par mission, avec un backlog clair, des tests et
une architecture qui garde Fusion 360 en adaptateur.

## Entrees produit

Entrees V0/V1 :

- fichier JSON local ;
- dimensions internes de boite ;
- hauteur utile ;
- tolerances ;
- modules demandes ;
- strategie de layout ;
- exemples versionnes.

Entrees futures :

- CSV ;
- Google Sheets ;
- formulaire local ;
- assistant de conception ;
- presets par jeu ou type de composants.

## Sorties produit

Sorties actuelles :

- rapport Markdown ;
- rapport JSON ;
- cellules theoriques ;
- corps imprimables rectangulaires simples.

Sorties futures :

- composants Fusion 360 ;
- exports STL ou 3MF ;
- fiches de fabrication ;
- variantes de layouts scorees ;
- documentation utilisateur par projet.

## Capacites actuelles

Etat actuel experimental :

- chargement JSON ;
- modeles Python types par dataclasses ;
- validation de dimensions de base ;
- layout `row_fill` deterministe ;
- application de tolerances par face pour volumes rectangulaires ;
- rapport Markdown/JSON ;
- tests unitaires hors Fusion 360.

Ces capacites sont utiles pour construire le socle, mais ne constituent pas encore
un produit final imprimable.

## Capacites attendues

Le produit final doit couvrir :

- modules rectangulaires simples ;
- cavites pour cartes, cartes sleevees, tokens, meeples et des ;
- modules composites en L/T ou volumes soudes ;
- couvercles poses et coulissants ;
- mecanismes simples avec jeux fonctionnels ;
- labels, gravures, embossage et textures ;
- assistant de layout avec scoring ;
- integration Fusion 360 robuste ;
- documentation utilisateur et exemples reels.

## Principes UX

- Le mode simple doit rester rassurant pour un utilisateur non expert.
- Les options avancees doivent exister sans surcharger l'entree minimale.
- Les rapports doivent expliquer les choix, les dimensions et les limites.
- Une valeur de tolerance doit etre visible et modifiable.
- Le systeme ne doit pas pretendre qu'une impression sera parfaite sans test
  physique.

## Non-objectifs immediats

- Optimisation parfaite du rangement.
- Interface graphique complete.
- Dependances SaaS obligatoires.
- Generation directe STL/3MF avant stabilisation du modele geometrique.
- Fusion 360 comme dependance du coeur Python.
- Garantie d'impression sans prototype.

## Criteres de succes par maturite

### Fondation

Un agent peut reprendre le depot, comprendre la mission active, lancer les tests
et proposer le prochain increment sans contexte oral.

### Moteur pur

Une configuration locale produit des resultats validates, reproductibles et
testes hors Fusion 360.

### CAD

Une configuration valide produit des composants Fusion 360 inspectables, nommes
et dimensionnes correctement.

### Produit imprimable

Un utilisateur peut imprimer des modules fonctionnels pour un jeu reel, ajuster
les tolerances et documenter les ecarts constates.

### Produit assiste

Le systeme propose plusieurs layouts, explique les arbitrages et aide a choisir
selon compacite, ergonomie, impression et setup.
