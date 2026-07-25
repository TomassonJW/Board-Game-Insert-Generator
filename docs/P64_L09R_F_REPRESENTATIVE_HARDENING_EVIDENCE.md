# P64-L09R-F — Preuve de durcissement représentatif

Date : 2026-07-25

Statut : `implemented-product`, `automated-validated`, `gate-prepared-not-installed`.

## Matrice représentative

| Contrôle | Preuve | Résultat |
| --- | --- | --- |
| Cas public 28x30 | reçu public à digest, 28 placements recertifiés, aucun holdout lu | OK |
| Plateau/livret | fixture publique P66 réutilisée, réservations présentes dans le plan minimal | OK |
| Préférence petits-dessous | fixture publique dédiée, deux petits bacs sous le grand avec effort Normal | OK, préférence seulement |
| Inversion nécessaire | test large-dessous/petit-dessus avec axe de classement non dur | OK |
| Ouverture | plan enveloppe certifié malgré diagnostic matière négatif | OK |
| Collision | corps flottant rejeté par le certificat commun | OK |
| Réservation | zones SCIP exactes et cas non représentable fail-closed | OK |
| Deadline calcul | absence d’incumbent => `no_solution_within_budget`, aucune preuve impossible | OK |
| Deadline finition | timeout Quick conserve le digest minimal exact | OK |
| Fin anticipée | incumbent certifié conservé et publication normale avant budget admise | OK |

## Cycle calcul / finition séparé

Le préflight P64-L09R-V exécute deux fixtures publiques avec un `StagedCalculationSession` réel :

- calcul minimal Normal, budget total 20 000 ms ;
- sélection et construction CAD de `minimal_layout` avant finition ;
- finition Rapide, budget indépendant 3 000 ms ;
- sélection et construction CAD de `finalized_plan` seulement après certificat ;
- deux durées observées distinctes, informatives et non utilisées comme seuil de performance.

Le digest du reçu exclut uniquement ces durées de machine. Il couvre le résultat effectivement obtenu, notamment projets, placements, artefacts, réservations, budgets et statuts. Une finition bornée peut trouver des plans finaux équivalents différents entre deux exécutions ; la preuve n'en déduit donc pas une reproductibilité bit à bit.

## Préparation de la gate

- Add-in versionné 0.1.64 pour ne jamais confondre cette gate avec P64-L09V 0.1.63 annulée.
- Préflight : `scripts/fusion/p64_l09rv_preflight.py`.
- Préparateur futur : `scripts/fusion/prepare_p64_l09rv_gate.ps1`.
- Fixtures produites seulement dans le répertoire temporaire local puis installées par le préparateur de V.
- Recette humaine canonique : `docs/P64_L09R_V_FUSION_GATE_RECIPE.md`.
- Aucune installation Fusion n’est exécutée dans F.

## Validation

- Préflight représentatif : OK, deux fixtures, deux réservations plateau, reçu 28x30 intègre.
- Tests ciblés : 126/126, un test natif SCIP ignoré sous Python 3.10.
- Dry-run du préparateur : OK en 24,5 s ; 108 tests rejoués ; sortie explicite `No AppData files were changed`.
- Syntaxe Python et PowerShell : OK.
- Tests documentaires : 2/2.
- Suite complète : 873/873 en 239,310 s ; un test natif SCIP ignoré sous Python 3.10.
- `git diff --check` : OK.

## Frontières

- Aucun benchmark historique, tournoi ou holdout consommé n’est exécuté.
- Aucune valeur physique, tolérance, géométrie produit ou règle de couvercle n’est recalibrée.
- Aucune installation, observation Fusion ou impression n’est revendiquée.
- La prochaine et unique étape est la gate humaine P64-L09R-V.