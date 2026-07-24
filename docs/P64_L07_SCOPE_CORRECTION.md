# P64-L07 — correction de portée et statut historique

Date : 2026-07-24
Autorité : ADR-0083.

## Décision courte

P64-L07 n'est pas le benchmark complet du solveur BGIG. Il est conservé comme
benchmark externe partiel d'un sous-problème de placement au sol, rectangulaire
et à un seul niveau.

La conclusion historique « benchmark externe terminé » est donc supersédée pour
toute affirmation sur le solvage 3D global, les cas limites BGIG, la vitesse du
parcours Auto ou le choix définitif d'un moteur.

## Faits vérifiés

| Élément | Contrat ou fait initial | Réalité mesurée |
| --- | --- | --- |
| Programme L07 | Cas BGIG à un à trois niveaux, réservations et rotations. | Corpus V2 construit avec ces dimensions. |
| Adapter commun L07C | Même entrée pour OR-Tools, HiGHS, SCIP et LAFF. | `external_floor_problem.v1` : un seul niveau au fond de la boîte. |
| Contraintes perdues | Niveaux, réservations, support, empilement, retrait. | Réponse `unsupported`, jamais simplification silencieuse. |
| Holdout L07 | 64 cas neufs. | 7 traduisibles, 5 solutions certifiées, 2 `bounded_unknown`, 55 `unsupported`. |
| Lane HiGHS intégrée | CLI local et recertification BGIG. | Modèle `axis_aligned_single_floor_rectangles_v1`, sans empilement. |

Les détails historiques restent dans les preuves L07B à L07E. Ils ne sont pas
effacés ni réécrits.

## Ce que L07 reste autorisé à démontrer

- un audit de licences, packaging et exécution hors ligne de candidats externes ;
- une infrastructure de tournoi reproductible et de recertification ;
- un gain possible de HiGHS sur certains placements plats rectangulaires ;
- un fallback sûr lorsque cette lane est indisponible.

## Ce que L07 ne démontre pas

- la résolution de l'empilement, de plusieurs niveaux ou d'appuis réels ;
- la résolution de réservations supérieures, retraits ou variantes P45 à grande
  échelle ;
- un gain sur les cas limites à nombreux conteneurs et contenus ;
- une amélioration de vitesse du solveur 3D ;
- la pertinence d'une intégration produit par défaut ;
- une validation Fusion ou impression.

## Action remplacée

P64-L07V est annulée comme prochaine action. La priorité devient P64-L08 :
benchmark 3D adversarial, corpus de cas limites, sélection scellée et intégration
seulement après victoire fonctionnelle et de performance sur ce périmètre.
