# Fusion 360 Strategy

## Decision centrale

Fusion 360 est une cible de sortie, pas le coeur du projet.

Le moteur Python doit pouvoir calculer un layout, appliquer les tolerances et
produire un rapport sans importer `adsk.core`, `adsk.fusion` ou toute API Fusion.

## Role de Fusion 360

Fusion 360 doit servir a :

- creer des composants inspectables ;
- produire des corps parametriques ;
- appliquer des operations CAD ;
- verifier visuellement les modules ;
- exporter des fichiers imprimables dans une phase future.

Fusion 360 ne doit pas servir a :

- decider du layout ;
- recalculer les tolerances ;
- interpreter directement le JSON en contournant le moteur ;
- porter la logique de modules composites ;
- masquer les erreurs metier derriere des erreurs Fusion.

## Integration cible

L'integration future prendra probablement la forme d'un add-in Python Fusion 360
ou d'un script d'automatisation structure.

Responsabilites de l'adaptateur :

- lire ou recevoir une configuration ;
- appeler le moteur pur ;
- creer une boite de reference ;
- creer un composant par module ;
- nommer proprement les composants ;
- creer les esquisses, extrusions, shells, fillets et chamfers ;
- appliquer des parametres utilisateurs Fusion si utile ;
- exporter les modules en STL ou 3MF dans une phase ulterieure.

## Representation intermediaire

Le moteur fournit maintenant une CAD IR V0 documentee dans
`docs/CAD_IR_CONTRACT.md` et implementee dans
`src/board_game_insert_generator/cad_ir.py`.

La scene V0 contient :

- boite de reference non imprimable ;
- composants nommes ;
- corps imprimables rectangulaires ;
- dimensions theoriques et dimensions imprimables ;
- classifications de faces ;
- tolerances appliquees ;
- operations abstraites `create_rectangular_prism` ;
- parametres et metadata de nommage ;
- warnings du moteur.

L'adaptateur Fusion convertira cette representation en operations CAO sans
recalculer layout ou tolerances.

## Premiere cible Fusion

La premiere cible Fusion doit se limiter a des blanks rectangulaires :

- composants nommes ;
- dimensions correctes ;
- rayons simples ;
- boite de reference ;
- aucun creusage avance ;
- aucun couvercle ;
- aucun algorithme d'optimisation nouveau.

## Debug local

Avant de lancer Fusion 360, chaque configuration doit pouvoir etre testee par :

```powershell
$env:PYTHONPATH = "src"
python -m board_game_insert_generator examples/simple_box.json --format markdown
python -m unittest discover -s tests
```

Cette boucle courte evite de debugger la logique metier dans l'environnement
Fusion.

## Strategie de test

Tests hors Fusion :

- validation de config ;
- layout ;
- tolerances ;
- rapports ;
- serialization de la representation intermediaire.

Verifications dans Fusion :

- presence des composants ;
- noms ;
- dimensions ;
- origine ;
- rayons ;
- exports ;
- absence de recalcul metier dans l'adaptateur.

## Limitations attendues

- L'API Fusion 360 impose son modele d'objets et ses contraintes d'unites.
- Le debug d'add-in est plus lent que le debug Python local.
- Les operations booleennes complexes peuvent echouer si la geometrie est fragile.
- Les exports STL/3MF devront etre verifies par module.
- Une verification Fusion ne remplace pas une validation par impression reelle.

## Rapport de gate actuel

Le rapport `docs/FUSION_360_GATE_REPORT.md` a prepare la decision humaine avant
toute integration Fusion 360 executable. La mission `P4-M001` a maintenant livre
le contrat CAD-agnostic. La prochaine gate concerne le perimetre de `P4-M002`,
c'est-a-dire un eventuel squelette d'adaptateur Fusion.

## Gates avant implementation Fusion

Avant de coder l'adaptateur Fusion :

- `docs/STATUS.md` doit indiquer que le contrat intermediaire est pret ;
- le backlog doit pointer une mission Fusion precise ;
- les tests du coeur Python doivent passer ;
- aucune logique metier nouvelle ne doit etre prevue uniquement dans Fusion.
