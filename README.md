# Board Game Insert Generator

Board Game Insert Generator est une fondation Python pour concevoir des inserts parametriques de boites de jeux de societe, avec une cible initiale claire : generer a terme des composants Fusion 360 via son API Python, sans enfermer la logique produit dans Fusion 360.

Statut actuel : **V0 fondateur experimental**. Le depot contient un moteur pur minimal, des exemples JSON, des tests unitaires et une documentation de conception. Il ne genere pas encore de geometrie Fusion 360, STL ou 3MF.

## Vision courte

Le projet vise a transformer une description de boite, d'assets internes et d'intentions de rangement en propositions d'inserts imprimables en 3D FDM.

En V0, le systeme sait :

- charger une configuration JSON lisible ;
- valider les dimensions principales ;
- representer une boite, des modules demandes, des cellules de layout et des corps imprimables ;
- appliquer un modele simple de tolerance sur les faces exposees ;
- produire un layout rectangulaire trivial par lignes ;
- generer un rapport Markdown ou JSON ;
- executer des tests hors Fusion 360.

## Installation locale

Prerequis :

- Python 3.10 ou plus recent ;
- aucune dependance externe obligatoire pour la V0.

Depuis la racine du depot :

```powershell
$env:PYTHONPATH = "src"
python -m board_game_insert_generator examples/simple_box.json --format markdown
```

Pour produire un rapport JSON :

```powershell
$env:PYTHONPATH = "src"
python -m board_game_insert_generator examples/cards_and_tokens.json --format json
```

## Tests

```powershell
$env:PYTHONPATH = "src"
python -m unittest discover -s tests
```

## Architecture

Le coeur logique est volontairement independant de Fusion 360 :

- `config_loader.py` charge les fichiers JSON ;
- `models.py` definit le vocabulaire metier ;
- `validation.py` verifie les contraintes de base ;
- `layout.py` place les cellules theoriques ;
- `tolerance.py` transforme les cellules en corps imprimables ;
- `report.py` produit une representation lisible.

Fusion 360 sera ajoute comme adaptateur de sortie, pas comme moteur de decision. Voir [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) et [docs/FUSION_360_STRATEGY.md](docs/FUSION_360_STRATEGY.md).

## Principe important

Le projet ne confond pas :

- le volume interieur reel de la boite ;
- le volume utile disponible ;
- les cellules theoriques de layout ;
- les modules imprimables ajustes ;
- les cavites internes ;
- les features ajoutees ou retirees.

Cette separation est documentee dans [docs/GEOMETRY_MODEL.md](docs/GEOMETRY_MODEL.md) et [docs/TOLERANCE_MODEL.md](docs/TOLERANCE_MODEL.md).

## Limites de la V0

- Le layout automatique est volontairement simple : placement par lignes, trie par priorite.
- Les modules composites sont modelises mais pas encore generes par algorithme dedie.
- Les cavites, couvercles, charnieres, rainures et gravures sont prevus mais non implementes.
- Les tolerances sont appliquees de maniere prudente sur des volumes rectangulaires simples.
- Toute valeur de tolerance devra etre confirmee par impression reelle.

## Documentation principale

- [North Star](docs/NORTH_STAR.md)
- [Product brief](docs/PRODUCT_BRIEF.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Modele geometrique](docs/GEOMETRY_MODEL.md)
- [Modele de tolerance](docs/TOLERANCE_MODEL.md)
- [Strategie Fusion 360](docs/FUSION_360_STRATEGY.md)
- [Schema de configuration](docs/CONFIG_SCHEMA.md)
- [Roadmap](docs/ROADMAP.md)
- [Glossaire](docs/GLOSSARY.md)
- [Regles qualite](docs/QUALITY_RULES.md)

## Licence

Licence a definir avant publication ou distribution large.
