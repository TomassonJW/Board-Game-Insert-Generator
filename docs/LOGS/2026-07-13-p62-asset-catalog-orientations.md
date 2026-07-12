# P62 - Catalogue d elements et orientations

## Objectif

Donner au solveur des dimensions de cavite correctes pour les cartes sans
attendre le solveur multi-etages P64 : formats locaux, sleeves, epaisseur de
paquet et orientation doivent etre resolus dans le coeur pur avant le layout.

## Contrat livre

- cinq formats de cartes locaux avec dimensions non sleevees et sleevees ;
- dimensions manuelles toujours prioritaires sur le catalogue ;
- epaisseur du paquet mesuree directement ou calculee par nombre de cartes ;
- orientations a plat, debout sur grand cote, debout sur petit cote et auto ;
- separation entre `base_dimensions_mm` et enveloppe XYZ `dimensions_mm` ;
- migration additive des projets historiques vers explicite + a plat ;
- presets personnels versionnes, atomiques et stockes hors du package Fusion ;
- import, export, reutilisation et suppression depuis la palette.

## Invariants

- aucune logique de resolution dans JavaScript ou `adsk` ;
- la cavite consomme uniquement les dimensions resolues par Python ;
- une modification invalide le plan sans regenerer Fusion automatiquement ;
- aucun catalogue distant, compte, cloud ou dependance externe ;
- P62 ne revendique ni encastrement superieur P63 ni solveur Z P64.

## Validation

401 tests automatises passent. La syntaxe Python et JavaScript est validee et
les nouveaux modules sont obligatoires dans le package Fusion 0.1.12. La
validation visuelle dans Fusion et toute validation impression restent ouvertes.
