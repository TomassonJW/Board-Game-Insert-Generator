# Next Actions

Derniere mise a jour : 2026-07-07

Ce fichier indique les prochaines missions recommandees. Il doit rester court,
priorise et directement actionnable. Si aucune mission explicite n'est donnee,
Codex doit choisir la premiere mission `ready` listee ici, sauf gate humaine.

## Politique active - Integration Git autonome

Statut : `active`.

Le chemin standard est `direct-to-main` : une mission doit etre testee, commitee,
integree directement dans `main`, puis poussee vers `origin/main` avant selection
d'une mission suivante. Les pull requests sont reservees aux cas de repli :
protection GitHub, review imposee, conflit, divergence non triviale, risque
structurant, authentification absente ou refus de push direct.

## Gate humaine active

Statut : `required_before_next_product_expansion`.

La validation humaine `P12-M001V` est confirmee apres le commit `a12ef42` : commande visible, bouton toolbar visible dans `Design workspace > Utilities > Add-Ins`, reouverture sans redemarrer l'add-in, generation `simple_asset_product_scene` via UI, `Body sizing report`, occurrences liees et `UI reopen policy` presents. `print-validated: false` reste explicite.

Action humaine requise : `P12-NEXT-GATE` avant toute extension vers palette persistante HTML, generation depuis config BGIG, nettoyage automatique de scene, parametres avances ou regeneration plus ambitieuse.

## Mission ready non gated

Aucune mission non-gated supplementaire n'est recommandee apres la validation `P12-M001V`. La prochaine action est une gate produit : choisir explicitement le prochain increment UI avant d'elargir le perimetre.

## Mission bloquee par gate

`P8-FUSION-GATE - Generation Fusion volumetrique ou vue 3D`.

`P10-SOLVER-GATE - Solveur complexe, backtracking ou optimisation globale`.

`P12-NEXT-GATE - Choisir la prochaine extension UI Fusion`.

- Capability : `C-FUSION-UI`, `C-FUSION-EXPLODED`, `C-COMPOSITE`, `C-SOLVER`,
  `C-GRID-3D`, `C-CALIBRATION` selon l'option choisie.
- Objectif : choisir explicitement la prochaine vague : UI produit plus complete,
  solveur plus automatique, modules composites, generation volumetrique plus
  avancee, export ou impression/calibration.
- Statut : `blocked` jusqu'a validation humaine.

## Fin de chaque mission

Appliquer la politique active `direct-to-main` : tests complets, commit propre,
integration directe dans `main`, push vers `origin/main`, puis reprise depuis
`origin/main` si aucune vraie gate humaine n'est atteinte.
