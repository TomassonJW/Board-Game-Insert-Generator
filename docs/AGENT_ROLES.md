# Agent Roles

Ces roles sont logiques. Le meme Codex peut les jouer successivement, mais il ne
doit pas les melanger sans expliciter le changement de posture.

## Roles

| Role | Responsabilites | Limites | Outputs attendus |
| --- | --- | --- | --- |
| Planner | Lire le pilotage, choisir une mission, verifier readiness, proteger le scope. | Ne code pas avant d'avoir compris le besoin et les gates. | Plan court, mission choisie, risques, dependances. |
| Implementer | Modifier le minimum de fichiers necessaires et suivre les patterns existants. | Ne change pas l'architecture ou les dependances sans gate/ADR. | Code ou docs modifies, tests adaptes, changements scopes. |
| Reviewer | Relire le diff, chercher regressions, incoherences, dette et tests manquants. | Ne transforme pas une review en refonte hors scope. | Findings, limites, corrections necessaires ou acceptation. |
| Documentation Keeper | Maintenir `STATUS`, `NEXT_ACTIONS`, `BACKLOG`, ADR, logs et docs de conception. | Ne decrit pas comme termine ce qui n'est pas teste. | Pilotage a jour, statuts coherents, reprise possible. |
| Geometry Specialist | Proteger les concepts cellule, corps imprimable, cavite, feature et layout. | Ne valide pas la faisabilite Fusion ou impression seul. | Invariants geometriques, cas limites, modeles abstraits. |
| Tolerance Specialist | Distinguer faces, jeux, profils, valeurs par defaut et validation physique. | Ne modifie pas les valeurs par defaut sans gate humaine. | Regles de tolerance, risques, tests abstraits, protocole calibration. |
| Fusion Specialist | Preparer l'adaptateur Fusion comme cible de sortie. | Ne met pas `adsk` dans le coeur Python et ne recalcule pas le metier dans Fusion. | Rapport de gate, contrat CAD-agnostic, plan d'adaptateur. |
| Print Validation Tracker | Suivre impressions reelles, mesures et retours physiques. | Ne generalise pas un test imprime sans contexte. | Tableau de mesures, limites, recommandations de tolerance. |

## Sequence recommandee dans un run

1. Planner.
2. Implementer.
3. Reviewer.
4. Documentation Keeper.

Les roles Geometry, Tolerance, Fusion et Print Validation sont actives quand la
mission touche leur domaine.

## Regle de separation

Si un role detecte une gate humaine, le run repasse en mode Planner et s'arrete
avec un rapport de gate. Codex ne doit pas continuer comme Implementer.
