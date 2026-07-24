# Runtime SCIP produit

Ce dossier contient le build minimal SCIP 10.0.2 qualifié par P64-L08J pour le
Python `cp314` de Fusion 360.

Le paquet est hors ligne et ne requiert ni installation globale, ni service, ni
compte, ni secret, ni télémétrie. `ARTIFACT.json` verrouille l'archive, l'arbre
extrait et les deux fichiers exacts du worker 3D du tournoi. L'installateur
Fusion vérifie puis extrait l'archive sous le dossier installé.

Un résultat SCIP ne devient jamais un plan BGIG par lui-même : l'adaptateur
produit recalcule les appuis, reconstruit les espaces et exige le certificat BGIG
commun. Les avis PySCIPOpt, SCIP, SoPlex, NumPy et Microsoft sont inclus dans
l'archive sous `runtime/notices`.

Voir `docs/DECISIONS/ADR-0085-scip-primary-product-lane.md` et
`docs/P64_L08J_MINIMAL_SCIP_RUNTIME_BUILD_EVIDENCE.md`.
