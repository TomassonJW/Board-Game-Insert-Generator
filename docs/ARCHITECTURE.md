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
- `docs/ROADMAP.md` pour les phases macro ;
- `docs/BACKLOG.md` pour les missions ;
- `docs/DECISIONS/` pour les ADR ;
- `docs/LOGS/` pour les jalons et changements d'orientation.

## Couches logicielles

### 1. Configuration

Responsabilite : charger une description utilisateur depuis JSON V0.

Fichiers actuels :

- `src/board_game_insert_generator/config_loader.py`
- `docs/CONFIG_SCHEMA.md`
- `examples/*.json`

La configuration ne doit contenir aucun secret et toutes les dimensions sont en
millimetres.

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

- `row_fill` est la seule strategie implementee ;
- `grid` et `columns` sont des identifiants reserves pour missions futures, pas
  des comportements executables ;
- le layout produit uniquement des `Cell` theoriques, sans appliquer de
  tolerance et sans creer de geometrie CAD ;
- le tri de `row_fill` reste deterministe : priorite descendante, puis ordre de
  declaration dans la configuration ;
- une extension de strategie doit rester dans le coeur Python pur et recevoir
  ses tests avant tout adaptateur Fusion 360.

### 5. Tolerances

Responsabilite : transformer les cellules theoriques en corps imprimables.

Fichier actuel :

- `src/board_game_insert_generator/tolerance.py`

Le moteur applique des jeux selon les faces : contre la boite, contre un voisin,
libre, ou sous couvercle. Les volumes internes soudes d'un meme futur module
composite ne doivent pas recevoir de jeu entre eux.

### 6. Geometrie abstraite

Responsabilite : produire une representation intermediaire claire, independante
de Fusion.

Etat actuel :

- dataclasses Python ;
- rapport JSON ;
- rapport Markdown ;
- concepts de primitives, cavites et features deja nommes.

Etat cible :

- operations geometriques abstraites ;
- booleens conceptuels : union, cut, shell, fillet, chamfer ;
- metadata de nommage ;
- mapping vers Fusion 360.

### 7. Adaptateur Fusion 360

Responsabilite future : convertir la geometrie abstraite en composants Fusion
360.

Cette couche ne doit pas recalculer le layout, ni porter les decisions de
tolerance. Elle doit recevoir des `PrintableBody`, `Cavity` et `Feature` deja
resolus.

### 8. Interfaces utilisateur futures

Responsabilite future : rendre la configuration accessible.

Options possibles :

- CLI locale ;
- formulaire desktop ou web local ;
- import CSV ;
- import Google Sheets ;
- assistant de conception.

Ces options ne doivent pas modifier le contrat du moteur pur.

## Flux actuel

1. Lire un fichier JSON.
2. Construire `InsertConfig`.
3. Valider la configuration.
4. Generer des `Cell`.
5. Appliquer les tolerances pour produire des `PrintableBody`.
6. Generer un rapport Markdown ou JSON.

## Flux cible Fusion

1. Lire une configuration ou un projet deja resolu.
2. Executer le moteur pur.
3. Recevoir une representation CAD-agnostic.
4. Creer une boite de reference Fusion.
5. Creer un composant par module.
6. Appliquer esquisses, extrusions, shells, cuts, fillets et chamfers.
7. Exporter ou laisser inspecter les composants.

## Decisions structurantes connues

- ADR-0001 : moteur Python pur avant Fusion 360.
- ADR-0002 : separation cellule theorique / corps imprimable.
- ADR-0003 : JSON d'abord, CSV/Sheets plus tard.
- ADR-0004 : documentation comme plan de controle projet.
