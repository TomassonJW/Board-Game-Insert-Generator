# Next Actions

Derniere mise a jour : 2026-07-11

## Politique active - Integration Git autonome

Statut : `active` pour les missions non gatees. Les missions Fusion et physiques restent soumises aux gates documentees.

## Etat courant

P31 remplace les blocks P28 par de vrais bacs ouverts dans la CAD IR : une enveloppe P21, quatre parois, un fond conserve et une cavite unique ouverte en haut. Le Studio les decrit comme `a verifier dans Fusion`, jamais comme imprimes ou valides.

## Gate humaine active

`P31-FUSION-SMOKE - Premiere cavite issue d une selection P21` est maintenant la seule gate active. Le protocole est `docs/P31_FUSION_OPEN_TRAY_SMOKE.md`. Codex prepare l add-in et la scene apres integration ; Thomas devra seulement ouvrir Fusion, lancer BGIG et constater les trois bacs.

## Hors scope maintenu

- Fusion ne devient jamais source de verite du plan.
- Aucun score, placement ou tolerance existante ne change.
- Aucun compartiment multi-assets, encoche, arrondi, couvercle, clip ou charniere n est ajoute.
- Aucun statut `print-validated` ne sera utilise sans prototype mesure.

## Prochaine action

Apres retour `P31 Fusion OK` ou `P31 Fusion KO`, qualifier le comportement Fusion. En cas de OK, la suite autonome est P32 : palette Fusion secondaire claire et concise.

## Fin de chaque mission

Appliquer direct-to-main pour tout lot non gate : tests pertinents, `git diff --check`, commit atomique, integration et push de `main`.