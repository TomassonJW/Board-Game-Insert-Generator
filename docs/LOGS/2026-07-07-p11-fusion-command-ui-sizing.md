# 2026-07-07 - P11-M003 UI Fusion minimale et sizing asset-first

## Mission

Gate humaine validee apres P11-M002V : corriger la coherence dimensionnelle entre
modules asset-first, grille multi-layer et generation Fusion, puis ajouter une
premiere commande UI Fusion minimale.

## Diagnostic

Le pipeline P10/P11 produisait deja `source_size_mm` pour les modules asset-first,
mais l'adaptateur Fusion utilisait `placement.size_mm` comme taille de body. Pour
les plans generes, ce champ representait alors le span de grille :

- `simple_asset_executable_plan` : `30 x 30 x 10 mm` ;
- `simple_multilayer_grid_scene`, module bas : `90 x 90 x 10 mm` ;
- `simple_multilayer_grid_scene`, module haut : `60 x 60 x 20 mm`.

Ces valeurs sont utiles comme reservations de grille, mais elles ne sont pas les
corps imprimables derives des assets.

## Correction

Le plan asset-first expose maintenant explicitement :

- `theoretical_grid_origin_mm` / `theoretical_grid_extent_mm` ;
- `asset_fit_size_mm` ;
- `printable_body_origin_mm` / `printable_body_size_mm` ;
- `grid_slack_mm` ;
- `clearance_applied`.

Fusion cree les modules asset-first depuis `printable_body_size_mm` quand le champ
est present. Les spans grille restent transportes et valides comme metadata.

Dimensions attendues apres correction :

- `simple_asset_executable_plan` : body asset-first `25.6 x 25.6 x 9.8 mm`, span
  grille `30 x 30 x 10 mm` ;
- `simple_multilayer_grid_scene`, module bas : body `61.6 x 61.6 x 7.8 mm`, span
  grille `90 x 90 x 10 mm` ;
- `simple_multilayer_grid_scene`, module haut : body `37.6 x 37.6 x 17.8 mm`,
  span grille `60 x 60 x 20 mm`.

Les clearances peripheriques/inter-modules de ce plan asset-first restent
explicites a `0.0` et non revendiquees comme appliquees par face.

## UI Fusion

L'add-in enregistre la commande `Generate Board Game Insert` avec :

- champ `CAD IR JSON path` ;
- mode `compact_only` / `compact_and_exploded` ;
- resume indiquant que Fusion consomme la CAD IR sans recalculer layout,
  clearances ou tolerances.

`cad_ir_path.txt` et `exploded_view_mode.txt` restent supportes comme valeurs par
defaut heritees, mais ne sont plus le flux utilisateur recommande.

## Validation

Tests automatises a relancer avant commit final : suite unittest complete, CLI
Markdown/JSON/export CAD IR sur exemples demandes, `git diff --check` et absence
`adsk` dans `src/board_game_insert_generator`.

Statut : `implemented-fusion`, validation Fusion manuelle P11-M003V requise,
`print-validated: false`.
