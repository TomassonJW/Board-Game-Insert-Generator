# Next Actions

Derniere mise a jour : 2026-07-13

## Version active

V0.1 - vrai MVP Fusion-only selon ADR-0055 et rebase P60-R accepte.

## Derniere mission terminee

P65-M001 - jeux X-Y/Z, budget vertical et action Fusion persistante, package 0.1.16.

## Derniere preuve automatisee

Socle conserve : P64 - solveur volumetrique multi-etages.

Le coeur compose des arrangements XY par etages Z et sait aussi placer un corps
haut a cote de piles plus courtes. Les rotations sont revalidees dans leur repere
local, les cavites conservent leur profondeur utile sous les plateaux et les noms
techniques Fusion restent uniques meme si les libelles utilisateur sont repetes.
Une proposition partielle reste bloquee avant Fusion.
Le contrat, le solveur, la palette, la CAD IR et le garde-fou Fusion sont couverts par 430 tests.
Aucune validation Fusion P64 ou impression n est revendiquee.

## Mission courante

Aucune mission en cours. P65-M001 est implemente ; P65 reste en cours par increments bornes.

## Prochaine action prete

P65 - Conteneurs, Reglages et Apercu integres.

Increment pret : P65-M002 - Jeux boite/conteneurs et inter-conteneurs separes.

Contrat a implementer :

1. conserver `layout_clearance_mm` comme jeu X-Y total entre conteneurs ;
2. ajouter `container_box_xy_clearance_mm`, applique par cote entre les corps et
   les quatre parois X-Y de la boite ;
3. conserver `container_z_clearance_mm` comme jeu Z total entre conteneurs ;
4. reutiliser `box.lid_clearance_mm` comme jeu conteneur/boite Z au-dessus et le
   renommer clairement dans l UI ; le fond reste ancre a Z=0 ;
5. migrer un ancien projet sans le nouveau champ X-Y boite en copiant
   `layout_clearance_mm`, afin de conserver exactement ses placements ;
6. conserver les valeurs par defaut actuelles : le zero est autorise mais n est
   pas adopte comme nouveau default sans calibration humaine.

Acceptation automatisee obligatoire :

- jeu boite X-Y nul avec jeu inter-conteneurs non nul ;
- jeu boite X-Y non nul avec jeu inter-conteneurs nul ;
- variation du jeu Z inter-conteneurs sans modifier la marge Z superieure ;
- variation de la marge Z superieure sans modifier les espaces entre etages ;
- ancien projet normalise sans changement de resultat ;
- politique de jeu et CAD IR exposent quatre roles non ambigus ;
- palette Fusion affiche une seule fois les quatre libelles ;
- aucun corps, support ou espace imprimable automatique n est cree.

Hors scope : jeu sous les bacs, supports/cales, recalibrage des valeurs, refonte
visuelle, nouvelle heuristique de solveur ou changement de formes de cavite.

Instruction d autonomie : mission atomique, deux passes de review (contrat puis
diff/tests), suite complete verte, installation locale 0.1.17 et integration
`direct-to-main`. Arret uniquement sur divergence de schema, regression solveur
non bornee ou ambiguite contraire a ces invariants.

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
