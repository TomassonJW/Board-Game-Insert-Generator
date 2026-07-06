# 2026-07-06 - P10-M005 asset candidate variants

## Mission

`P10-M005 - Generer des variantes simples depuis candidats assets`.

## Changement

Le moteur expose une variante deterministe `asset-candidates:row_fill` depuis les
`module_candidates`. Elle peut etre `recommended` si tous les candidats imprimables
rentrent, ou `rejected` avec raisons structurees.

## Limites

- Report-only : aucune mutation de `config.modules`.
- Aucun solveur global, aucun backtracking, aucune dependance lourde.
- Aucune generation Fusion nouvelle.
