# P64-H03R — Préserver la baseline de recherche dirigée

Statut : `implemented`, `automated-validated`. Décision produit explicite du
2026-07-17 : une amélioration H03 qui résout davantage de cas réels ne doit pas
être retirée parce qu'un autre cas dense reste en échec.

## Objectif

Réintégrer le chemin H03 par contraintes au-dessus de P64-H04, sans le présenter
comme une solution générale ni une validation Fusion. La baseline de P64-H05 et
des solveurs suivants comprend donc : chemin canonique, ordres structurés H03,
puis reprise hash H02, avec les statuts et la télémétrie H04.

## Portée

- conserver le chemin canonique sans coût supplémentaire lorsqu'il réussit ;
- conserver les sept ordres H03, le faisceau de piles diversifié, le contrôle
  des réservations hautes et le transfert Z borné ;
- conserver les sorties H04, les digests stables et la matérialisation explicite ;
- conserver les tests H03 qui construisent le cas dense, +6 assets et le stress
  à 28 conteneurs.

## Limites et vérité produit

Un nouveau cas réel dense peut encore échouer : c'est
`no_solution_within_budget`, jamais une régression volontaire vers la baseline
H02 ni une preuve d'impossibilité. P64-H06 et P64-H07 restent nécessaires pour
un placement 3D réellement différent et un portefeuille plus robuste.

`fusion-validated: false` pour H03R ; la dernière preuve Fusion solveur reste
P64-H01 0.1.42. `print-validated: false`.

## Validation requise

- régressions H03 de partition et de solveur volumétrique ;
- régressions H04 de résultat/transport/CAD ;
- suite complète, `compileall`, frontière `adsk`, `git diff --check` ;
- aucun changement de schéma, defaults, valeurs physiques, tolérances,
  réservations, cavités ou matérialisation automatique.

## Suite

P64-H05 reste la prochaine mission : encapsuler cette baseline conservée derrière
le contrat commun stratégie/candidat/certificat. P64-H06 à H08 restent bloquées.
