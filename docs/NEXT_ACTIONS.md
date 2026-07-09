# Next Actions

Derniere mise a jour : 2026-07-09

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

`P13-ASSET-M004V - Valider les compartiments asset-specific dans Fusion`.

Statut : gate humaine Fusion active. `P13-ASSET-M004` est implemente et prepare un module count-aware avec plusieurs cavites rectangulaires top-open, une par asset source supporte, via `asset_cavity_policy: per_source_asset_rectangular_compartments_v0`.

Action attendue : rejouer le smoke test Fusion prepare par `scripts/fusion/prepare_quick_asset_test.ps1`, verifier deux compartiments visibles, mur interne, regenerate sans doublon, clear preservant les objets non-BGIG, puis confirmer ou refuser `P13-ASSET-M004V`.

## Mission ready non gated

Aucune mission produit non-gated supplementaire n'est recommandee avant validation humaine `P13-ASSET-M004V`.

## Regle operationnelle Fusion

Pour toute future gate Fusion, Codex prepare automatiquement le smoke test avec
`scripts/fusion/`, installe l'add-in si les permissions AppData le permettent,
genere les CAD IR temporaires necessaires et fournit uniquement les actions
Fusion restantes a Thomas.

## Mission bloquee par gate

`P8-FUSION-GATE - Generation Fusion volumetrique ou vue 3D`.

`P10-SOLVER-GATE - Solveur complexe, backtracking ou optimisation globale`.

Palette persistante HTML, UI assets avancee/tableau, solveur plus automatique, cavites par pile/logements detailles, assets individuels Fusion, nouvelle geometrie produit complexe, export imprimable et validation d'impression restent gates ou missions separees. P13-ASSET-M004 implemente seulement des compartiments rectangulaires par asset source, sans assets individuels, sans cavites par pile/item, sans capacite physique garantie ni impression 3D.

## Fin de chaque mission

Appliquer la politique active `direct-to-main` : tests complets, commit propre,
integration directe dans `main`, push vers `origin/main`, puis reprise depuis
`origin/main` si aucune vraie gate humaine n'est atteinte.
