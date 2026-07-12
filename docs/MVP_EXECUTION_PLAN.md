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
| P43 | Smoke Fusion historique | Scene geometrique du jeu temoin | Observation Fusion ; ne vaut pas acceptance produit |

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

P43 a d abord ete defini comme une gate MVP, mais le retour produit du
2026-07-12 a etabli que son smoke ne couvre que la scene geometrique. La sortie
MVP est transferee a P60 : le contrat complet doit etre vert avant un smoke
Fusion de la scene finale. Une campagne physique reste distincte et
`print-validated: false` reste obligatoire.

Resultat historique : le jeu temoin de 20 pieces CAD et 19 cavites a recu le
retour `Fusion P43 OK`. Cette preuve est conservee comme
`fusion-validated-geometry-only`, jamais comme acceptation V0.1.

## Chemin V0.2, bloque jusqu'a P60

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

## Reprise corrective V0.1 apres P43

P43 est reouvert par ADR-0053 : son smoke valide une scene geometrique, pas le
MVP produit. ADR-0054 corrige ensuite la semantique de volume : les cavites sont
calibrees, les enveloppes exterieures des bacs sont extensibles et aucun corps de
remplissage automatique n est autorise. La sortie V0.1 est P60 :

| Lot | Resultat | Preuve de sortie |
| --- | --- | --- |
| P52 | Audit, contrat d acceptance et statuts corriges | Documents coherents avec vision, code et retour humain |
| P53 | Cavites fixes / enveloppes extensibles | ADR-0054, vision et invariants coherents |
| P54 | Architecture UX premium | Wireframe, composants, etats, mode simple/avance |
| P55 | Contrat executable cavite/minimum/final | Schema, migration et tests de non-deformation des cavites |
| P56 | Editeur premium complet | Tests d interaction sur toutes les saisies et validations |
| P57 | Partition et expansion des bacs | Zero corps automatique, couverture et diagnostics |
| P58 | Resultat premium fidele | Apercu issu du plan, surplus parois/fond explique |
| P59 | CAD/Fusion fidele | Correspondance plan/CAD, palette non bloquante |
| P60 | MVP V0.1 accepte | Scenarios verts puis smoke Fusion humain unique |

Les lots P44 a P50 restent hors chemin tant que P60 n est pas accepte.
