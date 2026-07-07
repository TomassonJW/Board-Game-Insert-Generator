# ADR-0025 - Fusion initial occurrence as compact view

## Statut

Accepte pour implementation, validation Fusion manuelle requise.

## Date

2026-07-07

## Carte liee

- `P12-UI-M002V5 - Restaurer l'occurrence compacte initiale visible`

## Contexte

ADR-0024 avait introduit une occurrence source/helper cachee pour eviter une
instance visible parasite. Le smoke test humain `P12-UI-M002V4` a montre que
cette strategie cassait la visibilite des bodies : les modules utiles ne se
voyaient plus, tandis que les gabarits/sketches restaient visibles.

La decision humaine impose d'abandonner la strategie `source_helper hidden`.

## Options

1. Masquer une occurrence source/helper et creer compact/exploded via references.
2. Utiliser l'occurrence initiale creee par `addNewComponent` comme occurrence
   compacte visible officielle, puis creer seulement l'occurrence eclatee via
   `addExistingComponent`.
3. Revenir a des copies independantes de bodies.

## Decision

Retenir l'option 2.

Pour chaque module physique BGIG :

- `addNewComponent` cree l'occurrence compacte visible officielle ;
- la geometrie du module est creee dans le `Component` de cette occurrence ;
- en mode `compact_and_exploded`, l'occurrence eclatee est creee via
  `addExistingComponent` et reference le meme `Component` ;
- aucune occurrence source/helper n'est creee ou masquee ;
- aucun body legacy independant n'est cree.

## Consequences

Effets positifs :

- les bodies restent visibles dans la vue compacte ;
- `compact_only` produit N occurrences compactes visibles pour N modules ;
- `compact_and_exploded` produit N compactes + N eclatees visibles ;
- les occurrences compactes/eclatees restent liees au meme composant ;
- le workflow ne revient pas aux copies independantes.

Risques et limites :

- l'occurrence initiale est a la fois le support de creation du composant et la
  vue compacte officielle ;
- il faut continuer a verifier dans Fusion qu'aucune instance parasite ne reste
  visible ;
- la validation reste manuelle cote Fusion.

## Alternatives refusees

L'option 1 est abandonnee apres KO critique P12-UI-M002V4.

L'option 3 reste refusee car elle casserait les occurrences liees et produirait
une vue eclatee morte.

## Suivi

- Smoke test humain `P12-UI-M002V5` requis dans Fusion.
- Verifier `compact_only`, `compact_and_exploded`, `generate`, `regenerate` et
  `clear_bgig_scene`.
- Gate separee avant toute nouvelle geometrie Fusion ou export STL/3MF.
