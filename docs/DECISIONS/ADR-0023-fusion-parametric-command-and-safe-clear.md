# ADR-0023 - Fusion parametric command and safe clear

## Statut

Accepte pour implementation, validation Fusion manuelle requise.

## Date

2026-07-07

## Carte liee

- `P12-UI-M002+ - UI Fusion parametrique V0`

## Contexte

Apres `P12-M001V`, l'add-in BGIG dispose d'une commande Fusion relancable par
bouton toolbar. Le flux reste toutefois encore trop proche d'un outil de debug :
l'utilisateur charge une CAD IR JSON deja generee et ne peut pas regenerer ou
nettoyer proprement depuis la commande.

La gate humaine P12-UI-M002+ autorise une premiere UI parametrique V0, sans UI
complete d'edition d'assets et sans nouvelle geometrie Fusion.

## Options

1. Creer une palette HTML persistante Fusion.
2. Etendre la commande Fusion existante avec champs parametriques et actions.
3. Conserver uniquement le mode CAD IR et documenter les limites.

## Decision

Retenir l'option 2.

La commande `Generate Board Game Insert` reste le point d'entree principal. Elle
expose maintenant :

- une action `generate`, `regenerate` ou `clear_bgig_scene` ;
- un chemin `CAD IR JSON path` ;
- un chemin optionnel `BGIG config JSON path` ;
- un champ optionnel `BGIG project root` ;
- un mode `compact_only` ou `compact_and_exploded` ;
- des overrides V0 pour dimensions de boite, taille de grille, epaisseurs,
  clearances principales et profil d'impression.

Quand une config BGIG est fournie, l'add-in peut importer le coeur Python pur en
ajoutant uniquement `<project root>/src` au `sys.path` cote add-in. Il applique
les overrides a une config temporaire, genere une CAD IR temporaire, puis consomme
cette CAD IR comme avant. Fusion ne recalcule toujours pas layout, placements,
clearances ou tolerances.

`Clear BGIG Scene` supprime uniquement les objets portant les attributs BGIG
ajoutes par les generations P12-M002+. Les objets utilisateur et les anciennes
geometries BGIG non taguees ne sont pas supprimes automatiquement.

## Consequences

Effets positifs :

- l'utilisateur peut tester une boucle config -> CAD IR -> Fusion depuis l'UI ;
- le workflow normal ne depend plus de `cad_ir_path.txt` ou
  `exploded_view_mode.txt` ;
- `Regenerate` peut nettoyer les objets BGIG tagues puis recreer la scene ;
- le nettoyage reste conservateur et evite de supprimer des objets utilisateur ;
- le coeur `src/board_game_insert_generator` reste sans `adsk`.

Risques et limites :

- la generation depuis config exige que Fusion puisse acceder au repo BGIG ou que
  l'utilisateur renseigne `BGIG project root` ;
- le nettoyage ne retire pas les objets BGIG historiques non tagues ;
- les champs parametriques V0 sont des overrides de config existante, pas une UI
  complete de creation d'assets ;
- la validation reelle dans Fusion reste manuelle.

## Alternatives refusees

La palette HTML persistante est refusee pour ce sprint : elle ajoute une surface
HTML/JS plus large alors qu'une commande Fusion classique suffit pour valider la
boucle V0.

Le maintien du mode CAD IR seul est refuse comme cible principale : il ne reduit
pas assez les manipulations externes.

## Suivi

- Smoke test humain `P12-UI-M002V` requis dans Fusion.
- Nouvelle gate avant UI assets complete, palette persistante large, solveur plus
  automatique, nouvelle geometrie Fusion, exports STL/3MF ou validation
  d'impression.
## Revision P12-M002V2

Le smoke test P12-M002V a montre que le tagging objet par objet n'etait pas assez
robuste pour `regenerate`, et que l'UI exposait trop de champs sans modes assez
clairs.

Decision corrective :

- ajouter un `Input mode` explicite ;
- utiliser `config_file` comme flux pre-rempli quand BGIG est detecte ;
- memoriser les derniers chemins valides dans `bgig_ui_settings.json` ;
- refuser les overrides en mode `cad_ir_file` ;
- garder `quick_parametric_box` visible mais desactive ;
- creer une racine Fusion taguee `BGIG Generated Scene` pour chaque generation ;
- faire de `Clear BGIG Scene` et `Regenerate` des operations de suppression
  taguee uniquement, preserves des objets non BGIG.

Cette revision ne change ni la geometrie generee, ni le contrat CAD IR, ni les
valeurs de tolerance par defaut.
