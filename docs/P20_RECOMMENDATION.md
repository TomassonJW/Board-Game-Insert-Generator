# P20 Recommendation - Deterministic BoxFill greedy 2D

## Decision requested

Recommandation : autoriser `P20-BOX-FILL-GREEDY-2D-SPRINT` comme prolongement borne de `box_fill_v1_greedy_2d`.

## Etat prouve par P19

`box_fill_plan.v0` est charge, valide et reporte par le moteur Python pur. Il represente une boite complete manuelle avec reservations, layers, modules, allocations explicites, coverage et FreeVolume aggregate. La CAD IR le transporte comme metadata sans creer de geometrie. Aucun placement automatique ne se cache dans Fusion ou la CAD IR.

## Scope P20 propose

- Consommer un `BoxFillPlan` V0 et des candidats de modules explicites.
- Preserver strictement les modules `locked` et les reservations.
- Placer de maniere deterministe en XY, layer par layer, selon un ordre documente.
- Produire un plan place ou des refus actionnables, sans backtracking ni score global.
- Conserver les sorties Markdown/JSON/CAD IR et le moteur sans `adsk`.

## Hors scope

- Pas de solveur global, backtracking, optimisation, variantes multiples, palette/app, materialisation Fusion, STL/3MF, nouvelle geometrie ou changement de tolerances.

## Criteres d'acceptation proposes

Une fixture de 2 a 4 modules/candidats et une reservation doit donner le meme plan a executions repetees, ne jamais deplacer un lock, refuser lisiblement un module qui ne tient pas, exposer les cellules/volumes restants et ne modifier aucune scene Fusion.

## Gate humaine

P20 change la source de positions de manuelle a semi-automatique. Autorisation produit explicite requise avant implementation. La gate ADR-0036 reste independante : aucune palette/app n'est incluse dans P20.