# Next Actions

Derniere mise a jour : 2026-07-12

## Version active

`V0.1 - MVP fonctionnel complet`.

La vision canonique est `docs/CANONICAL_PRODUCT_VISION.md`. Le chemin executable
est `docs/MVP_EXECUTION_PLAN.md`. L ordre V0.1 -> V0.2 -> V0.3 est verrouille par
ADR-0047.

## Derniere mission terminee

`P42 - Geometrie fonctionnelle V0.1` : le Studio construit maintenant les bacs,
logements, supports et remplissages resolus, puis prepare une scene CAD
fonctionnelle pour Fusion. Les 50 bacs, 72 familles et 25 elements plats sont
couverts en mode Fusion compact, sans statut Fusion ou impression revendique.

## Prochaine mission prete

`P43 - Acceptation MVP V0.1`.

Resultat attendu : preparer automatiquement le jeu temoin, l add-in et ses
reglages locaux, puis obtenir une seule observation humaine dans Fusion. Cette
observation doit confirmer les bacs ouverts, leurs logements, les supports, les
remplissages et l absence de doublon. Elle ne demande ni impression, ni revue UI
ou Git.

## Ce qui n est plus demande a Thomas

Aucune revue UI, Git, GitHub, schema ou backlog. Le smoke P34 reste archive. La
seule intervention humaine de ce run est l observation Fusion P43 preparee par
Codex.

## Gate humaine active

P43 : observation Fusion du jeu temoin. Codex installe l add-in, produit le CAD
IR et ecrit les reglages locaux si l environnement l autorise ; Thomas recevra
uniquement les actions restantes dans Fusion et le resultat visible attendu.

## Fin de chaque mission

Tests pertinents, `git diff --check`, commit atomique, integration directe dans
`main`, push, puis selection de la mission suivante seulement si elle est dans le
chemin critique de la version active.