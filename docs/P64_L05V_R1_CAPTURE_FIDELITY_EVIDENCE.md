# P64-L05V-R1 - Preuve de fidelite de capture DEV

Date : 2026-07-23
Statut : implemented-fusion-bridge, automated-validated ; fusion-validated: false ; print-validated: false.

## Observation reelle, en lecture seule

Les trois derniers SolverCaseBundle locaux de Mon insert sont valides : leurs digests complets sont verifies par validate_solver_case_bundle. Aucun bundle ni projet personnel n est copie dans le depot.

1. dfa2ac115d79 : revision 43, 17 conteneurs / 19 contenus, plan certifie solution_found, cache certifie reutilise et warm start accepte.
2. 20a029b2ad70 : revision 44, exactement un nouveau conteneur et un nouveau contenu, digest projet change, ancien plan marque stale.
3. 48a98a092851 : meme digest projet que la capture 2, puis recherche fraiche de 2707 ms, no_solution_within_budget / hard_budget_reached, aucun resultat negatif reutilise.

Le nouveau contenu observe est un lot de 10 jetons ronds 20 x 20 x 3 mm dans un conteneur automatique. Les bornes necessaires restent satisfaites : 1 788 000 mm3 utilisables, 1 017 891,502 mm3 d enveloppes minimales, solde positif 770 108,498 mm3. Cette marge ne prouve pas un placement.

## Defaut reproduit

Apres la validation qui produit le refus incremental, le clic DEV appelait une nouvelle synchronisation sur le meme projet. Cette synchronisation sans delta remplacait le rapport global_void_reuse utile par not_attempted / dependencies_unchanged avant la construction du bundle. Le couple de captures prouve donc le delta et l echec global, mais perd la raison et les compteurs exacts de l insertion locale.

## Correctif

Le bridge fige solver_case_snapshot avant sa propre synchronisation et transmet ce snapshot au producteur pur. Le projet, le solveur, les budgets, les lanes, la finalisation, la CAD et la scene restent inchanges.

Le test bridge calcule un plan, ajoute un conteneur hors limite, observe global_solve_required, capture, puis exige l egalite exacte entre le rapport refuse visible et le rapport stocke dans le bundle. Il exige aussi que minimal_layout reste stale.

## Validation

- bridge Fusion : 27/27 ;
- SolverCaseBundle : 3/3 ;
- insertion globale : 7/7 ;
- DOM : 38/38 ;
- suite complete : 682/682 en 205,616 s ;
- Ruff cible et py_compile : OK.

La premiere tentative de suite complete a ete interrompue par l enveloppe Codex a 41 s alors que le wrapper etait actif ; le PID a ete verifie absent avant une unique relance gardee. Cette relance est la preuve 682/682 ci-dessus.
