# ADR-0035 - Printable export and preprint V0

## Statut

Accepte

## Date

2026-07-09

## Carte liee

- `P17-M001 - ADR export/preprint V0`

## Contexte

P16 valide dans Fusion un plateau asset-first plus ergonomique : modules BGIG sous une racine de scene taguee, registry fiable, generation/regeneration sans doublon, compartiments, encoches et reporting printability V0. Le projet n'a cependant encore aucun export imprimable valide.

P17 doit ouvrir une boucle de pre-impression sans confondre export technique et validation physique. L'export doit donc etre strictement filtre, auditable et reversible. Il ne doit pas exporter les objets utilisateur, les sketches de debug, les outlines de reference, les helpers, les sources, les vues eclatees ou les elements BGIG non imprimables.

## Options

1. Exporter depuis le coeur Python.
   - Simple a tester hors Fusion, mais impossible de garantir que le fichier exporte represente la geometrie Fusion reelle avec coupes et notches.
2. Exporter depuis Fusion uniquement.
   - Plus proche de la geometrie reelle generee, mais depend de l'API Fusion et doit rester isole dans l'adaptateur.
3. Ajouter directement STL et 3MF avec logique avancee.
   - Plus complet, mais trop large pour une premiere boucle V0.

## Decision

P17 V0 exporte depuis Fusion uniquement. Le coeur Python reste sans dependance `adsk` et ne produit pas de STL/3MF. L'add-in Fusion peut ajouter une action de commande classique `export_printables` ou `export_stl` si l'API Fusion permet un export fiable par module.

Le format cible V0 est STL par module imprimable. 3MF reste reporte sauf si l'API Fusion l'expose de facon simple, stable et testable sans elargir la mission.

Un module est exportable seulement si toutes les conditions suivantes sont vraies :

- il appartient a la scene BGIG courante via le registry `bgig` ;
- il correspond a une occurrence compacte ou a un composant de module imprimable ;
- il contient au moins un body Fusion cible non vide ;
- il n'est pas une reference, un sketch debug, une outline, une occurrence source/helper, une occurrence eclatee par defaut, une racine de scene ou un objet non BGIG ;
- son rapport printability ne contient pas de blocker bloquant l'export.

L'export ecrit dans un dossier dedie par scene/export. Les noms de fichiers doivent etre deterministes et filesystem-safe, par exemple :

```text
<ordinal>-<module_id_slug>-<role>.stl
```

Chaque export doit produire :

- un ou plusieurs fichiers STL ;
- `bgig_export_manifest.json` ;
- `bgig_export_manifest.md`.

Le manifeste doit contenir au minimum : scene id, commit si disponible, timestamp, action, dossier de sortie, input mode, generation mode, preset/settings utiles, box/grid, assets, modules exportes, modules refuses avec raisons, dimensions planifiees, bbox Fusion si disponible, cavities/compartments/notches reportes, printability report, warnings et `print_validated: false`.

Le rapport Fusion doit afficher les compteurs :

- `printable_modules_detected` ;
- `printable_modules_exported` ;
- `printable_modules_refused` ;
- `export_format` ;
- `export_directory` ;
- `manifest_json` ;
- `manifest_markdown` ;
- `print_validated: false`.

Si l'export par module n'est pas fiable dans Fusion, P17-M002 doit s'arreter sur une gate technique et ne pas simuler un export reussi.

## Consequences

Effets positifs :

- l'export represente la geometrie Fusion reelle, pas une approximation du coeur ;
- les objets non BGIG et non imprimables restent exclus par construction ;
- chaque export est auditable via manifeste ;
- le statut `print-validated: false` reste visible jusqu'a une impression reelle.

Effets negatifs et risques :

- les tests hors Fusion ne peuvent valider que la planification, le filtrage et les messages, pas l'API d'export Fusion reelle ;
- l'API Fusion peut imposer un choix entre export de body, component ou occurrence ;
- les STL V0 ne transportent pas les metadonnees riches qu'un 3MF pourrait porter plus tard.

## Alternatives refusees

- Exporter depuis la CAD IR ou le coeur Python : refuse pour P17 car les coupes Fusion validees sont executees dans Fusion.
- Exporter toute la scene ou le root BGIG en un seul fichier : refuse car cela inclurait references, debug ou vues non imprimables et rendrait la validation module par module moins claire.
- Declarer l'export comme pret a imprimer : refuse tant qu'aucune impression physique n'est validee.

## Suivi

- `P17-M002` : implementer ou stopper techniquement l'action Fusion `export_printables`.
- `P17-M003` : produire les manifestes JSON/Markdown.
- `P17-M004` : enrichir les blockers printability et `printability_export_allowed`.
- `P17-M005` : preparer le protocole/coupon de preprint.
- `P17-M006` : preparer la gate Fusion P17 avec preset export.
