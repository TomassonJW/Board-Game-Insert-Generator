# Journal P64-L05D1 - corpus solveur et gate A/B

Date : 2026-07-22.

## Mission

Installer la boucle de developpement reproductible demandee apres le retour
L04V : capturer explicitement, rejouer, comparer, puis seulement optimiser.

## Livraisons

- schema et producteur purs de corpus ;
- validation exacte des SolverCaseBundle ;
- manifest anonymise de sept cas ;
- replay CI/extended avec preuve fonctionnelle deterministe ;
- temps mur separes et non normatifs ;
- comparaison A/B qui refuse toute regression fonctionnelle ;
- scripts CLI de replay et de comparaison ;
- ADR-0079, contrat, preuve et tests.

## Observation du projet personnel

Le projet indique par Thomas a ete lu et rejoue sans modification. Les trois
efforts echouent avant toute completion geometrique ; Deep atteint les limites
des lanes de variantes. Le SHA-256 du fichier est reste strictement identique.
Aucune donnee personnelle n'est entree dans le corpus.

## Decision de decoupage

P64-L05D est separe en deux missions atomiques :

- L05D1 : corpus, baseline et gate A/B ;
- L05D2 : premiere optimisation du solveur, mesuree contre cette baseline.

Ce decoupage empeche de modifier le solveur avant de posseder un filet de
non-regression fonctionnelle.

## Suite

Evaluer en L05D2 une optimisation semantiquement bornee des participants sous
ordre explicite. La conserver seulement si le corpus et les tests demontrent
l'absence de regression et un gain mesurable de travail ou de capacite.
