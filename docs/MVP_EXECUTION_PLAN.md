# Plan d'execution canonique BGIG

## Regle de pilotage

Une seule mission est executee a la fois. Jusqu'a l'acceptation de la V0.1, une
mission n'est `ready` que si elle ferme directement un critere V0.1. Les lots
V0.2 et V0.3 restent `deferred`.

## Chemin V0.1

| Lot | Resultat utilisateur | Changement technique principal | Preuve de sortie |
| --- | --- | --- | --- |
| P36 | Vision et ordre fiables | Docs, ADR, backlog, gates | Coherence documentaire |
| P37 | Projet V0.1 representable | Schema additif : groupes de bacs, elements plats, remplissages, reglages | Tests de migration et validation |
| P38 | Saisie enfin evidente | UI boite + tableau pieces + tableau plateaux/livrets + bacs | Tests UI, build et API locale |
| P39 | Les bacs suivent les pieces | Derivation quantite/forme/groupe vers logements et bacs | Fixtures rond/carre/rectangle/custom et groupes |
| P40 | Plateaux et livrets tiennent au-dessus | Pile superieure, hauteur et supports ajustes | Tests X/Y/Z et depassements |
| P41 | Tout le volume est affecte | Solveur volumetrique borne, residus, bacs vides/pleins/separateurs | Conservation du volume et cas grande cardinalite |
| P42 | Le resultat est un insert fonctionnel | CAD IR/Fusion des bacs, logements, supports et remplissages V0.1 | Tests CAD IR puis smoke Fusion prepare |
| P43 | MVP V0.1 accepte | Parcours complet, jeu temoin, export et limites | Tests UI automatiques + observation Fusion ; print reste distinct |

## Detail des missions

### P37 - Contrat projet V0.1

- introduire un schema additif sans casser les projets existants ;
- remplacer le lien indirect asset/candidate par `container_group_id` stable ;
- representer `flat_items[]` avec type, dimensions, epaisseur, quantite et ordre ;
- representer `fill_elements[]` avec `hollow`, `solid` ou `separator` ;
- ajouter `layout_clearance_mm` global et `wall_thickness_mm` par bac ;
- garder `appearance` et `mechanism` compatibles mais inactifs dans le parcours
  principal ;
- produire une migration explicite depuis `bgig.local_composer.v0`.

### P38 - Surface de saisie V0.1

- ne montrer que les zones utiles : boite, pieces, plateaux/livrets, bacs,
  remplissage, reglages et construction ;
- ajouter/supprimer des lignes sans modal technique ;
- adapter les champs de dimensions au preset choisi ;
- proposer `Nouveau bac` puis les bacs existants dans chaque ligne ;
- afficher les reglages de paroi par bac derive ;
- garder imports, diagnostics, policies et CAD dans un panneau expert ;
- masquer apparence et couvercles jusqu'aux versions correspondantes.

### P39 - Derivation des bacs

- calculer la capacite necessaire depuis forme, dimensions et quantite ;
- creer un logement par famille ou une repartition explicable de logements ;
- fusionner uniquement les familles partageant le meme groupe de bac ;
- supporter au minimum rond, carre, rectangle, cartes, cube/de, pion et custom ;
- refuser un groupe incompatible avec une raison et une correction ;
- ne plus demander la taille externe du bac comme entree novice.

### P40 - Pile superieure

- calculer l'epaisseur totale par ligne et pour la pile ;
- choisir un ordre deterministe, ajustable en avance ;
- reserver les empreintes et l'ordre de retrait ;
- ajuster la hauteur des bacs situes dessous ;
- verifier que les surfaces de support sont suffisantes ;
- refuser toute pile qui depasse la boite.

### P41 - Fermeture du volume

- passer d'un placement 2D par layer a une recherche X/Y/Z explicite ;
- faire varier les dimensions externes des bacs dans leurs bornes ;
- traiter chaque region libre exacte ;
- proposer d'abord extension utile d'un bac, puis bac creux, separateur, et enfin
  remplissage plein explicite ;
- garantir la conservation du volume et l'absence de collision ;
- ne pas avoir de limite metier codee en dur sur le nombre de lignes ;
- borner temps/memoire et retourner un diagnostic honnete en cas d'arret.

### P42 - Geometrie fonctionnelle

- materialiser chaque bac avec ses logements V0.1 ;
- materialiser supports, remplissages et separateurs retenus ;
- conserver jeux, parois, fonds et hauteurs resolus par le moteur ;
- generer une vue compacte et une vue d'export ;
- ne materialiser ni arrondi esthetique ni couvercle.

### P43 - Gate V0.1

Le MVP est accepte quand les tests prouvent qu'un projet vide peut etre saisi,
construit, explique et exporte, puis qu'un smoke humain Fusion confirme la scene
du jeu temoin. Cette gate ne transforme pas une preuve Fusion en preuve
d'impression. Une campagne physique peut suivre en V0.1.x sans bloquer
l'existence du MVP logiciel.

Resultat : le 2026-07-12, le jeu temoin de 20 pieces CAD et 19 cavites a recu le
retour humain `Fusion P43 OK`. Le MVP logiciel V0.1 est accepte dans Fusion ;
`print-validated: false` reste obligatoire.

## Chemin V0.2, bloque jusqu'a P43

| Lot | Resultat |
| --- | --- |
| P44 | Contrat de formes/ergonomie et contraintes de resistance |
| P45 | Arrondis externes, chanfreins, encoches et fonds faciles a vider |
| P46 | Preview live fidele, Fusion et acceptation V0.2 |

P33 sert seulement de matiere de prototype ; aucun statut V0.2 n'est herite.

## Chemin V0.3, bloque jusqu'a P46

| Lot | Resultat |
| --- | --- |
| P47 | Nouveau contrat de couvercles conforme a la vision canonique |
| P48 | Couvercle encastrable et hauteur integree au solveur |
| P49 | Couvercle coulissant dans trois rainures interieures, entree ouverte |
| P50 | Coupons, calibration 0-0,2 mm, Fusion puis impressions mesurees |

ADR-0045 et P34 ne sont pas reutilises comme specification fonctionnelle. Les
primitives generiques techniquement valides peuvent l'etre si elles respectent
le nouveau contrat.

## Risques a traiter explicitement

- le packing 3D et le dimensionnement conjoint peuvent devenir couteux ;
- une solution mathematiquement compacte peut etre peu imprimable ou difficile
  a retirer ;
- des plateaux de tailles differentes exigent plusieurs empreintes superieures ;
- un remplissage plein augmente poids et temps d'impression ;
- le jeu nul d'un couvercle n'est pas une garantie physique ;
- la grande cardinalite exige benchmarks et bornes, pas une promesse vague.

Chaque risque doit produire un test, un diagnostic ou une gate, jamais une note
cachee dans un rapport technique.
