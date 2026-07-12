# Next Actions

Derniere mise a jour : 2026-07-12

## Version active

`V0.1 - MVP fonctionnel complet`.

La vision canonique est `docs/CANONICAL_PRODUCT_VISION.md`. Le chemin executable
est `docs/MVP_EXECUTION_PLAN.md`. L'ordre V0.1 -> V0.2 -> V0.3 est verrouille par
ADR-0047.

## Derniere mission terminee

`P37 - Contrat projet V0.1 et migration` : `bgig.project.v1` represente la
boite, les pieces, les bacs partages, les plateaux/livrets et les remplissages.
Les projets P23 sont migrables sans perte ; les routes locales V1 et les tests
sont prets.

## Prochaine mission prete

`P38 - Tables dynamiques et parcours user-first`.

Resultat attendu : le Studio utilise `bgig.project.v1`, montre seulement boite,
pieces, plateaux/livrets et construction, permet de choisir un `Bac cible` par
ligne et masque candidats, layers, apparence et couvercles hors du parcours V0.1.

## Ce qui n'est plus demande a Thomas

Aucune revue UI, Git, GitHub, schema ou backlog. Le smoke P34 reste archive. La
seule intervention humaine de ce run sera une observation Fusion preparee apres
la geometrie V0.1 complete.

## Gate humaine active

Aucune avant le smoke Fusion V0.1 de P42/P43. Codex prepare automatiquement la
scene, l'add-in et les reglages locaux ; Thomas recevra seulement les actions
restantes dans Fusion et le resultat visible attendu.

## Fin de chaque mission

Tests pertinents, `git diff --check`, commit atomique, integration directe dans
`main`, push, puis selection de la mission suivante seulement si elle est dans le
chemin critique de la version active.