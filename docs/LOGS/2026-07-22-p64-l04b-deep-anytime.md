# 2026-07-22 — P64-L04B Approfondi anytime

## Contexte

L’observation exploratoire Fusion 0.1.57 montrait que Normal pouvait produire un
plan utile alors qu’Approfondi repartait sous des caps plus larges, prenait trop
longtemps et pouvait finir sans restituer cette solution.

## Décision exécutée

- exécuter le préfixe Normal exact en premier ;
- conserver son meilleur plan certifié comme incumbent ;
- exécuter seulement les trois lanes propres à Deep ;
- partager entre elles une deadline de 30 000 ms ;
- transmettre à chaque beam le temps restant ;
- remplacer l’incumbent seulement par une amélioration stricte ;
- distinguer expiration conservatrice et annulation stale fail-closed ;
- recertifier le plan sélectionné avec le validateur minimal commun.

Le contrat détaillé est
`docs/P64_L04B_DEEP_ANYTIME_CONTRACT.md`.

## Résultat

- 14/14 tests solveur minimal ;
- 639/639 suite complète ;
- Ruff ciblé, py_compile, compileall, frontière adsk et diff-check OK ;
- aucune modification du manifest 0.1.58 ;
- aucune finalisation, CAD, scène, forme P45, valeur physique ou revendication
  dense ;
- `fusion-validated: false`, `print-validated: false`.

## Suite

P64-L04C devient `ready` pour l’activité, l’étape courante et le temps écoulé
honnêtes. La gate humaine L04V reste différée après L04C.
