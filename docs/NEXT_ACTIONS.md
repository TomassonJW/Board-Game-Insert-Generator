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

Statut : aucune mission produit non-gated active. `P12-M004V` est validee humainement dans Fusion apres `ab488dc`.

La gate humaine P12-M004 a ete validee et le smoke test P12-M004V confirme la persistance des champs UI, la rehydratation, `generate`, `regenerate`, `clear_bgig_scene` et la preservation non-BGIG. Impression 3D non validee.

## Mission ready non gated

Aucune mission produit non-gated supplementaire n'est recommandee dans ce run. Prochaine action : gate produit explicite avant palette persistante, UI assets complete, solveur plus automatique, nouvelle geometrie Fusion, export imprimable ou validation d'impression.

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
