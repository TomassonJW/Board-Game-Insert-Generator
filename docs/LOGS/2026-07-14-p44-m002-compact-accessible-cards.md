# P44-M002 - Cartes compactes accessibles

Date : 2026-07-14
Statut : `implemented`, `automated-validated`, `fusion-retest-required`,
`print-validated: false`.

## Resultat

La palette Fusion 0.1.22 conserve les reglages editables quand la densite
Compact est activee. Les cartes utilisent des grilles adaptees, un espacement
plus serre, des titres renforces et des actions de 40 px minimum.

Les cartes Conteneurs conservent `Solidite`, paroi minimale et fond minimal
en permanence. Les informations calculees - taille, etage, appui, surplus et
raisons par axe - sont rassemblees dans `Details calcules`, replie par defaut.

## Frontieres preservees

Aucun schema, loader, coeur Python, bridge metier, solveur, score, tolerance,
reservation, geometrie, CAD IR ou scene Fusion n est modifie. Les complements
restent en quarantaine. Les invariants de stabilite P44-M001 restent actifs et
aucun calcul metier n est ajoute au JavaScript.

## Preuves obtenues avant cloture Git

- 454 tests automatises, incluant les invariants DOM de densite et de details ;
- syntaxe JavaScript, exemple CLI, `compileall`, controle `adsk` et
  `git diff --check` passes ;
- observation Fusion differee : le lot reste `fusion-retest-required`.

## Suite

P44-M003 peut ouvrir les quatre onglets et Boite/plateaux/livrets seulement
apres integration de P44-M002 dans `main`.