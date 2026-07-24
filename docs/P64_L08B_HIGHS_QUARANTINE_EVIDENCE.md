# P64-L08B — mesure et quarantaine de la lane HiGHS de sol

Date : 2026-07-24
Statut : `automated-validated`, `quarantined-from-auto`.

## 1. Question vérifiée

La lane HiGHS intégrée par L07 rallonge-t-elle le solvage courant sans apporter
un gain applicable aux cas limites BGIG en 3D ?

Le même corpus de régression existant a été exécuté trois fois par mode :

- `internal_only` : runtime HiGHS non configuré ;
- `highs_configured` : binaire produit 1.15.1 verrouillé, même machine, même
  projet, mêmes efforts et même recertification BGIG.

Le holdout L06/L07 n'a pas été ouvert et aucun réseau n'a été appelé.

## 2. Preuve reproductible

- Script : `scripts/solver/diagnose_highs_product_lane.py`.
- Corpus : `tests/fixtures/p64_l05d_solver_case_corpus.v1.json`, sept cas.
- Répétitions : 3 par mode et par cas ; mesures P50/P95 en temps mur.
- Digest corpus :
  `a017cbbcc0f841afde2fb0721d10809d2a8a1f681b4093394c7b3ba6c3239a17`.
- Digest de la mesure :
  `e6a020e62e89d8c85b9640b3cbf6790db4cf1378a27843c824125c7a58d20689`.
- Mémoire : le pic Python est relevé ; le RSS du sous-processus n'est pas
  présenté comme mesuré, faute d'ajouter une dépendance de monitoring.

## 3. Résultats mesurés

Les écarts sont `highs_configured - internal_only` en millisecondes. Un nombre
positif est un ralentissement.

| Cas | Statut HiGHS | Appels | Δ P50 | Δ P95 | Résultat utile à la gate 3D |
| --- | --- | ---: | ---: | ---: | --- |
| `continuous-closure-normal` | `unsupported` | 0 | +3,6 | -50,7 | non |
| `dense-11x34-quick` | `unsupported` | 0 | +10,0 | +13,5 | non |
| `localized-reservation-normal` | `unsupported` | 0 | +12,8 | +5,5 | non |
| `multi-cavity-normal` | `solution_found` | 3 | +42,1 | +63,6 | gain de sol seulement |
| `simple-quick` | `solution_found` | 3 | +53,4 | +54,2 | gain de sol seulement |
| `variant-dead-end-quick` | `bounded_unknown` | 3 | +34,0 | +35,3 | non |
| `variant-unsolved-quick` | `bounded_unknown` | 3 | +38,8 | +38,9 | non |

Les trois cas les plus liés aux contraintes 3D sont refusés sans processus,
mais passent quand même par la préparation de la lane. Les deux cas où HiGHS est
sélectionné restent des cas de sol ; ils ne démontrent aucun empilement, appui,
réservation haute, accès ou charge élevée. Les deux cas variantes consomment le
budget externe sans proposition certifiée.

## 4. Décision appliquée

`_solve_minimal_layout_once` désactive désormais la lane externe par défaut.
Même avec le runtime HiGHS configuré, le parcours Auto et le profil Deep ne la
lancent plus ; le portefeuille interne reste déterministe. Le binaire, son
contrat hors ligne et le script de diagnostic sont conservés uniquement comme
matériel expérimental, hors parcours produit.

La lane ne pourra revenir que si P64-L08C à L08F produit un candidat dont la
fidélité 3D complète et le gain sur les familles limites sont prouvés. L07 ne
constitue pas cette preuve.

## 5. Frontières maintenues

Aucune dimension, tolérance, géométrie, certificat, propriété P45,
finalisation, CAD, scène, Fusion ou statut d'impression n'a été changé.
