# P60 - Preparation de l acceptance Fusion-only

## Resultat

Le projet de smoke, le preparateur d installation exacte et la checklist P60
sont reproductibles. Le fixture construit 2 corps, 3 cavites, 0 complement et
0 corps automatique en mode Fusion compact.

## Defaut detecte avant gate

Une cavite plus courte que la cavite maximale restait sous la face superieure
apres expansion Z. Le correctif conserve sa taille P55 et la recale sur le top
final, conformement a la distribution P57 `below > 0`, `above = 0`.

## Gate restante

Observation humaine dans Fusion du parcours palette, materialisation,
regeneration sans doublon, inspection et export de deux STL. Aucune validation
d impression n est incluse.