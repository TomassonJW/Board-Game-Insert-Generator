# Log - Correction P7 vue eclatee par occurrences liees

## Date

2026-07-06

## Declencheur

Smoke test humain `P7-M001V` partiellement refuse : la vue eclatee etait visible
mais generee comme copies independantes de bodies.

## Correction

- Remplacement du plan `exploded_blanks` par `compact_occurrences` et
  `exploded_occurrences`.
- Creation d'un composant Fusion par module physique BGIG.
- Creation d'une occurrence compacte via `addNewComponent`.
- Creation d'une occurrence eclatee liee via `addExistingComponent`.
- Execution des cavites et encoches supportees dans la definition du composant,
  en coordonnees locales, afin que les occurrences partagent la geometrie.
- Message Fusion enrichi avec composants, occurrences compactes, occurrences
  eclatees et statut de liaison.

## Limites

- Validation Fusion manuelle requise.
- Certains documents Part Design peuvent refuser plusieurs composants enfants ;
  le smoke test doit utiliser un design compatible avec composants/occurrences.
- Aucun export, fillet, module composite ou solveur nouveau.

## Suite

Stop pour smoke test humain `P7-M001V2`.
