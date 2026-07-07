# Fusion UI Strategy

Derniere mise a jour : 2026-07-07

## Objectif

P12-UI transforme l'add-in Fusion BGIG d'un flux developpeur vers une interface utilisable et relancable depuis Fusion.

La priorite est volontairement pragmatique : stabiliser d'abord un bouton Fusion visible et une commande relancable, puis evaluer une palette persistante HTML seulement si elle reste simple et maintenable.

## Strategie retenue P12-M001

Statut : `implemented-fusion`, validation Fusion manuelle requise.

La premiere strategie officielle est `toolbar_button_reopens_command_without_addin_restart` :

- l'add-in cree une `CommandDefinition` nommee `Generate Board Game Insert` ;
- il ajoute un bouton dans `Design workspace > Utilities > Add-Ins` ;
- `run(context)` ouvre encore la commande immediatement pour le premier lancement ;
- si la boite de dialogue perd le focus ou se ferme, l'utilisateur doit pouvoir cliquer le bouton toolbar pour la rouvrir sans redemarrer l'add-in ;
- les handlers Fusion restent conserves au niveau module pour eviter le garbage collection ;
- `stop(context)` supprime le bouton, la definition de commande courante et l'ancien identifiant de commande ;
- `cad_ir_path.txt` et `exploded_view_mode.txt` restent des valeurs par defaut/fallback, pas le flux normal.

## Palette persistante

Une palette persistante BGIG reste une option P12 suivante, pas encore implementee.

Elle doit etre arretee ou gatee si elle impose une architecture HTML/JS large, fragile ou difficile a tester hors Fusion. Le chemin de repli reste une commande Fusion classique plus robuste.

## Modes d'entree

### CAD IR input

Mode courant valide : l'utilisateur choisit un fichier CAD IR JSON deja genere. Fusion consomme la CAD IR, sans recalculer layout, clearances, tolerances ou solveur.

### Config input

Mode futur : l'utilisateur choisit une configuration BGIG JSON et l'add-in genere ou demande une CAD IR. Ce mode exige de verifier comment le coeur Python est disponible dans l'environnement Fusion et ne doit pas introduire `adsk` dans `src/board_game_insert_generator`.

## Regeneration V0

P12-M001 ne nettoie pas encore la scene. La regeneration V0 consiste a rouvrir la commande via le bouton toolbar et relancer la generation avec le meme fichier CAD IR ou un fichier modifie.

Tant que le nettoyage n'est pas code, le smoke test doit utiliser un document vide ou supprimer manuellement les objets BGIG avant regeneration.

## Limites

- Pas de palette HTML persistante codee dans P12-M001.
- Pas de generation depuis config BGIG dans Fusion.
- Pas de nettoyage automatique de scene.
- Pas de nouvelle geometrie Fusion.
- Pas d'export STL/3MF.
- Pas de validation d'impression 3D.
