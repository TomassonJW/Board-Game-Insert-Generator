# Log - P12-M004 persistance UI Fusion

Date : 2026-07-08

## Gate

Gate humaine P12-M004 validee pour ameliorer le workflow d iteration UI Fusion :
persistance des champs, rehydratation a la reouverture et regeneration plus
confortable. Le perimetre interdit reste inchange : pas de nouvelle geometrie,
pas de solveur, pas de changement de tolerances, pas d export STL/3MF, pas de
palette persistante HTML et pas de dependance `adsk` dans le coeur Python.

## Implementation

- `bgig_ui_settings.json` conserve maintenant action, input mode, generation mode,
  dernier chemin CAD IR utilisateur, dernier chemin config, project root, CAD IR
  temporaire generee et tous les champs parametriques P12.
- `commandCreated` restaure ces valeurs dans la commande Fusion.
- `quick_parametric_box` est pre-rempli avec les dernieres valeurs utilisees.
- `cad_ir_file` ignore les champs parametriques persistants pour eviter qu une
  saisie quick precedente casse le chargement direct d une CAD IR.
- Si une scene BGIG existe deja, la commande prefere `Action = regenerate` a l
  ouverture pour guider vers un remplacement sans doublon.

## Validation automatique

Validation hors Fusion requise avant integration : suite unitaire, py_compile de
l add-in, CLI Markdown/JSON/export CAD IR sur exemples P12, `git diff --check` et
verification `rg -n "adsk" src/board_game_insert_generator`.

## Validation Fusion attendue

Smoke test P12-M004V : ouvrir BGIG, choisir `quick_parametric_box`, saisir
`120 x 80 x 30`, grille `4 x 4 x 3`, epaisseurs, clearances et profil, generer,
rouvrir et verifier la rehydratation, changer `box_inner_x_mm` a `160`, lancer
`regenerate`, verifier le remplacement sans doublon, rouvrir et verifier `160`,
puis lancer `clear_bgig_scene` en confirmant que les objets non BGIG sont
preserves.

Statut : `implemented-fusion`, validation Fusion manuelle requise,
`print-validated: false`.
