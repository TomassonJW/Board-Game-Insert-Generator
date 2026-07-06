# Next Actions

Derniere mise a jour : 2026-07-06

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

Statut : `required_before_next_fusion_geometry`.

P7-M001V4 est validee humainement dans Fusion : document Assembly-compatible,
mode `compact_and_exploded`, composants sources partages par occurrences
compactes/eclatees, message `Linked exploded occurrences: yes` et aucun
renommage direct d'occurrence. P7-M001 est donc `fusion-validated`, avec
`print-validated: false`.

P11-M002 est codee : l'exemple `simple_multilayer_grid_scene` produit une scene
Fusion compacte + eclatee depuis `metadata.executable_asset_plan`, avec un module
bas, un module plus haut sur deux unites Z et un placement explicite a `Z=1`.
L'add-in affiche les compteurs multi-layer et conserve la strategie `Component`
source + occurrences compactes/eclatees liees.

Action humaine requise : smoke test Fusion `P11-M002V` avant toute nouvelle
mission qui genere reellement de la grille 3D, des layers, des modules composites,
une vue eclatee avancee, de la geometrie courbe, des exports STL/3MF ou une
preparation d'impression. L'impression 3D reste non validee.

## Mission ready non gated

Aucune mission non-gated supplementaire n'est recommandee apres `P11-M002` tant
que le smoke test Fusion P11-M002V de la scene multi-layer compacte/eclatee n'est
pas valide. La boucle asset-first produit maintenant candidats, variante
recommandee, plan de modules concret, placement grille greedy borne, generation
Fusion compacte validee, vue eclatee basique validee et scene multi-layer codee.

Prochaine action recommandee : executer le smoke test humain P11-M002V, puis
preparer une gate si l'on veut passer a un solveur complexe, a du backtracking,
a une optimisation globale, a des modules composites ou a une generation Fusion
volumetrique plus avancee.

## Mission bloquee par gate

`P8-FUSION-GATE - Generation Fusion volumetrique ou vue 3D`.

`P10-SOLVER-GATE - Solveur complexe, backtracking ou optimisation globale`.

`P11-M002V - Smoke test humain Fusion de la scene multi-layer compacte/eclatee depuis simple_multilayer_grid_scene`.

`P11-NEXT-GATE - Choisir le prochain elargissement produit apres scene compacte/eclatee multi-layer`.

- Capability : `C-FUSION-EXPLODED`, `C-COMPOSITE`, `C-SOLVER`, `C-GRID-3D`,
  `C-CALIBRATION` selon l'option choisie.
- Objectif : choisir explicitement la prochaine vague : vue eclatee, solveur plus
  automatique, modules composites, generation volumetrique plus avancee ou
  impression/calibration.
- Statut : `blocked` jusqu'a validation humaine.

## Fin de chaque mission

Appliquer la politique active `direct-to-main` : tests complets, commit propre,
integration directe dans `main`, push vers `origin/main`, puis reprise depuis
`origin/main` si aucune vraie gate humaine n'est atteinte.