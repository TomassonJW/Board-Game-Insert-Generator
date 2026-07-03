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

L'integration future prend la forme d'un add-in Python Fusion 360 isole dans
`fusion_addin/BoardGameInsertGenerator`.

Responsabilites de l'adaptateur :

- lire ou recevoir une CAD IR deja resolue ;
- creer une boite de reference ;
- creer d'abord des bodies nommes dans le composant racine pour le smoke test minimal ;
- reserver la creation de composants enfants a une phase compatible Assembly ;
- creer les esquisses et extrusions autorisees ;
- appliquer des parametres utilisateurs Fusion si utile dans une phase future ;
- exporter les modules en STL ou 3MF dans une phase ulterieure.

## Squelette et generation minimale

Le squelette actuel vit dans `fusion_addin/BoardGameInsertGenerator`, hors du
coeur `src/board_game_insert_generator`.

Il contient :

- un manifeste d'add-in JSON `BoardGameInsertGenerator.manifest` ;
- un point d'entree Fusion `BoardGameInsertGenerator.py` avec `run(context)` et
  `stop(context)` ;
- une couche `fusion_skeleton.py` testable hors Fusion ;
- une fixture locale `cad_ir_input.json` pour le smoke test manuel ;
- un override local optionnel `cad_ir_path.txt` pour pointer vers une CAD IR exportee ailleurs.

Le squelette peut importer `adsk` uniquement dans le fichier d'entree Fusion. La
couche testable et le coeur Python restent sans dependance Fusion.

Le smoke test P4-M003 evite volontairement `Occurrences.addNewComponent` afin
de rester compatible avec les documents Fusion Part Design qui n'acceptent qu'un
seul composant. Les composants CAD IR sont donc materialises par des sketches,
features et bodies nommes dans le composant racine.

Depuis `P4-M003`, l'add-in code une premiere generation minimale :

- detection d'un document Fusion actif ;
- signalement explicite du cas Zero Doc ;
- chargement de `cad_ir_input.json` dans le dossier add-in ;
- validation de la CAD IR serialisee ;
- creation d'une esquisse de reference de boite non imprimable ;
- creation de sketches et bodies rectangulaires simples dans le composant racine ;
- statut `manual validation required` tant que Fusion 360 n'a pas ete lance et
  inspecte par Thomas.

Depuis `P4-M004`, le pipeline d'entree est stabilise sans elargir la geometrie :

- l'add-in resout l'entree depuis `cad_ir_input.json` ou depuis le chemin declare
  dans `cad_ir_path.txt` ;
- les chemins relatifs de `cad_ir_path.txt` sont resolus depuis le dossier de
  l'add-in ;
- les erreurs d'override vide, fichier absent, JSON invalide, schema invalide et
  unites invalides affichent un message Fusion actionnable ;
- le fichier charge reste une CAD IR deja calculee par le coeur Python.

## Representation intermediaire

Le moteur fournit maintenant une CAD IR V0 documentee dans
`docs/CAD_IR_CONTRACT.md` et implementee dans
`src/board_game_insert_generator/cad_ir.py`.

La scene V0 contient :

- boite de reference non imprimable ;
- composants CAD IR nommes ;
- corps imprimables rectangulaires ;
- dimensions theoriques et dimensions imprimables ;
- classifications de faces ;
- tolerances appliquees ;
- operations abstraites `create_rectangular_prism` ;
- parametres et metadata de nommage ;
- warnings du moteur.

L'adaptateur Fusion convertit cette representation en operations CAO sans
recalculer layout ou tolerances.

## Premiere cible Fusion

La premiere cible Fusion se limite a des blanks rectangulaires :

- sketches, features et bodies nommes dans le composant racine ;
- dimensions issues de `printable_origin_mm` et `printable_size_mm` ;
- boite de reference sous forme d'esquisse non imprimable ;
- aucun creusage avance ;
- aucun couvercle ;
- aucun fillet/conge ;
- aucun export STL/3MF ;
- aucun algorithme d'optimisation nouveau.

## Choix API Fusion P4-M003

Apres verification de la documentation officielle Autodesk, l'approche retenue
est `sketch + extrusion` :

- `Design.rootComponent` fournit le composant racine utilise par le smoke test ;
- `Sketches.add` cree une esquisse sur le plan XY du composant racine ;
- `SketchLines.addTwoPointRectangle` cree l'empreinte rectangulaire ;
- `ExtrudeFeatures.addSimple` cree le body avec `NewBodyFeatureOperation` ;
- `ValueInput.createByString("... mm")` garde des longueurs explicites en
  millimetres pour l'extrusion.

Liens de reference :

- <https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/Design_rootComponent.htm>
- <https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/Sketches_add.htm>
- <https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/SketchLines_addTwoPointRectangle.htm>
- <https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/ExtrudeFeatures_addSimple.htm>
- <https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/ValueInput_createByString.htm>

Le B-Rep direct est reporte : il est plus adapte a une couche geometrique plus
avancee, alors que P4-M003 doit seulement prouver des blocs rectangulaires
inspectables.

## Debug local

Avant de lancer Fusion 360, chaque configuration doit pouvoir etre testee par :

```powershell
$env:PYTHONPATH = "src"
python -m board_game_insert_generator examples/simple_box.json --format markdown
python -m unittest discover -s tests
```

Cette boucle courte evite de debugger la logique metier dans l'environnement
Fusion.

La partie testable du squelette Fusion peut aussi etre lancee hors Fusion :

```powershell
$env:PYTHONPATH = "src"
python -m unittest discover -s tests -p test_fusion_skeleton.py
```

## Strategie de test

Tests hors Fusion :

- validation de config ;
- layout ;
- tolerances ;
- rapports ;
- serialization de la representation intermediaire ;
- chargement CAD IR locale ou pointee par `cad_ir_path.txt` ;
- plan de generation Fusion sans import `adsk` ;
- resolution du fichier CAD IR et erreurs de chargement testees hors Fusion ;
- conversion millimetres vers centimetres internes Fusion.

Verifications dans Fusion :

- presence du sketch de reference non imprimable dans le composant racine ;
- presence des bodies de blanks dans le composant racine ;
- noms ;
- dimensions ;
- origines ;
- absence de cavites, couvercles, fillets et exports ;
- absence de recalcul metier dans l'adaptateur.

## Limitations attendues

- L'API Fusion 360 impose son modele d'objets et ses contraintes d'unites.
- Le debug d'add-in est plus lent que le debug Python local.
- Les operations booleennes complexes peuvent echouer si la geometrie est fragile.
- Les exports STL/3MF devront etre verifies par module dans une phase future.
- Une verification Fusion ne remplace pas une validation par impression reelle.

## Rapport de gate actuel

Le rapport `docs/FUSION_360_GATE_REPORT.md` a prepare la decision humaine avant
toute integration Fusion 360 executable. La mission `P4-M001` a livre le contrat
CAD-agnostic. La mission `P4-M002` ajoute un squelette d'adaptateur isole. La
mission `P4-M003` code la premiere generation minimale de blanks rectangulaires.
La mission de stabilisation P4-M004/P4-M006 rend le chemin CAD IR consommable par
Fusion plus robuste sans ajouter de geometrie.

La fixture P4-M003 a ete validee manuellement dans Fusion. Toute nouvelle CAD IR
exportee doit encore etre inspectee dans Fusion avant d'etre consideree validee,
et aucune validation d'impression reelle n'est revendiquee.

## Gates avant elargissement Fusion

Avant d'elargir la generation Fusion :

- `docs/STATUS.md` doit indiquer que le contrat intermediaire, le squelette et la
  generation minimale sont prets ;
- le backlog doit pointer une mission Fusion precise ;
- les tests du coeur Python doivent passer ;
- la validation manuelle P4-M003 est documentee, mais toute nouvelle CAD IR doit
  etre inspectee avant usage ;
- aucune logique metier nouvelle ne doit etre prevue uniquement dans Fusion.