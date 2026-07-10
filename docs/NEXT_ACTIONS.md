# Next Actions

Derniere mise a jour : 2026-07-10

## Politique active - Integration Git autonome

Statut : `active`. Le chemin standard reste `direct-to-main` apres tests, diff propre et verification de `origin/main`.

## Etat courant

`P19-BOX-FILL-MANUAL-MODULES-SPRINT` est termine : `box_fill_plan.v0` est une source de verite manuelle, versionnee, CAD-agnostic et retrocompatible dans le moteur pur. Les modules, reservations, layers, allocations, coverage, validation et FreeVolume aggregate sont exposes dans Markdown/JSON/CAD IR metadata. Fusion ne materialise pas encore ce plan.

## Gate humaine active

Decision requise : accepter ou refuser `P20-BOX-FILL-GREEDY-2D-SPRINT` selon `docs/P20_RECOMMENDATION.md`. P20 introduirait seulement un placement XY deterministe par layer, sans backtracking ni optimisation globale.

La gate ADR-0036 reste active et independante avant toute palette Fusion ou app locale/web. L'impression 3D physique reste non validee.

## Mission suivante si gate acceptee

`P20-BOX-FILL-GREEDY-2D-SPRINT` : placer des modules/candidats non verrouilles dans un BoxFillPlan, preserver reservations et locks, refuser lisiblement les placements impossibles, sans changer Fusion ou les tolerances.

## Missions bloquees par gate

- P20 greedy 2D ci-dessus.
- Palette persistante HTML, app locale/web, UI assets avancee/tableau et editeur interactif.
- Solveur global, backtracking, optimisation avancee et variantes scorees.
- Materialisation Fusion de BoxFillPlan, nouvelle geometrie produit, assets individuels Fusion et impression 3D validee.

## Fin de chaque mission

Appliquer la politique active direct-to-main : tests pertinents, git diff --check, commit atomique, integration directe dans main, push vers origin/main, puis reprise depuis une branche propre si aucune vraie gate humaine n'est atteinte.
