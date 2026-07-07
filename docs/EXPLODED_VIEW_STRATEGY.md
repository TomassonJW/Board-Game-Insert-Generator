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
- La validation Fusion manuelle P7-M001V4 en document Assembly-compatible est confirmee le 2026-07-06 : compact/exploded sont des occurrences liees des memes composants sources, et l'add-in ne renomme pas directement les occurrences.
- P11-M002 est validee humainement pour une premiere scene eclatee multi-layer depuis placements grille X/Y/Z.
- P11-M003 conserve les occurrences liees et ajoute une commande UI minimale ; la validation Fusion P11-M003V4 a valide le flux UI et le sizing asset-first clarifie.
- P12-M002V5 remplace la strategie source/helper cachee : l occurrence initiale Fusion est l occurrence compacte visible officielle ; seule l occurrence eclatee est ajoutee par reference.
- Aucun export STL/3MF et aucune validation d'impression ne sont revendiques.

## Strategie P7 corrigee

La vue eclatee basique est une aide d'inspection, pas une nouvelle logique
metier.

Invariants :

- un module physique BGIG correspond a un unique `Component` Fusion ;
- un document Part Design incompatible doit echouer proprement avec `assembly document required` ;
- la vue compacte est l'occurrence initiale visible creee par `addNewComponent` ;
- la geometrie rectangulaire, les cavites et les encoches supportees sont creees
  dans le `Component` de cette occurrence compacte ;
- aucune occurrence source/helper cachee n'est creee ;
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
- les roles compact et exploded restent explicites dans le plan
  hors Fusion et le message final de l'add-in ;
- le message final doit afficher les occurrences visibles attendues/reelles et
  `Visible BGIG source/helper occurrences: 0` ;
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

- P7-M001V4, P11-M002V et P11-M003V4 sont validees humainement ; prochaine gate : smoke test P12-UI-M002V6 pour verifier l ownership par scene racine unique.
- Nouvelle gate avant vue eclatee avancee, modules composites, export STL/3MF ou
  preparation d'impression.

## Correction P12-M002V6 - scene root ownership

La vue compacte et la vue eclatee restent des occurrences liees. Elles sont
maintenant toujours creees sous une occurrence racine BGIG unique taguee
`bgig:role = scene_root`.

`clear_bgig_scene` et `regenerate` suppriment cette occurrence racine via
`deleteMe()` au lieu de poursuivre les occurrences compactes/eclatees une par
une. Validation Fusion attendue : `P12-UI-M002V6`.