# ADR-0066 — Diversification bornée après cul-de-sac de validation

## Statut

Acceptée le 2026-07-17 par le GO explicite de correction du faux `Calcul impossible`
observé dans le projet Fusion laissé ouvert.

## Contexte

ADR-0065 ajoute des partitions adaptatives et équilibre X/Y/Z, mais le solveur
reste sensible aux quatre ordres canoniques des participants. Dans le nouveau cas
réel, huit arrangements occupent correctement le volume ; ils sont toutefois tous
rejetés parce qu’une cavité haute se retrouve sous une réservation localisée. Une
permutation différente des mêmes corps, sans changer aucune dimension, construit
une partition complète en deux niveaux.

Augmenter systématiquement les ordres ralentirait chaque recalcul, y compris les
projets simples. Ignorer la validation de cavité ou réduire implicitement une
réservation violerait les contrats physiques.

## Options

1. Augmenter toujours le nombre d’ordres canoniques.
2. Relâcher la validation des cavités sous les plateaux.
3. Relancer une petite série d’ordres diversifiés uniquement après un cul-de-sac
   de recherche ou de validation.
4. Introduire immédiatement un solveur externe global.

## Décision

Retenir l’option 3.

Le portefeuille canonique demeure inchangé et prioritaire. Seulement après
`NO_STAGE_COMPOSITION_FITS` ou `NO_VALIDATED_STAGE_PROPOSAL`, le moteur peut
évaluer jusqu’à six portefeuilles supplémentaires. Chacun contient un ordre unique,
dérivé de façon stable par SHA-256 à partir d’un seed borné et de l’identifiant
métier du participant. Le premier résultat complet est retenu ; les métriques
agrègent le travail réellement effectué.

Cette diversification change l’ordre d’exploration, jamais les données métier ni
les validations. Elle reste heuristique, déterministe, sans dépendance externe et
ne revendique aucune optimalité globale.

## Conséquences

- les projets déjà résolus gardent exactement le chemin rapide canonique ;
- les faux impossibles sensibles à l’ordre disposent d’une reprise bornée ;
- un vrai impossible peut coûter jusqu’à six portefeuilles supplémentaires ;
- les compteurs `portfolios_evaluated` et `diversified_portfolios_evaluated`
  rendent ce coût visible ;
- les dimensions, defaults, jeux, cavités, supports et réservations restent
  intégralement validés ;
- toute adoption future de CP-SAT, MIP ou d’un autre optimiseur exige une ADR.

## Validation

- fixture anonymisée avec 8 conteneurs et réservations localisées ;
- reproduction exacte de l’autosauvegarde Fusion ;
- déterminisme d’un seed diversifié ;
- suite complète, compilation, frontière `adsk`, diff-check et gate Fusion 0.1.44.
