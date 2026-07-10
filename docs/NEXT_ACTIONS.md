# Next Actions

Derniere mise a jour : 2026-07-10

## Politique active - Integration Git autonome

Statut : `active`. Apres chaque mission, tests pertinents, diff propre, commit atomique, integration directe dans `main` et push vers `origin/main`.

## Etat courant

P19, P20 et P21 sont termines dans le moteur Python pur. BGIG sait maintenant verifier un plan manuel de boite, produire un placement greedy XY borne, comparer un portefeuille de variantes deterministes et exporter une selection explicite avec metadata CAD IR. Le dashboard P21 est un artefact HTML statique de comparaison, pas l UX persistante finale.

## Mission ready suivante

`P22-M001 - Rapport de gate pour la premiere surface UX persistante` : comparer palette Fusion et app locale de composition, recommander un premier spike et documenter son contrat sans ecrire de surface persistante.

- Capability : C-FUSION-UI, C-PRODUCT-VISION.
- Milestone : M14 Usable beta.
- Validation : rapport de gate ADR-0036 lisible, options, recommandation, risques, perimetre exact et criteres d acceptation.
- Gate : aucune pour le rapport documentaire ; une decision humaine explicite reste obligatoire avant implementation de palette ou d app.

## Gate humaine active

- ADR-0036 : choisir et autoriser la premiere surface UX persistante avant implementation.
- Premiere materialisation Fusion du plan selectionne : gate distincte.
- Premiere impression 3D et calibration physique : gate distincte.

## Hors scope maintenu

- Aucun solveur global, backtracking, optimisation opaque ou IA non evaluee.
- Aucune UI persistante, palette Fusion ou app locale/web avant la gate ADR-0036.
- Fusion ne devient jamais source de verite du plan ; l impression reste non validee.


## Fin de chaque mission

Appliquer la politique direct-to-main : lancer les tests pertinents, verifier git diff --check, committer un scope atomique, integrer dans main, pousser vers origin/main, puis repartir d une branche propre avant la mission suivante.
