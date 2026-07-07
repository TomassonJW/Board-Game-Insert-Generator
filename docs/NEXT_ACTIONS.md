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

P11-M003V4 est validee humainement dans Fusion apres le commit `134863c` : add-in recopie, commande UI `Generate Board Game Insert`, chargement de `simple_asset_product_scene`, mode `compact_and_exploded`, generation OK, zero blank legacy, un module asset-first, occurrences compactes/eclatees liees, `Module source mapping`, `Body sizing report`, bbox Fusion comparable et `size match yes`. `print-validated: false` reste explicite.

Action humaine requise : `P11-NEXT-GATE` avant toute nouvelle mission produit qui elargit l'UI, le solveur, les modules composites, la vue volumetrique, la geometrie courbe, les exports STL/3MF ou la preparation d'impression/calibration.

## Mission ready non gated

Aucune mission non-gated supplementaire n'est recommandee apres la validation `P11-M003V4`. La boucle asset-first produit maintenant candidats, variante recommandee, plan de modules concret, placement grille greedy borne, generation Fusion compacte/eclatee liee, scene multi-layer, commande utilisateur minimale et smoke test produit non ambigu valide dans Fusion.

La prochaine action est une gate produit : choisir explicitement la prochaine vague avant d'elargir le perimetre.

## Mission bloquee par gate

`P8-FUSION-GATE - Generation Fusion volumetrique ou vue 3D`.

`P10-SOLVER-GATE - Solveur complexe, backtracking ou optimisation globale`.

`P11-NEXT-GATE - Choisir le prochain elargissement produit apres UI Fusion minimale et sizing corrige`.

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
