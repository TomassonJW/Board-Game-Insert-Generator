# ADR-0024 - Fusion hidden source helper occurrences

## Statut

Remplacee par ADR-0025 apres KO critique P12-UI-M002V4.

## Date

2026-07-07

## Carte liee

- `P12-UI-M002V4 - Corriger les occurrences source visibles parasites`

## Contexte

La strategie produit P7/P12 reste correcte : un module physique BGIG doit etre un
`Component` Fusion unique, partage par une occurrence compacte et, si le mode le
demande, une occurrence eclatee liee.

Le smoke test `P12-UI-M002V3` a toutefois montre une instance visible parasite :
une scene ou occurrence source semblait rester superposee aux occurrences
compactes/eclatees attendues. Ce comportement rend le resultat produit ambigu et
peut donner l'impression de modules dupliques.

## Options

1. Continuer a utiliser l'occurrence creee par `addNewComponent` comme occurrence
   compacte implicite.
2. Creer une occurrence source/helper cachee, creer la geometrie dans son
   composant, puis creer les occurrences visibles compactes/eclatees via
   `addExistingComponent`.
3. Revenir a des copies independantes de bodies pour la vue eclatee.

## Decision

Retenir l'option 2.

L'add-in cree un composant source par module physique via une occurrence helper
`source_helper_occurrence`, cache cette occurrence, puis cree explicitement :

- une occurrence `compact_occurrence` pour la vue compacte ;
- une occurrence `exploded_occurrence` uniquement en mode `compact_and_exploded`.

Les occurrences compactes et eclatees referencent le meme composant source. Le
message Fusion affiche le nombre de modules physiques, les composants sources,
les occurrences visibles attendues/reelles, les helpers visibles et les legacy
bodies.

## Consequences

Effets positifs :

- le nombre d'instances visibles devient explicite et testable ;
- `compact_only` ne doit afficher que les occurrences compactes ;
- `compact_and_exploded` ne doit afficher que les occurrences compactes et
  eclatees ;
- les occurrences restent liees au meme composant physique ;
- aucun retour aux copies independantes de bodies n'est introduit.

Risques et limites :

- la validation reelle depend du comportement Fusion de masquage des occurrences ;
- si Fusion refuse de masquer l'occurrence helper, la generation doit echouer
  plutot que produire une instance parasite ;
- le core Python reste sans connaissance de cette strategie Fusion.

## Alternatives refusees

L'option 1 est refusee car elle a produit une ambiguite visible pendant le smoke
test humain.

L'option 3 est refusee car elle casserait la vision produit : une vue compacte et
une vue eclatee doivent rester deux occurrences liees du meme composant, pas deux
copies mortes independantes.

## Suivi

- Smoke test humain `P12-UI-M002V4` requis dans Fusion.
- Verifier `compact_only`, `compact_and_exploded`, `generate`, `regenerate` et
  `clear_bgig_scene`.
- Gate separee avant toute nouvelle geometrie Fusion, export STL/3MF ou
  changement de solveur.

## Remplacement

Le smoke test P12-UI-M002V4 a montre que masquer l'occurrence source/helper
rendait les bodies utiles invisibles dans Fusion. Cette strategie est abandonnee
et remplacee par `ADR-0025-fusion-initial-occurrence-as-compact-view.md`.
