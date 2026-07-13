# Next Actions

Derniere mise a jour : 2026-07-13

## Version active

V0.1 - vrai MVP Fusion-only selon ADR-0055 et rebase P60-R accepte.

## Derniere mission terminee

P65-M001 - jeux X-Y/Z, budget vertical et action Fusion persistante, package 0.1.16.

## Derniere preuve automatisee

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

Increment pret : P65-M002 - Tailles et estimation lisibles dans Conteneurs.

Scope borne :

1. afficher minimum, cible et taille calculee au meme endroit ;
2. proposer une estimation explicite sans modifier le projet ni creer de corps ;
3. conserver Auto/Cible/Fixe et les axes extensibles comme contrat moteur ;
4. garder les corps explicites et suggestions confirmables par l utilisateur ;
5. ne pas ouvrir la refonte generale des styles avant le MVP.

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
