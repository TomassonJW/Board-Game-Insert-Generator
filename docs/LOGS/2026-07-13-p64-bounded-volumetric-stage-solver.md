# 2026-07-13 - P64 solveur volumetrique borne par etages

## Contexte

P57 imposait une hauteur unique a tous les corps et ne pouvait pas composer une
boite par niveaux. ADR-0059 avait retenu un solveur pur, heuristique, borne et
deterministe, sans dependance d optimisation externe.

## Changements

- Ajout de `bgig.volumetric_stage_solver.v1` : arrangements XY, rotations,
  composition Z, appui, retrait, budget explicite et sous-scores.
- Les conteneurs exposent `Auto`, `Cible` et `Fixe` par axe, avec migration
  additive des anciens locks ; les cavites P55 restent calibrees et revalidees.
- `proposal_with_residuals` expose des zones non imprimables et une suggestion
  de cale optionnelle, sans creer ni muter un corps automatique.
- La CAD IR transporte les origines Z et metadata d etage. Une proposition
  partielle est visible dans la palette mais bloquee avant toute synchronisation
  Fusion.
- Les reservations P63 sont revalidees avec P64 et ne coupent que les corps de
  l etage superieur effectivement intersecte.
- Le package Fusion passe a 0.1.14 et son script d installation verifie que le
  nouveau solveur pur est embarque.

## Verifications

- `PYTHONPATH=src; python -m unittest discover -s tests` : 423 tests OK.
- Tests cibles : solveur, result view, CAD IR, bridge palette, synchronisation
  Fusion, reservations P63 x P64 et contrat de packaging.
- Compilation Python, syntaxe JavaScript extraite de `palette.html`, absence de
  `adsk` dans le coeur et controle de diff sont prepares pour la cloture.

## Impact

Le coeur peut maintenant proposer une vraie organisation multi-etages sans
inventer de volume imprimable. Le comportement est `implemented` et
`automated-validated`, mais pas encore `fusion-validated` ni `print-validated`.

## Suivi

- P65 est la prochaine mission ready : rendre les dimensions, tolerances,
  estimations, sous-scores et materialisation plus lisibles dans la palette.
- P66 reste la gate humaine Fusion-only du MVP revise.
