# 2026-07-12 - P57 partition sans corps automatique

## Contexte

ADR-0054 rejette le chemin historique region libre vers filler. P57 devait
remplacer P41 pour le produit Fusion-only sans deplacer le solveur dans Fusion.

## Changements

- solveur pur bgig.partition_plan.v1 ;
- partitions bornees par rangees, ordres et rotations ;
- expansion conjointe revalidee par P55 ;
- pile P40 et supports traces ;
- complements exacts explicites, mode auto refuse ;
- bridge et palette Calculer la partition ;
- retrait des actions CAD historiques avant P59.

## Verifications

- 9 tests solveur : OK ;
- 7 tests bridge : OK ;
- 5 tests DOM : OK ;
- 87 tests Fusion historiques : OK ;
- 50 bacs, determinisme, contraintes et diagnostics couverts.

## Impact

P58 peut afficher le vrai plan. Aucun CAD, statut fusion-validated ou
print-validated n est revendique.

## Suivi

- P58 : resultat premium, vue dessus et coupe derivees des placements P57.
