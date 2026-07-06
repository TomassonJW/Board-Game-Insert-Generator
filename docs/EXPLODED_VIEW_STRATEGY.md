# Exploded View Strategy

## Objectif

Fusion doit produire deux vues utiles : une vue compacte dans la boite et une vue
eclatee ou repartie a plat pour inspecter, nommer, mesurer et preparer de futurs
exports.

## Etat actuel

- La vue compacte P11-M001 est `fusion-validated` pour les modules asset-first
  positionnes par grille X/Y/Z.
- P7-M001 code une premiere vue eclatee basique dans l'add-in Fusion.
- Cette vue eclatee duplique les bodies rectangulaires deja planifies et les
  espace a droite de la boite sur une grille 2D deterministe.
- La validation Fusion manuelle P7-M001V reste requise.
- Aucun export STL/3MF et aucune validation d'impression ne sont revendiques.

## Strategie P7-M001

La vue eclatee basique est une aide d'inspection, pas une nouvelle logique
metier.

Invariants :

- la vue compacte reste generee ;
- Fusion ne recalcule ni solveur, ni placements compacts, ni clearances, ni
  tolerances ;
- les dimensions exploded sont recopiees depuis la CAD IR ;
- les bodies exploded recoivent un suffixe `exploded` ;
- la disposition exploded est locale a l'add-in, deterministe et uniquement
  visuelle ;
- les cavites, encoches et features restent portees par la vue compacte supportee
  existante ;
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

- `compact_view` : modules places selon le layout reel dans la boite.
- `exploded_view` : modules separes avec espacement lisible, labels et axes
  stables.
- `inspection_metadata` : liens entre module, asset, cavite, tolerance et
  operation.
- `export_group` : future selection par module ou par layer.

## Gates

- Smoke test humain P7-M001V avant statut `fusion-validated`.
- Nouvelle gate avant vue eclatee avancee, composants enfants Fusion, modules
  composites, export STL/3MF ou preparation d'impression.
