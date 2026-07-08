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

`P13-ASSET-M002 - Autoriser le sizing count-aware et le debug visuel asset`.

Statut : gate produit active. `P13-M001V` est validee humainement comme V0 honnete, mais les limites confirmees ouvrent une decision produit avant implementation : traiter ou non le `count` comme capacite de stockage reelle, definir jusqu'ou visualiser les assets, et cadrer les cavites/logements sans ajouter de solveur complexe premature.

Decision attendue : autoriser une mission bornee de sizing count-aware/reporting capacite, ou reporter cette capacite et rester sur le proxy asset-first V0.

## Mission ready non gated

Aucune mission produit non-gated supplementaire n'est recommandee avant decision humaine sur `P13-ASSET-M002`.

## Regle operationnelle Fusion

Pour toute future gate Fusion, Codex prepare automatiquement le smoke test avec
`scripts/fusion/`, installe l'add-in si les permissions AppData le permettent,
genere les CAD IR temporaires necessaires et fournit uniquement les actions
Fusion restantes a Thomas.

## Mission bloquee par gate

`P8-FUSION-GATE - Generation Fusion volumetrique ou vue 3D`.

`P10-SOLVER-GATE - Solveur complexe, backtracking ou optimisation globale`.

Palette persistante HTML, UI assets avancee/tableau, sizing count-aware reel, solveur plus automatique, cavites/logements assets, nouvelle geometrie Fusion produit, export imprimable et validation d'impression restent gates ou missions separees. P13-M001V ne valide pas ces capacites.

## Fin de chaque mission

Appliquer la politique active `direct-to-main` : tests complets, commit propre,
integration directe dans `main`, push vers `origin/main`, puis reprise depuis
`origin/main` si aucune vraie gate humaine n'est atteinte.
