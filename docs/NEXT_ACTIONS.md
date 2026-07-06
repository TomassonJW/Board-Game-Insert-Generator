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

P11-M002V est validee humainement dans Fusion pour la scene multi-layer : add-in
lance, CAD IR chargee, message conforme, vue compacte/eclatee generee et modules
multi-layer visibles. `print-validated: false` reste explicite.

P11-M003 est maintenant codee : le plan asset-first distingue span grille,
asset-fit et taille imprimable, et l'add-in expose une commande UI minimale pour
choisir le fichier CAD IR et le mode `compact_only` / `compact_and_exploded`.
Cette mission change volontairement les dimensions de bodies asset-first attendues
par rapport aux anciens smoke tests :

- `simple_asset_executable_plan` : body asset-first attendu `25.6 x 25.6 x 9.8 mm`, span grille `30 x 30 x 10 mm` ;
- `simple_multilayer_grid_scene` : body bas attendu `61.6 x 61.6 x 7.8 mm`, span grille `90 x 90 x 10 mm` ;
- `simple_multilayer_grid_scene` : body haut attendu `37.6 x 37.6 x 17.8 mm`, span grille `60 x 60 x 20 mm`.

Action humaine requise : smoke test Fusion `P11-M003V` avant toute nouvelle
mission produit qui elargit l'UI, le solveur, les modules composites, la vue
volumetrique, la geometrie courbe, les exports STL/3MF ou la preparation
d'impression. L'impression 3D reste non validee.

## Mission ready non gated

Aucune mission non-gated supplementaire n'est recommandee apres `P11-M003` tant
que le smoke test Fusion P11-M003V de la commande UI et du sizing asset-first
n'est pas valide. La boucle asset-first produit maintenant candidats, variante
recommandee, plan de modules concret, placement grille greedy borne, generation
Fusion compacte/eclatee liee, scene multi-layer et premiere commande utilisateur
Fusion minimale.

## Mission bloquee par gate

`P11-M003V - Smoke test humain Fusion de la commande UI et du sizing asset-first`.

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
