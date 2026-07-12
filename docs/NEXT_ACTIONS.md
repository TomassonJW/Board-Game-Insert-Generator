# Next Actions

Derniere mise a jour : 2026-07-12

## Version active

`V0.1 - MVP fonctionnel complet`.

La vision canonique est `docs/CANONICAL_PRODUCT_VISION.md`. Le chemin executable
est `docs/MVP_EXECUTION_PLAN.md`. L'ordre V0.1 -> V0.2 -> V0.3 est verrouille par
ADR-0047.

## Derniere mission terminee

`P38 - Tables dynamiques et parcours user-first` : le Studio V0.1 permet de
saisir la boite, les pieces, leur bac cible, les plateaux/livrets, les volumes de
remplissage et les reglages de fabrication. Il charge, migre et sauvegarde le
contrat `bgig.project.v1` sans vocabulaire moteur dans le parcours principal.

## Prochaine mission prete

`P39 - Derivation des bacs et logements`.

Resultat attendu : le moteur derive des bacs et logements explicables depuis la
forme, les mesures, la quantite et le `Bac cible`, sans demander une taille de
bac externe a l utilisateur.

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