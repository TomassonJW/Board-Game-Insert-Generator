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

Aucune gate humaine active apres validation Fusion `P15-TRAY-SEMANTICS-ALIGNMENT-SPRINT-V` confirmee le 2026-07-09 sur `648eba9`.

## Sprint actif

`P16-ERGONOMIC-2D-TRAY-PACKING-SPRINT` est lance explicitement le 2026-07-09 apres validation P15.

Mission interne ready : `P16-M001 - Documenter la strategie flat_tray_2d`, ADR et docs. Objectif : definir `flat_tray_linear_v0`, `flat_tray_2d_v0`, `vertical_stack`, `pile_count`, `items_per_pile`, `pile_grid_columns`, `pile_grid_rows`, `target_aspect_ratio`, `max_module_length_mm`, `max_stack_height_mm` et la grille comme `placement_reservation_lattice_v0`.

Mission interne suivante : `P16-M002 - Implementer packing 2D V0 des piles`, heuristique deterministe pour tokens/dice/meeples/generic sans solveur global.

Mission interne suivante : `P16-M003 - Aligner compartiments, cavites et notches sur le packing 2D`.

Mission interne suivante : `P16-M004 - Clarifier UI et reporting P16`.

Mission interne suivante : `P16-M005 - Preset P16 realiste`.

Mission interne suivante : `P16-M006 - Preparation gate Fusion P16`.

## Mission ready non gated

`P16-M001 - Documenter la strategie flat_tray_2d`.

## Regle operationnelle Fusion

Pour toute future gate Fusion, Codex prepare automatiquement le smoke test avec
`scripts/fusion/`, installe l'add-in si les permissions AppData le permettent,
genere les CAD IR temporaires necessaires et fournit uniquement les actions
Fusion restantes a Thomas.

## Missions bloquees par gate

`P8-FUSION-GATE - Generation Fusion volumetrique ou vue 3D`.

`P10-SOLVER-GATE - Solveur complexe, backtracking ou optimisation globale`.

Palette persistante HTML, UI assets avancee/tableau, solveur global, cavites par pile/logements detailles, assets individuels Fusion, nouvelle geometrie produit complexe, export imprimable et validation d'impression restent gates ou missions separees.

## Fin de chaque mission

Appliquer la politique active `direct-to-main` : tests complets, commit propre,
integration directe dans `main`, push vers `origin/main`, puis reprise depuis
`origin/main` si aucune vraie gate humaine n'est atteinte.