# Box Fill Solver Roadmap

## But

Passer de l'heuristique locale actuelle a des `BoxFillPlan` explicables, sans sauter directement vers un optimiseur opaque.

| Etape | Entrees | Sorties | Tests et gate | Risque |
| --- | --- | --- | --- | --- |
| `box_fill_v0_manual_modules` | Box, reservations, modules manuels, positions | collisions, coverage, `FreeVolume`, warnings | unitaires volume/collision + gate produit P19 | modele trop pauvre |
| `box_fill_v1_greedy_2d` | modules V0 et intentions simples | placement XY deterministe par layer | fixtures reproductibles, refus lisibles | ordre greedy mediocre |
| `box_fill_v2_layers_and_reservations` | boards, rules, lid, removal order | layers et contraintes Z valides | tests collision/retrait + gate physique si support revendique | contraintes contradictoires |
| `box_fill_v3_variant_generation` | contraintes et candidats | 3-5 variantes scorees | scores decomposes, determinisme, gate produit | score trompeur |
| `box_fill_v4_interactive_editor` | variante + locks/deplacements | regeneration locale sans deplacer les locks | contrats UI/moteur + gate UX | etat UI complexe |
| `box_fill_v5_full_assistant` | projet, preferences, historique | propositions expliquees et actions assistees | evaluation explicable + gate IA | automatisation opaque |

## Regles de progression

- Chaque etape conserve un moteur Python pur et une CAD IR sans recalcul Fusion.
- Les contraintes sont versionnees, visibles dans les rapports et associees a une raison de refus ou relaxation.
- Les reservations et le retrait passent avant l'optimisation de compacite.
- Une validation Fusion prouve une materialisation, une impression reelle seule prouve la physique.

## Etat apres P19

`box_fill_v0_manual_modules` est termine : P19 a livre le BoxFillPlan manuel, sa validation et son transport CAD IR metadata. La prochaine etape recommandee est `box_fill_v1_greedy_2d`, mais elle reste bloquee par une gate produit explicite car elle introduit la premiere source de positions semi-automatique. Elle ne doit pas etre confondue avec un solveur global, une palette ou une variante scoree.
## P19 completion addendum

P19 est complet contre son contrat autorise : cellules libres AABB exactes (`exact_aabb_cells_v0`), conservation de volume, diagnostics structures, coverage par asset, CLI `validate-box-fill` / `report-box-fill` / `export-box-fill-plan`, fixtures valide et invalides, bridge explicite `derived_from_executable_asset_plan` et transport CAD IR metadata. Les cellules decrivent le residuel et ne constituent pas un placement automatique. P20 greedy reste bloque par gate humaine ; Fusion ne recalcule ni ne materialise ce plan.
## P20 completion - 2026-07-10

Statut : `done`, `implemented-core`, `implemented-cli`, `implemented-cad-ir-metadata`. Le moteur `box_fill_greedy_2d.v0` produit un nouveau BoxFillPlan sans muter la source, respecte locks, modules manuels, reservations et layers, supporte la rotation XY 90 degres et expose diagnostics, digest, metrics, rapports JSON/Markdown, preview SVG et metadata CAD IR. Aucun backtracking, solveur global, UI persistante, geometrie Fusion ou validation d impression n est ajoute. P21 reste gate et recommande les variantes/scoring.
## Etat apres P21

`box_fill_v3_variant_generation` est implemente dans son scope borne : policies deterministes, portfolios dedupliques, Pareto, sous-scores, preference, preview statique et selection explicite. Les policies restent des heuristiques d ordre de candidats ; elles ne constituent ni une recherche exhaustive ni une preuve ergonomique. L etape suivante est `box_fill_v4_interactive_editor`, mais sa surface persistante reste bloquee par la gate ADR-0036.

## Actualisation P64 — recherche globale produit

Les étapes historiques P19-P21 restent des fondations utiles, mais la route
produit P64 est désormais : observabilité, contrat commun, baseline par étages,
greedy 3D EP/EMS, beam, portfolio Auto, puis UI/gate. Les variantes P21 ne sont
pas une recherche 3D et ne prouvent pas l'impossibilité.

La finition continue/modulaire est une phase séparée après P46. Le mode exact est
un horizon optionnel, non une dépendance actuelle. Le détail exécutable et les
budgets à benchmarker sont dans `P64_MULTI_SOLVER_PORTFOLIO_PROGRAM.md`.
