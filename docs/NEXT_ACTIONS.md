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

Aucune implementation en cours. Le cadrage fonctionnel de P65-M003 est termine
et la mission est `ready` dans `docs/P65_M003_FUNCTIONAL_CONTRACT.md`.

## Prochaine action recommandee

P65 - Conteneurs, Reglages et Apercu integres.

P65-M003 - Tailles minimum/demandee/calculee et estimation dans Conteneurs.

Statut : `ready`. Contrat d execution :
`docs/P65_M003_FUNCTIONAL_CONTRACT.md`. Cible : palette Fusion 0.1.18.

Le lot doit :

- distinguer le minimum derive, le contrat Auto/Cible/Fixe et la taille issue
  du vrai plan ;
- exposer les etats non calcule, a jour, perime, partiel et impossible ;
- ajouter un unique CTA local `Estimer les tailles` qui reutilise
  `solve_project`, reste dans Conteneurs et ne mute ni projet ni scene ;
- expliquer les ecarts par axe sans code moteur au premier niveau ;
- conserver `Recalculer` et `Materialiser dans Fusion` comme actions globales,
  avec les gardes existantes.

Interdits : nouveau solveur, nouvelle heuristique, recalibrage de tolerance,
corps/cale/support automatique, changement de cavite ou calcul metier JS.

Deux revues avant integration sont obligatoires : fonctionnelle contre les cas
d acceptation du contrat, puis architecture/scope contre ADR-0055 et les
exclusions du lot.

## Mission suivante apres P65-M003

P65-M004 - Explications et actions finales de l Apercu. Cette mission reste
`planned` et depend de P65-M003. Elle traduira les sous-scores, appuis, ordre de
retrait, residuels et suggestions, sans modifier leurs formules ni le solveur.

## Route suivante jusqu au MVP

1. P65-M003 - tailles et estimation non mutante ;
2. P65-M004 - lisibilite finale de l Apercu ;
3. P66-M001 - preparation automatique du projet canonique, du package et de la
   checklist Fusion ;
4. P66 - gate humaine unique dans Fusion ;
5. si KO seulement, correctifs P66-Hxx bornes puis nouvelle observation.

Le MVP V0.1 est accepte uniquement apres un P66 vert. La publication/tag de
release reste une gate humaine separee ; P44 V0.2 ne s ouvre qu apres P66.

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
