# Fusion 360 Strategy

## Decision centrale

Fusion 360 est une cible de sortie, pas le coeur du projet.

Le moteur Python doit pouvoir calculer un layout, appliquer les tolerances et produire un rapport sans importer `adsk.core`, `adsk.fusion` ou toute API Fusion.

## Integration cible

L'integration future prendra probablement la forme d'un add-in Python Fusion 360.

Responsabilites de l'add-in :

- lire ou recevoir une configuration ;
- appeler le moteur pur ;
- creer une boite de reference ;
- creer un composant par module ;
- nommer proprement les composants ;
- creer les esquisses, extrusions, shells, fillets et chamfers ;
- appliquer des parametres utilisateurs Fusion si utile ;
- exporter les modules en STL ou 3MF dans une phase ulterieure.

## Ce que l'adaptateur ne doit pas faire

- Decider du layout.
- Recalculer les tolerances.
- Interpreter directement le JSON en contournant le moteur.
- Porter la logique de modules composites.
- Masquer les erreurs metier derriere des erreurs Fusion.

## Representation intermediaire

Le moteur doit fournir une representation claire :

- corps imprimables ;
- primitives ;
- cavites ;
- features ;
- metadata de nommage ;
- warnings ;
- rapport de validation.

L'adaptateur Fusion convertit cette representation en operations CAO.

## Debug local

Avant de lancer Fusion 360, chaque configuration doit pouvoir etre testee par :

```powershell
$env:PYTHONPATH = "src"
python -m board_game_insert_generator examples/simple_box.json --format markdown
python -m unittest discover -s tests
```

Cette boucle courte evite de debugger la logique metier dans l'environnement Fusion.

## Limitations attendues

- L'API Fusion 360 impose son modele d'objets et ses contraintes d'unites.
- Le debug d'add-in est plus lent que le debug Python local.
- Les operations booleennes complexes peuvent echouer si la geometrie est fragile.
- Les exports STL/3MF devront etre verifies par module.

## Premiere cible Fusion V1

La V1 doit se limiter a des blanks rectangulaires :

- composants nommes ;
- dimensions correctes ;
- rayons simples ;
- boite de reference ;
- aucun creusage avance ;
- aucun couvercle ;
- aucun algorithme d'optimisation nouveau.
