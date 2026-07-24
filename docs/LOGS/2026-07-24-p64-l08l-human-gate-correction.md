# 2026-07-24 — P64-L08L correction de la gate humaine SCIP 3D

La première gate 0.1.61 a échoué : Approfondi était plafonné à 30 s et l’interface ramenait l’état SCIP à `bounded_portfolio_exhausted`. Le projet public 18x20 et le projet réel local 28x30 terminaient sans plan.

Correction décidée par ADR-0086 : emphase faisabilité SCIP, arrêt au premier plan, plafond Approfondi de 120 s, remplissage déterministe des petites familles répétées et recertification BGIG complète.

Preuves avant gate Fusion :

- projet réel local 28x30 : 28 placements recertifiés, un appel SCIP, zéro voie interne, environ 20 s ; données privées non versionnées ;
- régression publique 28x30 : 28 placements recertifiés, moteur hybride, un appel SCIP, zéro voie interne ;
- archive runtime inchangée ; worker et artefact re-scellés ;
- interface et journal enrichis avec l’état SCIP réel.

La version produit devient 0.1.62. La prochaine action est l’intégration, l’installation locale vérifiée puis la gate humaine décrite dans `P64_L08L_FUSION_GATE_CHECKLIST.md`.

`fusion-validated=false`. `print-validated=false`. Holdout non rouvert.