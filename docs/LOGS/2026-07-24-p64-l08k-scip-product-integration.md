# 2026-07-24 — P64-L08K intégration produit SCIP

## Décision

ADR-0085 retient SCIP 10.0.2 seul comme lane produit 3D prioritaire. Le runtime
minimal L08J exact est embarqué dans l'add-in 0.1.61 et chargé dans le CPython
`cp314` de Fusion. BGIG reste l'autorité de certificat.

## Livré

- archive déterministe et manifeste SCIP produit ;
- installateur avec vérification SHA-256 et extraction locale ;
- adaptateur Python pur X/Y/Z, jeux, rotations et variantes ;
- budgets 1 / 5 / 30 s, 1 024 Mio, un thread ;
- arrêt sans second budget interne sur timeout ;
- fallback explicite sur runtime, représentation, erreur ou certificat ;
- préparateur et checklist de gate Fusion réelle.

## Faits

- contrôle forcé trois niveaux Z : solution SCIP, certificat BGIG, une
  invocation, zéro lane interne, deux runs déterministes ;
- cas public revu 18 conteneurs / 20 éléments : SCIP réellement invoqué, mais
  `bounded_unknown` à 5 s et 30 s ;
- aucune lecture ou répétition du holdout, aucun tuning post-holdout ;
- staging installateur 0.1.61 : OK ;
- validation finale : 828/828 tests en 252,471 s ; garde documentaire 2/2,
  alignement Fusion-only 6/6, Ruff, format, compilation et parse PowerShell : OK ;
- usion-validated=false, print-validated=false.

## Suite

P64-L08V intègre et pousse L08K, installe 0.1.61 depuis le commit distant
vérifié, puis remet à Thomas uniquement le test Fusion du cas public et de son
vrai projet limite.