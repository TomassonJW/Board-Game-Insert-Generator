# CAD IR Contract

## Objectif

La CAD IR est une representation intermediaire CAD-agnostic entre le moteur BGIG
et les futurs adaptateurs CAD. Elle prepare Fusion 360 sans importer Fusion,
sans creer elle-meme d'add-in executable et sans exporter de STL/3MF.

## Statut

Statut : `implemente` pour le contrat V0 de blanks rectangulaires, couvert par
tests unitaires Python purs.

La sortie Fusion concrete est maintenant codee pour des blanks rectangulaires
minimaux dans le composant racine. Elle a ete lancee et mesuree pour la fixture
P4-M003, mais toute nouvelle CAD IR exportee doit rester inspectee dans Fusion.
Cela ne vaut pas validation d'impression reelle.

## Frontieres

La CAD IR doit :

- rester dans le coeur Python pur ;
- etre serialisable en structures Python simples ;
- utiliser uniquement des millimetres ;
- recevoir des donnees deja resolues par le moteur ;
- exposer les dimensions theoriques et imprimables sans les recalculer ;
- conserver les classifications de faces et tolerances appliquees ;
- fournir des noms et metadata utiles aux futurs adaptateurs.

La CAD IR ne doit pas :

- importer `adsk` ;
- appeler Fusion 360 ;
- recalculer layout ou tolerances ;
- creer un script ou add-in Fusion executable ;
- exporter STL/3MF ;
- pretendre a une validation CAD ou impression.

## Scene V0

Le module `board_game_insert_generator.cad_ir` expose `build_blank_cad_scene`.
Cette fonction transforme un `InsertConfig` et un `LayoutResult` deja resolus en
`CadScene`.

La scene contient :

- `schema_version` : version du contrat, actuellement `cad_ir.v0` ;
- `units` : toujours `mm` ;
- `coordinate_system` : `right_handed_z_up_mm` ;
- `frame` : repere global ;
- `box_reference` : boite de reference non imprimable ;
- `parameters` : valeurs utiles au futur adaptateur ;
- `components` : un composant par instance de module ;
- `metadata` : projet, source, strategie de layout, profil d'impression et warnings.

## Export CLI

La commande `export-cad-ir` execute le coeur BGIG puis serialise la scene CAD IR
V0 dans un JSON stable et lisible :

```powershell
$env:PYTHONPATH = "src"
python -m board_game_insert_generator export-cad-ir examples/simple_box.json --output fusion_addin/BoardGameInsertGenerator/cad_ir_input.json
```

Le chemin de sortie est libre. Pour alimenter l'add-in Fusion installe, deux
methodes sont supportees :

1. ecrire ou copier le fichier genere sous le nom `cad_ir_input.json` dans le
   dossier `BoardGameInsertGenerator` charge par Fusion ;
2. ecrire le fichier ailleurs et placer dans le dossier de l'add-in un fichier
   `cad_ir_path.txt` dont la premiere ligne non vide pointe vers ce JSON.

L'export ne modifie pas les valeurs de tolerance, ne recalcule pas dans Fusion et
ne cree aucun STL/3MF.

## Composants et corps

Chaque composant represente un module imprimable rectangulaire V0. Il contient :

- un identifiant stable `component:<instance_id>` ;
- un nom humain derive de l'instance et du label ;
- le `module_id`, `instance_id` et `functional_type` ;
- un corps `rectangular_blank` ;
- des metadata de source : label, index source et rotation.

Chaque corps conserve deux volumes distincts :

- `theoretical_origin_mm` et `theoretical_size_mm`, issus de la `Cell` ;
- `printable_origin_mm` et `printable_size_mm`, issus du `PrintableBody` apres
  application des tolerances.

## Operations abstraites

La CAD IR V0 represente l'intention minimale sous forme d'operations abstraites.
Pour chaque blank rectangulaire, l'operation principale est :

- `create_rectangular_prism` : creer un prisme depuis `printable_origin_mm` et
  `printable_size_mm` dans le repere de scene ;
- `subtract_rectangular_cavity` : decrire une future soustraction de cavite
  rectangulaire depuis une origine locale et une taille deja validees par le
  moteur.

Les cavites sont aussi exposees dans `body.cavities` avec `status: abstract_only`,
`fusion_generation: not_implemented` et `clearance_source`. Pour les cavites
`cards`, `sleeved_cards`, `tokens`, `dice` et `meeples`, `clearance_source`
indique si le jeu vient de `tolerances.card_clearance_mm`,
`tolerances.sleeved_card_clearance_mm`, `tolerances.token_clearance_mm` ou
`tolerances.meeple_clearance_mm`.

Ces operations sont des intentions CAD-agnostic. Elles ne sont pas des appels
Fusion et ne garantissent pas encore une sortie CAD concrete sans validation
manuelle.

## Consommation par l'adaptateur Fusion

Le squelette `P4-M002` consommait uniquement une CAD IR serialisee et produisait
un plan `planned_only`.

Depuis `P4-M003`, l'adaptateur cree une premiere geometrie minimale. Depuis
`P4-M004`, le pipeline de chargement est stabilise : l'add-in resout d'abord le
fichier CAD IR a consommer, puis valide le contrat minimal avant de construire le
plan de generation.

Resolution d'entree :

- par defaut : `cad_ir_input.json` dans le dossier `BoardGameInsertGenerator` ;
- override optionnel : `cad_ir_path.txt` dans le meme dossier ;
- dans `cad_ir_path.txt`, la premiere ligne non vide et non commentee est un
  chemin absolu ou relatif au dossier de l'add-in ;
- les erreurs de fichier absent, override vide, JSON invalide, schema ou unites
  incompatibles sont signalees avec un message actionnable dans Fusion.

Validation minimale consommee par l'add-in :

- payload JSON objet ;
- `schema_version == cad_ir.v0` ;
- `units == mm` ;
- `box_reference` objet ;
- `components` liste non vide d'objets ;
- `metadata` objet si present.

Le plan copie :

- `box_reference.origin_mm` et `box_reference.size_mm` pour une esquisse de
  reference non imprimable ;
- `body.printable_origin_mm` et `body.printable_size_mm` pour les blanks ;
- les noms de composants CAD IR, sketches, features et bodies Fusion.

Fusion ne recalcule pas les cellules, offsets, roles de faces ou tolerances. La
generation reelle reste limitee a des rectangles extrudes dans le composant
racine et ne produit aucun STL/3MF. La generation actuelle ne cree pas de
composants enfants Fusion, pour rester compatible avec les documents Part Design.
Si la CAD IR contient des operations `subtract_rectangular_cavity`, l'adaptateur
P4 les conserve comme donnees de planification mais ne les execute pas encore.

## Face roles et tolerances

La scene transporte les donnees explicables de tolerance :

- face (`x_min`, `x_max`, `y_min`, `y_max`, `z_min`, `z_max`) ;
- role (`peripheral`, `neighbor`, `exposed`, `functional`, `internal`, `welded`) ;
- raison de classification ;
- voisin eventuel ;
- offset applique ;
- regle et source de clearance ;
- indication `receives_clearance`.

Un adaptateur CAD futur doit utiliser ces donnees comme metadata et ne doit pas
les recalculer.

## Validation

Le contrat V0 est valide par tests unitaires :

- generation d'une scene depuis les exemples existants ;
- separation explicite cellule theorique / corps imprimable ;
- serialization des classifications et tolerances ;
- refus d'un layout incoherent sans corps imprimable correspondant ;
- chargement d'une fixture CAD IR locale par le squelette Fusion ;
- resolution du fichier d'entree Fusion par defaut ou via `cad_ir_path.txt` ;
- erreurs actionnables pour override vide, fichier absent et contrat CAD IR invalide ;
- export CLI d'une CAD IR JSON depuis `examples/simple_box.json` ;
- transformation en plan de generation hors Fusion ;
- serialization de cavites rectangulaires abstraites et de l'operation
  `subtract_rectangular_cavity` depuis `examples/simple_tray.json`.

La validation automatisee ne couvre pas l'execution reelle dans Fusion 360, les
exports STL/3MF ou l'impression reelle.

## Gate suivante

`P4-M003 - Generer des blanks rectangulaires Fusion` est code et valide
manuellement pour la fixture P4-M003. `P4-M005 - Exporter une CAD IR depuis la
CLI` rend la fixture regenerable depuis une configuration BGIG. `P4-M006 -
Stabiliser le pipeline CAD IR vers Fusion`, autorisee par gate humaine sous le
libelle `P4-M004`, stabilise le choix du fichier d'entree et les messages
d'erreur Fusion.

Toute extension Fusion au-dela du chargement, de la validation et des blanks
rectangulaires, notamment la premiere execution reelle de
`subtract_rectangular_cavity` par sketch/extrusion cut/boolean, ou tout export
imprimable, reste soumise a une nouvelle gate humaine.
