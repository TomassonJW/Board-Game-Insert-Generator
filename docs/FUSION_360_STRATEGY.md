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

Depuis `P4-M003`, l'add-in a code une premiere generation minimale :

- detection d'un document Fusion actif ;
- signalement explicite du cas Zero Doc ;
- chargement de `cad_ir_input.json` dans le dossier add-in ;
- validation de la CAD IR serialisee ;
- creation d'une esquisse de reference de boite non imprimable ;
- creation initiale de sketches et bodies rectangulaires simples dans le composant racine ;
- statut `manual validation required` tant que Fusion 360 n'a pas ete lance et
  inspecte par Thomas.

La correction P7-M001V change le chemin vue compacte/eclatee : les modules sont
desormais des composants Fusion avec occurrences liees, car la vision produit
refuse les copies independantes de bodies pour la vue eclatee.

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

## Cible Fusion actuelle

La cible Fusion actuelle a commence par des blanks rectangulaires, ajoute les cavites rectangulaires simples, puis les encoches simples de paroi :

- composants Fusion nommes pour les modules physiques, avec occurrences compactes/eclatees liees quand le mode P7 le demande ;
- dimensions issues de `printable_origin_mm` et `printable_size_mm` ;
- boite de reference sous forme d'esquisse non imprimable ;
- aucun creusage avance execute dans Fusion ;
- les cavites rectangulaires simples P5 peuvent etre presentes dans la CAD IR
  et sont executees par P6-M001 sous forme de cuts rectangulaires verticaux ;
- les features d'encoche simple de paroi P5-M004 sont executees par P6-M002 sous
  forme de coupes rectangulaires de bounding box ;
- les demi-lunes restent une intention abstraite, non une geometrie courbe
  revendiquee ;
- les fonds arrondis, aides avancees et fillets restent `abstract_only` et non
  executes ;
- aucun couvercle ;
- aucun fillet/conge ;
- aucun export STL/3MF ;
- aucun algorithme d'optimisation nouveau.
- depuis P11-M001, les modules generes par `metadata.executable_asset_plan` peuvent aussi etre crees comme modules rectangulaires positionnes par les placements grille.
- depuis la correction P7-M001V, l'add-in cree la vue compacte et la vue eclatee comme occurrences liees d'un meme composant physique, espacees a droite de la boite pour inspection.
- depuis P11-M003, l'add-in expose une commande UI minimale pour choisir le fichier CAD IR et le mode de generation, et utilise `printable_body_size_mm` pour les bodies asset-first generes quand ce champ est present.


## Coupes rectangulaires P6-M001

Depuis `P6-M001`, l'add-in peut executer l'operation CAD IR
`subtract_rectangular_cavity` pour les cavites rectangulaires simples.

Convention retenue :

- Fusion consomme uniquement les dimensions deja resolues dans la CAD IR ;
- la footprint X/Y de la coupe vient de `parameters.local_origin_mm.x/y` et
  `parameters.size_mm.x/y` ;
- la coupe commence sur le dessus du blank imprime (`printable_origin_mm.z + printable_size_mm.z`) et descend verticalement de `parameters.size_mm.z` ;
- `parameters.local_origin_mm.z` est interprete par l'adaptateur comme garde de
  plancher minimale demandee ;
- la coupe est refusee si elle depasse le blank X/Y, si sa profondeur retire tout
  le corps, ou si le plancher conserve est inferieur a `local_origin_mm.z` ;
- les operations `describe_cavity_feature` restent ignorees par P6-M001 ; P6-M002
  n'execute que les encoches simples de paroi sous forme rectangulaire.

Choix API Fusion : `sketch + extrusion cut` avec `CutFeatureOperation`,
`DistanceExtentDefinition`, `NegativeExtentDirection` et `participantBodies` pour
limiter la coupe au body cible. Ce choix reste plus lisible et testable qu'un
B-Rep direct pour des cavites rectangulaires simples.

Validation : le code et le plan hors Fusion sont testes automatiquement, mais la
creation et la mesure dans Fusion restent `manual validation required` tant que
Thomas n'a pas execute le smoke test P6-M001.

Liens de reference :

- <https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/ExtrudeFeatures_createInput.htm>
- <https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/FeatureOperations.htm>
- <https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/ExtrudeFeatureInput_setOneSideExtent.htm>
- <https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/DistanceExtentDefinition_create.htm>
- <https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/ParticipantBodiesSample_Sample.htm>

## Encoches simples P6-M002

Depuis `P6-M002`, l'add-in peut executer une partie des operations CAD IR
`describe_cavity_feature` : les encoches simples placees sur une paroi.

Convention retenue :

- les kinds acceptes sont `finger_notch`, `side_notch`, `center_notch` et
  `half_moon_notch` quand le placement cible `front`, `back`, `left` ou `right` ;
- la position, la taille et la cavite cible viennent uniquement de la CAD IR ;
- `half_moon_notch` est executee comme une coupe rectangulaire de bounding box,
  avec `geometry_approximation: rectangular_bounding_cut` ;
- pour ces fallbacks rectangulaires, `size_mm.z` est interprete comme
  `notch_depth_from_top_mm` ;
- le profil de coupe depasse le haut du body afin de produire une morsure ouverte
  sur le rebord, pas une fenetre fermee ;
- `rounded_floor`, fillets, conges, fonds arrondis et geometrie courbe reelle
  restent non executes ;
- la coupe est esquisse sur un plan XZ ou YZ decale sur la paroi cible ;
- les points modele du profil sont convertis en espace sketch via
  `modelToSketchSpace`, indispensable pour les plans non XY ;
- l'extrusion utilise la direction positive ou negative selon la paroi cible ;
- `participantBodies` limite la coupe au blank cible.

Validation : les plans et garde-fous sont testes hors Fusion. Les deux premiers
smoke tests P6-M002V ont revele successivement un sketch sans cut, puis une
fenetre fermee dans la paroi. Le smoke test humain apres `b27c2e7` valide une
vraie encoche top-open reliee au bord superieur du tray. Cette validation couvre
`top_open_rectangular_notch` uniquement, avec `print-validated: false`.

## Vue compacte depuis placements grille P11-M001

Depuis P11-M001, l'add-in peut consommer `metadata.executable_asset_plan` dans
une CAD IR exportee depuis un exemple asset-first. Depuis P11-M003V4,
`examples/simple_asset_product_scene.json` est le smoke test produit principal :
il ne declare aucun module manuel et ne genere aucun blank legacy. `simple_asset_executable_plan.json` reste une fixture technique de collision.

Convention retenue :

- le coeur Python decide les modules generes et leurs placements X/Y/Z ;
- Fusion consomme seulement `generated_modules`, `placements` et leurs champs de
  sizing deja resolus ;
- `printable_body_origin_mm` devient l'origine scene du body Fusion quand present,
  avec fallback sur `origin_mm` pour les anciennes CAD IR ;
- `printable_body_size_mm` devient la taille du body rectangulaire cree pour les placements asset-first modernes ;
- `module_source`, `placement_source`, `source_asset_ids`, `candidate_id` et `clearance_applied` alimentent le rapport Fusion `Module source mapping` ;
- si un placement declare `theoretical_grid_extent_mm` mais ne fournit pas `printable_body_size_mm`, l'add-in refuse de generer le body au lieu d'utiliser silencieusement le span grille ;
- le fallback `source_size_mm` / `size_mm` reste limite aux anciennes CAD IR qui ne declarent pas de span grille theorique ;
- `theoretical_grid_origin_mm` et `theoretical_grid_extent_mm` restent des
  metadata d'occupation et de validation, pas des dimensions de body ;
- les origines Z non nulles sont creees sur un plan XY decale ;
- les garde-fous hors Fusion refusent placement absent ou mal forme, dimensions
  manquantes, span hors grille, body hors boite et collision manifeste ;
- les refus deja presents dans `rejected_modules` sont reportes dans le plan et le
  message Fusion, sans creer de body ;
- les cavites rectangulaires et encoches top-open deja supportees restent
  executees pour les composants CAD IR existants ;
- aucune vue eclatee, aucun solveur, aucun module composite et aucun export STL/3MF
  ne sont ajoutes.

Validation : les conversions et garde-fous sont testes hors Fusion. Le smoke test
humain `P11-M001V` du 2026-07-06 a valide dans Fusion le chargement de
`simple_asset_executable_plan`, le message attendu, la creation de deux bodies
dont un module asset-first positionne par grille, et les dimensions alors
attendues `30.0 x 30.0 x 10.0 mm` a la position `X 30.0 mm`, `Y 0.0 mm`,
`Z 0.0 mm`. P11-M003 corrige ensuite l'ambiguite produit : `30 x 30 x 10 mm`
est l'etendue theorique d'une cellule de grille, tandis que le body imprimable
genere depuis les assets est `25.6 x 25.6 x 9.8 mm`. Depuis P11-M003V4,
`simple_asset_product_scene` devient le smoke test produit non ambigu : un seul
body asset-first, aucun blank legacy, source `asset_candidate` et placement
`grid_placement`. Cette correction requiert un nouveau smoke test Fusion et ne
vaut pas validation d'impression 3D. Depuis P11-M003V2, le message final affiche aussi un `Body sizing report` avec span grille, taille imprimable prevue, bbox reelle Fusion et `size match yes/no`. Depuis P11-M003V4, il affiche en plus `Module source mapping` : source du module, source de placement, assets contenus, vues compact/exploded, origine, span, taille imprimable et clearances peripherique/inter-module.

## Scene multi-layer depuis placements grille P11-M002

P11-M002 etend le meme chemin sans recalcul Fusion : l'add-in consomme les
placements X/Y/Z deja presents dans `metadata.executable_asset_plan` pour creer
une scene compacte + eclatee ou plusieurs modules generes occupent des hauteurs
et origines Z differentes.

Convention retenue :

- l'exemple de smoke test est `examples/simple_multilayer_grid_scene.json` ;
- le coeur Python produit un module bas `3 x 3 x 1` a `Z=0` et un module plus
  haut `2 x 2 x 2` place a `Z=1` ;
- Fusion convertit uniquement les millimetres deja resolus en transforms
  d'occurrences ;
- depuis P11-M003, les bodies multi-layer generes utilisent les dimensions
  imprimables : le module bas attend `61.6 x 61.6 x 7.8 mm`, le module haut
  attend `37.6 x 37.6 x 17.8 mm`, tandis que les spans grille restent
  respectivement `90 x 90 x 10 mm` et `60 x 60 x 20 mm` ;
- les compteurs `Multi-layer grid modules planned`, `Grid modules with Z
  placement` et `Grid module height variants` sont reportes dans le message ;
- la vue compacte et la vue eclatee restent deux occurrences liees du meme
  `Component` source ;
- aucun solveur, support physique, tolerance ou clearance n'est recalcule dans
  Fusion.

Validation : les plans et conversions sont testes hors Fusion. L'execution reelle
P11-M002 reste `manual validation required` tant que Thomas n'a pas lance le
smoke test dans Fusion. Aucune validation d'impression 3D ou de portance n'est
revendiquee.


## Commande UI Fusion minimale P11-M003

Depuis P11-M003, l'add-in n'impose plus de modifier manuellement
`cad_ir_path.txt` ou `exploded_view_mode.txt` pour un usage courant. Depuis la
correction P11-M003V3, `run(context)` enregistre une vraie commande Fusion
`Generate Board Game Insert`, l'ajoute quand possible au panneau
`Design workspace > Utilities > Add-Ins`, puis execute la commande pour ouvrir
la boite de dialogue. `run(context)` ne lance plus directement une generation de
scene sans passer par cette commande UI.

La commande affiche :

- un champ texte `CAD IR JSON path` ;
- un choix de mode `compact_only` ou `compact_and_exploded` ;
- un resume rappelant que Fusion consomme la CAD IR et ne recalcule pas layout,
  clearances ou tolerances.

Les anciens fichiers locaux restent supportes comme valeurs par defaut et comme
fallback de compatibilite, mais la procedure utilisateur normale devient :
exporter une CAD IR, lancer l'add-in, choisir le fichier et le mode, valider la
commande. Cette UI reste minimale : elle ne modifie pas les assets, ne lit pas la
configuration BGIG source et ne cree aucune nouvelle geometrie.

Validation : les helpers de requete et de mode sont testes hors Fusion. La
commande Fusion reelle reste `manual validation required` jusqu'au smoke test
P11-M003V4. P11-M003V a ete KO partiel parce que les dimensions reelles des
bodies n'etaient pas affichables/verifiables dans le message Fusion. Le test
humain suivant a ensuite montre que la commande UI n'etait pas visible ni
exploitable ; P11-M003V3 corrige l'identifiant de commande Fusion, garde les
handlers au niveau module pour eviter le garbage collection, conserve les
fichiers texte uniquement comme fallback et nettoie commande/bouton dans
`stop(context)`. P11-M003V3 a ensuite ete KO partiel cote produit parce que le smoke test utilisait une fixture melangeant blank legacy et module asset-first ; P11-M003V4 introduit `simple_asset_product_scene.json` et le rapport `Module source mapping`.

## Vue eclatee basique P7-M001

Depuis la correction P7-M001V, l'add-in peut creer une vue eclatee basique en
plus de la vue compacte sans dupliquer les bodies de maniere independante.

Convention retenue :

- le mode local par defaut est `compact_and_exploded` ;
- un fichier optionnel `exploded_view_mode.txt` peut contenir `compact_only` pour
  revenir au comportement compact seul ;
- toute autre valeur de mode est refusee avant generation ;
- chaque module physique BGIG devient un unique `Component` Fusion ;
- la geometrie rectangulaire, les cavites et les encoches top-open deja
  supportees sont creees dans la definition du composant ;
- l'occurrence compacte est positionnee selon l'origine CAD IR deja resolue ;
- l'occurrence eclatee est creee via reference au meme composant et placee sur
  une grille 2D simple a droite de la boite ;
- les noms lisibles sont portes par les composants sources ;
- les noms exacts d'occurrences dans le Browser peuvent etre generes par Fusion ;
- l'add-in ne tente pas de renommer directement `Occurrence.name` ;
- les roles compact/exploded sont explicites dans le plan hors Fusion et le message final ;
- les dimensions restent celles de la CAD IR ;
- aucun module composite, export, fillet, courbe ou solveur supplementaire n'est
  ajoute.

Cette strategie exige un document Fusion compatible avec plusieurs
composants/occurrences. Un document `Part Design` qui affiche `Part Design
documents can only contain one component` est incompatible avec P7 linked
occurrences. L'add-in intercepte ce cas et affiche `assembly document required`
avec une action claire : ouvrir/creer un document Assembly-compatible ou ajouter
le Part a une Assembly avant de relancer.

Validation : le plan, le message d'erreur et la politique de non-renommage
direct des occurrences sont testes hors Fusion. P7-M001V3 a revele que certains
contextes Fusion exposent `Occurrence.name` en lecture seule ; P7-M001V4 conserve
les occurrences liees mais ne depend plus du renommage direct des occurrences.
Le smoke test humain P7-M001V4 du 2026-07-06 valide dans un document
Assembly-compatible la vue compacte/eclatee, les occurrences liees et l'absence
de renommage direct d'occurrence. Cette validation ne vaut pas validation
d'impression 3D.
## Vue compacte et vue eclatee

La strategie long terme distingue deux sorties Fusion inspectables :

- `compact view` : modules places dans le repere de boite, utile pour verifier
  encombrement, collisions et hauteur utile ;
- `exploded view` : modules repartis a plat ou decales, utile pour inspection,
  nommage, preparation d'exports futurs et documentation.

La vue compacte existe pour les blanks rectangulaires simples et pour les
modules asset-first places par grille. La vue eclatee basique existe maintenant
comme occurrences liees d'inspection et P7-M001V4 est validee dans un document
Assembly-compatible. P11-M002 code une scene compacte/eclatee multi-layer depuis
placements X/Y/Z ; cette extension reste a valider manuellement dans Fusion.

Fusion ne doit pas inventer les positions compactes. Pour P7-M001 uniquement,
l'add-in peut calculer une disposition eclatee de presentation a partir des
volumes deja resolus dans la CAD IR ; cette disposition ne modifie pas le layout
compact, les tolerances ou les decisions moteur.

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
- conversion millimetres vers centimetres internes Fusion ;
- compatibilite des CAD IR enrichies avec cavites et features abstraites ;
- plan de coupes rectangulaires simples depuis `subtract_rectangular_cavity` ;
- garde-fous hors Fusion pour debordement X/Y, profondeur impossible, plancher
  insuffisant et body cible absent ;
- plan de coupes d'encoches simples de paroi depuis `describe_cavity_feature` ;
- garde-fous hors Fusion pour cavite absente, placement unsupported, debordement
  d'encoche et epaisseur de paroi insuffisante.

Verifications dans Fusion :

- presence du sketch de reference non imprimable dans le composant racine ;
- presence des bodies de blanks dans le composant racine ;
- presence de coupes reelles pour `subtract_rectangular_cavity` des cavites
  rectangulaires simples ;
- presence d'une coupe rectangulaire d'encoche simple de paroi pour P6-M002,
  validee comme `top_open_rectangular_notch` ;
- absence de generation reelle pour fonds arrondis, fillets et geometrie courbe ;
- noms ;
- dimensions ;
- origines ;
- dimensions et positions des cavites rectangulaires simples ;
- absence de fonds arrondis, couvercles, fillets et exports ;
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
Fusion plus robuste sans ajouter de geometrie. La mission `P6-M001` ajoute la
premiere execution reelle limitee de cavites rectangulaires simples, encore sous
validation manuelle Fusion.

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
- aucune logique metier nouvelle ne doit etre prevue uniquement dans Fusion ;
- toute execution reelle au-dela des cavites rectangulaires simples P6-M001,
  notamment features ergonomiques, booleans complexes ou geometrie courbe, doit
  repasser par une gate humaine dediee ;
- toute vue eclatee executable ou repositionnement CAD non trivial doit etre
  limite a une mission dediee et documentee.

## UI Fusion P12

P12-M001 stabilise le lancement UI sans changer la geometrie : la commande `Generate Board Game Insert` reste la commande principale, mais le bouton toolbar dans `Design workspace > Utilities > Add-Ins` devient le point de reouverture attendu si la boite de dialogue se ferme ou perd le focus.

Strategie : `toolbar_button_reopens_command_without_addin_restart`.

Invariants :

- Fusion consomme toujours une CAD IR deja resolue ;
- Fusion ne recalcule pas layout, solveur, clearances ou tolerances ;
- `cad_ir_path.txt` et `exploded_view_mode.txt` restent des defaults/fallbacks ;
- la palette persistante HTML reste une option future, documentee dans `docs/FUSION_UI_STRATEGY.md` ;
- P12-M001 ne cree aucune nouvelle geometrie et ne valide aucune impression 3D.

## UI Fusion P12-M002+ - Commande parametrique V0

P12-M002+ etend la commande Fusion existante sans changer la geometrie generee.
La strategie retenue est une commande classique enrichie, pas une palette HTML
persistante.

La commande expose maintenant `Action`, `CAD IR JSON path`, `BGIG config JSON
path`, `BGIG project root`, `Generation mode` et des champs V0 de boite, grille,
epaisseurs, clearances et profil d'impression. Quand une config est fournie,
l'add-in genere une config temporaire puis une CAD IR temporaire en important le
coeur Python pur depuis `<BGIG project root>/src`. Cette importation reste cote
add-in ; le coeur `src/board_game_insert_generator` ne depend toujours pas de
`adsk`.

Invariants :

- Fusion consomme toujours une CAD IR resolue avant generation ;
- Fusion ne recalcule pas layout, solveur, clearances ou tolerances ;
- les champs UI sont des overrides de config existante, pas une UI assets complete ;
- `Regenerate` nettoie seulement les objets BGIG tagues puis regenere ;
- `Clear BGIG Scene` refuse de supprimer les objets non tagues ;
- les geometries, dimensions et statuts physiques existants ne changent pas ;
- validation Fusion manuelle requise, `print-validated: false`.

### Correction P12-M002V2 - Clear et regenerate utilisables

P12-M002V2 conserve la geometrie Fusion existante, mais change le conteneur de
scene : chaque generation cree une occurrence racine taguee `BGIG Generated
Scene`. Les composants de modules, occurrences compactes/eclatees, sketches et
cuts restent issus de la CAD IR deja resolue.

`Clear BGIG Scene` et `Regenerate` utilisent les attributs BGIG pour supprimer
uniquement les objets BGIG. Les objets utilisateur non tagues doivent rester
presents apres clear. `Regenerate` planifie et valide la nouvelle CAD IR avant de
nettoyer l'ancienne scene, pour eviter une suppression suivie d'un echec de
chargement.

Le project root BGIG est auto-detecte ou memorise localement ; le mode CAD IR
direct reste supporte. Les overrides UI sont appliques seulement au flux
`config_file`.

### Correction P12-M002V3 - Generate refuse les doublons

P12-M002V3 conserve la geometrie Fusion existante et ne change pas la CAD IR.
La correction porte uniquement sur la securite d'action de la commande Fusion :

- l'add-in compte les racines BGIG taguees avant generation ;
- `generate` cree une scene seulement si aucune scene BGIG n'existe deja ;
- si une scene existe, `generate` refuse avec un message actionnable demandant
  `regenerate` ou `clear_bgig_scene` ;
- `regenerate` reste le chemin officiel pour remplacer une scene BGIG existante ;
- `clear_bgig_scene` reste le chemin officiel pour supprimer explicitement la
  scene BGIG ;
- les objets non BGIG ne sont pas cibles par le clear.

Cette correction evite l'accumulation silencieuse de scenes BGIG dans un document
Fusion et rend le smoke test P12 centre sur generate/regenerate/clear.

### Correction P12-M002V4 - Occurrences visibles exactes

P12-M002V4 conserve les composants lies et ne revient pas aux copies
independantes. La correction porte sur le role de l'occurrence initiale Fusion :
`addNewComponent` sert uniquement a creer le composant source, via une occurrence
helper cachee. Les occurrences visibles compactes et eclatees sont creees ensuite
avec `addExistingComponent`.

Regles :

- `compact_only` : N modules physiques donnent N occurrences compactes visibles ;
- `compact_and_exploded` : N modules physiques donnent N occurrences compactes et
  N occurrences eclatees visibles ;
- les helpers source doivent rester invisibles ;
- aucun body legacy independant ne doit etre cree ;
- `clear_bgig_scene` doit supprimer les racines, helpers, occurrences compactes
  et occurrences eclatees BGIG tagues, sans cibler les objets non BGIG.
