# Next Actions

Derniere mise a jour : 2026-07-10

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

Aucune gate humaine active pour le travail documentaire `P18-VISION-UX-VOLUMETRIC-REBASE-SPRINT` explicitement autorise. Une nouvelle gate sera requise avant toute implementation de palette persistante, app externe ou solveur global.

## Sprint actif

`P18-VISION-UX-VOLUMETRIC-REBASE-SPRINT` est lance explicitement le 2026-07-10 apres validation humaine P17. Il est borne a la vision produit, l'UX cible, le contrat volumetrique, la roadmap solver et l'ADR UX; il n'autorise ni palette, ni solveur global, ni nouvelle geometrie.

Mission interne terminee : P16 validation - `fusion-validated-v0`, export/print toujours non valide physiquement.

Mission interne terminee : P17-M001 - ADR export/preprint V0, `ADR-0035` acceptee.

Mission interne terminee : P17-M002 - Action Fusion `export_printables`, implementation STL V0 non encore validee dans Fusion.

Mission interne terminee : P17-M003 - Export manifest V0, manifestes JSON/Markdown V0 produits par `export_printables`.

Mission interne terminee : P17-M004 - Printability blockers V0, statuts/issues/export_allowed ajoutes.

Mission interne terminee : P17-M005 - Calibration coupon / preprint check V0, protocole preprint et exemple JSON ajoutes.

Mission interne terminee : P17-M006 - Validation Fusion export/preprint, STL par module BGIG, manifestes, exclusions registry et clear post-export valides; `print-validated: false` maintenu.

## Mission ready non gated

`P18-M005 - ADR architecture UX` est ready. Il doit comparer commande Fusion, palette, app locale et hybride, puis preparer la gate humaine avant implementation.

## Regle operationnelle Fusion

Pour toute future gate Fusion, Codex prepare automatiquement le smoke test avec
`scripts/fusion/`, installe l'add-in si les permissions AppData le permettent,
genere les CAD IR temporaires necessaires et fournit uniquement les actions
Fusion restantes a Thomas.

## Missions bloquees par gate

`P8-FUSION-GATE - Generation Fusion volumetrique ou vue 3D`.

`P10-SOLVER-GATE - Solveur complexe, backtracking ou optimisation globale`.

Palette persistante HTML, UI assets avancee/tableau, solveur global, cavites par pile/logements detailles, assets individuels Fusion, nouvelle geometrie produit complexe et validation d'impression restent gates ou missions separees. P17 valide seulement l'export/preprint V0 sans validation physique.

## Fin de chaque mission

Appliquer la politique active `direct-to-main` : tests complets, commit propre,
integration directe dans `main`, push vers `origin/main`, puis reprise depuis
`origin/main` si aucune vraie gate humaine n'est atteinte.
