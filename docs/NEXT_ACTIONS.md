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

`P13-ASSET-M003-GATE - Autoriser la prochaine etape asset-first apres enveloppe count-aware`.

Statut : gate produit active. `P13-ASSET-M002V` est validee humainement comme premier sizing count-aware V0 pour assets simples, avec debug visuel d'enveloppe et limitations explicites. La prochaine decision produit doit choisir si BGIG avance vers des cavites/logements asset-first reels, une visualisation d'items/proxies plus detaillee, ou une amelioration UI assets, sans introduire de solveur global premature.

Decision attendue : autoriser une mission bornee post-M002, ou confirmer que les cavites/logements, assets individuels, UI assets avancee, solveur global et impression restent reportes.

## Mission ready non gated

Aucune mission produit non-gated supplementaire n'est recommandee avant decision humaine sur `P13-ASSET-M003-GATE`.

## Regle operationnelle Fusion

Pour toute future gate Fusion, Codex prepare automatiquement le smoke test avec
`scripts/fusion/`, installe l'add-in si les permissions AppData le permettent,
genere les CAD IR temporaires necessaires et fournit uniquement les actions
Fusion restantes a Thomas.

## Mission bloquee par gate

`P8-FUSION-GATE - Generation Fusion volumetrique ou vue 3D`.

`P10-SOLVER-GATE - Solveur complexe, backtracking ou optimisation globale`.

Palette persistante HTML, UI assets avancee/tableau, solveur plus automatique, cavites/logements assets, assets individuels Fusion, nouvelle geometrie produit complexe, export imprimable et validation d'impression restent gates ou missions separees. P13-ASSET-M002 ne valide qu'une enveloppe count-aware heuristique et un sketch debug non imprimable.

## Fin de chaque mission

Appliquer la politique active `direct-to-main` : tests complets, commit propre,
integration directe dans `main`, push vers `origin/main`, puis reprise depuis
`origin/main` si aucune vraie gate humaine n'est atteinte.
