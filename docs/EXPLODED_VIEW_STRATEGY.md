# Exploded View Strategy

## Objectif

Fusion doit produire deux vues utiles : une vue compacte dans la boite et une vue
eclatee ou repartie a plat pour inspecter, nommer, mesurer et preparer de futurs
exports.

## Etat actuel

- La vue compacte P11-M001 est `fusion-validated` pour les modules asset-first
  positionnes par grille X/Y/Z.
- P7-M001 code une premiere vue eclatee basique dans l'add-in Fusion.
- Le premier smoke test P7-M001V a refuse la strategie de copies independantes
  de bodies.
- La correction P7 remplace ces copies par deux occurrences liees d'un meme
  composant physique : une occurrence compacte et une occurrence eclatee.
- P7-M001V2 a bloque en document Part Design ; P7 affiche maintenant `assembly document required` dans ce contexte.
- P7-M001V3 a bloque sur le renommage direct des occurrences (`property '_get_name' of 'Occurrence' object has no setter`).
- La correction P7-M001V4 ne tente plus de faire `occurrence.name = ...` ; les noms lisibles sont portes par les composants sources et le mapping compact/exploded dans le plan/message.
- La validation Fusion manuelle P7-M001V4 en document Assembly-compatible reste requise.
- Aucun export STL/3MF et aucune validation d'impression ne sont revendiques.

## Strategie P7 corrigee

La vue eclatee basique est une aide d'inspection, pas une nouvelle logique
metier.

Invariants :

- un module physique BGIG correspond a un unique `Component` Fusion ;
- un document Part Design incompatible doit echouer proprement avec `assembly document required` ;
- la geometrie rectangulaire, les cavites et les encoches supportees sont creees
  dans la definition de ce composant ;
- la vue compacte est une occurrence de ce composant ;
- la vue eclatee est une autre occurrence du meme composant, creee via reference
  au composant existant ;
- Fusion ne recalcule ni solveur, ni placements compacts, ni clearances, ni
  tolerances ;
- les transforms d'occurrence utilisent les positions deja resolues ou la grille
  eclatee de presentation de l'add-in ;
- les composants sources recoivent des noms lisibles ;
- les noms exacts des occurrences dans le Browser Fusion peuvent etre generes
  par Fusion et ne sont pas un critere de validation ;
- l'add-in ne tente pas de renommer directement `Occurrence.name` ;
- les roles compact/exploded restent explicites dans le plan hors Fusion et le
  message final de l'add-in ;
- aucune geometrie courbe, fillet, module composite ou export n'est ajoute.

## Mode local

Par defaut, l'add-in utilise :

```text
compact_and_exploded
```

Un fichier optionnel local, ignore par Git, peut etre place dans le dossier de
l'add-in :

```text
BoardGameInsertGenerator/exploded_view_mode.txt
```

Valeurs supportees :

- `compact_and_exploded` : genere la vue compacte et la vue eclatee basique ;
- `compact_only` : genere uniquement la vue compacte.

Toute autre valeur est refusee avant generation.

## Strategie cible future

- `compact_view` : modules places dans le repere de boite, utile pour verifier
  encombrement, collisions et hauteur utile.
- `exploded_view` : occurrences separees avec espacement lisible, labels et axes
  stables.
- `inspection_metadata` : liens entre module, asset, cavite, tolerance et
  operation.
- `export_group` : future selection par module ou par layer.

## Gates

- Smoke test humain P7-M001V4 en document Assembly-compatible avant statut `fusion-validated`.
- Nouvelle gate avant vue eclatee avancee, modules composites, export STL/3MF ou
  preparation d'impression.
