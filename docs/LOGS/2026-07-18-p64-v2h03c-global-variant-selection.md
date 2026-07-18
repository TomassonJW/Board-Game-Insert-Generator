# Log — P64-V2H03C sélection globale des variantes

Date : 2026-07-18
Mission : P64-V2H03C
Statut : `implemented-core`, `automated-validated`

## Décision appliquée

ADR-0070 est exécutée sans nouvelle décision structurante : P45 reste
propriétaire de la géométrie locale et de son certificat ; P64 consomme les
frontières H03B, choisit paresseusement variante et placement, puis réapplique
le certificat produit commun.

## Réalisation

- fallback H03C seulement après le portefeuille canonique complet ;
- options variante-placement injectées dans les états beam, sans produit
  cartésien ;
- fermeture continue conservant l'identité de variante ;
- reconstruction des cavités retenues et certificat global explicite ;
- lanes Quick/Normal/Deep préfixées, caps H03B consommés et télémétrie secondaire ;
- fixtures globales multi-cavités, réservation localisée, dense, budget et stale.

## Preuve

Voir `docs/P64_V2H03C_GLOBAL_SELECTION_EVIDENCE.md`.

Suite complète : 566/566 OK en 150,895 s. Le cul-de-sac minimal est résolu ; le
mécanisme dense 11 × 34 reste `no_solution_within_budget` jusqu'en Approfondi.
Ce résultat ne prouve ni impossibilité, ni validation Fusion, ni impression.

## Suite

P64-V2H03V devient `ready` parce que H03C peut changer le résultat visible d'un
projet. Sa préparation devra installer un package dédié et demander uniquement
l'observation du résultat, du diagnostic secondaire, de la stabilité de palette
et de l'absence de scène automatique.
