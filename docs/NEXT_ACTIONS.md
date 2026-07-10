# Next Actions

Derniere mise a jour : 2026-07-10

## Politique active - Integration Git autonome

Statut : `active`. Les missions non gatees restent testees, committeees puis integrees directement dans `main`.

## Etat courant

P19 a P21 donnent les contrats et propositions moteur. P22 a P25 livrent une surface locale testable : composition, export explicite, import robuste, allocations multi-assets et demarrage guide par drafts V0 locaux. Fusion reste un adaptateur CAD/export futur.

## Gate humaine active

- L option D est approuvee : React/Vite local + adaptateur Python loopback, formalises par ADR-0040.
- Toute materialisation Fusion d une selection locale reste une gate distincte.
- Une impression, un slicer ou une promesse ergonomique physique restent des gates physiques distinctes.

## Premiere mission ready

`P26-M001 - Resume de preparation avant generation` : donner a un debutant une lecture claire des mesures, allocations et limites avant toute proposition, sans creer une nouvelle logique de decision.

## Hors scope maintenu

- Aucun solveur global, backtracking, optimisation opaque ou IA non evaluee.
- Fusion ne devient jamais source de verite du plan.
- Aucune validation d impression, de slicer ou d ergonomie reelle n est revendiquee.

## Fin de chaque mission

Appliquer direct-to-main : tests pertinents, `git diff --check`, commit atomique, integration et push de `main`, puis reprise propre.
