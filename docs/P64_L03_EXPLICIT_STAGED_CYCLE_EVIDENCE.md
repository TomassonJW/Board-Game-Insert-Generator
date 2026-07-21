# P64-L03 — Preuve du cycle explicite et de la finalisation staged

Date : 2026-07-21
Statut : implemented-core, implemented-fusion-bridge, implemented-fusion-ui,
automated-validated
Validation Fusion : false
Validation impression : false

## Portée livrée

P64-L03 remplace le solve global temporisé par trois transitions explicites :
Calculer l'agencement, Finaliser le volume, puis Matérialiser dans Fusion.
L'analyse locale reste réactive ; aucune édition ordinaire ne lance le solveur
global et les deux premières étapes ne créent aucune scène.

## État staged, provenance et cache

Le module staged_calculation.py expose bgig.staged_calculation.v1 et sépare
agencement global, plan final et préparation CAD. Il publie clés, digests,
cache, identifiant de requête, raison d'arrêt et action suivante.

La clé globale inclut les frontières, le contexte boîte, les réservations, les
réglages, le classement et le digest de l'entrée solveur normalisée. Deux
projets différents ne peuvent donc pas réutiliser silencieusement un résultat
global malgré des frontières locales identiques.

## Finalisation de compatibilité

Le finaliseur preserve_existing_certified_closure accepte seulement une
partition construite, courante et certifiée. Il conserve le même plan_digest,
ne change aucune géométrie et n'ajoute aucun corps. F01, F02, F03, remplissage,
harmonisation et cales restent verrouillés.

## Rejet fail-closed

- une modification rend l'agencement et le plan final obsolètes sans solve ;
- une réponse globale tardive devient stale_or_cancelled ;
- une matérialisation directe ou obsolète est refusée ;
- une proposition partielle ou bloquée ne peut pas être finalisée ;
- la préparation CAD ne revendique aucune observation Fusion.

## UX Fusion

Une seule action primaire progresse de Calculer à Finaliser puis Matérialiser.
L'ancien aperçu reste visible mais grisé. Le diagnostic reste replié et les
méthodes, budgets et raisons d'arrêt restent observables.

AUTO_SOLVE_STABILITY_MS, scheduleAdaptiveSolve et autoSolveTimer sont supprimés.
Le debounce de 350 ms déclenche uniquement validate_project.

## Validation automatisée

- 7/7 tests purs staged ;
- 21/21 tests bridge palette ;
- 32/32 tests DOM palette ;
- 7/7 tests résultat palette ;
- 5/5 tests de continuité P66 ;
- suite complète : 606/606 OK ;
- syntaxe JavaScript : OK ;
- Ruff : OK ;
- compileall : OK ;
- frontière adsk : OK ;
- git diff --check : OK.

## Limites

Le cas dense 11 × 34 reste no_solution_within_budget. Aucun budget, méthode,
tolérance, défaut, schéma ou valeur physique ne change. fusion-validated et
print-validated restent false.

## Suite

P64-L03V est la seule prochaine gate. Elle observe dans Fusion l'absence de
solve silencieux, les trois actions, le stale honnête, le focus stable et
l'absence de scène avant matérialisation.

## Revue Fusion 0.1.56 et supersession

La revue humaine P64-L03V refuse la sémantique géométrique observée : le solve
courant distribue déjà les surplus de boîte, tandis que la finalisation de
compatibilité conserve cette géométrie sans transformation. Elle observe aussi
qu'un ancien digest peut masquer la nécessité de mettre la scène à jour.

Cette preuve reste valable pour le retrait du solve automatique, l'orchestration
explicite, le stale fail-closed et les tests automatisés. Elle ne prouve pas la
séparation minimal/final et ne constitue aucune validation Fusion.

ADR-0074 et le contrat P64-L03R supersèdent ces limites. P64-L03V est
`contextual-KO`; `fusion-validated: false`, `print-validated: false`.
