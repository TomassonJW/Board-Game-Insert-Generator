# Next Actions

Derniere mise a jour : 2026-07-13

## Version active

V0.1 - vrai MVP Fusion-only selon ADR-0055 et rebase P60-R accepte.

## Derniere mission terminee

P65-M002 - frontieres de jeu boite/conteneurs et inter-conteneurs, palette et package 0.1.17.

## Derniere preuve automatisee

P65-M002 conserve le solveur volumetrique P64 et separe quatre roles : jeu
X-Y total entre conteneurs, jeu X-Y par cote de boite, jeu Z total entre
conteneurs et marge Z superieure. Les projets historiques sans le nouveau champ
X-Y de boite gardent leurs placements. La CAD IR et la palette Fusion exposent
les quatre roles ; les sketches de reference restent tagues/inspectables et
sont caches par defaut. Aucun corps, support ou espace imprimable automatique
n est cree.

Preuves : 434 tests executes verts en trois lots courts, compilation Python,
git diff --check et exemple CLI verts. Aucune validation Fusion ni impression
reelle n est revendiquee.

## Mission courante

Aucune mission en cours. P65-M002 est implemente ; P65 reste en cours par increments bornes.

## Prochaine action recommandee

P65 - Conteneurs, Reglages et Apercu integres.

P65-M003 - Minimum, cible, calculee et estimation dans Conteneurs.

Statut : a cadrer avant implementation. Le prochain increment ne doit ni
modifier automatiquement un corps explicite, ni recalibrer les tolerances, ni
elargir les formes de cavites. Il doit expliciter une estimation non mutante et
les dimensions minimum/cible/calculee, apres validation du parcours UX.
## Mission suivante apres P65

P66 - acceptance humaine V0.1 revisee Fusion-only, apres P65.

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
