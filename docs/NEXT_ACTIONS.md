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

`P13-ASSET-M003V - Valider dans Fusion la cavite asset-fit globale V0`.

Statut : gate Fusion active. `P13-ASSET-M003` est implementee et doit etre validee humainement dans Fusion avant toute mission produit suivante.

Validation attendue : ouvrir Fusion avec un document Assembly-compatible, lancer BGIG en `quick_asset_box`, generer le cas count-aware prepare, verifier le module exterieur `50.0 x 39.0 x 48.0`, la cavite rectangulaire reelle `47.6 x 36.6 x 46.8 mm`, `asset_cavities_generated: yes`, `asset_cavity_policy: single_asset_fit_rectangular_cavity_v0`, fond/murs attendus, regenerate sans doublon, clear preservant les objets non-BGIG et `Print validation: false`.

## Mission ready non gated

Aucune mission produit non-gated supplementaire n'est recommandee avant validation humaine `P13-ASSET-M003V`.

## Regle operationnelle Fusion

Pour toute future gate Fusion, Codex prepare automatiquement le smoke test avec
`scripts/fusion/`, installe l'add-in si les permissions AppData le permettent,
genere les CAD IR temporaires necessaires et fournit uniquement les actions
Fusion restantes a Thomas.

## Mission bloquee par gate

`P8-FUSION-GATE - Generation Fusion volumetrique ou vue 3D`.

`P10-SOLVER-GATE - Solveur complexe, backtracking ou optimisation globale`.

Palette persistante HTML, UI assets avancee/tableau, solveur plus automatique, cavites par pile/logements detailles, assets individuels Fusion, nouvelle geometrie produit complexe, export imprimable et validation d'impression restent gates ou missions separees. P13-ASSET-M003 ne valide qu'une cavite rectangulaire globale asset-fit V0, en attente de validation Fusion.

## Fin de chaque mission

Appliquer la politique active `direct-to-main` : tests complets, commit propre,
integration directe dans `main`, push vers `origin/main`, puis reprise depuis
`origin/main` si aucune vraie gate humaine n'est atteinte.
