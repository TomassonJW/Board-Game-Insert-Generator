# P65-M002 - Separation des frontieres de jeu

Date : 2026-07-13

## Decision et perimetre

P65-M002 separe le jeu X-Y par cote de boite du jeu X-Y total entre
conteneurs. Le jeu Z total entre conteneurs reste distinct de
`box.lid_clearance_mm`, qui represente la marge superieure. Le bas reste ancre
a Z=0.

Les projets V1 sans `container_box_xy_clearance_mm` heritent de
`layout_clearance_mm` pour conserver leurs placements. Les valeurs par defaut
restent 0,6 mm ; zero reste autorise sans recalibrage.

## Fusion et CAD IR

La palette 0.1.17 expose chaque role une seule fois. La CAD IR transporte les
quatre roles. Les sketches de reference bottom/top restent crees, tagues et
inspectables, mais `isLightBulbOn` est desactive apres leur creation, y compris
en regeneration.

## Preuves

- migration historique sans changement de placements ;
- cas XY bord nul/inter-conteneurs non nul et inverse ;
- independance du jeu Z entre etages et de la marge superieure ;
- CAD IR et palette a quatre roles explicites ;
- 434 tests executes verts en lots courts, compilation et exemple CLI verts.

## Limites

Le comportement n est pas encore observe dans Fusion 360 ni valide par
impression reelle. Aucun support, cale, corps automatique, jeu inferieur,
heuristique nouvelle ou refonte visuelle n est ajoute.