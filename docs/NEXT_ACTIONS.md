# Next Actions

Derniere mise a jour : 2026-07-11

## Politique active - Integration Git autonome

Statut : `active` pour les missions non gatees. Les missions Fusion et physiques restent soumises aux gates documentees.

## Etat courant

P30 est integre : le Studio est la surface principale, avec une boite visuelle vivante, cinq etapes progressives et un mode expert explicite. P28 reste une preuve de raccord technique seulement ; ses blocs ne sont pas des bacs.

ADR-0042 fixe Studio principal / palette Fusion secondaire. ADR-0043 est maintenant proposee pour le premier passage vers des bacs ouverts fonctionnels depuis une selection P21.

## Gate humaine active

`P31-GATE - Strategie de bacs fonctionnels` est preparee dans `docs/P31_FUNCTIONAL_TRAY_GATE.md`. Elle recommande un bac ouvert par module P21 : parois et fond issus des defaults existants, cavite unique top-open, refus structure si une cavite positive ne tient pas.

## Hors scope maintenu

- Fusion ne devient jamais source de verite du plan.
- Aucun score, placement ou tolerance existante ne change en P31.
- Aucun compartiment multi-assets, encoche, arrondi, couvercle, clip ou charniere ne sera ajoute dans ce premier pas.
- Aucun statut `fusion-validated` ou `print-validated` ne sera utilise sans preuve correspondante.

## Prochaine action

Attendre `P31 approuve`. Ensuite seulement, implementer `open_top_tray_from_selected_module.v0`, ses tests moteur/CAD IR et la preparation du smoke Fusion de cavites.

## Fin de chaque mission

Appliquer direct-to-main pour tout lot non gate : tests pertinents, `git diff --check`, commit atomique, integration et push de `main`.