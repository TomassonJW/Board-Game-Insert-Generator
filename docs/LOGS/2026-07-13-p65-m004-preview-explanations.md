# 2026-07-13 - P65-M004 explications d Apercu

## Livraison

P65-M004 est implemente dans la palette Fusion `0.1.19`.

Le coeur Python ajoute `bgig.preview_explanations.v1` au resultat de partition.
Cette projection traduit, sans modifier le plan P64, le score comparatif, les
appuis d etages, l appui des plateaux/livrets, l ordre de retrait, les residuels
et les suggestions optionnelles.

## Experience palette

- les sous-criteres du score sont nommes et expliques ;
- les statuts d appui n exposent plus d enum du solveur ;
- l ordre de retrait cite les noms des conteneurs, plateaux et livrets ;
- un residuel reste explicitement non materialise et une suggestion ne cree
  jamais un corps automatiquement ;
- `Exporter les imprimables` est primaire dans Apercu ;
- `Materialiser dans Fusion` reste l unique action persistante, a cote de
  `Recalculer`. Apercu ne les duplique plus.

## Bornes confirmees

- aucun changement de solveur, score, tolerance, cavite, reservation ou CAD IR ;
- aucune modification de plan ni de materialisabilite par la presentation ;
- aucun corps, appui, cale ou separateur automatique ;
- coeur Python sans `adsk` et parcours Fusion-only inchanges.

## Preuves

- 445 tests automatises verts ;
- syntaxe JavaScript de la palette et compilation Python vertes ;
- git diff --check, installation locale Fusion 0.1.19 depuis 23aaa70 et
  controle des marqueurs verts ;
- validation Fusion et impression reelle restent reportees a P66.