# Architecture

## Principe directeur

Le moteur pur decide. Les adaptateurs exportent.

Le projet separe volontairement les calculs metier de la cible Fusion 360. Cette separation evite de rendre les tests dependants d'un environnement CAD, facilite le debug et prepare d'autres sorties futures comme STL, 3MF, Markdown, JSON, CSV ou Google Sheets.

## Couches logicielles

### 1. Configuration

Responsabilite : charger une description utilisateur depuis JSON V0.

Fichiers actuels :

- `src/board_game_insert_generator/config_loader.py`
- `docs/CONFIG_SCHEMA.md`
- `examples/*.json`

La configuration ne doit contenir aucun secret et toutes les dimensions sont en millimetres.

### 2. Modele metier

Responsabilite : definir les concepts stables du domaine.

Fichier actuel :

- `src/board_game_insert_generator/models.py`

Concepts principaux :

- `BoxSpec`
- `ModuleRequest`
- `Cell`
- `PrimitiveVolume`
- `CompositeModule`
- `PrintableBody`
- `Cavity`
- `Feature`

### 3. Validation

Responsabilite : refuser les configurations incoherentes avant layout.

Fichier actuel :

- `src/board_game_insert_generator/validation.py`

La validation V0 couvre les dimensions positives, les unites, les hauteurs utiles, les quantites et les contraintes simples de taille.

### 4. Layout

Responsabilite : produire des cellules theoriques dans l'espace de la boite.

Fichier actuel :

- `src/board_game_insert_generator/layout.py`

Le layout V0 est volontairement simple : les modules sont tries par priorite et places par lignes. Cette strategie donne une base reproductible sans pretendre resoudre l'optimisation.

### 5. Tolerances

Responsabilite : transformer les cellules theoriques en corps imprimables.

Fichier actuel :

- `src/board_game_insert_generator/tolerance.py`

Le moteur applique les jeux selon les faces : contre la boite, contre un voisin, libre, ou sous couvercle. Les volumes internes soudes d'un meme futur module composite ne doivent pas recevoir de jeu entre eux.

### 6. Geometrie abstraite

Responsabilite : produire une representation intermediaire claire, independante de Fusion.

Etat V0 :

- dataclasses Python ;
- rapport JSON ;
- rapport Markdown.

Etat cible :

- operations geometriques abstraites ;
- booleens conceptuels : union, cut, shell, fillet, chamfer ;
- mapping vers Fusion 360.

### 7. Adaptateur Fusion 360

Responsabilite future : convertir la geometrie abstraite en composants Fusion 360.

Cette couche ne doit pas recalculer le layout, ni porter les decisions de tolerance. Elle doit recevoir des `PrintableBody`, `Cavity` et `Feature` deja resolus.

### 8. Interface utilisateur future

Responsabilite future : rendre la configuration accessible.

Options possibles :

- CLI locale ;
- formulaire desktop ou web local ;
- import CSV ;
- import Google Sheets ;
- assistant de conception.

Ces options ne doivent pas modifier le contrat du moteur pur.

## Flux V0

1. Lire un fichier JSON.
2. Construire `InsertConfig`.
3. Valider la configuration.
4. Generer des `Cell`.
5. Appliquer les tolerances pour produire des `PrintableBody`.
6. Generer un rapport Markdown ou JSON.

## Frontieres importantes

- Le moteur pur ne depend pas de Fusion 360.
- Les tolerances ne sont pas codees en dur dans le layout.
- Le format JSON n'est pas le modele interne.
- Les cellules theoriques ne sont pas des dimensions d'impression.
- Les modules composites ne doivent pas introduire de jeux internes entre primitives soudees.
