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

`P13-ASSET-M005V - Valider les encoches d'acces par compartiment dans Fusion`.

Statut : gate Fusion active. `P13-ASSET-M005` est implemente hors Fusion et le smoke test local doit etre prepare par Codex. La validation humaine doit confirmer que le flux `quick_asset_box` genere le module count-aware, les compartiments asset-specific et les encoches rectangulaires top-open reelles par compartiment supporte, sans doublon apres `regenerate`, avec `clear_bgig_scene` preservant les objets non-BGIG et `Print validation: false`.

## Mission ready non gated

Aucune mission produit non-gated supplementaire n'est recommandee avant validation humaine `P13-ASSET-M005V` ou nouvelle decision explicite.

## Regle operationnelle Fusion

Pour toute future gate Fusion, Codex prepare automatiquement le smoke test avec
`scripts/fusion/`, installe l'add-in si les permissions AppData le permettent,
genere les CAD IR temporaires necessaires et fournit uniquement les actions
Fusion restantes a Thomas.

## Mission bloquee par gate

`P8-FUSION-GATE - Generation Fusion volumetrique ou vue 3D`.

`P10-SOLVER-GATE - Solveur complexe, backtracking ou optimisation globale`.

Palette persistante HTML, UI assets avancee/tableau, solveur plus automatique, cavites par pile/logements detailles, assets individuels Fusion, nouvelle geometrie produit complexe, export imprimable et validation d'impression restent gates ou missions separees. P13-ASSET-M005 implemente seulement des encoches rectangulaires top-open V0 par compartiment supporte, sans courbes, fillets, garanties physiques ni impression 3D.

## Fin de chaque mission

Appliquer la politique active `direct-to-main` : tests complets, commit propre,
integration directe dans `main`, push vers `origin/main`, puis reprise depuis
`origin/main` si aucune vraie gate humaine n'est atteinte.
