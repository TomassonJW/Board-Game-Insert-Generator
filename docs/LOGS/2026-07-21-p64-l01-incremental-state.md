# P64-L01 — État incrémental et cache local

Date : 2026-07-21.

P64-L01 implémente dans le cœur Python les clés/digests, le graphe
d'invalidation ciblé, les états courants/obsolètes, les jetons stale et un cache
LRU fail-closed. Le runtime P44-M007, la palette, le solveur et le schéma projet
ne sont pas branchés sur cette API dans ce lot.

Les fixtures prouvent asset seul, conteneur seul, déplacement entre deux
conteneurs, boîte, defaults hérités, overrides, réponse tardive, identité de
requête, fill local et corpus de cinquante conteneurs. Le corpus dense 11 × 34
reste `no_solution_within_budget` et n'est pas résolu par L01.

Validation : 16 tests L01, 6 tests de continuité Fusion-only, 587 tests complets,
Ruff, compileall, frontière adsk et diff-check. P64-L02 devient `ready`.
`fusion-validated: false`, `print-validated: false`.
