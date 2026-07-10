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

## P19 completion addendum

P19 est complet contre son contrat autorise : cellules libres AABB exactes (`exact_aabb_cells_v0`), conservation de volume, diagnostics structures, coverage par asset, CLI `validate-box-fill` / `report-box-fill` / `export-box-fill-plan`, fixtures valide et invalides, bridge explicite `derived_from_executable_asset_plan` et transport CAD IR metadata. Les cellules decrivent le residuel et ne constituent pas un placement automatique. P20 greedy reste bloque par gate humaine ; Fusion ne recalcule ni ne materialise ce plan.
## P19-M007 - Completion des metriques de rapport

Statut : `done`. Les sorties JSON et Markdown exposent maintenant les volumes modules, reservations et libres par layer, les taux occupation/reservation et la couverture item-level. Les cellules libres restent exactes et descriptives; aucun solveur P20 n'est introduit.
## P19 product acceptance - 2026-07-10

Statut : `accepted`, `implemented-core`, `implemented-cad-ir-metadata`. P19 est accepte comme contrat executable BoxFillPlan manuel : validation volumetrique, coverage item-level, cellules libres AABB, metrics par layer, CLI, fixtures, bridge et metadata CAD IR. Il reste hors Fusion, sans solveur automatique et sans validation d'impression (`print_validated: false`). La gate P20 greedy 2D est levee ; la gate ADR-0036 palette/app reste distincte.
## P20 completion - 2026-07-10

Statut : `done`, `implemented-core`, `implemented-cli`, `implemented-cad-ir-metadata`. Le moteur `box_fill_greedy_2d.v0` produit un nouveau BoxFillPlan sans muter la source, respecte locks, modules manuels, reservations et layers, supporte la rotation XY 90 degres et expose diagnostics, digest, metrics, rapports JSON/Markdown, preview SVG et metadata CAD IR. Aucun backtracking, solveur global, UI persistante, geometrie Fusion ou validation d impression n est ajoute. P21 reste gate et recommande les variantes/scoring.