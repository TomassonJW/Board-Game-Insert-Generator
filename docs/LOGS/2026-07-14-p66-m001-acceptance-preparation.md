# 2026-07-14 - P66-M001 preparation de la gate Fusion MVP

## Contexte

P66-M000 est integree dans `main` avec le package Fusion 0.1.20. P66-M001
prepare exclusivement les preuves, fixtures, installation et observation humaine
du MVP Fusion-only ; il ne change pas le runtime produit.

## Changements

- fixtures deterministes : un projet complet sans complement et un projet
  impossible a contrainte fixe locale ;
- preflight Python : normalisation, plan, resultat, CAD IR et plan Fusion
  compact exportes dans un repertoire temporaire lisible ;
- preparateur unique : preuves ciblees, installation existante, marqueur de
  commit, rapport de preflight et sauvegarde utilisateur non destructive ;
- controle d installation : runtime palette, marqueurs et manifeste 0.1.20 ;
- checklist P66-V : 21 observations humaines, preservation d un objet non BGIG
  et format de retour OK/KO ;
- tests : cycle bridge, axes Auto/Cible/Fixe, cartes sleevees, reservations,
  CAD/Fusion, impossibilite et cardinalite 50.

## Resultats fixes

- fixture complete : 8 corps demandes, 0 complement, 0 automatique, 2 etages ;
- plan : `b5bf4e9c164642bfacc51bec038421827a1d30738f22149d2a00e6603d8abc9e` ;
- CAD IR : 8 composants, 9 cavites, 7 coupes d empreinte superieure ;
- fixture impossible : `CONTAINER_MINIMUM_BLOCKED`, aucun CAD materialisable.

## Impact et suivi

P66-M001 ne modifie ni solveur, ni score, ni tolerance, ni geometrie, ni
semantique future des complements. Le statut de sortie est `gate-prepared` :
aucune validation Fusion ou impression n est declaree. La prochaine action est
uniquement P66-V ; P67 et P44 restent fermes jusqu a un OK humain explicite.
