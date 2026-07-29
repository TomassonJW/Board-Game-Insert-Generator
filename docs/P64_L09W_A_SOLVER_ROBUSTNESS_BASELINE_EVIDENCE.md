# P64-L09W-A — preuve d’audit et baseline solveur 0.1.80

Date : 2026-07-29.

Statut : `complete`, `baseline-observed`, `P64-L09W-B-ready`.

## 1. Autorité conservée

P64-L09U-R9-V reste acquis :

- Fusion 0.1.80 est `human-positive` ;
- `fusion-validated=true` ;
- `print-validated=false` ;
- géométrie, ordre, dispositions, pipeline strictement soustractif et
  récupération de performance R9 sont conservés ;
- aucun temps humain séparé n’a été fourni ou inventé.

P64-L09W-A n’a rejoué aucun projet personnel et n’a demandé aucune nouvelle
gate humaine.

## 2. Artefacts audités

L’audit couvre :

- L05 : 7 cas, dont 5 CI et 2 étendus ;
- L06 : 192 cas générés, plus ses régressions ;
- L07 : 128 cas générés ouverts, plus ses régressions ;
- L08 : 41 cas 3D ouverts sur dix familles ;
- les générateurs, oracles, runners, solveurs, certificats, finalisation,
  CAD IR, matérialisation et télémétrie directement concernés.

La vue directe L05 à L07 contient 343 entrées avec doublons et 298 digests de
projet distincts.

Les anciens holdouts L06, L07 et L08 restent consommés. Ils servent uniquement
de régressions historiques.

## 3. Dérive historique prouvée

La reconstruction sous la sémantique 0.1.80 donne :

- 162 entrées encore reconstructibles ;
- 165 entrées en `historical-semantic-drift` ;
- L05 : 3 dérives ;
- L06 : 94 dérives sur 192 recettes ;
- L07 : 68 dérives sur 128 recettes.

Les 162 dérives L06/L07 portent toutes sur les réservations contraignantes.
La normalisation 0.1.80 retire l’origine fixe historique des éléments plats au
profit de leur placement automatique. Les anciens témoins ne prouvent donc pas
la sémantique courante.

Aucun ancien digest n’a été réécrit. Aucune fixture en dérive n’a été exécutée
comme vérité solveur.

Après déduplication de 15 projets générés, la baseline produit contient :

- 147 projets uniques ;
- 101 positifs faisables par construction ;
- 42 contrôles historiquement impossibles ;
- 4 régressions L05 à vérité historique ;
- 41 cas L08 séparés comme `core-only`.

## 4. Couverture réelle et trous

La matrice historique directe couvre :

- 1 à 50 conteneurs ;
- 1 à 189 enregistrements de contenu ;
- 2 à 431 unités ;
- 1 à 3 couches ;
- 0 à 2 éléments plats ;
- axes de boîte de 5,1 à 350,4 mm ;
- axes de contenu de 2,165 à 162,5 mm ;
- 313 calculs froids et 30 séquences d’édition ;
- 233 vérités positives construites, 87 impossibles historiques et 23
  régressions historiques.

Elle ne couvre pas le contrat demandé :

- aucun ancrage explicite à 30 %, 65 %, 85 % et 95 % ;
- les cas positifs historiques atteignent au plus environ 45,2 %, 78,8 % et
  83,1 % de charge externe selon leur étiquette ;
- aucun objectif à 64 conteneurs ;
- aucun objectif à 64 contenus par conteneur ;
- aucun cas à 3, 4, 5, 6 ou 10 plateaux/livrets ;
- aucune couche au-delà de 3 ;
- aucune matérialisation Fusion chronométrée dans une campagne commune.

Plus important : les 147 projets encore reconstructibles possèdent tous zéro
élément plat. La couverture historique de 1 ou 2 éléments plats appartient aux
fixtures dont la vérité a dérivé. Elle ne peut pas servir de baseline produit
0.1.80.

## 5. Correction d’attribution avant mesure

Le premier replay avec le vrai Python Fusion 3.14 et le runtime SCIP produit a
trouvé la même géométrie deux fois, mais deux `plan_digest` différents.

Cause :

- le digest du modèle SCIP engageait le temps global restant ;
- cette valeur varie de quelques fractions de seconde entre deux runs ;
- elle contredisait l’invariant
  `volatile_runtime_metrics_in_certifiable_payload=false`.

Correction :

- SCIP reçoit toujours le temps restant réel ;
- le digest engage la limite publique stable du profil d’effort ;
- aucune géométrie, recherche, limite, grille, epsilon ou valeur physique ne
  change.

La gate réelle CPython 3.14 + SCIP 10.0.2 passe ensuite deux runs identiques :

- reçu : `f218a566e8d033d49b0e89c4bb478837b5815e5334e3bda5d07c36ea99d9f2df` ;
- runtime :
  `be3b02bfe9591c72b7a25367e4b55aae8b08462ba543eff9a70d552229aff54a`.

## 6. Correction du runner avant baseline autoritative

Un premier rapport complet, digest
`1ccda13782f859bb5122014f1824e5eec02a3eb749bbcc2f314c7b291b9a9c49`,
est rejeté comme preuve :

1. les deux replays portaient des identifiants de requête différents ;
2. la finalisation héritait du profil de calcul des anciennes fixtures au lieu
   du profil produit `normal`.

Le runner a été corrigé puis rejoué entièrement. Aucun résultat du rapport
rejeté n’est utilisé dans le verdict.

## 7. Baseline produit autoritative

Environnement :

- baseline fonctionnelle : 0.1.80 ;
- Python : 3.14.0 ;
- plateforme : Windows ;
- runtime SCIP produit courant ;
- deux replays par projet ;
- profils et limites historiques inchangés ;
- durée du run gardé : 1 073 s ;
- digest du code mesuré :
  `3c27badb9727071e38f9031b8a0435b00a85b2ec8236cef09d65bd3fd2c671bc` ;
- checkpoint :
  `bb2c8fb4c8d00667b67147c73828e559ecaf32b6fd8b64e3f5743877a6a1eb79` ;
- rapport :
  `26aed0b36c47396ed54291193e89913c680f603c02090936fc4932e311987105`.

Résultats sur les 147 projets :

- 21 `certified_solution` ;
- 81 `bounded_unknown` ;
- 45 `unsupported`.

Sur les 101 vérités positives :

- 19 solutions certifiées ;
- 79 `bounded_unknown` ;
- 3 non supportées ;
- taux observé : 19/101, soit 18,8119 % ;
- zéro faux impossible ;
- zéro solution publiée sans certificat.

Ce taux n’est pas une estimation du futur domaine supporté. La distribution est
ancienne, incomplète, sans élément plat reconstructible et composée de splits
déjà consommés. Elle sert uniquement de point de départ causal.

Par densité historique positive :

| Strate | Certifiés | Total | Taux |
| --- | ---: | ---: | ---: |
| ample | 17 | 38 | 44,7368 % |
| dense | 1 | 25 | 4 % |
| presque saturée | 1 | 38 | 2,6316 % |

Par famille positive :

| Famille | Certifiés | Total |
| --- | ---: | ---: |
| peu de conteneurs, beaucoup de contenus | 1 | 21 |
| édition puis reconstruction froide | 3 | 15 |
| beaucoup de conteneurs et de contenus | 5 | 21 |
| beaucoup de conteneurs, un contenu | 5 | 22 |
| dense hétérogène | 5 | 22 |

Les 42 contrôles historiquement impossibles sont tous `unsupported` : leur
preuve suppose d’interdire une rotation, contrôle que `project.v1` n’expose
pas. Leur exécution valide est donc de zéro. Le compteur de contradiction nul
ne constitue pas une preuve négative.

## 8. Déterminisme

Parmi 105 projets réellement exécutés :

- 101 replays ont le même statut, digest certifiable, placement et route ;
- 4 replays gardent le même statut `bounded_unknown` mais changent de route à
  la frontière temporelle :
  - `L06:holdout-d-034` ;
  - `L06:holdout-e-005` ;
  - `L07:l07-v2-discovery-c-028` ;
  - `L07:l07-v2-tuning-e-035`.

Le résultat public reste honnêtement inconnu dans chaque replay. La campagne
B/C devra publier cette variance de route liée aux limites de temps au lieu de
la masquer.

## 9. Temps et mémoire

Sur les 105 exécutions produit :

| Mesure | p50 | p95 | p99 |
| --- | ---: | ---: | ---: |
| préparation | 58,590 ms | 276,949 ms | 299,158 ms |
| calcul | 374,590 ms | 20 448,376 ms | 20 552,029 ms |
| première solution certifiée | 188,117 ms | 403,673 ms | 724,343 ms |
| certification | 0 ms | 0,754 ms | 1,325 ms |
| mémoire de travail | 241 270 784 o | 281 198 592 o | 345 317 376 o |

La mémoire est échantillonnée toutes les 50 ms dans le processus qui contient
SCIP.

Premiers runs agrégés :

- 59 invocations SCIP ;
- 350 129 essais de pose ;
- 5 519 états de recherche ;
- 280 complétions admises ;
- 1 432 rejets de certificat ;
- 21 candidats après déduplication.

Ces compteurs ont des portées historiques différentes ; ils servent à
l’attribution, pas à comparer deux moteurs sans normalisation.

## 10. Finalisation et CAD IR

Les 21 calculs certifiés ont été recertifiés dans un audit aval indépendant :

- 21 placements identiques à la baseline ;
- 2 finalisations `solution_found` ;
- 19 finalisations `no_solution_within_budget` ;
- 19 motifs `flat_inset_subtraction_plan_rejected` ;
- zéro deadline atteinte ;
- zéro preuve d’impossibilité ;
- 2 CAD IR tentés et 2 `ready_for_fusion`.

Le refus survient en 9 à 47 ms environ, très loin de la limite `normal` de
20 s. Ce n’est ni un déplacement de coût ni un timeout : la stratégie aval
rejette immédiatement ces plans.

La matérialisation reste `not-measured-offline`. Aucun temps humain ou Fusion
n’est inventé.

Reçu aval :
`925fa00b22f6d9648a2ed3f52c80c381abbc937457d68dd94314337d2cefc15c`.

## 11. Résultat L08 séparé

Les 41 cas L08 de cœur produisent :

- 40 `bounded_unknown` ;
- 1 `unsupported` ;
- 10 contrôles négatifs restent honnêtement inconnus et ne sont pas déclarés
  impossibles.

Ce résultat mesure le worker de cœur historique. Il ne traverse ni projet
produit, ni finalisation, ni CAD IR, ni matérialisation et ne contribue pas au
taux produit.

## 12. Options comparées

### Réutiliser tous les anciens cas comme vérités courantes

Simple, mais faux : 165 fixtures ont dérivé et les holdouts sont consommés.
Option refusée.

### Réécrire les digests et témoins historiques

Peu coûteux à court terme, mais détruit la comparabilité et transforme une
nouvelle vérité en ancien résultat. Option refusée.

### Optimiser immédiatement le solveur sur les 82 pertes positives

Gain possible, mais faible robustesse : la matrice actuelle ne couvre ni les
éléments plats, ni 95 %, ni les cardinalités demandées. Elle confond aussi
pertes de calcul et refus aval. Option refusée avant B et C.

### Construire un nouveau générateur produit et des vérités indépendantes

Coût de maintenance supérieur, mais seule option qui soit robuste, testable et
compatible avec un holdout fermé. Option retenue par ADR-0107.

## 13. Verdict et prochaine mission

P64-L09W-A est terminée.

Les causes dominantes observées sont :

1. perte de vérité historique sur toutes les réservations contraignantes ;
2. récupération très faible sur dense et presque saturé ;
3. beaucoup de `bounded_unknown` à la limite globale ;
4. 19 rejets immédiats de finalisation après calcul certifié ;
5. contrôles impossibles non exécutables sous la sémantique de rotation
   actuelle ;
6. matrice sans éléments plats reconstructibles et sans densité 95 %.

Aucune optimisation de recherche n’est sélectionnée sur cette seule baseline.

P64-L09W-B doit maintenant :

1. implémenter ADR-0107 ;
2. construire les positifs par témoin indépendant recertifié ;
3. reconstruire des contrôles impossibles compatibles avec la rotation
   produit ;
4. couvrir 30 %, 65 %, 85 %, 95 %, 64 conteneurs, 64 contenus, 0 à 10
   éléments plats et les éditions ;
5. créer discovery, tuning, régression et un holdout neuf sans l’ouvrir ;
6. conserver calcul, finalisation, CAD IR et matérialisation comme résultats
   distincts.

Preuve machine compacte :
`tests/fixtures/p64_l09w_a_solver_robustness_baseline.v1.json`.

Digest de cette preuve :
`f7be893292a64879cc752eba9b55902956a7479a9012610e0ffaa4d21101ec89`.

## 14. Validations

- gate CPython 3.14 + SCIP 10.0.2 : deux runs identiques ;
- tests ciblés de campagne, corpus et adaptateurs : verts ;
- suite autorisée complète : 1 044 tests passés, 1 skip prévu ;
- anciens manifests L05 à L08 : inchangés ;
- matérialisation Fusion et impression réelle : non exécutées en A.
