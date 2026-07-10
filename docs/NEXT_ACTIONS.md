# Next Actions

Derniere mise a jour : 2026-07-11

## Politique active - Integration Git autonome

Statut : `active` pour les missions non gatees. Les missions Fusion et physiques restent soumises aux gates documentees.

## Etat courant

L objectif actif replace BGIG sur sa trajectoire premium. P19 a P21 fournissent le moteur de planification, P23 a P27 le Studio local, P28 un raccord CAD IR technique. Le raccord P28 est requalifie `KO produit/UX` : il ne doit plus etre presente comme une generation d insert utilisable.

ADR-0042 fixe la surface cible : Studio principal pour concevoir et visualiser ; palette Fusion secondaire pour materialiser, inspecter et exporter. Le plan complet est `docs/PREMIUM_PRODUCT_EXECUTION_PLAN.md`.

## Gate humaine active

`P30-GATE - Direction visuelle et interaction principale` est la prochaine gate reelle. Le choix demande est documente dans `docs/P30_VISUAL_DIRECTION_GATE.md` : valider ou ajuster la direction `Atelier de rangement` avant de coder la refonte visuelle du Studio.

## Hors scope maintenu

- Fusion ne devient jamais source de verite du plan.
- P28 reste une preuve de raccord technique, pas une geometrie de bac fini.
- Aucun couvercle, clip, charniere ou mecanisme ne sera declare fonctionnel avant gate et impression reelle.
- Aucun statut `print-validated` ne sera utilise sans prototype mesure.

## Prochaine action

Apres validation P30, executer `P30-M001` : premier flux Studio novice et apercu de boite vivant. P31 ne commencera qu apres une strategie documentee de projection vers de vrais bacs.

## Fin de chaque mission

Appliquer direct-to-main pour tout lot non gate : tests pertinents, `git diff --check`, commit atomique, integration et push de `main`.