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

`P13-M001V - Valider quick_asset_box dans Fusion`.

Statut : action humaine requise dans Fusion 360. Codex a implemente `quick_asset_box` et prepare le script `scripts/fusion/prepare_quick_asset_test.ps1`. La mission ne doit pas etre declaree `fusion-validated` avant smoke test humain.

Smoke attendu : ouvrir un document Assembly-compatible, ouvrir BGIG, confirmer `Input mode = quick_asset_box`, verifier les valeurs rehydratees et le champ assets, lancer `generate`, verifier assets lus, candidats, module(s) places, `Body sizing report`, registry OK et `Print validation: false`, rouvrir BGIG, modifier un asset ou une dimension, lancer `regenerate`, verifier absence de doublon, puis `clear_bgig_scene` en preservant les objets non-BGIG.

## Mission ready non gated

Aucune mission produit non-gated supplementaire n'est recommandee avant validation humaine `P13-M001V`.

## Regle operationnelle Fusion

Pour toute future gate Fusion, Codex prepare automatiquement le smoke test avec
`scripts/fusion/`, installe l'add-in si les permissions AppData le permettent,
genere les CAD IR temporaires necessaires et fournit uniquement les actions
Fusion restantes a Thomas.

## Mission bloquee par gate

`P8-FUSION-GATE - Generation Fusion volumetrique ou vue 3D`.

`P10-SOLVER-GATE - Solveur complexe, backtracking ou optimisation globale`.

Palette persistante HTML, UI assets avancee/tableau, solveur plus automatique, nouvelle geometrie Fusion, export imprimable et validation d'impression restent gates.

## Fin de chaque mission

Appliquer la politique active `direct-to-main` : tests complets, commit propre,
integration directe dans `main`, push vers `origin/main`, puis reprise depuis
`origin/main` si aucune vraie gate humaine n'est atteinte.
