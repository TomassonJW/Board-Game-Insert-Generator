# P64-L06 — rapport final du premier Goal autonome

## Ce qui fonctionne mieux

La mesure et la reprise du solveur sont désormais fiables et autonomes. BGIG dispose d'un journal local automatique, d'un corpus T0/T1 versionné, d'un petit oracle exact, de deux comparateurs offline et d'un runner qui reprend sans rejouer les résultats valides.

Le solveur produit, lui, n'est pas déclaré meilleur : aucune des trois variantes testées n'apporte de gain.

## Ce qui reste refusé ou non résolu

- 19 cas faisables discovery et 21 cas faisables tuning restent sans solution dans le budget pour le solveur courant lorsqu'ils sont effectivement tentables ;
- 33 à 37 cas par split demandent un contrôle de rotation que le schéma projet n'expose pas ;
- les réservations et la montée en nombre de conteneurs restent des limites importantes ;
- le cas dense historique 11 × 34 ne reçoit aucune nouvelle revendication ;
- aucune validation Fusion ou impression supplémentaire n'est déduite de la campagne offline.

## Coût réel

- 200 cas versionnés : 8 régressions, 64 discovery, 64 tuning et 64 holdout ;
- 904 exécutions cas/comparateur dans la campagne L06D ;
- un seul worker fonctionnel ;
- zéro dépendance externe ;
- zéro soak, car aucun gain ne le justifiait ;
- suite complète : 715/715 en 209,367 s sur la mission L06D.

## Décision finale

`no_algorithm_change_v1` est la seule sélection retenue. Les variantes `lane_center_quick_v1`, `lane_lowest_quick_v1` et `lane_interleave_quick_v1` sont rejetées faute de gain sur discovery et tuning. Le holdout confirme l'absence de gain et ne révèle aucune contradiction d'oracle.

Aucun changement algorithmique n'est intégré. Ce refus est le résultat attendu d'une gate honnête, pas une mission incomplète.

## Parcours livré

| Mission | Résultat | SHA intégré dans `main` |
| --- | --- | --- |
| P64-L05V-R2 | bouton DEV retiré, journal automatique 0.1.59 | `0ff340cc87344d913856d214934df47f29144d37` |
| P64-L06A | 13 bundles classés, un cas réel anonymisé | `ffaf6726f58b3a31b0c4445ed0fe908f88a74bb0` |
| P64-L06B | corpus 8 + 192, holdout fermé | `187a428171d467cfacaaa4857ac4d58f3a20d463` |
| P64-L06C | deux comparateurs et petit oracle exact | `30d7301cf92f03650a4467df729a729c1fd3c1e5` |
| P64-L06D | runner, tournoi, holdout et rapport négatif | `0b84d003090b2551c12013f83956b22d4ff1b038` |
| P64-L06E | décision finale négative | commit contenant ce rapport |

Chaque SHA renseigné a été poussé directement dans `main` puis vérifié à distance avant la mission suivante.

## Ce que Thomas doit faire dans Fusion

Rien pour clôturer ce Goal.

Le bouton DEV n'existe plus. Les actions normales dans BGIG continuent à alimenter automatiquement le journal local. Une future observation Fusion peut donc être analysée sans parcours spécial, sans recapture imposée et sans promotion automatique des projets personnels.

## Frontières conservées

- T0/T1 seulement ;
- aucune forme T2 à T4 ;
- aucun changement silencieux de budget, délai, certificat, schéma, tolérance ou valeur physique ;
- aucun déplacement de propriété entre P45 et P64 ;
- aucune finalisation, CAD ou scène automatique ajoutée ;
- `fusion-validated: false` pour L06 ;
- `print-validated: false`.

## Prochaine décision

Le Goal est terminé. La prochaine étape n'est pas une action technique automatique : il faut choisir si un second programme de recherche mérite d'être lancé. S'il l'est, il devra cibler une lacune précise — contrôle de rotation, réservations ou recherche multi-conteneurs — et créer un nouveau holdout avant toute sélection.
