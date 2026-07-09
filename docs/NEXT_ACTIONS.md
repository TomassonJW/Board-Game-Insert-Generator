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

Gate humaine active : `P15-TRAY-SEMANTICS-ALIGNMENT-SPRINT-V` apres preparation du preset `p15_tray_semantics`. Aucune nouvelle mission produit ne doit demarrer avant validation Fusion humaine.

## Sprint actif

`P14-USABLE-ASSET-TRAY-SPRINT` est lance explicitement le 2026-07-09 apres preflight post-crash OK.

Mission interne terminee : `P14-USABLE-ASSET-TRAY-M001 - Robustifier le layout multi-assets`, `implemented-core`, tests automatises OK, validation Fusion sprint P14 requise, `print-validated: false`.

Mission interne terminee : `P14-USABLE-ASSET-TRAY-M002 - Printability safety report V0`, `implemented-core`, tests automatises OK, validation Fusion sprint P14 requise, `print-validated: false`.

Mission interne terminee : `P14-USABLE-ASSET-TRAY-M003 - UX quick_asset_box V0 plus lisible`, `implemented-fusion-ui`, tests automatises OK, validation Fusion sprint P14 requise, `print-validated: false`.

Mission interne terminee : `P14-USABLE-ASSET-TRAY-M004 - Presets et scenarios quick asset`, `implemented-smoke-prep`, tests automatises OK, validation Fusion sprint P14 requise, `print-validated: false`.

Mission interne corrigee : `P14-USABLE-ASSET-TRAY-M005 - Preparation gate Fusion sprint P14`, add-in a reinstaller localement avec settings `quick_asset_box` preset `p14_complete`, marqueurs installes a verifier, validation Fusion humaine requise.

## Mission ready non gated

Aucune mission non gated. Prochaine action : validation humaine Fusion `P15-TRAY-SEMANTICS-ALIGNMENT-SPRINT-V`.

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
Mission interne terminee : `P15-M003 - max_stack_height_mm et reporting stack policy`, champ UI global optionnel persiste pour `quick_asset_box`, config temporaire applique `max_stack_height_mm`, resume Fusion expose `storage_orientation`, `stack_height_policy`, `max_stack_height_mm`, `stack_height_used_mm`, `xy_expansion_used` et `z_expansion_used`.
Mission interne terminee : `P15-M004 - Grid semantics report V0`, placements et rapports exposent `grid_semantics: placement_reservation_lattice_v0`, `body_snap_to_grid: no`, `grid_span_is_reserved_space: yes` et `body_size_may_be_smaller_than_grid_span: yes`.
Mission interne terminee : `P15-M005 - Preset smoke P15 realiste`, preset `p15_tray_semantics` par defaut, box `220 x 160 x 60`, grid `8 x 5 x 3`, 5 assets, `max_stack_height_mm = 18`, add-in/settings a preparer pour validation Fusion.
