# Next Actions

Derniere mise a jour : 2026-07-13

## Version active

V0.1 - vrai MVP Fusion-only selon ADR-0055 et rebase P60-R accepte.

## Derniere mission terminee

P65-M003 - tailles minimum/demandee/calculee et estimation non mutante, palette et package 0.1.18.

## Derniere preuve automatisee

P65-M003 ajoute bgig.container_sizing_view.v1 et la palette 0.1.18 : chaque
conteneur expose minimum derive, demande Auto/Cible/Fixe, taille du plan et
statut non calcule/a jour/perime/partiel/impossible. Estimer les tailles
reutilise solve_project, ne sauvegarde pas, ne modifie pas Fusion et ne lance
pas de solve concurrent. Aucun solveur, score, tolerance, corps ou geometrie
n est modifie.

Preuves : 440 tests automatises verts, syntaxe JavaScript, compilation Python,
git diff --check et dry-run d installation Fusion verts. Aucune validation
Fusion ni impression reelle n est revendiquee.
## Mission courante

Aucune implementation en cours. P65-M003 est implementee et doit etre integree
dans main avant le demarrage de P65-M004.

## Prochaine action recommandee

P65 - Conteneurs, Reglages et Apercu integres.

P65-M004 - Explications et actions finales de l Apercu.

Statut : ready apres integration de P65-M003. Le lot doit traduire et
condenser sous-scores, appuis, ordre de retrait, residuels et suggestions. Il
doit rendre l export imprimable visible dans Apercu et conserver Materialiser
comme action persistante unique. Il ne modifie ni formules de score, ni solveur,
ni tolerance, ni geometrie.

Enchainement deja borne : P65-M004, puis P66-M001 de preparation automatisee,
puis la gate humaine Fusion-only P66.
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
