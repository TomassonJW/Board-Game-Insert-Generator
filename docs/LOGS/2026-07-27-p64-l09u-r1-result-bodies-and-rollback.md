# Journal — P64-L09U-R1 corps résultats et rollback

Date : 2026-07-27.

## Fait humain

La candidate 0.1.71 démarre vierge, calcule et finalise, mais la matérialisation
échoue sur `ALL_TOOL_BODY_REFERENCE_LOST`. La scène visible contient des corps
outils partiels.

Verdict : `human-KO`, `do-not-run`.

## Diagnostic

`BRepBodies.add` était appelé pendant l'édition d'une BaseFeature. Les objets
sources renvoyés étaient conservés puis fournis à Combine après `finishEdit`.
Fusion attend alors les corps résultats de `baseFeature.bodies`.

## Correctif R1

- relire les corps résultats après la fin d'édition ;
- vérifier leur cardinalité ;
- fournir uniquement ces résultats aux lots Join/Cut ;
- rollback global des objets BGIG après toute erreur de génération ;
- candidate distincte 0.1.72.

## Retour produit cadré

- ADR-0095 : jobs annulables et progression Fusion par lots ;
- ADR-0096 : miniatures et sélection explicite de variantes locales ;
- ADR-0097 : épaisseur de séparateur d'assets distincte.

Ces trois propositions restent hors du correctif atomique R1.

## Statuts

- source R1 : `automated-validated` ;
- tests ciblés : `149/149` ;
- replays personnels : `6/6`, lecture seule ;
- suite globale autorisée : `881/881` en `408.131 s` ;
- une intégration SCIP native ignorée ;
- douze modules benchmark/corpus/tournoi exclus ;
- gate : `prepared-not-human-observed` ;
- `fusion-validated=false` ;
- `print-validated=false`.
