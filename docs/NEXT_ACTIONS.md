# Next Actions

Derniere mise a jour : 2026-07-10

## Politique active - Integration Git autonome

Statut : `active`. Les missions non gatees restent testees, committeees puis integrees directement dans `main`.

## Etat courant

P19, P20 et P21 sont termines dans le moteur Python pur. P22 est termine comme rapport de gate : une UX persistante est necessaire pour atteindre le parcours produit cible, mais son choix engage l architecture et les dependances.

## Gate humaine active

La validation attendue est dans `docs/P22_UX_SURFACE_GATE_REPORT.md`.

- Recommandation : D, app locale de conception + Fusion adaptateur CAD/export.
- Validation demandee : autoriser ou non ce chemin et la stack locale moderne proposee, ou choisir B/C/reporter.
- Limite : aucune palette, app, dependance UI majeure ou materialisation Fusion de la selection ne doit commencer avant reponse explicite.

## Mission suivante apres validation

`P23-M001 - Spike app locale de composition` : parcours boite -> assets -> intentions/reservations -> P21 variants -> selection/export local, sans generation Fusion automatique.

## Hors scope maintenu

- Aucun solveur global, backtracking, optimisation opaque ou IA non evaluee.
- Fusion ne devient jamais source de verite du plan.
- Aucune validation d impression, de slicer ou d ergonomie reelle n est revendiquee.

## Fin de chaque mission

Appliquer direct-to-main : tests pertinents, `git diff --check`, commit atomique, integration et push de `main`, puis reprise propre.
