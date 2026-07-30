# P64-L09W-C — preuve de campagne de référence

Date : 2026-07-30

Statut : `done`, `automated-validated`, `baseline-observed`,
`P64-L09W-D-ready`.

## Décision

La campagne de référence 0.1.80 est complète sur les 400 cas positifs ouverts.
Elle ne modifie ni le solveur, ni les budgets, ni la grille, ni les valeurs
physiques. Le holdout privé reste fermé et non exécuté.

Le résultat utile n'est pas un taux produit à revendiquer. Il est l'attribution
causale suivante :

1. la perte dominante se situe dans la fermeture/finalisation composite XY ;
2. la recherche bornée et SCIP ne sont pas le premier levier mesuré ;
3. P64-L09W-D doit traiter un seul incrément causal :
   `xy_composite_residual_owner_resolution_v1`.

Cet incrément cible uniquement la règle déterministe d'affectation des cellules
résiduelles que la fermeture XY ne sait actuellement rattacher à aucun
propriétaire. Il doit conserver les enveloppes minimales certifiées, les
frontières, les murs, les soustractions, la grille de `0,1 mm`, les budgets et
les digests fonctionnels des cas déjà prêts.

## Entrées figées

- release produit : `0.1.80` ;
- manifest ouvert :
  `tests/fixtures/p64_l09w_b_product_corpus.v1.json` ;
- 240 cas `discovery/common` ;
- 160 cas `tuning/stress` ;
- deux replays fonctionnels par cas ;
- Python runtime : `3.14.0` ;
- SCIP : artefact privé `10.0.2` Windows x86-64 ;
- digest du bundle candidat :
  `23a9e9a2a6f5657f8371da4a4a6eaaecab08df3ad370398ade786d57a22e8dd5` ;
- digest du reçu runtime :
  `f218a566e8d033d49b0e89c4bb478837b5815e5334e3bda5d07c36ea99d9f2df`.

Le runner impose des lots de 1 à 25 cas, un checkpoint atomique après chaque
cas, une reprise sans double exécution et le refus d'un digest incompatible.
La campagne a été reprise par lots bornés, sans relancer de commande
monolithique.

## Preuves de clôture

- statut du rapport : `complete` ;
- cas terminés : `400/400` ;
- cas restants : `0` ;
- replays fonctionnels : `400` ;
- checkpoint final :
  `57d5661a0dd12d71e23394132dfd3421f060b3fa615c4d6d2de8df6e2b9b4f62` ;
- ensemble de résultats :
  `312764c824119df70f23f5a2ca6aceb281e85d3a25a9e69cd5297ffaf200c654` ;
- rapport final :
  `52946c6c75538f23ad2d85dda47b05fc58678f2e402378d5753e9c3af13d9084`.

Les artefacts complets restent locaux et ignorés par Git :

- `.codex-work/p64-l09w-c/reference-checkpoint.json` ;
- `.codex-work/p64-l09w-c/reference-report.json`.

## Résultats globaux

| Mesure | Résultat |
| --- | ---: |
| Cas ouverts | 400 |
| `certified_solution` | 332 |
| `bounded_unknown` | 68 |
| Taux certifié ouvert | 83,00 % |
| Résultats prêts hors Fusion | 61 |
| Taux prêt hors Fusion | 15,25 % |
| Replays fonctionnellement identiques | 368/400 |
| Solutions non certifiées publiées | 0 |
| Faux impossibles | 0 |

Les seuils préenregistrés de 95 % global et 99 % sur les familles courantes ne
sont pas revendiqués. Ces résultats ouverts servent à choisir D ; ils ne
remplacent pas le verdict holdout de E.

## Résultats par strate

| Strate | Cas | Certifiés | Censurés | Prêts hors Fusion | Calcul p50 | Calcul p95 | Calcul p99 | Finalisation p95 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `common` | 240 | 200 | 40 | 55 | 0,990 s | 20,856 s | 21,393 s | 1,997 s |
| `stress` | 160 | 132 | 28 | 6 | 24,943 s | 77,117 s | 121,761 s | 20,200 s |
| global | 400 | 332 | 68 | 61 | 4,947 s | 51,795 s | 86,683 s | 20,078 s |

La longue traîne est donc réelle et concentrée sur `stress`. La mémoire de
pointe mesurée sur les cas certifiés vaut environ 118,3 Mio au p50,
182,2 Mio au p95 et 239,2 Mio au p99.

SCIP n'est pas le coût dominant mesuré : son p50 vaut `0 ms`, son p95
`16,775 ms` et son p99 `639,416 ms` sur les cas certifiés. Le certificat commun
porte l'essentiel du temps de calcul : p50 `4,233 s`, p95 `49,298 s` et p99
`79,864 s`.

## Attribution des pertes

| Cause | Nombre |
| --- | ---: |
| `certified_minimal_not_finalized` | 271 |
| `internal_lanes_exhausted_and_scip_not_certified` | 40 |
| `functional_nondeterminism` | 32 |
| `global_deadline_exhausted` | 28 |

Une même exécution peut contribuer à plusieurs pertes ; ces nombres ne sont
donc pas un partitionnement des 400 cas.

Détail de la cause dominante :

| Détail de finalisation | Nombre |
| --- | ---: |
| `xy_composite_residual_owner_not_found` | 237 |
| `xy_composite_deadline_reached` | 20 |
| `final_cavity_anchor_certificate_rejected` | 12 |
| `xy_composite_partial_residual_consumption` | 2 |

La première mission D cible les 237 observations
`xy_composite_residual_owner_not_found`. Elle ne doit pas contourner le
certificat, attribuer arbitrairement une cellule, augmenter une deadline ou
masquer un échec sous un statut prêt.

## Routes observées

| Route | Nombre |
| --- | ---: |
| `canonical_floor_maxrects` | 154 |
| `historical_legacy_corner` | 70 |
| `not_available` | 68 |
| `certified_witness_incumbent` | 44 |
| `historical_bridge_edge` | 42 |
| `variant_center_footprint` | 13 |
| `variant_edge_interleave` | 5 |
| `variant_corner_long_side` | 4 |

## Invariants

- `holdout_file_read=false` ;
- `holdout_opening_count=0` ;
- `holdout_solver_invocation_count=0` ;
- aucun témoin privé divulgué au solveur évalué ;
- `solver_budget_changed=false` ;
- `product_grid_changed=false` ;
- `geometry_epsilon_changed=false` ;
- `physical_value_changed=false` ;
- aucune matérialisation Fusion invoquée ;
- `fusion-validated=true` reste hérité de la candidate 0.1.80 validée ;
- `print-validated=false`.

La matérialisation n'est pas mesurée dans C. Seuls les 61 résultats finalisés
ont une CAD IR mesurée. Aucune observation Fusion nouvelle n'est requise avant
une éventuelle candidate modifiée en F.

## Validation automatisée

Commande ciblée :

```powershell
python -m unittest discover -s tests -p test_p64_l09w_c_reference_campaign.py
```

Résultat :

```text
Ran 7 tests in 0.164s
OK
```

La forme `python -m unittest tests.test_p64_l09w_c_reference_campaign` a échoué
avant exécution parce que `tests` n'est pas un package importable dans le
runtime Python 3.10 courant. La découverte canonique passe les sept tests.

Autres validations de clôture :

- contrat documentaire : `11/11` ;
- suite ciblée P64-L09W : `29/29` après ajout du verrou documentaire final ;
- compilation Python du runner et de ses tests : `OK` ;
- suite complète autorisée avant ce verrou documentaire : `1061/1061` en
  `582,188 s`, avec une intégration SCIP native ignorée ;
- `git diff --check` : `OK`.

`ruff` n'est pas disponible dans cet environnement. Cette absence n'est pas
présentée comme une gate verte ; les vérifications Python et Git ci-dessus sont
les contrôles effectivement exécutés.

## Gate de retour sur investissement pour D

P64-L09W-D commence par les cas ouverts qui portent
`xy_composite_residual_owner_not_found` :

1. reconstruire au moins un cas `common` et un cas `stress` sans modifier les
   budgets ;
2. prouver pourquoi aucune option de propriétaire n'est générée ;
3. définir une règle déterministe fondée sur les intersections et certificats
   existants, sans fallback arbitraire ;
4. ajouter les tests ciblés avant le changement ;
5. rejouer les cas concernés puis les 400 cas ouverts ;
6. refuser l'incrément s'il perd une solution certifiée, modifie un résultat
   déjà prêt, augmente un budget ou déplace le coût vers CAD/Fusion.

Le holdout reste fermé jusqu'à P64-L09W-E.
