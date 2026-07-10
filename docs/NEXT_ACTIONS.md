# Next Actions

Derniere mise a jour : 2026-07-11

## Politique active - Integration Git autonome

Statut : `active` pour les missions non gatees. Les missions Fusion et physiques restent soumises aux gates documentees.

## Etat courant

P19 a P21 fournissent les contrats et propositions moteur. P22 a P27 fournissent le Studio local. P28 relie maintenant une selection P21 explicite a la CAD IR standard attendue par Fusion, sous la forme prudente d enveloppes rectangulaires. Le moteur Python reste la source de verite.

## Gate humaine active

La decision de scope P28 est approuvee. La seule gate active est l observation reelle dans Fusion :

- le pont produit exactement les trois volumes selectionnes du starter de smoke ;
- Codex prepare l add-in et les settings locaux ;
- Thomas execute `Run` dans Fusion et confirme ou infirme la scene ;
- aucun statut `fusion-validated` ou `print-validated` n est permis avant ce retour humain.

Le protocole et les mesures attendues sont dans `docs/P28_FUSION_SELECTION_SMOKE.md`.

## Hors scope maintenu

- Aucun solveur global, backtracking, optimisation opaque ou IA non evaluee.
- Fusion ne devient jamais source de verite du plan.
- Les volumes P28 ne sont pas des bacs finis : pas de cavites, parois, encoches ou tolerances nouvelles.
- Aucune validation d impression, de slicer ou d ergonomie reelle n est revendiquee.

## Prochaine action

Terminer `P28-GATE` par le smoke humain Fusion prepare par `scripts/fusion/prepare_local_composer_selection_test.ps1`. Apres un resultat `OK` documente, choisir une seule prochaine mission `ready` qui etend la geometrie sans franchir la gate impression.

## Fin de chaque mission

Appliquer direct-to-main pour tout lot non gate : tests pertinents, `git diff --check`, commit atomique, integration et push de `main`. Pour P28, arreter avant toute declaration `fusion-validated` jusqu au retour humain.