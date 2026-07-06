# 2026-07-06 - P10-M008 executable asset module plan

## Mission

Implementer `P10-M008 - Generer un plan concret asset-first et placement grille greedy`.

## Livrables

- Fonction pure Python `build_executable_asset_module_plan`.
- Rapports Markdown/JSON enrichis avec `executable_asset_plan`.
- Metadata CAD IR additive `metadata.executable_asset_plan`.
- Exemple `examples/simple_asset_executable_plan.json`.
- Tests unitaires couvrant un placement greedy dans une grille 3D.

## Limites

- Heuristique greedy bornee `z/y/x`, sans backtracking ni optimisation globale.
- Aucune mutation de `modules`.
- Aucune generation Fusion nouvelle.
- Les dimensions restent derivees du moteur et de la grille, sans validation physique.
