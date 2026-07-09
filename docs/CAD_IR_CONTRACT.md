# CAD IR Contract

## Objectif

La CAD IR est une representation intermediaire CAD-agnostic entre le moteur BGIG
et les futurs adaptateurs CAD. Elle prepare Fusion 360 sans importer Fusion,
sans creer elle-meme d'add-in executable et sans exporter de STL/3MF.

## Statut

Statut : `implemente` pour le contrat V0 de blanks rectangulaires, couvert par
tests unitaires Python purs.

La sortie Fusion concrete est maintenant codee pour des blanks rectangulaires
minimaux et des cavites rectangulaires simples dans le composant racine. Les
blanks P4-M003 ont ete lances et mesures dans Fusion. Les coupes de cavites
P6-M001 sont codees mais restent a inspecter et mesurer manuellement dans
Fusion. Cela ne vaut pas validation d'impression reelle.

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
- `metadata` : projet, source, strategie de layout, profil d'impression, warnings et assets chargees.

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

## Extensions cible sans incompatibilite

La North Star elargie demande que la CAD IR transporte plus tard des informations
volumetriques sans forcer Fusion a recalculer :

- assets sources et liens vers modules/cavites derives ;
- layers et reservations de boards, livrets, plateaux ou couvercle ;
- volumes libres et contraintes d'empilement ;
- ordre de retrait et metadata d'accessibilite ;
- intentions de vue compacte et de vue eclatee ;
- scores et raisons de variantes quand un solveur existera. Depuis P10-M003, les rapports JSON exposent deja des `rejection_reasons` structurees ; elles ne sont pas encore transportees comme metadata CAD IR dediee.

Ces extensions devront rester additives ou passer par une nouvelle version de
schema. Elles ne doivent pas rendre une CAD IR `cad_ir.v0` existante invalide
sans ADR et gate humaine.
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
  moteur ;
- `describe_cavity_feature` : decrire une future aide ergonomique de cavite,
  comme une encoche de doigt, une demi-lune ou un fond arrondi, sans l'executer dans Fusion.

Les cavites sont aussi exposees dans `body.cavities` avec `status: abstract_only`,
`fusion_generation: not_implemented` et `clearance_source`. Pour les cavites
`cards`, `sleeved_cards`, `tokens`, `dice` et `meeples`, `clearance_source`
indique si le jeu vient de `tolerances.card_clearance_mm`,
`tolerances.sleeved_card_clearance_mm`, `tolerances.token_clearance_mm` ou
`tolerances.meeple_clearance_mm`.

Les features de cavites sont exposees dans `body.cavities[].features` avec
`status: abstract_only` et `fusion_generation: not_implemented`. Les operations
`describe_cavity_feature` recopient `kind`, `placement`, `position_mm`, `size_mm`
et `radius_mm` pour un futur adaptateur.

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
generation reelle reste limitee a des rectangles extrudes et ne produit aucun
STL/3MF. Les chemins P4/P6/P11 historiques creaient des bodies dans le composant
racine pour rester compatibles avec les documents Part Design ; la correction P7
cree maintenant un `Component` Fusion par module physique afin de produire des
occurrences compactes/eclatees liees.
Depuis `P6-M001`, si la CAD IR contient des operations
`subtract_rectangular_cavity`, l'adaptateur construit des coupes rectangulaires
simples : footprint locale X/Y, depart sur le dessus du blank, extrusion cut
verticale descendante, et `participantBodies` limite au body cible. Il refuse les
coupes qui debordent X/Y, retirent toute la hauteur ou violent le plancher minimal
exprime par `local_origin_mm.z`.

Depuis `P6-M002`, l'adaptateur peut aussi consommer les operations
`describe_cavity_feature` pour les encoches simples de paroi. Les kinds
`finger_notch`, `side_notch`, `center_notch` et `half_moon_notch` sont mappes en
coupe rectangulaire quand le placement est frontal. Pour `half_moon_notch`, cette
coupe est une approximation de bounding box top-open ; la CAD IR conserve
l'intention de demi-lune, mais Fusion ne cree pas encore de geometrie courbe.
Dans l'adaptateur Fusion, `size_mm.z` est la profondeur depuis le haut du body,
pas une hauteur de fenetre fermee. `rounded_floor` reste planifie seulement et
non execute.

## Metadata de grille volumetrique

Depuis P8-M001, `metadata.volumetric_grid` transporte une synthese additive quand
la configuration declare `volumetric_grid` : taille d'unite, nombre d'unites,
coverage en millimetres, cells `free` / `occupied` / `reserved` / `forbidden`,
layers, placements de modules, zones et volume libre approximatif.

Depuis P8-M002, cette metadata inclut aussi `support_surfaces` et
`removal_sequence`. Depuis P9-M002, `metadata.assets` transporte aussi les
assets charges avec `status: loaded_only`. Depuis P10-M004,
`metadata.module_candidates` transporte des propositions deterministes
`candidate_only`, `reservation_only` ou `blocked`, sans creer de composants CAD.
Depuis P10-M005, `metadata.asset_candidate_variants` et
`metadata.recommended_asset_candidate_variant` exposent aussi la variante
recommandee report-only. Depuis P10-M006, les candidats peuvent referencer
plusieurs `source_asset_ids` quand un grouping deterministe a ete applique.
Depuis P10-M007, une variante rejetee peut aussi etre transportee dans cette
metadata avec `rejection_reasons` et `recommended_asset_candidate_variant: null`.
Depuis P10-M008, `metadata.executable_asset_plan` transporte aussi les modules
generes abstraits, leurs placements grille X/Y/Z et leurs refus eventuels. Depuis
P11-M001, l'adaptateur Fusion peut consommer cette metadata pour creer une vue
compacte de bodies rectangulaires positionnes par le moteur. Le smoke test humain
`P11-M001V` du 2026-07-06 valide ce chemin pour `simple_asset_executable_plan`.
Depuis P11-M002, la meme metadata transporte la scene multi-layer
`simple_multilayer_grid_scene` : `summary` inclut `multi_layer_module_count`,
`z_placed_module_count` et `height_variant_count`.

Depuis P11-M003, les placements asset-first distinguent explicitement :

- `origin_units` / `size_units` : occupation discrete dans la grille ;
- `theoretical_grid_origin_mm` / `theoretical_grid_extent_mm` : reservation
  theorique en millimetres correspondant aux unites de grille ;
- `asset_fit_size_mm` : enveloppe asset avec clearance interne ;
- `printable_body_origin_mm` / `printable_body_size_mm` : corps rectangulaire
  imprimable que Fusion doit creer ;
- `size_mm` : alias de `printable_body_size_mm` pour les placements generes ;
- `module_source` : `asset_candidate` pour les modules generes depuis assets, `legacy_blank` pour les anciens components CAD IR ;
- `placement_source` : `grid_placement` pour les placements X/Y/Z resolus, `cad_ir_component` pour les blanks legacy ;
- `source_asset_ids` et `candidate_id` : mapping produit permettant de relier le body Fusion aux assets source ;
- `body_size_source` dans le plan Fusion hors CAD IR : source effective de sizing consommee par l'adaptateur ;
- `grid_slack_mm` : marge visible entre span grille et body imprimable ;
- `grid_semantics: placement_reservation_lattice_v0` : la grille reserve des cellules de placement ;
- `body_snap_to_grid: no` : le body n'est pas force a la taille exacte du span ;
- `grid_span_is_reserved_space: yes` : le span reste une reservation/occupation ;
- `body_size_may_be_smaller_than_grid_span: yes` : le body imprimable peut etre plus petit que le span theorique.

Les adaptateurs CAD doivent utiliser `printable_body_size_mm` pour la geometrie
reelle des modules asset-first generes. Ils peuvent afficher ou valider
`theoretical_grid_extent_mm`, mais ne doivent pas l'extruder comme body si une
taille imprimable est presente. Pour les placements modernes qui declarent un span grille theorique, une taille `printable_body_size_mm` manquante est une erreur de contrat et doit etre refusee par l'adaptateur. Ces donnees ne valident aucune portance physique
et ne doivent pas etre utilisees par Fusion pour recalculer le solveur.
Depuis P11-M003V4, une scene produit asset-first peut avoir `components: []` si `metadata.executable_asset_plan.placements` contient les modules generes a creer. Cette forme evite de melanger un blank legacy avec un module asset-first dans le smoke test produit. Les fixtures techniques peuvent encore combiner `components` et `executable_asset_plan` pour tester collisions et compatibilite.

Cette metadata ne change pas `schema_version`, ne cree aucune operation Fusion et
ne remplace pas les dimensions `theoretical_*` / `printable_*` des bodies. Un
adaptateur CAD peut l'ignorer sans invalider la CAD IR V0.

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
- plan de coupes rectangulaires simples depuis `subtract_rectangular_cavity` ;
- refus des coupes Fusion qui debordent X/Y ou qui suppriment le plancher requis ;
- plan de coupes d'encoches simples de paroi depuis `describe_cavity_feature` ;
- refus des encoches qui ciblent une cavite absente, depassent la cavite ou
  traversent plus que l'epaisseur de paroi disponible ;
- serialization de cavites rectangulaires abstraites et de l'operation
  `subtract_rectangular_cavity` depuis `examples/simple_tray.json` ;
- serialization de features ergonomiques abstraites et des operations
  `describe_cavity_feature` depuis `examples/simple_finger_notch_tray.json`.

La validation automatisee ne couvre pas l'execution reelle dans Fusion 360, les
exports STL/3MF ou l'impression reelle. Depuis P11-M001, elle couvre aussi le
plan de modules asset-first positionnes par grille, y compris conversion X/Y/Z,
collisions manifestes, sortie de boite et refus transportes. Depuis P11-M002,
elle couvre les compteurs multi-layer, les placements Z et le plan d'occurrences
liees sur `simple_multilayer_grid_scene`. Depuis P11-M003, elle verrouille aussi
la distinction entre span grille theorique, enveloppe asset-fit et taille de body
imprimable consommee par Fusion. Depuis P11-M003V2, elle couvre aussi le refus d'un placement grille moderne sans `printable_body_size_mm` et la presence du rapport Fusion `actual_fusion_body_bbox_mm`. Depuis P7-M001, elle couvre aussi le
plan d'occurrences compactes/eclatees liees, le mode `compact_only`, le rejet
d'un mode de generation inconnu, le message `assembly document required` pour les
documents Part Design incompatibles et la politique de non-renommage direct des
occurrences.

## Gate suivante

`P4-M003 - Generer des blanks rectangulaires Fusion` est code et valide
manuellement pour la fixture P4-M003. `P4-M005 - Exporter une CAD IR depuis la
CLI` rend la fixture regenerable depuis une configuration BGIG. `P4-M006 -
Stabiliser le pipeline CAD IR vers Fusion`, autorisee par gate humaine sous le
libelle `P4-M004`, stabilise le choix du fichier d'entree et les messages
d'erreur Fusion.

`P6-M001` execute les cavites rectangulaires simples depuis
`subtract_rectangular_cavity`, `P6-M002` execute les encoches simples de paroi
depuis `describe_cavity_feature`, et `P11-M001` execute la vue compacte issue des
placements grille asset-first. `P7-M001` est validee comme vue eclatee basique
par occurrences liees d'un meme composant physique. Le contexte Part Design
incompatible echoue proprement avec `assembly document required`. `P11-M002` code
la scene multi-layer compacte/eclatee. `P11-M003` corrige le sizing des modules
asset-first generes et ajoute la commande UI Fusion minimale ; cette correction
reste `manual validation required` dans Fusion. Les chemins deja valides restent
`print-validated: false`. Toute extension Fusion
au-dela de ces rectangles, notamment vue eclatee avancee, modules composites,
fonds arrondis, fillets, booleans complexes, geometrie courbe reelle ou tout
export imprimable, reste soumise a une nouvelle gate humaine.

## Note P12-M001 - UI Fusion sans changement de contrat

P12-M001 modifie uniquement le lancement UI Fusion : bouton toolbar relancable, commande `Generate Board Game Insert` et documentation de regeneration par relance. Le contrat CAD IR V0 ne change pas.

Une CAD IR reste la source unique de generation Fusion. L'add-in ne doit pas deduire ou recalculer les placements, dimensions, tolerances ou clearances depuis l'UI.

## Note P12-M002+ - UI config vers CAD IR temporaire

P12-M002+ ne change pas `schema_version` et ne modifie pas le contrat CAD IR V0.
L'add-in Fusion peut maintenant recevoir une config BGIG JSON depuis la commande
UI, appliquer des overrides V0, ecrire `bgig_ui_generated_config.json`, generer
`bgig_ui_generated_cad_ir.json` avec le coeur Python pur, puis consommer cette
CAD IR comme les exports CLI existants.

Cette couche reste un mode d'entree utilisateur. La CAD IR demeure la source de
verite pour la generation Fusion : l'adaptateur ne recalcule ni layout, ni
placements, ni clearances, ni tolerances. Les objets Fusion crees par P12-M002+
portent des attributs BGIG pour permettre un nettoyage conservateur ; ces
attributs ne font pas partie du contrat CAD IR.

### Note P12-M002V2 - Modes UI et settings locaux

P12-M002V2 ne change pas `schema_version` et ne modifie pas la CAD IR V0.
L'add-in expose des modes d'entree UI : `cad_ir_file`, `config_file` et
`quick_parametric_box` fonctionnel. `config_file` peut appliquer des overrides avant generation d'une CAD IR temporaire depuis le coeur Python ; `quick_parametric_box` construit une CAD IR temporaire minimale directement depuis les champs UI, sans changer `schema_version`.

Le fichier `bgig_ui_settings.json` est un fichier local d'add-in, hors contrat
CAD IR. Il memorise des chemins utilisateur pour eviter de retaper project root
et config a chaque generation.

## Fusion scene ownership note

La CAD IR ne porte pas la responsabilite de nettoyage de scene Fusion. Depuis
P12-M002V7, l'add-in Fusion encapsule toute generation CAD IR dans une occurrence
racine `BGIG Generated Scene` taguee `bgig:role = scene_root`.

Cette strategie est additive cote adaptateur et ne change pas le contrat CAD IR
V0 ni les dimensions exportees.
### Note P12-M003 - CAD IR temporaire quick_parametric_box

P12-M003 ne change pas `schema_version`. Le mode Fusion `quick_parametric_box` produit une CAD IR V0 temporaire locale avec :

- une boite de reference non imprimable ;
- un composant `quick-parametric-module` ;
- un corps `rectangular_blank` ;
- `theoretical_size_mm` issu d'une cellule de grille ;
- `printable_size_mm` issu des clearances et de l'epaisseur de fond ;
- metadata `quick_parametric_box` listant boite, grille, epaisseurs, clearances, profil et `print_validation: false`.

Fusion consomme cette CAD IR et ne recalcule pas le layout, les clearances ou les tolerances.

Validation Fusion `P12-M003V` du 2026-07-08 : une CAD IR temporaire
`quick_parametric_box` produite par l'add-in a genere une scene V0 en
`compact_only`, avec registry BGIG valide et bbox Fusion reelle conforme au body
imprimable planifie. Cette validation ne change pas `schema_version` et ne vaut
pas validation d'impression.

### Note P12-M004 - Settings UI hors contrat CAD IR

P12-M004 etend la persistance locale `bgig_ui_settings.json` pour restaurer les
champs de commande Fusion entre deux ouvertures. Ce fichier reste local a
l'add-in, hors contrat CAD IR, et ne change pas `schema_version`. Les adaptateurs
CAD doivent continuer a consommer la CAD IR deja resolue sans recalculer layout,
clearances ou tolerances.

## P13-M001 - Metadata quick_asset_box

La CAD IR V0 reste additive. Quand la source Fusion est `quick_asset_box`, l'addin ajoute `metadata.quick_asset_box` au payload genere par le moteur. Ce bloc reporte le format UI, les assets acceptes/refuses, les dimensions boite/grille, les compteurs de candidats, la variante recommandee et le resume `executable_asset_plan`. Il ne remplace pas `metadata.assets`, `metadata.module_candidates`, `metadata.recommended_asset_candidate_variant` ni `metadata.executable_asset_plan`.

## P13-ASSET-M002 - Metadata storage_sizing

Les candidats asset-first, modules generes et placements peuvent porter une metadata additive `storage_sizing`. Elle est informative et stable pour le reporting : `policy`, `derivation`, `count_aware_storage_sizing`, `storage_orientation`, `stack_height_policy`, `z_mm_semantics`, `available_asset_fit_height_mm`, `max_stack_height_mm`, `stack_height_used_mm`, `xy_expansion_used`, `z_expansion_used`, `total_count_read`, `declared_capacity_count`, `declared_capacity_guarantee`, `asset_diagnostics`, `pile_layout`, `content_footprint_mm`, `asset_fit_size_mm`, `module_size_mm` et `warnings`.

Cette metadata ne remplace pas les champs CAD IR existants (`dimensions_mm`, `asset_fit_size_mm`, `printable_body_size_mm`, placements grille). Fusion consomme toujours la geometrie existante et ajoute seulement un sketch debug non imprimable pour l'enveloppe asset-fit.
Depuis P15-M002, les diagnostics par asset ajoutent aussi `requested_max_stack_height_mm`, `max_stack_height_source`, `capacity_per_stack`, `items_per_pile` et la resolution de `storage_orientation`. `flat_tray` est le defaut resolu pour tokens/dice/meeples/generic ; `vertical_stack` signale explicitement le comportement legacy base sur la hauteur disponible.

Depuis P15-M003, `metadata.quick_asset_box` relaie ces informations dans les diagnostics de rapport : `max_stack_height_mm`, `storage_orientation`, `stack_height_policy`, `stack_height_used_mm`, `xy_expansion_used` et `z_expansion_used` sont visibles par asset et par candidat module pour expliquer pourquoi un plateau s'etale en XY ou monte en Z.

## P13-ASSET-M003 - Metadata asset_fit_cavity

Les modules issus de `metadata.executable_asset_plan.generated_modules` peuvent transporter une metadata additive `asset_fit_cavity`. Les placements recopient cette metadata pour que l'adaptateur Fusion puisse la consommer sans recalculer le moteur.

Payload planifie V0 :

```json
{
  "id": "asset-fit-cavity",
  "status": "planned",
  "policy": "single_asset_fit_rectangular_cavity_v0",
  "operation_kind": "subtract_rectangular_cavity",
  "coordinate_frame": "body.local",
  "local_origin_mm": {"x": 1.2, "y": 1.2, "z": 1.2},
  "size_mm": {"x": 47.6, "y": 36.6, "z": 46.8},
  "retained_floor_mm": 1.2,
  "expected_walls_mm": {"x_min": 1.2, "x_max": 1.2, "y_min": 1.2, "y_max": 1.2}
}
```

Si la cavite est impossible ou hors scope, le payload reste transportable avec `status: refused`, `code` et `reason`. Fusion ignore les cavites refusees et refuse les cavites planifiees invalides qui depassent le module ou ne conservent pas le fond demande.

## P13-ASSET-M004 - Metadata per-source compartments

La metadata `asset_fit_cavity` peut porter `policy: per_source_asset_rectangular_compartments_v0` et une liste `compartments[]`. Chaque compartiment expose `id`, `asset_id`, `source_asset_ids`, `local_origin_mm`, `size_mm`, `retained_floor_mm`, `expected_walls_mm`, diagnostics de count-aware sizing et `operation_kind: subtract_rectangular_cavity`.

Fusion consomme ces compartiments comme coupes rectangulaires top-open independantes, sans recalculer le layout.

## P13-ASSET-M005 - Metadata asset_access_notch

Chaque compartiment peut porter un objet `asset_access_notch` :

```json
{
  "id": "asset-access-notch:coin-tokens",
  "status": "planned",
  "policy": "per_compartment_top_open_rectangular_notch_v0",
  "asset_id": "coin-tokens",
  "compartment_id": "asset-compartment:coin-tokens",
  "target_wall": "front",
  "placement": "front_center",
  "coordinate_frame": "compartment.local",
  "operation_kind": "rectangular_finger_notch_cut",
  "width_mm": 18.0,
  "depth_from_top_mm": 10.0,
  "target_wall_thickness_mm": 1.2,
  "position_mm": {"x": 9.8, "y": 0.0, "z": 0.0},
  "size_mm": {"x": 18.0, "y": 1.2, "z": 10.0},
  "bbox_size_mm": {"x": 18.0, "y": 1.2, "z": 10.0},
  "reason": "Compartment touches the module front wall and has enough width/height for a rectangular top-open access notch V0."
}
```

Un refus reste serialise avec `status: refused`, `notch_generated: false` et `reason`. Les notches sont additives : elles ne changent pas `schema_version`, ne remplacent pas les operations CAD IR classiques et ne valident pas l'impression.

## P14-USABLE-ASSET-TRAY-M001 - Metadata layout multi-assets

La metadata `asset_fit_cavity` pour `per_source_asset_rectangular_compartments_v0` peut exposer `layout_strategy: deterministic_shelf_by_source_asset_v0` en plus des strategies row/column existantes. Les compartiments gardent `local_origin_mm`, `size_mm`, `expected_walls_mm`, `internal_wall_thickness_mm` et les roles optionnels `wall_role_*` pour documenter les parois internes.

Si le layout multi-assets ne tient pas, `asset_compartment_layout` peut porter `status: refused`, `code: ASSET_COMPARTMENTS_DO_NOT_FIT`, `layout_attempts` et `max_asset_fit_size_mm`. Dans ce cas, l'asset-fit cavity finale peut rester refusee avec `fallback_suppressed: true`; Fusion doit ignorer cette cavite refusee au lieu de creer une grande cavite globale trompeuse.

## P14-USABLE-ASSET-TRAY-M002 - Metadata printability_report_v0

Les entrees `metadata.executable_asset_plan.generated_modules[]` et `placements[]` peuvent transporter `printability_report_v0`. Le bloc est additif et contient `printability_checked`, `printability_validated_by_print`, `thresholds_mm`, `min_external_wall_mm`, `min_internal_wall_mm`, `min_retained_floor_mm`, `max_cavity_depth_mm`, `max_notch_depth_from_top_mm`, `checks[]` et `warnings[]`.

Cette metadata ne change pas `schema_version`, ne modifie pas les tolerances et ne vaut pas validation d'impression.


## P16-ERGONOMIC-2D-TRAY-PACKING-SPRINT - Metadata packing 2D

La CAD IR reste additive. P16 enrichit `storage_sizing`, `asset_diagnostics`, `asset_compartment_layout.compartments[]`, `asset_fit_cavity.compartments[]`, `asset_access_notch` et `metadata.quick_asset_box` avec les champs suivants quand ils sont disponibles :

- `tray_packing_policy` : `flat_tray_2d_v0` pour le nouveau comportement par defaut des assets simples, `flat_tray_linear_v0` pour le comportement legacy/fallback ;
- `target_aspect_ratio` : ratio cible largeur/profondeur utilise par l'heuristique locale ;
- `max_module_length_mm` : longueur maximale souple utilisee pour eviter une seule longue rangee ;
- `pile_grid_columns` et `pile_grid_rows` : grille locale de piles retenue ;
- `linear_layout_avoided` : `yes` si une grille multi-ranges remplace une ligne 1D, sinon `no`.

Ces champs sont informatifs et ne remplacent pas les tailles existantes (`asset_fit_size_mm`, `module_size_mm`, `printable_body_size_mm`, placements grille). Fusion consomme toujours les operations et dimensions resolues par le moteur. Les refus ou warnings doivent rester reportables sans changer `schema_version`.

P16 ne valide pas l'impression 3D, ne cree pas de geometrie par item individuel et ne rend pas le coeur Python dependant de Fusion.
