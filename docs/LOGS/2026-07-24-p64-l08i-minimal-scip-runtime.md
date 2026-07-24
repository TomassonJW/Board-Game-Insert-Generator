# 2026-07-24 — P64-L08I runtime SCIP minimal

## Mission

Cadrer avant build un runtime SCIP 10.0.2 / PySCIPOpt 6.2.1 `cp314`
redistribuable, sans rejouer le benchmark ni le holdout L08F.

## Décision

- ADR-0084 acceptée dans le Goal autonome post-benchmark ;
- SoPlex 8.0.2 conservé comme solveur LP nécessaire au MIP ;
- plugins MIP internes, symétrie `snauty` et LTO conservés ;
- Ipopt, MUMPS/METIS, runtimes Intel, PaPILO/TBB, GCG, ZIMPL, GMP et
  exact-solve retirés du premier candidat ;
- build Python `cp314` et natif entièrement local à `.codex-work` ;
- runtime Visual C++ `/MD`, avec seulement les DLL réellement requises issues
  du dossier officiel `VC/Redist` après scan du build.

## Preuves

- worker scellé : 18 sites `addVar`, uniquement `B`/`I`, aucun produit entre
  expressions de décision ni primitive non linéaire ;
- sept familles 3D protégées, dont empilement et appuis ;
- SCIP 10.0.2, SoPlex 8.0.2 et PySCIPOpt 6.2.1 verrouillés par tag, commit,
  taille et SHA-256 ;
- Python 3.14.0 NuGet, Cython 3.2.8, setuptools 83.0.0, wheel 0.47.0 et
  NumPy 2.5.1 verrouillés ;
- Visual Studio 17.14.2, MSVC 19.44.35207.1, SDK 10.0.26100.0 et CMake 4.0.2
  identifiés.

## Résultat

`minimal_scip_build_audit_pass`. Seul le build et l'équivalence publique L08J
sont autorisés. Aucun solveur, benchmark, holdout, runtime produit ou add-in
Fusion n'a été lancé ou modifié.

`fusion-validated=false`. `print-validated=false`.
