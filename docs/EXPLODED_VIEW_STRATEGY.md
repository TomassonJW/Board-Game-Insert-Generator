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
- La validation Fusion manuelle P7-M001V2 reste requise.
- Aucun export STL/3MF et aucune validation d'impression ne sont revendiques.

## Strategie P7 corrigee

La vue eclatee basique est une aide d'inspection, pas une nouvelle logique
metier.

Invariants :

- un module physique BGIG correspond a un unique `Component` Fusion ;
- la geometrie rectangulaire, les cavites et les encoches supportees sont creees
  dans la definition de ce composant ;
- la vue compacte est une occurrence de ce composant ;
- la vue eclatee est une autre occurrence du meme composant, creee via reference
  au composant existant ;
- Fusion ne recalcule ni solveur, ni placements compacts, ni clearances, ni
  tolerances ;
- les transforms d'occurrence utilisent les positions deja resolues ou la grille
  eclatee de presentation de l'add-in ;
- les noms d'occurrences recoivent un suffixe lisible `compact occurrence` ou
  `exploded occurrence` ;
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

- Smoke test humain P7-M001V2 avant statut `fusion-validated`.
- Nouvelle gate avant vue eclatee avancee, modules composites, export STL/3MF ou
  preparation d'impression.
