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

Statut : `manual_validation_required` pour `P12-M004V` ; P12-M004 est code et doit etre valide dans Fusion.

La gate humaine P12-M004 a ete validee pour ameliorer la persistance des champs UI et le workflow de regeneration, sans palette persistante, sans nouvelle geometrie, sans solveur et sans export imprimable.

## Mission ready non gated

Aucune mission produit non-gated supplementaire n'est recommandee avant validation Fusion P12-M004V. La preparation locale doit passer par `scripts/fusion/prepare_quick_parametric_test.ps1`. Action humaine restante : ouvrir Fusion, verifier le bloc UI `UI settings loaded: yes`, `Loaded input mode: quick_parametric_box`, les valeurs quick box chargees, puis smoke test de rehydratation, modification d une valeur, `regenerate`, reouverture et `clear_bgig_scene` avec preservation non-BGIG.

## Regle operationnelle Fusion

Pour toute future gate Fusion, Codex prepare automatiquement le smoke test avec
`scripts/fusion/`, installe l'add-in si les permissions AppData le permettent,
genere les CAD IR temporaires necessaires et fournit uniquement les actions
Fusion restantes a Thomas.
## Mission bloquee par gate


`P8-FUSION-GATE - Generation Fusion volumetrique ou vue 3D`.

`P10-SOLVER-GATE - Solveur complexe, backtracking ou optimisation globale`.

## Fin de chaque mission

Appliquer la politique active `direct-to-main` : tests complets, commit propre,
integration directe dans `main`, push vers `origin/main`, puis reprise depuis
`origin/main` si aucune vraie gate humaine n'est atteinte.
