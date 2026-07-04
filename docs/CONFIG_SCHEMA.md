# Configuration Schema V0

## Format

Le format V0 est JSON pour rester local, lisible et simple a valider.

Toutes les dimensions sont en millimetres. Le champ `units` doit valoir `mm`.

## Validation stricte

Le loader V0 refuse les champs inconnus aux niveaux suivants :

- racine du document, incluant `print_profile` ;
- `box` ;
- `box.inner_dimensions_mm` ;
- `tolerances` ;
- `defaults` ;
- `layout` ;
- chaque entree de `modules` ;
- chaque `modules[].min_dimensions_mm` ;
- chaque `modules[].cavities` ;
- chaque `modules[].cavities[].features`.

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
  "modules": []
}
```

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

Validation P5-M004 :

- position non negative ;
- taille strictement positive quand elle est presente ;
- position plus taille dans les dimensions locales de la cavite ;
- rayon strictement positif quand il est present ;
- rayon limite a la moitie de la plus petite dimension XY de la cavite ;
- statut implicite `abstract_only` et `fusion_generation: not_implemented` dans
  les rapports et la CAD IR.

Ces features ne creent pas de coupe, boolean, fillet, conge ou geometrie courbe
reelle dans Fusion 360.

Exemple :

```json
{
  "id": "front-half-moon-notch",
  "kind": "half_moon_notch",
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
