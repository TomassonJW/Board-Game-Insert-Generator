# Next Actions

Derniere mise a jour : 2026-07-12

## Version active

`V0.1 - MVP fonctionnel accepte dans Fusion`.

La vision canonique est `docs/CANONICAL_PRODUCT_VISION.md`. Le chemin executable
est `docs/MVP_EXECUTION_PLAN.md`. L ordre V0.1 -> V0.2 -> V0.3 est verrouille par
ADR-0047.

## Derniere mission terminee

`P43 - Acceptation MVP V0.1` : le jeu temoin fonctionnel a ete prepare avec
20 pieces CAD et 19 cavites, puis confirme dans Fusion par le retour humain
`Fusion P43 OK` du 2026-07-12. Le MVP logiciel V0.1 est donc accepte dans
Fusion ; l impression 3D reste a valider separement.

## Suite recommandee, non lancee

`P51 - Qualite des volumes de complement V0.1.1` : reduire les remplissages
automatiques peu utiles et rendre leur lecture Fusion plus claire, sans casser
la conservation de volume ni le parcours Studio. C est le suivi direct du
retour produit P43 ; ce lot n est pas bloquant pour l acceptation du MVP et
reouvrira un smoke Fusion seulement s il change la geometrie.

`P44 - Contrat de formes et ergonomie V0.2` est maintenant autorise par la
roadmap, mais il n est pas demarre : aucun arrondi, encoche ou couvercle ne doit
etre ajoute par anticipation.

## Gate humaine active

Aucune gate humaine active pour le MVP V0.1 accepte. Une nouvelle observation
Fusion ne sera demandee que par un lot qui modifie effectivement la scene CAD.
## Fin de chaque mission

Tests pertinents, `git diff --check`, commit atomique, integration directe dans
`main`, push, puis selection de la mission suivante seulement si elle est dans le
chemin critique de la version active.