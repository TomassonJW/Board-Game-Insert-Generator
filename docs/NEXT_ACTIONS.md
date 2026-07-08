# Next Actions

Derniere mise a jour : 2026-07-08

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

Statut : aucune gate de validation P12-M003V active.

La validation humaine `P12-M003V` du 2026-07-08 confirme le mode Fusion `quick_parametric_box` en `compact_only` : CAD IR temporaire creee, registry OK, une occurrence compacte visible, bbox Fusion conforme au body imprimable planifie et `Print validation: false`.

## Mission ready non gated

Aucune mission produit non-gated supplementaire n'est recommandee apres P12-M003V. Stopper sur gate produit avant palette persistante, UI assets complete, solveur plus automatique, nouvelle geometrie Fusion, export imprimable ou validation d'impression.

## Mission bloquee par gate


`P8-FUSION-GATE - Generation Fusion volumetrique ou vue 3D`.

`P10-SOLVER-GATE - Solveur complexe, backtracking ou optimisation globale`.

## Fin de chaque mission

Appliquer la politique active `direct-to-main` : tests complets, commit propre,
integration directe dans `main`, push vers `origin/main`, puis reprise depuis
`origin/main` si aucune vraie gate humaine n'est atteinte.
