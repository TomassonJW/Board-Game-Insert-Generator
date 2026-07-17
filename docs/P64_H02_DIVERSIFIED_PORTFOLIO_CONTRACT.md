# P64-H02 — Portefeuilles diversifiés après cul-de-sac

## Statut

Implémenté et automated-validated dans le package 0.1.44.
P64-H02V a reçu un KO contextuel sur un nouveau faux impossible ; aucune preuve
Fusion OK n'est revendiquée. `fusion-validated: false`,
`print-validated: false`. La trajectoire est supersédée par P64-A01 puis H04-H08.

## Déclencheur

Un projet réel de 250 × 180 × 70 mm, avec 8 conteneurs, 11 éléments et deux
réservations supérieures localisées, possède encore une solution complète. Le
portefeuille canonique trouve huit arrangements XY, mais ils placent tous une
cavité trop haute sous le plateau ou le livret et sont rejetés après validation.
Un autre ordre déterministe des mêmes corps construit immédiatement deux niveaux.

## Objectif

- ne plus conclure `Calcul impossible` quand seul l’ordre borné des participants
  empêche d’atteindre une composition valide ;
- conserver le chemin rapide canonique pour tous les projets déjà résolus ;
- rendre la reprise observable, déterministe et strictement bornée ;
- corriger en parallèle la croix d’élément pour qu’elle reste dans la même cellule
  d’action que le menu `...`, immédiatement à sa droite.

## Contrat

Le solveur exécute d’abord le portefeuille canonique inchangé. Une diversification
n’est autorisée que si ce portefeuille se termine par `NO_STAGE_COMPOSITION_FITS`
ou `NO_VALIDATED_STAGE_PROPOSAL`. Il essaie alors au plus six portefeuilles
supplémentaires, chacun fondé sur un ordre unique obtenu par SHA-256 à partir
d’un seed borné et de l’identifiant métier stable du conteneur ou complément.

Chaque portefeuille diversifié réutilise les mêmes dimensions, modes, jeux, règles
de support, partitions d’étages, validations de cavités et réservations. Le premier
candidat complet gagne ; une proposition résiduelle n’est conservée qu’en secours
si aucune solution complète n’est trouvée. Les compteurs agrégés et le nombre de
portefeuilles réellement évalués sont exposés dans `solver.search`.

## Invariants

- aucun default, minimum, mode, jeu, tolérance ou valeur physique ne change ;
- aucun schéma projet ne change ;
- aucune cavité ni réservation n’est assouplie ou ignorée ;
- aucune dépendance d’optimisation externe n’est ajoutée ;
- le cœur reste pur Python, déterministe, borné et sans import `adsk` ;
- aucune scène ou matérialisation automatique n’est ajoutée ;
- la recherche canonique ne paie aucun coût supplémentaire lorsqu’elle réussit.

## Acceptation automatisée

- la fixture anonymisée du cas à réservations localisées échoue dans le
  portefeuille canonique puis construit ses 8 conteneurs grâce à la reprise ;
- l’état exact sauvegardé par Fusion construit 8 conteneurs sur 2 niveaux après
  3 portefeuilles évalués, dont 2 diversifiés ;
- un seed diversifié produit un seul ordre, stable entre deux exécutions ;
- les régressions P64-H01, support, conservation, déterminisme et UI restent vertes.

## Gate P64-H02V — historique

Préparation historique — ne pas relancer : `scripts/fusion/prepare_p64_h02_diversified_portfolio_test.ps1`.

Vérifier le projet laissé ouvert, le retour à une proposition complète en deux
niveaux, l’absence de faux diagnostic de plateau, la fraîcheur après une petite
édition, la croix sur la même ligne que `...` et la scène inchangée avant
`Matérialiser dans Fusion`.

Retour historique non reçu — ne pas envoyer : `P64-H02 Fusion OK 0.1.44 - commit <sha>`.

Cette preuve ne calibre aucune valeur physique et ne vaut pas impression réelle.

## Retour P64-H02V

Le placement problématique initial et l'alignement de la croix sont observés
comme corrigés. Un ajout ultérieur d'asset dans un projet disposant encore de
volume reproduit toutefois `Calcul impossible`. Le package 0.1.44 ne reçoit donc
pas de preuve Fusion OK. P64-H02 reste une amélioration automatisée utile, mais
pas une solution générale. Ne pas prolonger ce contrat par de nouveaux seeds :
suivre `P64_MULTI_SOLVER_PORTFOLIO_PROGRAM.md` à partir de P64-H04.
