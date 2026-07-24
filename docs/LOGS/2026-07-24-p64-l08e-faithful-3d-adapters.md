# 2026-07-24 — P64-L08E, adaptateurs externes 3D fidèles

- PackingSolver `box` est verrouillé au SHA `0cae9d0`, construit localement en
  MSVC x64 Release et reste `benchmark-only` avant audit final de redistribution.
- OR-Tools CP-SAT 9.15.6755, SCIP 10.0.2/PySCIPOpt 6.2.1, PackingSolver et LAFF
  4.2.1 représentent quatre moteurs et quatre familles externes.
- Le protocole commun transporte X/Y/Z, variantes, rotations, appuis,
  réservations, fragmentation, accès et contenus ; aucun témoin L08D n'est
  transmis.
- Les quatre moteurs produisent un empilement à deux niveaux recertifié par
  BGIG. OR-Tools et SCIP passent les six contrôles, dont une impossibilité
  prouvée. PackingSolver et LAFF déclarent quatre règles `unsupported` et
  conservent `bounded_unknown` sur le négatif.
- Reçu : `a3c35ee1bddc5578aeb41e79639c507e1d8236d470a39769ace77d2303192d76`.
- Le holdout L08D reste fermé et à zéro invocation. Aucun gagnant, aucune
  intégration produit, aucune validation Fusion ou impression.
- Suite : P64-L08F, régressions, discovery, tuning, sélection scellée puis
  ouverture unique du holdout.