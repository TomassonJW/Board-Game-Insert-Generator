# Next Actions

Derniere mise a jour : 2026-07-13

## Version active

V0.1 - vrai MVP Fusion-only selon ADR-0055 et rebase P60-R accepte.

## Derniere mission terminee

P64 - solveur volumetrique multi-etages, durcissement runtime et Fusion, package 0.1.15.

## Derniere preuve automatisee

Le coeur compose des arrangements XY par etages Z et sait aussi placer un corps
haut a cote de piles plus courtes. Les rotations sont revalidees dans leur repere
local, les cavites conservent leur profondeur utile sous les plateaux et les noms
techniques Fusion restent uniques meme si les libelles utilisateur sont repetes.
Une proposition partielle reste bloquee avant Fusion.
Le contrat, la palette, la CAD IR et le garde-fou Fusion sont couverts par 428 tests.
Aucune validation Fusion P64 ou impression n est revendiquee.

## Mission courante

Aucune mission en cours. P64 est automatise et durci ; P65 reste la premiere mission ready.

## Prochaine action prete

P65 - Conteneurs, Reglages et Apercu integres, selon ADR-0060 acceptee.

Scope borne :

1. rendre taille minimale, cible et calculee lisibles au meme endroit ;
2. integrer estimation, corps explicites et suggestions sans mutation ;
3. rendre les sous-scores, appuis, retraits et residuels explicables sans jargon ;
4. rendre `Materialiser dans Fusion` primaire uniquement pour une solution complete ;
5. conserver les tolerances experimentales et ne pas changer leurs valeurs.

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
