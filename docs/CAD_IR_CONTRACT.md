# CAD IR Contract

## Objectif

La CAD IR est une representation intermediaire CAD-agnostic entre le moteur BGIG
et les futurs adaptateurs CAD. Elle prepare Fusion 360 sans importer Fusion,
sans creer elle-meme d'add-in executable et sans exporter de STL/3MF.

## Statut

Statut : `implemente` pour le contrat V0 de blanks rectangulaires, couvert par
tests unitaires Python purs.

La couche reste experimentale pour toute sortie CAD concrete : aucun composant
Fusion, aucun fichier imprimable et aucune validation physique ne sont produits.

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
  `printable_size_mm` dans le repere de scene.

Ces operations sont des intentions CAD-agnostic. Elles ne sont pas des appels
Fusion et ne garantissent pas encore une sortie CAD concrete.

## Consommation par le squelette Fusion

Le squelette `P4-M002` consomme uniquement une CAD IR serialisee. Il valide la
version de schema, les unites `mm` et la liste de composants, puis transforme les
operations abstraites en plan `planned_only`.

Ce plan est une preparation d'adaptateur : il ne cree aucun composant Fusion,
aucun corps, aucune esquisse, aucune extrusion et aucun export.

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
- refus d'un layout incoherent sans corps imprimable correspondant.

La validation ne couvre pas Fusion 360, les exports STL/3MF ou l'impression
reelle.

## Gate suivante

`P4-M002 - Creer un squelette d'adaptateur Fusion 360` est implemente comme
squelette non generateur. La prochaine gate est `P4-M003 - Generer des blanks
rectangulaires Fusion`, car elle introduira la premiere creation reelle de
geometrie Fusion.
