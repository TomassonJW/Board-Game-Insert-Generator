# Log - Fusion Part Design root component fix

## Date

2026-07-03

## Contexte

Le smoke test manuel de l'add-in P4-M003 a affiche dans Fusion :

`Part Design documents can only contain one component, please add this Part to an Assembly to add multiple components.`

La generation P4-M003 utilisait `Occurrences.addNewComponent` pour creer un
composant enfant par blank. Cette API est pertinente pour un document Assembly,
mais le document ouvert par Thomas etait un document Part Design limite a un seul
composant.

## Correction

- Suppression de `addNewComponent` dans le chemin de smoke test minimal.
- Creation des sketches directement sur le plan XY du composant racine.
- Creation des bodies rectangulaires dans le composant racine avec noms lisibles.
- Conservation des dimensions CAD IR : Fusion ne recalcule ni layout, ni offsets,
  ni tolerances.
- Ajout d'un test de garde verifiant que le point d'entree n'utilise plus
  `addNewComponent` pour P4-M003.

## Statut

Le code est pret pour un nouveau smoke test manuel Fusion. La generation reste
`manual validation required` tant que le test n'a pas ete execute et documente.
