# 2026-07-31 — P64-L09W-D-T rejetée

- Le rejeu SCIP tardif sur enveloppes minimales a été sondé sur trois cas
  `common` avec élément plat : trois passages
  `bounded_unknown -> certified_solution`.
- Le candidat ne changeait ni budget, ni grille, ni epsilon, ni valeur
  physique, ni certificat, ni ordre produit.
- Les tests ciblés passent `60/60`.
- La campagne s'arrête à `15/16` sentinelles : toutes les gates fonctionnelles
  passent, mais `tuning-384` mesure `28 782,506 ms` contre une limite gelée de
  `28 699,258 ms`.
- La voie candidate n'est pas invoquée sur cette sentinelle, mais la gate de
  performance reste dure ; aucun rejeu opportuniste n'est lancé.
- Le code candidat est retiré. Les 48 et les 400 ne sont pas exécutés.
- Le holdout reste scellé et E reste bloquée à `348/400` au plafond retenu.

Preuve :
`docs/P64_L09W_D_T_FLAT_MINIMUM_ENVELOPE_RETRY_REJECTION_EVIDENCE.md`.
