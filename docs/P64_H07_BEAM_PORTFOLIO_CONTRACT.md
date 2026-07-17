# P64-H07 — Beam robuste et portefeuille Auto

Statut : `implemented`, `automated-validated` dans le package 0.1.50.

## Objectif borné

P64-H07 ajoute la famille interne `free_3d_beam` et l'orchestrateur
`portfolio_auto`. Le chemin public `solve_partition_plan` reste
`stage_stack` : méthode, effort et diagnostic Fusion appartiennent à P64-H08.

Le lot ne modifie ni schéma projet, ni asset, ni cavité, ni valeur physique,
ni jeu, ni tolérance, ni réservation, ni CAD IR et ne crée aucun corps ou
scène automatiquement.

## Recherche 3D

Le beam conserve plusieurs états constitués de placements, points extrêmes,
espaces maximaux vides et participants restants. Il explore les rotations X/Y
0/90 et les dimensions finales autorisées par `Auto/Cible/Fixe`.

Une solution libre complète ne résulte pas d'un gonflement après faisabilité :
la recherche place directement les enveloppes finales. Elle n'est admissible
que lorsque plus aucun EMS imprimable ne reste. Les volumes réservés au
périmètre et entre corps restent des jeux techniques ; aucun résiduel n'est
reclassé arbitrairement en jeu. P64-F01/F02 gardent donc la propriété exclusive
des futures finitions continue et modulaire.

Les limites dures couvrent largeur de beam, états, essais, branches de
participants, options, EMS, points extrêmes, candidats complets et temps. Un
budget ou une frontière épuisés produisent `no_solution_within_budget`, jamais
`proven_impossible`. L'annulation produit `stale_or_cancelled`.

## Reconstruction et certificat produit

`free_3d_plan_adapter.py` redérive les faits canoniques du projet et restaure :

- enveloppes finales et modes de dimension ;
- cavités, parois et fonds ;
- réservations supérieures et compensations autorisées ;
- appuis, intervalles Z et ordre de retrait ;
- conservation et absence de corps automatique.

Le certificat commun vérifie aussi que le snapshot immuable du candidat
correspond exactement aux placements du plan. Toute divergence, réservation
refusée ou conservation incomplète ferme l'adaptateur sans plan matérialisable.

## Profils monotones internes

| Profil | Familles autorisées | Beam | États beam | Essais beam | Temps de garde |
| --- | --- | ---: | ---: | ---: | ---: |
| Rapide | stage, greedy, beam | 8 | 512 | 30 000 | 1 s |
| Normal | stage, greedy, beam | 24 | 4 096 | 250 000 | 5 s |
| Approfondi | stage, greedy, beam | 64 | 20 000 | 1 000 000 | 15 s |

Chaque profil plus profond conserve toutes les familles et ne réduit aucune
limite partagée. Ces valeurs sont bornées et observables ; elles deviennent des
réglages produit seulement après P64-H08. Le temps reste une garde de sécurité,
pas une promesse de durée ni un SLA.

## Portefeuille Auto

`solver_portfolio.py` :

1. exécute la baseline certifiée ;
2. conserve son fast path lorsqu'une composition canonique complète possède un
   seul niveau Z de départ ;
3. sinon exécute greedy puis beam sous le profil choisi ;
4. refuse les candidats seulement géométriques ou avec résiduel ;
5. déduplique entre familles par placements réels ;
6. classe uniquement les plans certifiés avec les scores déjà mesurés.

Le corpus H04 simple, dense H01 et réservations H02 conserve au moins une
proposition Auto certifiée. Sur le benchmark de développement, les neuf runs
Rapide/Normal/Approfondi du corpus H01/H02/H03R ont terminé en environ 40 s au
total ; la baseline reste retenue sur ces fixtures. Ce relevé vérifie le budget,
mais ne constitue ni seuil produit ni preuve de supériorité du beam.

## Validation automatisée

- fermeture EMS et certificat produit d'un cas libre ;
- topologie multi-niveaux distincte certifiée ;
- monotonie Rapide/Normal/Approfondi ;
- fast path simple ;
- comparaison des trois familles hors fast path ;
- déduplication inter-familles ;
- timeout et annulation honnêtes ;
- mismatch candidat/plan refusé ;
- corpus H04 conservé ;
- parité et régressions H05/H06 inchangées.

## Limites et suite

- le beam est borné et incomplet ; son échec reste heuristique ;
- `free_3d_greedy` peut encore ne fournir qu'une admission géométrique ; il
  n'entre alors pas au classement produit ;
- aucune UI, persistance ou valeur par défaut n'est ajoutée ;
- aucune preuve Fusion ou impression nouvelle n'est revendiquée.

P64-H08 est la prochaine mission : exposer méthode, effort et diagnostic
secondaire en préservant focus, autosave et matérialisation explicite, puis
préparer P64-V2. `print-validated: false`.
