# Fusion UI Strategy

Derniere mise a jour : 2026-07-07

## Objectif

P12-UI transforme l'add-in Fusion BGIG d'un flux developpeur vers une interface
utilisable et relancable depuis Fusion.

La strategie reste pragmatique : une commande Fusion classique enrichie est le
chemin principal tant qu'une palette persistante HTML n'apporte pas assez de
valeur pour justifier une architecture plus large.

## Strategie retenue P12-M001

Statut : `fusion-validated`, `print-validated: false`.

La premiere strategie officielle est `toolbar_button_reopens_command_without_addin_restart` :

- l'add-in cree une `CommandDefinition` nommee `Generate Board Game Insert` ;
- il ajoute un bouton dans `Design workspace > Utilities > Add-Ins` ;
- `run(context)` ouvre encore la commande immediatement pour le premier lancement ;
- si la boite de dialogue perd le focus ou se ferme, l'utilisateur peut cliquer
  le bouton toolbar pour rouvrir BGIG sans redemarrer l'add-in ;
- les handlers Fusion restent conserves au niveau module pour eviter le garbage
  collection ;
- `stop(context)` supprime le bouton, la definition de commande courante et
  l'ancien identifiant de commande ;
- `cad_ir_path.txt` et `exploded_view_mode.txt` restent des valeurs par
  defaut/fallback, pas le flux normal.

## Strategie retenue P12-M002+

Statut : `implemented-fusion`, validation Fusion manuelle requise,
`print-validated: false`.

La strategie P12-M002+ est `command_dialog_parametric_v0` :

- la meme commande `Generate Board Game Insert` expose une action `generate`,
  `regenerate` ou `clear_bgig_scene` ;
- l'utilisateur peut toujours fournir directement `CAD IR JSON path` ;
- l'utilisateur peut aussi fournir `BGIG config JSON path` et, si l'auto-detection
  echoue, `BGIG project root` ;
- l'add-in ajoute uniquement `<project root>/src` au `sys.path` cote add-in pour
  importer le coeur Python pur ;
- l'add-in applique les overrides de la commande a une config temporaire, genere
  une CAD IR temporaire, puis consomme cette CAD IR ;
- Fusion ne recalcule pas layout, solveur, clearances ou tolerances ;
- `Regenerate` nettoie les objets BGIG tagues puis regenere ;
- `Clear BGIG Scene` supprime uniquement les objets avec attributs BGIG crees par
  les generations P12-M002+.

Champs V0 exposes :

- `CAD IR JSON path` ;
- `BGIG config JSON path` ;
- `BGIG project root` ;
- `Generation mode` : `compact_only` ou `compact_and_exploded` ;
- dimensions de boite `box_inner_x_mm`, `box_inner_y_mm`, `box_inner_z_mm` ;
- grille `grid_units_x`, `grid_units_y`, `grid_units_z` ;
- `wall_thickness_mm`, `floor_thickness_mm` ;
- `peripheral_clearance_mm`, `module_gap_mm` ;
- `print_profile`.

Ces champs sont des overrides de configuration existante. Ils ne constituent pas
encore une UI complete de creation d'assets ou de modules.

## Palette persistante

Une palette persistante BGIG reste une option future, non implementee.

Elle doit etre arretee ou gatee si elle impose une architecture HTML/JS large,
fragile ou difficile a tester hors Fusion. Le chemin de repli reste une commande
Fusion classique plus robuste.

## Modes d'entree

### CAD IR input

Mode valide : l'utilisateur choisit un fichier CAD IR JSON deja genere. Fusion
consomme la CAD IR, sans recalculer layout, clearances, tolerances ou solveur.

### Config input

Mode code en P12-M002+ : l'utilisateur choisit une configuration BGIG JSON.
L'add-in genere une config temporaire avec overrides, puis une CAD IR temporaire.
Ce mode exige que Fusion puisse acceder au repo BGIG via auto-detection ou champ
`BGIG project root`.

## Regeneration V0

P12-M002+ ajoute une regeneration bornee : `regenerate` appelle d'abord
`Clear BGIG Scene`, puis relance la generation depuis la source choisie.

Le nettoyage est conservateur : seuls les objets tagues par BGIG sont supprimes.
Les anciennes geometries non taguees et les objets utilisateur ne sont pas
supprimes automatiquement.

## Limites

- Pas de palette HTML persistante codee.
- Pas d'UI assets complete.
- Pas de nouvelle geometrie Fusion.
- Pas de solveur ou recalcul metier dans Fusion.
- Pas d'export STL/3MF.
- Pas de validation d'impression 3D.
- Validation Fusion manuelle requise pour P12-M002+.