# P64-L09U-R6 — régions locales exactes et micro-chevauchements

## Objectif

Corriger les deux défauts humains de 0.1.76 sans perdre les acquis R5 :

1. profondeur réelle d’une cavité sous un micro-chevauchement ;
2. empilement local de plusieurs plateaux ou livrets de tailles différentes.

Candidate cible : version suivant 0.1.76.

## Autorités

- `docs/P64_L09U_R5_V_0176_HUMAN_KO_EVIDENCE.md` ;
- `docs/DECISIONS/ADR-0100-plateau-amovible-et-cavite-sans-paroi-intermediaire.md` ;
- `docs/DECISIONS/ADR-0101-acces-local-des-cavites-partiellement-recouvertes.md` ;
- `docs/DECISIONS/ADR-0102-empilement-local-exact-des-reservations-superieures.md`.

## Invariants

- Aucun changement de valeur physique, jeu ou tolérance.
- Cavités figées en X/Y, orientation, identité et profondeur.
- Fonds, parois, appuis et enveloppes minimales conservés.
- Réservations virtuelles, jamais corps utilisateur ou supports artificiels.
- BRep transitoire, zéro Combine rectangulaire, rollback et respiration
  conservés.
- Aucun benchmark, holdout, corpus ou tournoi solveur.
- Projets personnels strictement en lecture seule.

## Programme

1. Consigner 0.1.76 en `human-KO`, `do-not-run`.
2. Rejouer `CasLimite02+` en `60×80`, `60×82` et `60×85`.
3. Remplacer la garde Z globale par l’union exacte des régions locales.
4. Transporter chaque intervalle de pile dans les coupes finales.
5. Ancrer toute cavité sur une intersection locale réelle supérieure à
   l’epsilon.
6. Ajouter les régressions micro-chevauchement, imbriqué, partiel, disjoint et
   côte à côte.
7. Vérifier aperçu, CAD IR et plan Fusion.
8. Lancer les tests ciblés puis la suite autorisée sans les douze modules
   interdits.
9. Vérifier les SHA personnels, intégrer, installer la candidate et ouvrir une
   nouvelle gate humaine.

## Arrêt

Le programme s’arrête après installation de la candidate. Thomas reste seul à
promouvoir un verdict Fusion.

`fusion-validated=false`, `print-validated=false`.
