# Next Actions

Derniere mise a jour : 2026-07-10

## Politique active - Integration Git autonome

Statut : `active`. Les missions non gatees restent testees, committeees puis integrees directement dans `main`.

## Etat courant

P19, P20 et P21 sont termines dans le moteur Python pur. P22 est accepte et P23 livre le premier parcours local executable : boite -> assets -> contraintes -> variantes -> selection -> export. Fusion reste un adaptateur CAD/export futur.

## Gate humaine active

- L option D a ete approuvee le 2026-07-10 : React/Vite local + adaptateur Python loopback, formalises par ADR-0040.
- Toute materialisation Fusion d une selection P23 reste une gate distincte.
- Une impression, un slicer ou une promesse ergonomique physique restent des gates physiques distinctes.

## Premiere mission ready

`P24-M001 - Qualite du projet local` : rendre l edition des allocations multi-assets, les erreurs de saisie et la recuperation de projet plus explicites, sans ajouter de moteur, de materialisation Fusion ou de persistence serveur.

## Hors scope maintenu

- Aucun solveur global, backtracking, optimisation opaque ou IA non evaluee.
- Fusion ne devient jamais source de verite du plan.
- Aucune validation d impression, de slicer ou d ergonomie reelle n est revendiquee.

## Fin de chaque mission

Appliquer direct-to-main : tests pertinents, `git diff --check`, commit atomique, integration et push de `main`, puis reprise propre.
