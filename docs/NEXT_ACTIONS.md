# Next Actions

Derniere mise a jour : 2026-07-12

## Version active

`V0.1 - MVP fonctionnel complet`.

La vision canonique est `docs/CANONICAL_PRODUCT_VISION.md`. Le chemin executable
est `docs/MVP_EXECUTION_PLAN.md`. L'ordre V0.1 -> V0.2 -> V0.3 est verrouille par
ADR-0047.

## Derniere mission terminee

`P36 - Rebase vision, audit et chemin critique` : vision, audit, ADR et plan de
releases verifies.

## Prochaine mission prete

`P37 - Contrat projet V0.1 et migration`.

Resultat attendu : le projet sait representer des groupes de bacs choisis depuis
les lignes de pieces, un tableau de plateaux/livrets, des remplissages, un jeu
commun et une epaisseur de paroi par bac, tout en rechargeant les anciens drafts.

## Ce qui n'est plus demande a Thomas

Le smoke P34 n'est plus une action active. Le coupon a rails exterieurs ne
correspond pas au couvercle coulissant canonique et les couvercles appartiennent
a la V0.3, apres acceptation de la V0.1 puis de la V0.2.

## Gate humaine active

Aucun pour P36 puis P37. La prochaine validation humaine produit obligatoire est
P43, apres livraison du parcours V0.1 complet. Des recettes UI intermediaires
peuvent etre preparees automatiquement ; si une observation humaine devient
indispensable, le rapport indiquera exactement l'ecran, l'action et le resultat
OK/KO attendus.

## Fin de chaque mission

Tests pertinents, `git diff --check`, commit atomique, integration directe dans
`main`, push, puis selection de la mission suivante seulement si elle est dans le
chemin critique de la version active.