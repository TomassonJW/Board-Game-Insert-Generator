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

Aucune gate humaine active apres validation Fusion `P16-ERGONOMIC-2D-TRAY-PACKING-SPRINT-V` confirmee le 2026-07-09 sur `a75688e`.

## Sprint actif

`P17-PRINTABLE-EXPORT-AND-PREPRINT-SPRINT` est lance explicitement le 2026-07-09 apres validation P16.

Mission interne terminee : P16 validation - `fusion-validated-v0`, export/print toujours non valide physiquement.

Mission interne terminee : P17-M001 - ADR export/preprint V0, `ADR-0035` acceptee.

Mission interne terminee : P17-M002 - Action Fusion `export_printables`, implementation STL V0 non encore validee dans Fusion.

Mission interne terminee : P17-M003 - Export manifest V0, manifestes JSON/Markdown V0 produits par `export_printables`.

Mission interne terminee : P17-M004 - Printability blockers V0, statuts/issues/export_allowed ajoutes.

Mission interne terminee : P17-M005 - Calibration coupon / preprint check V0, protocole preprint et exemple JSON ajoutes.

Mission interne ready : P17-M006 - Preparation gate Fusion P17.

## Mission ready non gated

`P17-M006 - Preparation gate Fusion P17`.

## Regle operationnelle Fusion

Pour toute future gate Fusion, Codex prepare automatiquement le smoke test avec
`scripts/fusion/`, installe l'add-in si les permissions AppData le permettent,
genere les CAD IR temporaires necessaires et fournit uniquement les actions
Fusion restantes a Thomas.

## Missions bloquees par gate

`P8-FUSION-GATE - Generation Fusion volumetrique ou vue 3D`.

`P10-SOLVER-GATE - Solveur complexe, backtracking ou optimisation globale`.

Palette persistante HTML, UI assets avancee/tableau, solveur global, cavites par pile/logements detailles, assets individuels Fusion, nouvelle geometrie produit complexe et validation d'impression restent gates ou missions separees. P17 autorise seulement l'export/preprint V0 sans validation physique.

## Fin de chaque mission

Appliquer la politique active `direct-to-main` : tests complets, commit propre,
integration directe dans `main`, push vers `origin/main`, puis reprise depuis
`origin/main` si aucune vraie gate humaine n'est atteinte.