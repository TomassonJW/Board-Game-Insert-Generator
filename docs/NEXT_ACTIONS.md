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

`P13-ASSET-M005-GATE - Decider la prochaine etape apres compartiments asset-specific V0`.

Statut : gate produit active. `P13-ASSET-M004V` est validee humainement comme premiere generation de compartiments asset-specific V0 : module exterieur count-aware + deux cavites rectangulaires top-open separees par asset source, regenerate/clear valides, registry OK, `print-validated: false`.

Decision attendue : choisir explicitement la prochaine mission bornee. Options candidates : dette UI/UX `quick_asset_box` (formats, unites, sections, presets, aide), visualisation/proxies d'assets, cavites par pile/item, sizing capacitaire plus garanti, traitement cartes/decks, solveur/optimisation, fillets/conges, export imprimable ou protocole d'impression.

## Mission ready non gated

Aucune mission produit non-gated supplementaire n'est recommandee avant decision humaine sur `P13-ASSET-M005-GATE`.

## Regle operationnelle Fusion

Pour toute future gate Fusion, Codex prepare automatiquement le smoke test avec
`scripts/fusion/`, installe l'add-in si les permissions AppData le permettent,
genere les CAD IR temporaires necessaires et fournit uniquement les actions
Fusion restantes a Thomas.

## Mission bloquee par gate

`P8-FUSION-GATE - Generation Fusion volumetrique ou vue 3D`.

`P10-SOLVER-GATE - Solveur complexe, backtracking ou optimisation globale`.

Palette persistante HTML, UI assets avancee/tableau, solveur plus automatique, cavites par pile/logements detailles, assets individuels Fusion, nouvelle geometrie produit complexe, export imprimable et validation d'impression restent gates ou missions separees. P13-ASSET-M004V valide seulement des compartiments rectangulaires par asset source, sans assets individuels, sans cavites par pile/item, sans capacite physique garantie ni impression 3D. La dette UX `quick_asset_box` est documentee et gatee pour une mission separee.

## Fin de chaque mission

Appliquer la politique active `direct-to-main` : tests complets, commit propre,
integration directe dans `main`, push vers `origin/main`, puis reprise depuis
`origin/main` si aucune vraie gate humaine n'est atteinte.
