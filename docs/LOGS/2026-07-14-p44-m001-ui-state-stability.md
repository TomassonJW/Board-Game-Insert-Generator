# P44-M001 - Stabilite de saisie de la palette

Date : 2026-07-14
Statut : `implemented`, `automated-validated`, `fusion-retest-required`,
`print-validated: false`.

## Resultat

La palette Fusion 0.1.21 conserve son contexte d interaction lors des rendus de
listes : focus, selection/caret, details ouverts, carte active et scroll. Les
cles UI sont derivees des identifiants stables de contenus, plateaux/livrets,
conteneurs et complements historiques ; aucun contexte n est restaure par index
instable.

Chaque mutation source incremente une revision. Une reponse `validate_project`
ou `solve_project` arrivee pour une revision ancienne est ignoree. Les resets
legitimes d import, chargement et bootstrap n essayent pas de restaurer un ancien
contexte visuel.

## Frontieres preservees

Aucun schema, loader, coeur Python, solveur, score, tolerance, reservation,
geometrie, scene Fusion, navigation, complement ou semantique produit n est
modifie. La palette ne recoit aucun calcul metier supplementaire et la
materialisation reste explicite avec ses gardes existantes.

## Preuves obtenues avant cloture Git

- 453 tests passes, dont les tests DOM, bridge et transport de palette ;
- syntaxe JavaScript, exemple CLI, `compileall`, controle `adsk` et
  `git diff --check` passes ;
- observation Fusion differee : le lot reste `fusion-retest-required`.

## Suite

P44-M002 pourra traiter la densite et la hierarchie de cartes seulement apres
integration de P44-M001 dans `main`.
