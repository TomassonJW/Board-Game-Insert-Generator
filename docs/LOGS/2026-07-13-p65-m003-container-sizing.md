# 2026-07-13 - P65-M003 tailles de conteneurs et estimation

## Livraison

P65-M003 est implemente dans la palette Fusion `0.1.18`.

Le coeur Python expose `bgig.container_sizing_view.v1`, une projection additive
par identifiant stable de conteneur. Elle separe le minimum derive, la demande
Auto/Cible/Fixe, la taille du dernier plan, le surplus, l etage et l appui.
Elle ne modifie ni projet, ni solveur, ni scene Fusion.

## Comportement palette

- les cartes compactes montrent minimum, reglage, taille calculee et statut ;
- la vue detaillee montre les trois axes, motifs du solveur, surplus et etage ;
- `Estimer les tailles` appelle uniquement `solve_project` ;
- aucun nouvel endpoint, estimateur JavaScript, sauvegarde ou materialisation
  n est ajoute ;
- les etats non calcule, a jour, perime, partiel et impossible restent
  distinguables ;
- un double clic ne lance pas deux estimations simultanees.

## Bornes confirmees

- aucun changement de solveur, score, tolerance, cavite, reservation ou CAD IR ;
- aucun corps, support ou separateur automatique ;
- `Materialiser dans Fusion` conserve ses gardes complete/a-jour ;
- Fusion-only et coeur sans `adsk` inchanges.

## Preuves

- 440 tests automatises verts ;
- syntaxe JavaScript de la palette validee par Node ;
- compilation Python validee ;
- `git diff --check` vert ;
- dry-run de l installation Fusion 0.1.18 vert, sans ecriture AppData.

La validation humaine Fusion et l impression reelle restent reportees a P66.
