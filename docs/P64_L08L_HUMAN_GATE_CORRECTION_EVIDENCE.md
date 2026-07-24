# P64-L08L — Preuve de correction de la gate humaine SCIP 3D

## Résultat

La gate humaine 0.1.61 est classée KO. L’arrêt observé à environ 29 secondes n’était pas une preuve d’impossibilité : le plafond produit SCIP était fixé à 30 secondes et l’interface masquait son état `bounded_unknown` derrière `bounded_portfolio_exhausted`.

La correction 0.1.62 :

- cherche d’abord un plan faisable ;
- s’arrête au premier plan trouvé ;
- autorise jusqu’à 120 secondes en Approfondi sans imposer cette durée ;
- extrait les longues séries de petits conteneurs identiques du cœur combinatoire, tout en conservant deux représentants dans SCIP ;
- recertifie le plan complet avec BGIG ;
- expose l’état réel de SCIP dans le diagnostic et le journal local.

## Preuves réelles locales, non versionnées

Le journal local de Fusion confirme deux échecs 0.1.61 :

- projet public : 18 conteneurs / 20 éléments, environ 29,4 s, `no_solution_within_budget` ;
- projet limite de Thomas : 28 conteneurs / 30 éléments, environ 30,7 s, `no_solution_within_budget`.

Après correction, le même projet limite local 28x30 produit :

- `solution_found` ;
- 28 placements ;
- moteur `hybrid_anchor_and_fill` ;
- recertification BGIG positive ;
- un seul appel SCIP ;
- zéro voie interne ;
- environ 20 secondes sur ce contrôle.

Aucun instantané, nom métier ou contenu privé de ce projet n’est ajouté au dépôt.

## Régression publique versionnée

`tests/fixtures/p64_l08l_scip_repeated_fill_regression.v1.json` est générée depuis `real-18-containers-20-contents-normal` en ajoutant dix copies anonymisées du petit conteneur public. Elle contient 28 conteneurs et 30 éléments.

Résultat CPython Fusion 3.14 avec le paquet produit :

- 28 placements ;
- `solution_found` ;
- source `external_scip_real_3d` ;
- moteur `hybrid_anchor_and_fill` ;
- recertification BGIG positive ;
- un appel SCIP ;
- aucune voie interne ;
- `globally_optimal=false` ;
- holdout non lu.

Le script reproductible est `scripts/solver/validate_scip_repeated_fill_regression.py`.

## Paquet produit

- add-in : 0.1.62 ;
- SCIP : 10.0.2 ;
- PySCIPOpt : 6.2.1 ;
- archive runtime inchangée : `0a718ea5884d6326d66777db0ab853a31fa981e6392b89f184342fde27d465c6` ;
- nouvel artefact worker : `05d4566e93efef2b6606b0d1807abaaf29bc460c37accee31da20ae2a6462065`.

## Limites et vérité de statut

Cette preuve démontre un gain réel sur le cas limite local observé et sur une régression publique 28x30. Elle ne démontre pas une solution pour toute géométrie 3D ni une optimalité globale. La correction n’élargit pas les formes, tolérances, règles physiques, finalisation ou matérialisation.

`fusion-validated=false` jusqu’à la prochaine exécution dans Fusion. `print-validated=false`.
## Validation automatisée finale

- preuve publique 28x30 CPython Fusion 3.14 : OK ;
- preuve privée locale 28x30 avec le paquet final : OK, environ 20 s ;
- préflight et installation à blanc 0.1.62 : OK ;
- tests ciblés solveur, palette, préflight et audit : OK ;
- suite complète : 834/834 en 273,459 s ;
- Ruff, format, compilation Python, parse PowerShell et contrôles de diff : OK.