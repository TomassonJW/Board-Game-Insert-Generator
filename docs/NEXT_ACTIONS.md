# Next Actions

Derniere mise a jour : 2026-07-11

## Politique active - Integration Git autonome

Statut : `active` pour les missions non gatees. Les missions Fusion et physiques restent soumises aux gates documentees.

## Etat courant

L objectif actif replace BGIG sur sa trajectoire premium. P19 a P21 fournissent le moteur de planification, P23 a P27 le Studio local, P28 un raccord CAD IR technique. Le raccord P28 est requalifie `KO produit/UX` : il ne doit plus etre presente comme une generation d insert utilisable.

P30 materialise ADR-0042 : le Studio est la surface principale avec une boite visuelle vivante, un parcours en cinq etapes et un mode expert progressif. La palette Fusion reste une surface secondaire prevue par P32. Le plan complet est `docs/PREMIUM_PRODUCT_EXECUTION_PLAN.md`.

## Gate humaine active

`P31-GATE - Strategie de bacs fonctionnels` est la prochaine gate reelle. P31 doit choisir puis documenter la projection des modules selectionnes vers de vrais bacs (parois, fond, logements et prise), avant toute nouvelle materialisation Fusion.

## Hors scope maintenu

- Fusion ne devient jamais source de verite du plan.
- P28 reste une preuve de raccord technique, pas une geometrie de bac fini.
- Aucun couvercle, clip, charniere ou mecanisme ne sera declare fonctionnel avant gate et impression reelle.
- Aucun statut `print-validated` ne sera utilise sans prototype mesure.

## Prochaine action

Preparer le rapport `P31-GATE` : options de projection vers des bacs fonctionnels, invariants de parois/fond/logements, tests moteur/CAD IR et perimetre de la premiere preuve Fusion. Aucun code P31 ne commencera avant cette validation humaine.

## Fin de chaque mission

Appliquer direct-to-main pour tout lot non gate : tests pertinents, `git diff --check`, commit atomique, integration et push de `main`.