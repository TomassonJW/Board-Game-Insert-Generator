# Configuration Schema V0

## Format

Le format V0 est JSON pour rester local, lisible et simple a valider.

Toutes les dimensions sont en millimetres. Le champ `units` doit valoir `mm`.

## Validation stricte

Le loader V0 refuse les champs inconnus aux niveaux suivants :

- racine du document, incluant `print_profile`, `assets` et `volumetric_grid` ;
- `box` ;
- `box.inner_dimensions_mm` ;
- `tolerances` ;
- `defaults` ;
- `layout` ;
- chaque entree de `modules` ;
- chaque `modules[].min_dimensions_mm` ;
- chaque `modules[].cavities` ;
- chaque `modules[].cavities[].features` ;
- `volumetric_grid`, ses `layers`, `module_placements`, `zones` et
  `support_surfaces`.

Les types sont egalement verifies au chargement :

- les dimensions, tolerances et valeurs de defaults doivent etre numeriques ;
- `priority` et `quantity` doivent etre des entiers JSON ;
- `allow_rotation` et `layout.allow_global_rotation` doivent etre booleens ;
- `project_name`, `id`, `name` et `comment` doivent etre des chaines si fournis.

Les contraintes metier agregees, comme dimensions positives, hauteur utile,
quantites strictement positives et ids dupliques, restent validees par
`validation.py` afin de retourner plusieurs issues actionnables quand c'est
possible.

## Structure generale

```json
{
  "project_name": "Example insert",
  "units": "mm",
  "box": {},
  "print_profile": "default",
  "tolerances": {},
  "defaults": {},
  "layout": {},
  "assets": [],
  "volumetric_grid": {},
  "modules": []
}
```

## Cible asset-first et volumetrique

Le schema V0 reste `module-first` : le loader accepte `modules`, `cavities`,
`features` et le bloc optionnel `volumetric_grid`. Il n'accepte pas encore de
champ racine `reservations` independantes ou `solver`. Le champ racine `assets` est accepte depuis P9-M002 comme donnees passives.

La cible produit de Phase 8/9 introduira, sous gate si le schema public change :

- `assets` : materiel reel a ranger, avec dimensions exactes ou approximatives ;
- `volumetric_grid.zones` : reservations ou zones interdites declaratives ;
- `volumetric_grid.layers` : contraintes de hauteur et etages declaratifs ;
- `accessibility` : ordre de retrait, zones de prise et contraintes de setup ;
- `solver_preferences` : preferences de nombre de modules, compacite, ergonomie
  et variantes.

Ces champs sont documentes dans `docs/ASSET_MODEL_STRATEGY.md`,
`docs/VOLUMETRIC_LAYOUT_STRATEGY.md`, `docs/LAYER_AND_STACKING_MODEL.md` et
`docs/ACCESSIBILITY_MODEL.md`. En P8-M001/P8-M002, seul `volumetric_grid` est implemente
comme extension additive du loader V0 : grille, layers, placements explicites,
zones reservees/interdites, ordre de retrait abstrait et surfaces de support
non validees physiquement.
## `box`

Champs obligatoires :

- `inner_dimensions_mm.x`
- `inner_dimensions_mm.y`
- `inner_dimensions_mm.z`
- `usable_height_mm`
- `lid_clearance_mm`

Convention :

- `inner_dimensions_mm` represente le volume interieur mesure ;
- `usable_height_mm` represente la hauteur maximale allouee aux modules ;
- `lid_clearance_mm` represente une contrainte physique reservee sous couvercle.

## `print_profile`

Champ optionnel racine.

Valeurs reconnues :

- `default` : valeurs V0 par defaut ;
- `pla_standard` : point de depart PLA standard ;
- `petg_standard` : point de depart PETG standard ;
- `fast_draft` : point de depart impression rapide ;
- `fine_detail` : point de depart detail fin.

Le profil est resolu en `ToleranceProfile`, puis les champs explicites de
`tolerances` surchargent les valeurs du profil champ par champ. Les profils sont
experimentaux et ne constituent pas une validation physique.

## `tolerances`

Champs reconnus :

- `peripheral_clearance_mm`
- `module_gap_mm`
- `vertical_lid_clearance_mm`
- `card_clearance_mm`
- `sleeved_card_clearance_mm`
- `token_clearance_mm`
- `meeple_clearance_mm`
- `sliding_lid_clearance_mm`
- `hinge_clearance_mm`
- `printer_compensation_mm`
- `default_corner_radius_mm`
- `default_chamfer_mm`

Les valeurs absentes utilisent les valeurs par defaut du moteur.

## `defaults`

Champs reconnus :

- `wall_thickness_mm`
- `floor_thickness_mm`
- `corner_radius_mm`

Ces champs ne pilotent pas encore une geometrie creuse en V0, mais ils fixent le contrat pour les versions suivantes.

## `layout`

Champs reconnus :

- `strategy` : `row_fill` ou `grid` en V0. L'identifiant `columns` est reserve
  dans le contrat interne, mais encore refuse par la validation.
- `allow_global_rotation` : reserve pour evolution future.


## `volumetric_grid`

Champ optionnel racine introduit par P8-M001. Il decrit une grille X/Y/Z
declarative dans le coeur Python pur. Il ne declenche aucun solveur automatique
et aucune generation Fusion reelle.

Champs reconnus :

- `unit_mm.x`, `unit_mm.y`, `unit_mm.z` : dimensions d'une unite discrete ;
- `size_units.x`, `size_units.y`, `size_units.z` : nombre d'unites dans la grille ;
- `layers` : liste optionnelle de bandes Z ;
- `module_placements` : liste optionnelle d'occupations explicites de modules ;
- `zones` : liste optionnelle de zones `reserved` ou `forbidden` ;
- `support_surfaces` : liste optionnelle de surfaces de support abstraites ;
- `comment` : note humaine optionnelle.

Validation P8-M001 :

- `unit_mm` doit etre strictement positif ;
- `size_units` doit etre strictement positif ;
- `unit_mm.x * size_units.x` doit couvrir `box.inner_dimensions_mm.x` ;
- `unit_mm.y * size_units.y` doit couvrir `box.inner_dimensions_mm.y` ;
- `unit_mm.z * size_units.z` doit couvrir `box.usable_height_mm` ;
- les layers, placements et zones doivent rester dans la grille ;
- un placement de module doit referencer un module existant ;
- les dimensions millimetres couvertes par un placement doivent etre au moins
  egales a la demande de module ;
- les collisions entre placements, zones reservees et zones interdites sont
  refusees ;
- P8-M002 valide les references de surfaces de support, les directions d'acces
  et les ordres de retrait abstraits.

### `volumetric_grid.layers[]`

- `id` : identifiant stable ;
- `name` : nom humain ;
- `z_start` : index Z de depart ;
- `z_count` : nombre d'unites Z ;
- `role` : role documentaire ;
- `comment` : note optionnelle.

### `volumetric_grid.module_placements[]`

- `id` : identifiant stable ;
- `module_id` : module reference ;
- `instance_id` : instance attendue optionnelle, par exemple `cards-stack-01` ;
- `origin_units.x/y/z` : origine discrete ;
- `size_units.x/y/z` : extension discrete ;
- `layer_id` : layer optionnel ;
- `removal_order` : ordre de retrait abstrait optionnel, entier strictement positif ;
- `access_direction` : `top`, `front`, `back`, `left`, `right`, `any` ou
  `unspecified` ; requis si `removal_order` est defini ;
- `support_surface_id` : reference optionnelle vers une surface de support ;
- `comment` : note optionnelle.

### `volumetric_grid.zones[]`

- `id` : identifiant stable ;
- `kind` : `reserved` ou `forbidden` ;
- `purpose` : intention, par exemple `future_board_or_rulebook_reservation` ;
- `origin_units.x/y/z` : origine discrete ;
- `size_units.x/y/z` : extension discrete ;
- `layer_id` : layer optionnel ;
- `reservation_kind` : classification documentaire, par exemple `flat_asset_layer` ;
- `asset_kind` : type d'asset reserve, par exemple `board_or_rules` ;
- `removal_order` : ordre de retrait abstrait optionnel, refuse sur les zones
  `forbidden` ;
- `access_direction` : direction d'acces declaree ;
- `support_surface_id` : reference optionnelle vers une surface de support ;
- `comment` : note optionnelle.

### `volumetric_grid.support_surfaces[]`

- `id` : identifiant stable ;
- `owner_type` : `grid_floor`, `module_placement` ou `zone` ;
- `owner_id` : `grid` pour `grid_floor`, sinon id du placement ou de la zone ;
- `face` : `top`, `bottom`, `front`, `back`, `left` ou `right` ;
- `origin_units.x/y/z` : origine discrete de la surface ;
- `size_units.x/y/z` : extension discrete ;
- `layer_id` : layer optionnel ;
- `purpose` : intention, par exemple `abstract_support` ;
- `comment` : note optionnelle.

Ces surfaces sont des intentions abstraites. Elles ne prouvent ni resistance,
ni portance, ni imprimabilite physique.

Voir `examples/simple_3d_grid.json`, `examples/simple_3d_reservations.json`, `examples/simple_asset_product_scene.json` et `examples/simple_asset_executable_plan.json`.

Depuis P10-M008, aucun nouveau champ de configuration n'est ajoute : le plan executable asset-first est derive des champs existants `assets`, `modules` et `volumetric_grid`. Depuis P11-M003V4, un exemple produit asset-first peut declarer `modules: []` : dans ce cas, seuls les modules generes depuis `assets` sont exportes vers `metadata.executable_asset_plan`, sans blank legacy issu de `components`. `simple_asset_executable_plan.json` reste une fixture technique avec module manuel declare.

## `modules`

Chaque module contient :

- `id` : identifiant stable ;
- `name` : nom humain ;
- `functional_type` : `cards`, `sleeved_cards`, `tokens`, `meeples`, `dice`, `free`, `other` ;
- `min_dimensions_mm.x` ;
- `min_dimensions_mm.y` ;
- `height_mm` ;
- `priority` ;
- `allow_rotation` ;
- `quantity` ;
- `comment` ;
- `cavities` : liste optionnelle de cavites rectangulaires simples abstraites.

`min_dimensions_mm.z` est accepte mais optionnel. Si absent, le moteur utilise `height_mm`.

## `modules[].cavities`

Chaque cavite simple est un volume rectangulaire local au module. Elle decrit une
intention de creusage future, sans execution Fusion en P5-M001.

Champs reconnus :

- `id` : identifiant stable de cavite, optionnel mais recommande ;
- `functional_type` : type fonctionnel de la cavite, optionnel ; par defaut le
  type du module est utilise ;
- `origin_mm.x`, `origin_mm.y`, `origin_mm.z` : origine locale de la cavite dans
  le module ;
- `size_mm.x`, `size_mm.y`, `size_mm.z` : dimensions internes de la cavite ;
- `clearance_mm` : jeu fonctionnel associe a la cavite. Obligatoire pour les cavites `free` et `other` ; optionnel pour `cards`, `sleeved_cards`, `tokens`, `dice` et `meeples`, ou il est resolu depuis le profil actif ;
- `comment` : note humaine optionnelle ;
- `features` : liste optionnelle de features ergonomiques abstraites associees a
  la cavite.

Validation P5-M001/P5-M002/P5-M003 :

- dimensions de cavite strictement positives ;
- origine et clearance non negatives ;
- les cavites `cards`, `sleeved_cards`, `tokens`, `dice` et `meeples` doivent respecter au minimum le jeu du profil actif ;
- les rapports et la CAD IR exposent `clearance_source` (`explicit`, `tolerances.card_clearance_mm`, `tolerances.sleeved_card_clearance_mm`, `tolerances.token_clearance_mm` ou `tolerances.meeple_clearance_mm`) ;
- la cavite doit rester dans les dimensions externes du module ;
- les parois X/Y doivent conserver `defaults.wall_thickness_mm` ;
- le fond doit conserver `defaults.floor_thickness_mm` ;
- la cavite reste abstraite et non validee par impression ;
- les features de cavite restent abstraites et ne sont pas generees dans Fusion.

## `modules[].cavities[].features`

Chaque feature de cavite est une intention ergonomique locale a une cavite. Elle
prepare une future generation CAD sans l'autoriser encore.

Champs reconnus :

- `id` : identifiant stable de feature, optionnel mais recommande ;
- `kind` : obligatoire, parmi `finger_notch`, `side_notch`, `center_notch`,
  `half_moon_notch`, `rounded_floor` et `grip_aid` ;
- `taxonomy` : optionnel, parmi `top_open_rectangular_notch`,
  `top_open_half_moon_notch`, `through_wall_window`,
  `blind_internal_thumb_scoop`, `side_relief_notch`, `dual_side_card_access`
  et `rounded_floor_intent`. Si absent, le moteur derive la taxonomie depuis
  `kind` ;
- `placement` : positionnement humain, par exemple `front_center`, `left_side`,
  `center` ou `cavity_floor` ;
- `position_mm.x`, `position_mm.y`, `position_mm.z` : position locale dans la
  cavite ;
- `size_mm.x`, `size_mm.y`, `size_mm.z` : taille abstraite de la feature,
  requise pour `finger_notch`, `side_notch`, `center_notch`, `half_moon_notch`
  et `grip_aid` ;
- `radius_mm` : rayon abstrait, requis pour `half_moon_notch` et
  `rounded_floor` ;
- `comment` : note humaine optionnelle.

Validation P5-M004/P6-M003 :

- position non negative ;
- taille strictement positive quand elle est presente ;
- position plus taille dans les dimensions locales de la cavite ;
- rayon strictement positif quand il est present ;
- rayon limite a la moitie de la plus petite dimension XY de la cavite ;
- statut implicite `abstract_only` et `fusion_generation: not_implemented` dans
  les rapports et la CAD IR.

`top_open_rectangular_notch` est la seule aide de prise validee dans Fusion a ce
stade. `top_open_half_moon_notch` reste une intention courbe avec fallback
rectangulaire top-open. Les autres taxonomies ne creent pas de coupe, boolean,
fillet, conge ou geometrie courbe reelle dans Fusion 360.

Exemple :

```json
{
  "id": "front-half-moon-notch",
  "kind": "half_moon_notch",
  "taxonomy": "top_open_half_moon_notch",
  "placement": "front_center",
  "position_mm": { "x": 22, "y": 0, "z": 8 },
  "size_mm": { "x": 18, "y": 4, "z": 10 },
  "radius_mm": 9,
  "comment": "Abstract half-moon finger notch intent; no Fusion cut yet."
}
```

Voir `examples/simple_finger_notch_tray.json` pour un exemple complet.

## Exemple minimal

```json
{
  "project_name": "Small box",
  "units": "mm",
  "box": {
    "inner_dimensions_mm": { "x": 200, "y": 150, "z": 60 },
    "usable_height_mm": 45,
    "lid_clearance_mm": 5
  },
  "print_profile": "default",
  "tolerances": {
    "peripheral_clearance_mm": 0.8,
    "module_gap_mm": 0.6,
    "vertical_lid_clearance_mm": 1.0
  },
  "defaults": {
    "wall_thickness_mm": 1.2,
    "floor_thickness_mm": 1.2,
    "corner_radius_mm": 1.5
  },
  "layout": {
    "strategy": "row_fill"
  },
  "modules": [
    {
      "id": "cards",
      "name": "Cards",
      "functional_type": "sleeved_cards",
      "min_dimensions_mm": { "x": 72, "y": 98 },
      "height_mm": 40,
      "priority": 100,
      "allow_rotation": true,
      "quantity": 1,
      "comment": "Main deck"
    }
  ]
}
```

## Evolution CSV et Google Sheets

CSV et Google Sheets ne doivent pas remplacer le modele interne. Ils doivent etre des formats d'entree convertis vers `InsertConfig`.

Approche prevue :

1. Definir un mapping colonnes vers champs JSON.
2. Valider les unites explicitement.
3. Convertir chaque ligne en `ModuleRequest`.
4. Generer un JSON canonique ou un `InsertConfig`.
5. Reutiliser exactement le meme moteur.

## `assets`

Le bloc racine `assets` est charge depuis P9-M002 comme donnees passives. Il
sert a decrire le materiel reel avant de deriver modules, cavites ou
reservations. Depuis P10-M004, le moteur expose une synthese `module_candidates`
dans les rapports et la CAD IR metadata, mais ne genere toujours aucun
`modules[]` depuis ces assets.

Champs cibles :

- `assets[].id`, `name`, `kind` ;
- `assets[].quantity.count`, `quantity.grouping` ;
- `assets[].dimensions_mm.x/y/z` ;
- `assets[].dimension_confidence` : `exact`, `approximate`, `unknown_z` ;
- `assets[].containment_intent` ;
- `assets[].reservation_ref` vers une zone volumetrique optionnelle ;
- `assets[].module_hint` optionnel ;
- `assets[].storage_orientation` optionnel : `auto`, `flat_tray` ou `vertical_stack` ;
- `assets[].max_stack_height_mm` optionnel : hauteur maximale de pile pour les assets count-aware ;
- `assets[].comment`.

Validation P9-M002 : ids uniques, quantite strictement positive, dimensions X/Y
positives, Z positive sauf `dimension_confidence: unknown_z` ou Z peut valoir 0,
`reservation_ref` vers une zone volumetrique existante si fourni, `module_hint`
vers un module existant si fourni. `storage_orientation` doit appartenir aux valeurs supportees et `max_stack_height_mm`, si fourni, doit etre strictement positif. P10-M006 peut grouper des assets compatibles dans les rapports sans ajouter de nouveau champ de configuration.

Depuis P15-M002, `tokens`, `dice`, `meeples` et `generic` resolvent `storage_orientation: auto` vers `flat_tray`. Ce mode garde `z_mm` comme epaisseur unitaire mais limite la pile par `max_stack_height_mm` ou par les defaults moteur : tokens `12.0`, dice `20.0`, meeples `24.0`, generic `16.0`. `vertical_stack` est le mode explicite pour conserver l'ancien comportement qui utilise la hauteur disponible de la boite/grille.
## Overrides UI Fusion P12-M002+

La commande Fusion P12-M002+ peut appliquer des overrides temporaires sur une
configuration BGIG avant de generer une CAD IR temporaire. Ces champs ne changent
pas le schema JSON public : ils mappent vers des champs deja existants.

Mapping V0 :

- `box_inner_x_mm`, `box_inner_y_mm`, `box_inner_z_mm` -> `box.inner_dimensions_mm.x/y/z` ;
- `grid_units_x`, `grid_units_y`, `grid_units_z` -> `volumetric_grid.size_units.x/y/z` ;
- `wall_thickness_mm` -> `defaults.wall_thickness_mm` ;
- `floor_thickness_mm` -> `defaults.floor_thickness_mm` ;
- `peripheral_clearance_mm` -> `tolerances.peripheral_clearance_mm` ;
- `module_gap_mm` -> `tolerances.module_gap_mm` ;
- `print_profile` -> champ racine `print_profile`.

Les overrides de grille exigent que la config contienne deja `volumetric_grid`.
La commande Fusion ne cree pas encore une config asset-first complete depuis
zero et ne modifie pas les valeurs de tolerance par defaut du moteur.

### Note P12-M002V2 - Overrides connectes a config_file uniquement

Les champs UI P12 sont connectes uniquement au mode `config_file`. En mode
`cad_ir_file`, tout override renseigne doit etre refuse plutot qu'ignore. Le mode
`quick_parametric_box` reste desactive jusqu'a la definition d'un builder de
configuration temporaire complet.

### Note P12-M003 - quick_parametric_box UI

Le mode Fusion `quick_parametric_box` n'ajoute pas encore de nouveau format de configuration JSON. Les champs UI requis sont convertis en CAD IR temporaire dans l'add-in :

- `box_inner_x_mm`, `box_inner_y_mm`, `box_inner_z_mm` -> boite de reference non imprimable ;
- `grid_units_x`, `grid_units_y`, `grid_units_z` -> taille theorique de cellule ;
- `wall_thickness_mm`, `floor_thickness_mm` -> metadata et calcul de hauteur imprimable V0 ;
- `peripheral_clearance_mm`, `inter_module_clearance_mm` -> offsets explicites du module V0 ;
- `print_profile` -> metadata du profil.

La commande CLI d'export reste `python -m board_game_insert_generator export-cad-ir ... --output ...`; `--export-cad-ir` n'est pas une option CLI.

### Note P12-M004 - Persistance UI hors schema JSON

La persistance P12-M004 de `bgig_ui_settings.json` ne modifie pas le schema de
configuration BGIG. Elle memorise seulement les derniers champs de la commande
Fusion pour eviter la ressaisie : input mode, action, generation mode, chemins et
champs parametriques P12. Les configurations JSON restent validees par le loader
V0 existant.

## P13-M001 - Config temporaire quick_asset_box

`quick_asset_box` ne modifie pas le schema JSON public. La commande Fusion fabrique une config temporaire conforme au schema existant avec `box`, `print_profile`, `tolerances`, `defaults`, `layout`, `assets`, `volumetric_grid` et `modules: []`.

Format UI V0 : `asset_id,type,count,x_mm,y_mm,z_mm,fit`, entrees separees par `;` ou saut de ligne. `generic` est mappe vers `assets[].kind = other`. `fit=exact` devient `dimension_confidence=exact`; `fit=loose` ou `fit=approximate` deviennent `dimension_confidence=approximate`.

## P13-ASSET-M002 - Semantique count/z pour quick_asset_box

Depuis P15-M002, le schema JSON public accepte aussi les champs additifs `assets[].storage_orientation` et `assets[].max_stack_height_mm`. Depuis P16-M004, il accepte aussi `assets[].target_aspect_ratio` et `assets[].max_module_length_mm` comme nombres strictement positifs optionnels pour piloter le packing local `flat_tray_2d_v0`. Dans les configs temporaires `quick_asset_box`, `count` influence le sizing pour `tokens`, `dice`, `meeples` et `generic`, avec `z_mm` interprete comme epaisseur unitaire d'un item. Depuis P15-M003, la commande Fusion classique peut renseigner un `max_stack_height_mm` global optionnel ; depuis P16-M004, elle peut aussi renseigner un ratio cible et une longueur maximale globale. Ces champs sont appliques aux assets itemises supportes et laissent les cards/sleeved_cards avec leur semantique de deck total.

Pour `cards` et `sleeved_cards`, `z_mm` est interprete comme hauteur totale du paquet/deck fourni ; `count` est reporte mais non multiplie. Cette limitation est volontaire et doit rester visible dans le reporting tant qu'un modele cartes plus fin n'est pas valide.

## `box_fill_plan`

Depuis P19-M002, le champ racine optionnel `box_fill_plan` est charge comme extension additive `box_fill_plan.v0`. Son absence conserve le comportement historique. La boite et les assets du plan sont derives de `box` et `assets` deja charges : le bloc ne duplique donc pas leurs dimensions ni leur inventaire.

Champs V0 :

- `schema_version` : obligatoire, exactement `box_fill_plan.v0` ;
- `id`, `box_id`, `metadata` : identite et notes libres ;
- `layers[]` : `id`, `origin_z_mm`, `height_mm`, role, ordre de retrait et references declaratives ;
- `reservations[]` : volume non imprimable, kind `board`, `rulebook`, `lid_clearance`, `existing_tray`, `non_printable_volume` ou `generic`, origine et taille mm ;
- `modules[]` : module manuel, origine/taille mm, orientation, locks, printable, layer et references de compartiments/features ;
- `allocations[]` : `asset_id`, `quantity`, `module_id`, compartment optionnel, source, intention et statut declare ;
- `compartments[]` : reutilisent le contrat existant `Cavity` ;
- `access_features[]` : reutilisent le contrat existant `Feature`.

P19-M002 charge strictement les types et les champs inconnus. Les invariants de volume, collisions, references, coverage et volume libre sont implementes dans P19-M003 ; ce chargement seul ne pretend pas valider un plan physique ou Fusion.
### Validation P19-M003

Le loader charge la structure; `validate_config` verifie ensuite les IDs, dimensions, limites dans la hauteur utile, layers, collisions module/module et module/reservation, collisions reservation/reservation (autorisees seulement si les deux reservations portent `allow_overlap: true`), references et allocations. Chaque asset doit etre couvert a hauteur de son `quantity.count`; une quantite manquante ou excedentaire est une erreur. Le `FreeVolume` V0 est un agregat de volume, pas une decomposition de regions libres.
### Reporting P19-M004

Les sorties Markdown/JSON incluent `box_fill_plan` lorsque le bloc est declare. La CAD IR V0 le transporte sous `metadata.box_fill_plan` avec coverage, validation et FreeVolume. Ce transport est declaratif : il ne demande aucune nouvelle operation CAD et Fusion ne le consomme pas encore comme scene ou geometrie.