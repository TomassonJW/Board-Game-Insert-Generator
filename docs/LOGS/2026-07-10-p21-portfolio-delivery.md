# 2026-07-10 - P21 deterministic variant portfolio delivery

## Mission

Terminer P21 : rendre le portefeuille de variantes P20 comparable, selectionnable et transportable sans franchir la gate UX persistante.

## Livrables

- `box_fill_variants.v0` avec policies bornees, deduplication geometrique, Pareto, sous-scores et recommendation sure.
- Rapports Markdown/JSON, dashboard HTML statique et export de selection explicite.
- Metadata CAD IR de portefeuille, selection et solution choisie sans materialisation Fusion.
- Fixture P21 et tests de determinisme, CLI et serialisation.

## Limites

Pas de backtracking, solveur global, UI persistante, materialisation Fusion, impression ou validation ergonomique physique.

## Suite

P22-M001 peut preparer le rapport de gate ADR-0036 sur le choix de la premiere surface UX persistante.
