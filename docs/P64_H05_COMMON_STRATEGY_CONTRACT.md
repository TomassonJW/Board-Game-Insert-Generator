# P64-H05 — Contrat commun et baseline `Étages et piles`

Statut : `implemented`, `automated-validated` dans le package 0.1.48.

## Objectif borné

P64-H05 place la baseline H03R derrière une frontière interne commune sans
changer le schéma utilisateur, les dimensions, les valeurs physiques, les jeux,
les réservations, la CAD IR ou l'interface Fusion. Le chemin public reste
`solve_partition_plan` ; son résultat reste identique aux références H04.

## Contrat interne

`solver_contract.py` définit des valeurs immuables :

- `SolverStrategy` : famille et version ;
- `SolverBudget` : limites ordonnées, comparables de façon monotone ;
- `PlacementSnapshot` et `SolverCandidate` : proposition figée et digestée ;
- `ValidationCheck` et `ValidationCertificate` : certificat déterministe ;
- `StrategyRun` : candidats et certificats d'une famille.

Pour H05, la seule famille est `stage_stack`. Son budget est une projection
immuable de ses limites existantes, avec le profil interne `baseline`. Aucun
profil produit Rapide/Normal/Approfondi ni réglage Fusion n'est introduit avant
P64-H07/H08.

## Autorité de validation

`validate_placement_geometry` devient l'unique validation géométrique employée
pendant la sélection H03R et lors de la certification. Un certificat complet
vérifie : enveloppe utile, jeu boîte et inter-corps, absence de collision,
contrat d'enveloppe, cavités/parois/fonds, réservations et appuis, séquence de
retrait, conservation du volume et absence de corps automatique.

L'adaptateur `run_stage_stack_adapter` retourne exactement le plan historique,
mais refuse de l'exposer comme solution matérialisable sans certificat valide.
Une non-solution expose zéro candidat au futur portefeuille. Les certificats
restent internes dans H05 afin de préserver le schéma et le digest public ; H07
pourra les comparer entre familles sous un contrat déjà stable.

## Parité et invariants

- les fixtures H04 simple, dense H01 et réservations H02 sont identiques
  bit-à-bit entre baseline interne et adaptateur ;
- les ordres canoniques, structurés H03 et hash H02, les budgets et le score ne
  changent pas ;
- aucune famille actuelle ou future ne peut déclarer une solution complète sans
  passer par le validateur commun ;
- un certificat refusé ne devient jamais `Impossible prouvé` ;
- aucun corps de remplissage, aucune scène et aucune matérialisation automatique
  ne sont ajoutés.

## Hors scope

P64-H05 ne livre ni EP/EMS, ni beam, ni portefeuille Auto, ni nouveau score,
ni nouvelle interface, ni finition continue/modulaire, ni dépendance externe.
P64-H06 reste le prochain lot : un greedy 3D libre réellement distinct.

## Validation automatisée

- tests de parité H04 et déterminisme du digest ;
- test d'immuabilité et de monotonie du budget ;
- test de certificat complet ;
- test fail-closed : une solution falsifiée hors boîte est refusée par
  l'adaptateur ;
- régressions H03R partition et solveur volumétrique, suite complète, compileall,
  frontière `adsk`, exemple CLI et `git diff --check`.

`fusion-validated` ne change pas : la dernière preuve solveur reste P64-H01
0.1.42. `print-validated: false`.
