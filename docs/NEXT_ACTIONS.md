# Next Actions

Derniere mise a jour : 2026-07-13

## Version active

V0.1 - vrai MVP Fusion-only selon ADR-0055 et rebase P60-R accepte.

## Derniere mission terminee

P65-M004 - explications de l Apercu et actions finales, palette et package 0.1.19.

## Derniere preuve automatisee

P65-M004 ajoute bgig.preview_explanations.v1 au resultat Python. La palette
traduit score comparatif, appuis, ordre de retrait, residuels et suggestions
sans exposer de codes solveur. Exporter les imprimables est primaire dans
Apercu ; Recalculer et Materialiser dans Fusion restent uniquement dans la
barre persistante. Aucun score, solveur, tolerance, corps ou geometrie n est
modifie.

Preuves : 445 tests automatises verts, syntaxe JavaScript, compilation Python,
git diff --check, installation locale Fusion 0.1.19 et controle des marqueurs verts.
Aucune validation Fusion ni impression reelle n est revendiquee.

## Mission courante

Aucune implementation en cours. P65 est integree dans main ; P66-M001 est la
prochaine mission preparee.

## Prochaine action recommandee

P66-M001 - Preparation automatisee de la gate Fusion V0.1.

Statut : ready. Produire le projet canonique, les
CAD IR, le package installe, les marqueurs et une checklist afin de ne laisser
a l humain que les observations dans Fusion. Aucun correctif produit ne doit
etre anticipe avant une observation KO.

Contrat d execution delegable : `docs/P66_TERRA_EXECUTION_CONTRACT.md`.
P66-M001 livre uniquement fixtures, preuves, preparateur, installation et
checklist. La gate P66 reste humaine ; tout KO ouvre un hotfix P66-Hxx atomique
avant de rejouer la gate complete.

## Releases bloquees

P44 a P50 restent
bloques jusqu a l acceptation humaine P66. P47 a P50 restent aussi bloques
jusqu a l acceptation de P46.

## Gate humaine active

Aucune gate avant P66 tant que P62-P65 restent dans les ADR acceptees et
n introduisent ni dependance lourde ni changement de tolerance. P66 demandera
une observation Fusion preparee automatiquement.

## Fin de chaque mission

Documenter chaque OK/KO sans extrapoler a l impression, mettre a jour le
pilotage, committer et integrer directement dans main quand les preuves
automatisees sont vertes. print-validated: false reste obligatoire.
