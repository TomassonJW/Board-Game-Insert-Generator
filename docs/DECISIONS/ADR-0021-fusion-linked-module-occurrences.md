# ADR-0021 - Fusion linked module occurrences for compact and exploded views

## Statut

Accepte pour implementation, validation Fusion manuelle requise.

## Date

2026-07-06

## Carte liee

- Correction `P7-M001V KO partiel`

## Contexte

Le smoke test humain P7-M001V a valide que la vue compacte et la vue eclatee
etaient visibles, mais a refuse partiellement le resultat produit : les elements
`exploded` etaient des copies independantes de bodies. Modifier un module compact
ne pouvait donc pas se refleter dans la vue eclatee.

La vision produit demande qu'un module physique BGIG corresponde a un unique
`Component` Fusion, puis que les vues compacte et eclatee soient deux
`Occurrence` du meme composant avec des transforms differentes.

## Decision

Remplacer la duplication de bodies `exploded` par une structure liee :

- creation d'un `Component` Fusion par module physique BGIG ;
- creation de la geometrie rectangulaire, cavites et encoches supportees dans la
  definition de ce composant ;
- creation d'une occurrence compacte du composant, positionnee selon la CAD IR ;
- creation d'une occurrence eclatee du meme composant via `addExistingComponent` ;
- application des transforms d'occurrence en millimetres convertis vers les
  unites internes Fusion ;
- conservation du mode local `compact_and_exploded` / `compact_only`.

Fusion ne recalcule toujours ni solveur, ni tolerances, ni placements compacts.
La disposition eclatee reste une aide de presentation locale a l'add-in.

## Consequences

Effets positifs :

- une modification de la definition du module peut se refl?ter dans les deux
  occurrences ;
- la vue compacte et la vue eclatee representent le meme objet physique ;
- les cavites et encoches supportees sont portees par le composant source, pas
  par une copie independante ;
- les tests hors Fusion verrouillent des occurrences liees plutot que des copies
  de bodies.

Risques :

- cette strategie reintroduit des composants enfants Fusion, ce qui peut echouer
  dans certains documents Part Design qui refusent plusieurs composants ;
- le smoke test doit verifier le comportement dans un design Fusion compatible
  avec des composants/occurrences ;
- la validation reste `manual validation required` tant que Thomas n'a pas
  confirme la liaison dans Fusion.

## Alternatives refusees

Conserver les copies de bodies est refuse : visible mais contraire au modele
produit.

Ajouter des positions exploded dans la CAD IR est reporte : la correction concerne
l'adaptateur Fusion et ne doit pas modifier le contrat CAD IR de maniere
incompatible.


## Amendement P7-M001V2 - Contexte document Fusion

Le smoke test P7-M001V2 a confirme que les documents Fusion `Part Design`
peuvent refuser la creation de composants enfants avec le message `Part Design
documents can only contain one component`.

Decision complementaire : ne pas revenir aux copies independantes et ne pas
tenter de convertir automatiquement le document actif. L'add-in doit detecter
ce cas et afficher `assembly document required`, en demandant d'ouvrir/creer un
document Assembly-compatible ou d'ajouter le Part a une Assembly avant de
relancer.

## Suivi

- Smoke test humain P7-M001V3 requis en document Assembly-compatible.
- Nouvelle gate avant vue eclatee avancee, modules composites, exports ou
  geometrie Fusion plus ambitieuse.
