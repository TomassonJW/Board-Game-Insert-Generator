# 2026-07-29 — P64-L09W-A audit et baseline solveur

## Mission

Auditer les preuves solveur existantes, préenregistrer le futur domaine de
robustesse et mesurer 0.1.80 uniquement sur les fixtures versionnées avant
toute optimisation.

## Décisions

- ADR-0107 sépare fixtures reconstructibles, dérives historiques et cas de
  cœur.
- Le futur holdout contient 400 cas positifs construits, dont 240 `common`.
- Gate préenregistrée : 380/400 globalement, 238/240 sur `common`, zéro faux
  impossible et zéro solution non certifiée.
- Les anciens holdouts L06 à L08 restent consommés.
- La matérialisation reste une phase Fusion séparée.

## Résultats

- 165 fixtures historiques ne reconstruisent plus leur vérité.
- 147 projets produit uniques restent mesurables, dont 101 positifs.
- Baseline positive : 19/101 certifiés.
- 42 contrôles impossibles non exécutables sous leur ancienne contrainte de
  rotation.
- Déterminisme : 101/105 replays ; quatre variations de route à résultat
  `bounded_unknown` constant.
- Finalisation : 2/21 ; 19 refus
  `flat_inset_subtraction_plan_rejected`.
- CAD IR : 2/2 après finalisation réussie.
- L08 cœur : 40 `bounded_unknown`, 1 `unsupported`.
- Validation finale : 1 044 tests passés, 1 skip prévu.

## Correction d’attribution

Le digest modèle SCIP n’engage plus le temps restant volatil. Le runtime reçoit
toujours la même limite d’exécution réelle. La gate Python 3.14 + SCIP 10.0.2
est déterministe après correction.

Les validateurs L05/L06 distinguent maintenant l’intégrité cryptographique d’un
ancien reçu de sa reconstructibilité produit courante. Ils conservent uniquement
la migration historique connue des origines plates ; l’audit continue de classer
ces cas en dérive et aucun ancien manifest n’est réécrit.

## Suite

P64-L09W-B construit le générateur produit, les vérités indépendantes, les
contrôles impossibles compatibles avec le produit et le nouveau holdout fermé.

Preuve :
`docs/P64_L09W_A_SOLVER_ROBUSTNESS_BASELINE_EVIDENCE.md`.
