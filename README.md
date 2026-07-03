# Board Game Insert Generator

Board Game Insert Generator est un projet Python pour construire progressivement
un generateur intelligent d'inserts parametriques de jeux de societe imprimables
en 3D.

Le projet vise d'abord un moteur Python pur, testable hors Fusion 360, puis une
integration Fusion 360 comme cible de generation de composants CAD. Fusion 360 ne
doit pas porter la logique de layout, de tolerance ou de validation.

## Statut actuel

Statut : **V0 fondateur experimental**.

Le depot contient :

- un moteur Python minimal ;
- des exemples JSON ;
- des layouts rectangulaires simples `row_fill` et `grid` ;
- une application simple des tolerances par face ;
- des rapports Markdown/JSON ;
- des tests unitaires hors Fusion 360 ;
- une documentation de pilotage pour travailler mission par mission.

Le depot ne genere pas encore de composants Fusion 360, STL ou 3MF.

Consulter d'abord :

- [AGENTS.md](AGENTS.md)
- [Statut projet](docs/STATUS.md)
- [Roadmap](docs/ROADMAP.md)
- [Backlog](docs/BACKLOG.md)
- [Next actions](docs/NEXT_ACTIONS.md)

## North Star

Transformer des contraintes de rangement mesurees en geometries imprimables,
modulaires, tolerancees, comprehensibles et iterables, sans enfermer la logique de
conception dans Fusion 360.

Le produit cible doit aider a concevoir des modules pour cartes, cartes sleevees,
tokens, meeples, des, livrets, couvercles et modules composites, avec des
tolerances visibles et ajustables.

## Installation locale

Prerequis :

- Python 3.10 ou plus recent ;
- aucune dependance externe obligatoire pour le socle actuel.

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

Pour tester la strategie grille :

```powershell
$env:PYTHONPATH = "src"
python -m board_game_insert_generator examples/simple_grid.json --format markdown
```

Les rapports exposent un resume de diagnostic : strategie de layout, nombre de
modules demandes, instances generees, corps imprimables, rotations, empreinte du
layout, comparaison simple `row_fill` / `grid`, tolerances principales et
warnings. Ces informations restent une validation abstraite du moteur, pas une
validation Fusion 360 ou impression 3D.

Pour lancer un diagnostic court sans choisir un format de rapport :

```powershell
$env:PYTHONPATH = "src"
python -m board_game_insert_generator diagnose examples/simple_box.json
```

Resultat attendu : code de sortie `0` si la configuration se charge, si le layout
se genere et si les rapports Markdown/JSON peuvent etre produits. En erreur, la
CLI retourne `2` avec une categorie lisible : configuration, validation, layout
ou tolerance.

## Tests

```powershell
$env:PYTHONPATH = "src"
python -m unittest discover -s tests
```

## Architecture courte

Le coeur logique est volontairement independant de Fusion 360 :

- `config_loader.py` charge les fichiers JSON ;
- `models.py` definit le vocabulaire metier ;
- `validation.py` verifie les contraintes de base ;
- `layout.py` place les cellules theoriques ;
- `tolerance.py` transforme les cellules en corps imprimables ;
- `report.py` produit une representation lisible.

Fusion 360 sera ajoute comme adaptateur de sortie. Voir
[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) et
[docs/FUSION_360_STRATEGY.md](docs/FUSION_360_STRATEGY.md).

## Documentation principale

- [North Star](docs/NORTH_STAR.md)
- [Product Spec](docs/PRODUCT_SPEC.md)
- [Product Brief](docs/PRODUCT_BRIEF.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Modele geometrique](docs/GEOMETRY_MODEL.md)
- [Modele de tolerance](docs/TOLERANCE_MODEL.md)
- [Strategie Fusion 360](docs/FUSION_360_STRATEGY.md)
- [Schema de configuration](docs/CONFIG_SCHEMA.md)
- [Roadmap](docs/ROADMAP.md)
- [Backlog](docs/BACKLOG.md)
- [Statut](docs/STATUS.md)
- [Next actions](docs/NEXT_ACTIONS.md)
- [Glossaire](docs/GLOSSARY.md)
- [Regles qualite](docs/QUALITY_RULES.md)
- [Protocole de calibration](docs/CALIBRATION_PROTOCOL.md)
- [Decisions](docs/DECISIONS/README.md)
- [Logs](docs/LOGS/README.md)

## Regle de contribution

Avant chaque mission, lire `AGENTS.md`, `docs/STATUS.md`, `docs/ROADMAP.md`,
`docs/BACKLOG.md` et `docs/NEXT_ACTIONS.md`.

Une mission terminee doit mettre a jour le statut, le backlog et les prochaines
actions si necessaire, puis lancer les tests disponibles.

## Limites importantes

- Le layout actuel est deterministe mais non optimise.
- Les cavites, couvercles, modules composites et mecanismes sont prevus mais non
  fonctionnels.
- Les tolerances par defaut doivent etre validees par impression reelle.
- Aucun comportement Fusion 360 n'est encore implemente.

## Licence

Licence a definir avant publication ou distribution large.
