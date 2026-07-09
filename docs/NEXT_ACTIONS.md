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

Aucune gate humaine active pendant les missions automatisables du sprint `P15-TRAY-SEMANTICS-ALIGNMENT-SPRINT` explicitement autorise. Validation Fusion attendue apres preparation P15.

## Sprint actif

`P14-USABLE-ASSET-TRAY-SPRINT` est lance explicitement le 2026-07-09 apres preflight post-crash OK.

Mission interne terminee : `P14-USABLE-ASSET-TRAY-M001 - Robustifier le layout multi-assets`, `implemented-core`, tests automatises OK, validation Fusion sprint P14 requise, `print-validated: false`.

Mission interne terminee : `P14-USABLE-ASSET-TRAY-M002 - Printability safety report V0`, `implemented-core`, tests automatises OK, validation Fusion sprint P14 requise, `print-validated: false`.

Mission interne terminee : `P14-USABLE-ASSET-TRAY-M003 - UX quick_asset_box V0 plus lisible`, `implemented-fusion-ui`, tests automatises OK, validation Fusion sprint P14 requise, `print-validated: false`.

Mission interne terminee : `P14-USABLE-ASSET-TRAY-M004 - Presets et scenarios quick asset`, `implemented-smoke-prep`, tests automatises OK, validation Fusion sprint P14 requise, `print-validated: false`.

Mission interne corrigee : `P14-USABLE-ASSET-TRAY-M005 - Preparation gate Fusion sprint P14`, add-in a reinstaller localement avec settings `quick_asset_box` preset `p14_complete`, marqueurs installes a verifier, validation Fusion humaine requise.

## Mission ready non gated

Mission interne suivante : `P15-M003 - max_stack_height_mm et reporting stack policy`.

## Regle operationnelle Fusion

Pour toute future gate Fusion, Codex prepare automatiquement le smoke test avec
`scripts/fusion/`, installe l'add-in si les permissions AppData le permettent,
genere les CAD IR temporaires necessaires et fournit uniquement les actions
Fusion restantes a Thomas.

## Mission bloquee par gate

`P8-FUSION-GATE - Generation Fusion volumetrique ou vue 3D`.

`P10-SOLVER-GATE - Solveur complexe, backtracking ou optimisation globale`.

Palette persistante HTML, UI assets avancee/tableau, solveur plus automatique, cavites par pile/logements detailles, assets individuels Fusion, nouvelle geometrie produit complexe, export imprimable et validation d'impression restent gates ou missions separees. P13-ASSET-M005V valide seulement des encoches rectangulaires top-open V0 par compartiment supporte, sans courbes, fillets, garanties physiques ni impression 3D. La dette UX `quick_asset_box` est documentee et gatee pour une mission separee.

## Fin de chaque mission

Appliquer la politique active `direct-to-main` : tests complets, commit propre,
integration directe dans `main`, push vers `origin/main`, puis reprise depuis
`origin/main` si aucune vraie gate humaine n'est atteinte.
Mission interne terminee : `P15-M001 - Audit semantique z/grid/grouping`, ADR-0033 acceptee, pas de changement moteur.
Mission interne terminee : `P15-M002 - storage_orientation flat_tray V0`, moteur core implemente, `auto` -> `flat_tray` pour tokens/dice/meeples/generic, `vertical_stack` explicite conserve, champs JSON additifs `storage_orientation` et `max_stack_height_mm`, tests assets OK.
