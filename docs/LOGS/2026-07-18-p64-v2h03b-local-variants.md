# P64-V2H03B — Frontière locale, certificats et caps

## Déclencheur

Le GO du 2026-07-18 ouvre H03B après ADR-0070 et le contrat de coordination.

## Résultat

Le cœur dispose de types immuables, deux producteurs, un digest, un certificat
local fail-closed, une déduplication traçable, une frontière de Pareto et des
caps monotones. Aucun branchement n'est fait dans le portefeuille public.

## Preuves

- fixtures H03B 1 à 8 automatisées ;
- corpus dense 11 × 34 : 231 layouts bruts, caps 24/48/96 atteints ;
- tests ciblés cumulés : 27 OK ;
- suite complète : 556/556 OK (166,087 s).

Voir `docs/P64_V2H03B_LOCAL_VARIANT_EVIDENCE.md`.

## Statut

H03B : `implemented-core`, `automated-validated`.
H03C devient `ready`. Aucune gate Fusion n'est ouverte.
