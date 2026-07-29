# Next Actions

<!-- P64-L09U-NEXT -->
## Action courante : P64-L09U-R8-G — candidate et nouvelle gate

0.1.78 est `human-KO`, `do-not-run`.

Le nouvel objectif n'est pas une réparation de rendu en aval. Il faut vérifier
puis imposer le pipeline produit suivant :

1. assembler les enveloppes minimales dans la boîte ;
2. finaliser les conteneurs pour remplir le volume disponible ;
3. appliquer les plateaux et livrets comme des coupes locales seulement ;
4. ne créer aucun volume positif, corps, plaque, rail ou support pour eux.

R8-A est terminée :

- projets personnels inchangés après replays en lecture seule ;
- première matière positive localisée dans la finalisation composite ;
- `125 019,76 mm³` ajoutés au-dessus des corps dits finaux sur
  `CasLimite02++` ;
- trois intervalles livret déplacés de `+4 mm` par le plan Fusion ;
- `31 209,20 mm³` du vide demandé non retiré par la BRep ;
- recherche, lanes, candidats, rejets, temps et mémoire profilés ;
- aucune modification de code produit.

R8-B est terminée :

- ADR-0105 retient le conteneur finalisé puis la passe uniquement soustractive ;
- la matière finale vaut
  `conteneurs finalisés - union des encastrements` ;
- tout volume, corps ou union positifs liés à un élément plat sont interdits ;
- le digest positif est figé avant la passe plate ;
- les intervalles métier, CAD IR, Fusion et BRep doivent être identiques ;
- aucun solveur, budget ou valeur physique ne change.

R8-C est terminée :

- `bgig.minimal_flat_geometry_certificate.v1` est publié et contrôlé ;
- les réservations restent non imprimables ;
- corps, unions, supports, coupes et volume positifs liés aux plats valent zéro ;
- une compensation Z positive est rejetée avec son volume exact ;
- le solveur et ses budgets restent inchangés sous une nouvelle identité ;
- validation ciblée `67/67`.

R8-D est terminée :

- `bgig.finalized_container_geometry.v1` et le composite v3 sont publiés ;
- `closure_*` et `final_*` ont des responsabilités distinctes ;
- les nouveaux corps ne publient plus aucun champ exécutable `cad_*` ;
- toute géométrie positive est attribuée à `container_finalization` ;
- le digest positif exclut les opérations soustractives ;
- corps, unions, opérations et volume positifs plats valent zéro ;
- la CAD IR refuse un certificat positif plat non nul ;
- validation ciblée `90/90`.

R8-E est terminée :

- extraire `bgig.flat_inset_subtraction_plan.v1` ;
- toutes les opérations plates sont des volumes négatifs `difference` ;
- les profondeurs locales `2/4/6 mm` sont certifiées ;
- le digest positif R8-D reste identique avant et après la passe ;
- corps, support, union, opération et volume positifs plats valent zéro ;
- CAD IR, plan Fusion et BRep partagent le même intervalle `[bottom, top]` ;
- validation ciblée `207/207`.

R8-F est terminée :

- faire de l’aperçu et du résultat lisible des projections du plan canonique ;
- aperçu, CAD IR, Fusion et BRep portent les mêmes opérations et intervalles ;
- la régression forcée prouve `2/4/6 mm` ;
- cavités, accès, parois, ordre, grille et rollback restent couverts ;
- `CasLimite02+` passe avec `20` opérations identiques de bout en bout ;
- `CasLimite02++` passe avec `23` opérations et `2/4/6 mm` ;
- les deux SHA personnels restent inchangés ;
- validation ciblée `302/302`.

R8-G est en cours :

- candidate 0.1.79, préflight et préparateur créés ;
- préparateur à blanc `153/153`, deux replays personnels en lecture seule ;
- préflight stable `ebd2d0b0...3f71`, compteurs positifs plats tous nuls ;
- exécuter exactement la suite autorisée en excluant avant import les douze
  modules nommés dans la preuve corrective ;
- figer le commit de candidate, intégrer et pousser `main` ;
- installer automatiquement l’add-in et ses réglages locaux ;
- livrer uniquement la recette humaine finale.

Preuves :

- `docs/P64_L09U_R7_V_0178_HUMAN_KO_EVIDENCE.md` ;
- `docs/P64_L09U_R8_A_SUBTRACTIVE_PIPELINE_DIAGNOSTIC_EVIDENCE.md` ;
- `docs/DECISIONS/ADR-0105-conteneurs-finalises-et-encastrements-strictement-soustractifs.md` ;
- `docs/P64_L09U_R8_B_SUBTRACTIVE_PIPELINE_DECISION_EVIDENCE.md` ;
- `docs/P64_L09U_R8_C_MINIMAL_SUBTRACTIVE_BOUNDARY_EVIDENCE.md` ;
- `docs/P64_L09U_R8_D_FINALIZED_CONTAINER_GEOMETRY_EVIDENCE.md` ;
- `docs/P64_L09U_R8_E_SUBTRACTIVE_FLAT_INSET_PLAN_EVIDENCE.md` ;
- `docs/P64_L09U_R8_F_END_TO_END_FIDELITY_EVIDENCE.md` ;
- `docs/P64_L09U_R8_0179_CORRECTIVE_EVIDENCE.md`.

Hand-off :
`docs/P64_L09U_R8_SUBTRACTIVE_FLAT_INSETS_HANDOFF.md`.

Aucun benchmark/holdout/corpus/tournoi. Les projets personnels restent en
lecture seule. `fusion-validated=false`, `print-validated=false`.

### Historique R7 clôturé en human-KO

## Action courante : P64-L09U-R7-F — validation et candidate

0.1.77 est `human-KO`, `do-not-run`. Sa correction de profondeur est confirmée
et doit être conservée, mais le placement automatique, les parois finales et
l'ordre de pile restent faux.

R7-A est terminé :

1. verdict humain consigné fidèlement ;
2. `CasLimite02+` et `CasLimite02++` rejoués en lecture seule ;
3. première divergence localisée dans le plan minimal des réservations ;
4. micro-coupes `0,5 mm × ... × 6 mm` retrouvées avant Fusion ;
5. absence de quantification produit complète démontrée.

R7-B est terminé :

- ADR-0103 : contraintes dures, score lexicographique, ordre automatique et
  migration de `stack_order` ;
- ADR-0104 : ticks `0,1 mm`, arrondis conservateurs, digests et migrations ;
- contrat automatique testable du minimum au plan Fusion.

R7-C1 est terminé :

- ticks `0,1 mm` et arrondis conservateurs ;
- candidats, empreintes et prises automatiques quantifiés ;
- `74` ancres admissibles fusionnées sur le replay, mais `2450` poses toujours
  évaluées ;
- aucun gain de temps revendiqué.

R7-C2 est terminé :

- marge canonique dure au bord de boîte et entre zones plates disjointes ;
- score couverture/recouvrement/centrage utile ;
- `62/62` tests ciblés ;
- deux replays personnels exacts et SHA inchangés.

R7-C3 est terminé :

- jeu de boîte puis paroi minimale certifiés ;
- fragments et composantes de coupe sous `1,2 mm` refusés ;
- aucun déplacement silencieux en finalisation ;
- `66/66`, deux SHA personnels inchangés ;
- zéro micro-prisme et zéro micro-coupe sur les deux replays.

R7-D est terminé :

- petit élément sous le grand selon l'empreinte orientée ;
- ordre historique tracé puis surchargé explicitement ;
- intervalles Z exacts propagés jusqu'au plan Fusion ;
- zéro volume additif résiduel au-dessus des corps finaux ;
- `75/75`, deux SHA personnels inchangés.

R7-E est terminé :

- zéro longueur effective hors grille sur les deux replays ;
- migration source/effectif sans écriture ;
- digest fonctionnel en ticks et finaliseur v13 ;
- aucun gain de performance revendiqué ;
- `77/77`, deux SHA personnels inchangés.

R7-E2 et la validation complète sont terminés :

- allocation volumétrique et surplus d'enveloppe en ticks entiers ;
- migration P66 `79,0667 -> 79,1 mm` sans écrire le projet source ;
- `120/120` tests ciblés élargis ;
- `926/926` tests autorisés, un test ignoré ;
- douze modules benchmark/corpus/tournoi exclus avant import ;
- audits `5 453/5 453` et `5 888/5 888` sur la grille ;
- deux SHA personnels inchangés.

Candidate 0.1.78 préparée :

- matrice release `59/59`, un test ignoré ;
- préparateur à blanc `84/84` ;
- préflight
  `30ea1b1055d7eec38b6824cb7e575f86e6e1557aa9a43abfe705fa8af802f59f`.

Candidate 0.1.78 installée et vérifiée depuis `35b17d7`. Suite autorisée finale :
`928/928`, un test ignoré.

Gate R7-V close en `human-KO`; cette section est historique.

Contrat : `docs/P64_L09U_R7_END_TO_END_RUNBOOK.md`.
Preuve : `docs/P64_L09U_R6_V_0177_HUMAN_KO_EVIDENCE.md`.
Décisions : ADR-0103 et ADR-0104.
Preuve C1 : `docs/P64_L09U_R7_C1_PRODUCT_GRID_CANDIDATES_EVIDENCE.md`.
Preuve C2 :
`docs/P64_L09U_R7_C2_CANONICAL_WALLS_AND_SCORE_EVIDENCE.md`.
Preuve C3 :
`docs/P64_L09U_R7_C3_FINAL_MATERIAL_RECERTIFICATION_EVIDENCE.md`.
Preuve D :
`docs/P64_L09U_R7_D_AUTOMATIC_STACK_AND_MATERIALIZATION_EVIDENCE.md`.
Preuve E :
`docs/P64_L09U_R7_E_PRODUCT_GRID_AND_MIGRATION_EVIDENCE.md`.
Preuve E2 :
`docs/P64_L09U_R7_E2_FULL_LAYOUT_GRID_EVIDENCE.md`.
Preuve candidate :
`docs/P64_L09U_R7_0178_CORRECTIVE_EVIDENCE.md`.
Recette :
`docs/P64_L09U_R7_V_0178_FUSION_GATE_RECIPE.md`.

Aucun benchmark/holdout/corpus/tournoi. Les projets personnels restent en
lecture seule. `fusion-validated=false`, `print-validated=false`.

### Historique R6 clôturé en human-KO

## Action courante : exécuter la gate P64-L09U-R6-V

0.1.76 est `human-KO`, `do-not-run`. Les accès R5 restent acquis, mais une
micro-partie de cavité perd `6 mm` et deux éléments plats de tailles différentes
ne gardent pas leurs deux encastrements locaux.

La candidate 0.1.77 est automatisée-validée, intégrée et installée depuis le
commit `e81737d`. Thomas suit maintenant uniquement la recette R6-V.

Contrat :
`docs/P64_L09U_R6_END_TO_END_RUNBOOK.md`.

Preuve :
`docs/P64_L09U_R6_0177_CORRECTIVE_EVIDENCE.md`.

Recette :
`docs/P64_L09U_R6_V_0177_FUSION_GATE_RECIPE.md`.

Aucun benchmark/holdout/corpus/tournoi. Les projets personnels restent en
lecture seule. `fusion-validated=false`, `print-validated=false`.

### Historique R2 clôturé en human-KO

#### Ancienne action : exécuter la gate P64-L09U-R2-V

0.1.72 est `human-KO`, `do-not-run`. Son calcul et sa finalisation pouvaient
réussir, mais la matérialisation finale n'était ni fidèle ni robuste.

0.1.73 :

1. finalise exactement le plan minimal affiché ;
2. projette dans l'aperçu les vrais prismes composites et cavités gelées ;
3. ferme les résiduels sans consommer les jeux externes XY/Z ;
4. résout l'insertion tardive d'un support large dans `CasLimite01++` ;
5. remplace les Combine rectangulaires par un corps transitoire unique par
   module, persisté une seule fois ;
6. conserve le rollback et rend la main à l'interface entre les modules.

La suite globale est passée, 0.1.73 est intégrée dans `origin/main`, puis le
package du commit `b5fb15b` a été installé et vérifié. Thomas suit maintenant
uniquement
`docs/P64_L09U_R2_V_0173_FUSION_GATE_RECIPE.md`.

Preflight source :
`e8392bc12c69074e654d1d9cecf99656df5fe9ac187eb17d1b981a713584b6fd`.

`fusion-validated=false`, `print-validated=false`.

Après le verdict R2, le prochain programme proposé reste strictement
séquentiel : jobs coopératifs et annulation, choix visuel des variantes, puis
épaisseur distincte de séparateur après gate physique.

### Historique R1 supersédé

#### Ancienne action : gate humaine P64-L09U-R1-V

0.1.71 est `human-KO` et `do-not-run`. Le démarrage vierge, le calcul et la
finalisation restent acquis, mais les corps sources d'une BaseFeature étaient
réutilisés après `finishEdit`, ce qui provoquait
`ALL_TOOL_BODY_REFERENCE_LOST`.

0.1.72 :

1. utilise uniquement les corps résultats de la BaseFeature ;
2. vérifie leur nombre avant Combine ;
3. supprime toute scène BGIG partielle après une erreur ;
4. conserve les six replays exacts en lecture seule ;
5. ne change aucune cavité, réservation ou valeur physique.

Thomas suit uniquement
`docs/P64_L09U_R1_V_FUSION_GATE_RECIPE.md`. Il vérifie d'abord l'absence de
corps outils et le rollback, puis matérialise les plans minimal et final des
cas « + ».

Preflight source :
`b3f8c6cfc183c4a929516d46d44e03e4cbb22cafd6f2c1f9a35a958cc80e555b`.

`fusion-validated=false`, `print-validated=false`.

Après le verdict R1, le prochain programme proposé est strictement séquentiel :

1. jobs coopératifs, progression Fusion par lots et vraie annulation ;
2. miniatures vues du dessus et allowlist de variantes locales certifiées ;
3. épaisseur distincte de séparateur d'assets après choix humain du défaut
   physique.

<!-- P64-L09T-NEXT -->
## Action courante : executer la gate humaine P64-L09T-V

Thomas a accepte ADR-0093 et autorise l'execution autonome sequentielle du
programme P64-L09T :

1. P64-L09T-A : `done`, automatisee-validee et integree ;
2. P64-L09T-B : `done`, diagnostics d'arret structures et UI explicable ;
3. P64-L09T-C : `done`, poses automatiques, migration et parois certifiees ;
4. P64-L09T-D : `done`, classement lexicographique plancher d'abord ;
5. P64-L09T-E : `done`, fermeture hybride v2 automatisee-validee ;
6. P64-L09T-F : `done`, certificat composite et CAD fidele ;
7. P64-L09T-G : `done`, durcissement, candidate 0.1.70, replays et preflight ;
8. P64-L09T-V : action courante, observation Fusion humaine.

Thomas suit uniquement `docs/P64_L09T_V_FUSION_GATE_RECIPE.md`. Aucun nouveau
developpement, benchmark, holdout, changement de valeur physique ou famille
P64-F03 ne commence avant son verdict.

Le package `0.1.69` est `human-KO`, `do-not-run`.
`fusion-validated=false`, `print-validated=false`.

Preuve A : `docs/P64_L09T_A_EXPLICIT_RECALCULATION_EVIDENCE.md`.
Validation A : `912/912`, un test SCIP natif ignore sous Python 3.10, aucun
benchmark/holdout solveur invoque.

Preuve B :
`docs/P64_L09T_B_EXPLAINABLE_FINALIZATION_STOPS_EVIDENCE.md`.
Validation B ciblee : `99/99` et syntaxe JavaScript `node --check` verte.
Suite complete : `922/922` en `299.3 s`, un test SCIP natif ignore sous
Python 3.10, aucun benchmark ou holdout solveur invoque.

Preuve C :
`docs/P64_L09T_C_AUTOMATIC_TOP_RESERVATIONS_EVIDENCE.md`.
Validation C : `135/135`, `17/17`, `47/47`, syntaxe JavaScript
`node --check` verte, puis gate globale autorisee `859/859` en `282.881 s`.
Les onze modules benchmark/corpus/tournoi restent exclus conformement au
contrat du Goal.

Preuve D : `docs/P64_L09T_D_FLOOR_FIRST_RANKING_EVIDENCE.md`.
Validation D : `107/107` tests cibles, `19/19` pour la lane SCIP avec une
integration native ignoree, puis gate globale autorisee `863/863` en
`286.898 s`. Les onze modules benchmark/corpus/tournoi restent exclus.

Preuve E : `docs/P64_L09T_E_HYBRID_COMPOSITE_CLOSURE_EVIDENCE.md`.
Validation E : `45/45` tests cibles, regression produit `1/1`, puis gate
globale autorisee `860/860` en `280.807 s`, avec une integration SCIP native
ignoree. Douze modules benchmark/corpus/tournoi sont exclus a partir de E :
l'adaptateur benchmark lie a l'identite v9 n'est pas regenere pendant le Goal.

Preuve F : `docs/P64_L09T_F_COMPOSITE_CAD_EVIDENCE.md`.
Validation F : `157/157` tests cibles, puis gate globale autorisee `866/866`
en `285.542 s`, avec une integration SCIP native ignoree. Les douze modules
interdits restent exclus. La fermeture hybride v2 est maintenant la geometrie
produit et CAD ; aucune installation Fusion n'a lieu avant G.

Preuve G : `docs/P64_L09T_G_RELEASE_GATE_EVIDENCE.md`.
Validation G : `158/158` tests cibles, six replays locaux exacts en lecture
seule, puis gate globale autorisee `873/873` en `374.311 s`, avec une
integration SCIP native ignoree. Candidate `0.1.70`, preflight
`f78017e31ff18ad81d0a2aef6e9e1e7d52e624372779f56482ad472ec069fa65`.
Statut : `prepared-not-human-observed`, `fusion-validated=false`,
`print-validated=false`.

<!-- P64-L09S-0168-NEXT -->
## Action courante : cloture corrective et gate P64-L09S-V

Codex termine la validation autorisee, integre `0.1.68`, installe le package et prepare la gate. Thomas observe ensuite le parcours complet sur `CasLimite01` avec un puis plusieurs plateaux et sur `CasLimite02` avec deux plateaux. Aucun nouveau GO Git n est requis. Aucun benchmark, holdout ou corpus. La gate reste humaine et `print-validated=false`.

<!-- P64-L09S-F -->
## Action courante : P64-L09S-V

P64-L09S-F est automatisee-validee et la preparation locale est confirmee : package 0.1.67, marqueur `12c9f93`, fixture recente et preflight digest `c590501d8199ed5463655c391757cf8e2e4f3ba7c06ed018a1d1f70b733ec308`. Thomas execute uniquement la recette humaine V. Aucun nouveau developpement, benchmark, holdout ou changement d'architecture avant le verdict `OK` ou `KO`.


<!-- P64-L09S-E -->
## Action courante : P64-L09S-F

P64-L09S-E est terminee. Durcir maintenant le parcours complet calcul minimal, finalisation composite, selection de l'artefact final et preparation de materialisation. Verifier les erreurs fail-closed, les identites courantes, les preuves du cas limite recent et preparer la gate Fusion V sans lancer de benchmark/holdout. L'installation Fusion n'intervient qu'en fin de F pour preparer V.


<!-- P64-L09S-D -->
## Action courante : P64-L09S-E

P64-L09S-D est terminee. Implementer maintenant la traduction fidele de chaque proprietaire composite dans le CAD IR : unir coeur et annexes en un seul composant utilisateur, puis appliquer les encoches plateau/livret uniquement aux corps finaux qui atteignent leur plan et chevauchent leur empreinte. Recertifier le plan courant avant toute publication finale.


## Prochaine mission autoritaire - P64-L09S-D

P64-L09S-A, B et C sont terminees et integrees mission par mission.

- P64-L09S-D : couvrir les partitions non tranchables par annexes XY soudees bornees.
- Proprietaire unique, vraie face verticale X ou Y, bas Z commun et corps connexe obligatoires.
- Aucune liaison Z seule, arete seule ou point seul.
- Aucun benchmark ou holdout. Aucune installation Fusion avant V.

## Prochaine mission autoritaire - P64-L09S-C

P64-L09S-A et B sont terminees et integrees mission par mission.

- P64-L09S-C : construire une fermeture rectangulaire globale, complete et equilibree de tout le volume imprimable.
- Une reussite doit publier un `finalized_plan` courant et recertifie.
- Aucun benchmark ou holdout. Aucune installation Fusion avant V.

## Prochaine mission autoritaire - P64-L09S-B

P64-L09S-A est terminee. Toute mention plus bas indiquant un Goal non lance est un historique de preparation.

- P64-L09S-B : verite du cycle, budgets reactifs et couleurs.
- Aucun nouveau GO requis.
- Aucun benchmark ou holdout. Aucune installation Fusion avant V.

Dernière mise à jour : 2026-07-25

## Version active

**Décision autoritaire du 2026-07-25 :** P64-L09R-V 0.1.65 est un KO humain.
ADR-0088 reste acquise pour le support par enveloppe, les budgets, la séparation
calcul/finition et le cycle UI, mais sa compensation Z et sa stratégie de
fermeture sont remises en cause par les faits Fusion.

ADR-0089 est proposée. Elle sera acceptée uniquement lorsque Thomas lancera le
Goal P64-L09S préparé. Avant ce lancement, aucun runtime ne change.

V0.1 reste `mvp-accepted` et `fusion-validated: true` pour son périmètre
historique. P64-L08L reste `fusion-validated` pour la correction de
performance observée en environ 25 s puis 34 s dans Fusion 0.1.62. Aucun fait
récent ne vaut validation d'impression ; `print-validated=false`.

## Acquis runtime historiques conservés

- une édition continue de recalculer uniquement ses dérivations locales ;
- une insertion interne admissible peut republier un `minimal_layout` courant
  sans solve global ni déplacement monde ;
- exactement un nouveau conteneur peut aussi être inséré à voisins figés si le
  certificat global accepte le plan complet ;
- le fallback global reste explicite et aucune scène n’est modifiée
  automatiquement ;
- Rapide reste préfixe de Normal, Normal devient le préfixe et l’incumbent
  d’Approfondi ;
- les six lanes Normal gardent leurs caps historiques ;
- seules les trois lanes supplémentaires Deep partagent ensuite une deadline de
  30 000 ms ;
- une expiration Deep conserve l’incumbent certifié et ne le transforme plus en
  `no_solution_within_budget` ;
- sans incumbent, l’échec reste honnête ; une annulation stale reste
  `stale_or_cancelled` ;
- budgets, temps, lanes, phases, incumbent et raison d’arrêt sont observables ;
- analyse, calcul, finalisation et matérialisation exposent désormais identité,
  étape et temps écoulé sans pourcentage ni ETA inventés ;
- un second lancement du même type est bloqué ; aucune annulation décorative
  n'est exposée ;
- un journal local automatique conserve clics, changements, demandes, résultats et états dédupliqués sans bouton spécial, sans solve supplémentaire, finalisation, CAD ou scène ;
- un witness certifie persistant est recertifie comme incumbent sans ajouter de lane, court-circuiter la recherche ou revendiquer un cache hit ;
- HiGHS est une lane expérimentale de sol, désormais retirée du parcours Auto
  après P64-L08B ; elle n'est pas un moteur de solvage 3D global ;
- le cas dense 11 × 34 ne reçoit aucune nouvelle revendication.

Preuves :
`docs/P64_L04A_INCREMENTAL_LOCAL_REUSE_EVIDENCE.md` et
[P64-L04B](P64_L04B_DEEP_ANYTIME_EVIDENCE.md) et
[P64-L04C](P64_L04C_OPERATION_ACTIVITY_EVIDENCE.md).

Preuve L05A : P64_L05A_GLOBAL_VOID_CONTAINER_REUSE_EVIDENCE.md.
Preuve L05B : P64_L05B_SOLVER_CASE_BUNDLE_EVIDENCE.md.
Preuve L05C : P64_L05C_CERTIFIED_PLAN_WITNESS_EVIDENCE.md.
Preuve L05D1 : P64_L05D1_SOLVER_CORPUS_EVIDENCE.md.
Preuve L06B : P64_L06B_BENCHMARK_CORPUS_EVIDENCE.md.
Preuve L06C : P64_L06C_OFFLINE_ADAPTER_AND_EXACT_ORACLE_EVIDENCE.md.
Preuve L06D : P64_L06D_PROGRESSIVE_CAMPAIGN_EVIDENCE.md.
Preuve L06E : P64_L06E_ALGORITHM_DECISION_EVIDENCE.md.
Rapport final : P64_L06_GOAL_FINAL_REPORT.md.
Preuve L07A : P64_L07A_EXTERNAL_SOLVER_AUDIT_EVIDENCE.md.
Preuve L07B : P64_L07B_CORPUS_V2_EVIDENCE.md.
Contrat L07C : P64_L07C_EXTERNAL_ADAPTERS_CONTRACT.md.
Preuve L07C : P64_L07C_EXTERNAL_ADAPTERS_EVIDENCE.md.
Preuve L07D : P64_L07D_EXTERNAL_TOURNAMENT_EVIDENCE.md.
Preuve L07E : P64_L07E_HIGHS_PRODUCT_INTEGRATION_EVIDENCE.md.
Preuve L08D : P64_L08D_REAL_3D_CORPUS_EVIDENCE.md.
Preuve L08E : P64_L08E_FAITHFUL_3D_ADAPTERS_EVIDENCE.md.
Preuve L08F : P64_L08F_REAL_3D_TOURNAMENT_EVIDENCE.md.
Preuve L08G : P64_L08G_SCIP_PRODUCT_GATE_EVIDENCE.md.
Preuve L08H : P64_L08H_SCIP_PACKAGE_REMEDIATION_EVIDENCE.md.
Preuve L08I : P64_L08I_MINIMAL_SCIP_RUNTIME_AUDIT_EVIDENCE.md.
Preuve L08J : P64_L08J_MINIMAL_SCIP_RUNTIME_BUILD_EVIDENCE.md.
Rapport final L08 : P64_L08_GOAL_FINAL_REPORT.md.
Preuve L09B : P64_L09B_MATERIAL_SUPPORT_EVIDENCE.md.
Preuve L09C : P64_L09C_SCIP_TOP_INSET_EVIDENCE.md.
Preuve L09R-B : P64_L09R_B_MINIMAL_CALCULATION_EVIDENCE.md.
Matrice L09 : P64_L09_VALIDATION_UNIFIEE.md.
Rapport final L07 : P64_L07_GOAL_FINAL_REPORT.md.

## Gate P64-L09R-V clôturée en KO

La 0.1.65 corrige le rafraîchissement du budget et retrouve un plan, mais ce plan
n'est pas minimal au sens produit : un conteneur 23,2 × 23,2 mm est allongé de
6,8 mm pour soutenir seulement 0,75 % du plateau. La finition conserve ensuite
775 266,384 mm³ de résiduel, ne publie aucun plan final et produit pourtant un
message et un stop reason de succès.

Preuve : `docs/P64_L09R_V_0165_HUMAN_KO_EVIDENCE.md`.

P64-L09R-V est `human-KO`, non acceptée et ne doit pas être rejouée avec
l'architecture 0.1.65. Le correctif UI de budget reste acquis.

## Préparation P64-L09S-P terminée

ADR-0089 propose la trajectoire hybride suivante :

1. SCIP conserve le calcul minimal 3D complexe ;
2. plateaux et livrets sont des réservations sans conteneur porteur artificiel ;
3. la finition construit une partition globale complète et équilibrée ;
4. des annexes XY soudées sont admises seulement en repli borné ;
5. le CAD IR et Fusion unissent chaque annexe à son propriétaire ;
6. l'interface ne déclare un succès qu'avec un plan final certifié.

Le principe historique de partition complète est repris sans restaurer le
solveur 2D par lignes. Le Goal est préparé par
`docs/P64_L09S_END_TO_END_GOAL_RUNBOOK.md`, mais il n'est ni créé ni lancé dans
cette mission documentaire.

## Prochaine action recommandée

### P64-L09S — lancement humain du Goal de stabilisation de bout en bout

Type : lancement explicite par Thomas, `ready-for-user-goal-launch`.

1. Thomas lance lui-même le Goal dans le clavardage de reprise.
2. Ce lancement accepte ADR-0089 et son périmètre composite borné.
3. Le Goal exécute une seule mission à la fois, A à F, avec tests, documentation,
   commit et intégration directe dans `main`.
4. Aucun nouveau GO humain n'est requis entre A et F.
5. P64-L09S-V reste la gate Fusion humaine obligatoire.

Avant ce lancement, le successeur reste en lecture seule : aucun code,
benchmark, package Fusion, installation ou mutation de projet.

## Programme ordonné après lancement

1. P64-L09S-A — plan minimal sans support ou compensation Z artificiels ;
2. P64-L09S-B — vérité du résultat, budgets réactifs et trois boutons colorés ;
3. P64-L09S-C — fermeture rectangulaire globale complète et équilibrée ;
4. P64-L09S-D — annexes XY composites bornées et certificat de connexité ;
5. P64-L09S-E — CAD IR, unions et encoches exactes de plateaux/livrets ;
6. P64-L09S-F — durcissement de bout en bout et préparation de gate ;
7. P64-L09S-V — observation Fusion humaine, sans validation d'impression.

## Lots verrouillés ou différés

- P64-U01 est absorbée par P64-L09R-D/E ;
- P64-L09B reste une preuve historique, mais sa règle anti-chute dure est
  remplacée par ADR-0088 ;
- P64-F01B/F02B restent des preuves historiques et des briques réutilisables, mais leur fermeture gloutonne n’est plus l’autorité de succès ;
- P64-C01/C02/C03 et P64-CV restent post-finalisation et verrouillés ;
- la modularité générale P64-F02, le résiduel/cales P64-F03 et P64-X01 restent différés ; seule l’annexe XY bornée d’ADR-0089 entre dans P64-L09S-D ;
- P45 conserve formes, intentions et certificat local ; son runtime n'est pas
  commencé ;
- P46, P47-P50 et P69 restent bloqués par l'ordre V0.2/V0.3 ;
- P68 reste disponible pour recueillir des faits réels sans recalibrage ;
- P70+ et les horizons produit restent différés jusqu'à la revue P69 ;
- aucune nouvelle valeur physique, pose de couvercle ou validation d'impression
  n'est implicite.

## Dette de pilotage historique à réconcilier

Ces anciennes cartes apparaissent encore ouvertes dans les phases historiques,
mais ne sont pas `ready` devant P64-L09R. Elles devront être réévaluées contre
les acquis plus récents avant toute activation :

- P0-M006 et P14-M002 — nomenclature puis processus de release stable ;
- P6-M003 — taxonomie d'aides de prise, probablement en partie couverte par
  ADR-0015 et les contrats ultérieurs ;
- P8-M003 — support abstrait, largement dépassé par les certificats P64 ;
- P11-C001 — vrais modules composites et primitives soudées ;
- P12-M001 — modèle abstrait de couvercle posé, à réconcilier avec P47-P50 et
  `F-CLOSED-CONTAINER-POSE` ;
- P13-M001/M002 — langage visuel, labels et gravure ;
- P14-M001 — exemple réel complet avec impression.

Leur présence conserve la vision, mais ne contourne ni L09R, ni l'ordre
P45/P46/P47-P50/P69, ni leurs gates humaines.
## Fin de chaque mission

Mettre à jour le pilotage, relire le diff, exécuter les preuves, committer puis
intégrer directement dans `main` lorsqu’aucune vraie gate humaine n’est active.
Une gate Fusion ne vaut jamais impression.

## Repères historiques conservés

- `P44-M009H05 Fusion OK 0.1.36 - commit 7c76ba0` ;
- P44-M007 a livré le package `0.1.37` ;
- `P64-H01 Fusion OK 0.1.42 - commit 5865645` ;
- P44-VH02 reste un retour contextuel supersédé, sans promotion
  `fusion-validated` ;
- `P64-V2H03V Fusion OK 0.1.55` ;
- `P44-V Fusion OK 0.1.55 - commit 70d45c6`.

## Mise a jour P64-L04V preparation (2026-07-22)

Le preparateur versionne scripts/fusion/prepare_p64_l04v_gate.ps1, le fixture portable et la checklist sont prets. Executer le preparateur depuis le commit integre, puis collecter le retour humain defini par docs/P64_L04V_FUSION_GATE_CHECKLIST.md.
Aucune promotion fusion-validated ne precede cette observation ; print-validated: false.

## Mise à jour après P64-L04R1 (2026-07-22)

P64-L04R1 est automated-validated : un échec ne satisfait plus une nouvelle
action explicite et seuls les plans certifiés sont réutilisés. La palette
distingue calcul frais, recherche initiale et restitution cache.

Prochaine mission unique : P64-L05A, insertion d'un nouveau conteneur dans le
vide global d'un plan minimal certifié avec voisins figés et recertification
complète. Le lot doit commencer par une ADR, car ADR-0075 exclut actuellement ce
comportement. L05B/L05C/L05D restent ensuite autorisés et ordonnés. Aucune gate
Fusion ni impression n'est revendiquée par R1.

## Mise à jour après P64-L05A (2026-07-22)

P64-L05A est automated-validated. Le producteur fixe tous les voisins, teste des
positions de contact contre les placements réels et rejoue le certificat global
commun. Il n’utilise pas les zones résiduelles affichées comme preuve et
n’appelle pas le portefeuille global.

Prochaine mission unique : P64-L05B, capture locale et versionnée d’un
SolverCaseBundle depuis un bouton DEV explicite. L05C puis L05D restent ordonnés.
Aucune validation Fusion ou impression n’est revendiquée.


## Mise a jour apres P64-L05B (2026-07-22)

P64-L05B est automated-validated. Un bouton DEV rouge produit localement un
SolverCaseBundle v1 reproductible avec etat staged observe, frontieres P45,
reglages, provenance, trace semantique filtree et identite de scene. La capture
ne declenche aucune operation de domaine et ne modifie pas le solveur.

Prochaine mission unique : P64-L05C, plan temoin certifie persistant et warm
start fail-closed. L05D reste ensuite ordonnee. Aucune validation Fusion ou
impression n'est revendiquee.

## Mise a jour apres P64-L05C (2026-07-22)

P64-L05C est automated-validated. Un sidecar exact conserve le meilleur plan
certifie par identite projet + frontieres P45. Il est recertifie comme incumbent,
les lanes courantes continuent et Deep garde son prefixe Normal historique. Un
fichier incompatible ou corrompu est rejete puis remplace apres un solve certifie.

Prochaine mission unique : P64-L05D, corpus versionne, replay borne, baseline et
optimisation mesuree des lanes. Aucune validation Fusion ou impression n'est
revendiquee.

## Mise a jour apres P64-L05D1 (2026-07-22)

P64-L05D1 est automated-validated. Le corpus versionne contient cinq cas CI et
deux extended ; les rapports separent preuves fonctionnelles et temps mur. La
gate A/B refuse une perte de solution, de certificat, de qualite ou de contrat
de lanes avant toute comparaison de vitesse.

Prochaine mission unique : P64-L05D2, premiere optimisation interne bornee et
mesuree. Aucune validation Fusion ou impression n'est revendiquee.

## Mise a jour apres P64-L05D2 (2026-07-22)

P64-L05D2 est automated-validated. Sous ordre explicite, les participants qui ne
peuvent plus entrer dans le quota de branches ne sont plus evalues. Le corpus
complet mesure 57 329 -> 31 901 essais, sans regression fonctionnelle, mais le
projet personnel reste sans solution.

Prochaine mission unique : P64-L05V-A, preparation puis installation de la gate
Fusion de capture reelle. La revue dans Fusion reste humaine.

## Mise a jour apres P64-L05V-A (2026-07-22)

P64-L05V-A est automated-validated et installe localement : add-in 0.1.58,
commit 261f7cc, runtime L05 et fixture sont verifies. P64-L05V devient la
prochaine action, exclusivement humaine dans Fusion.

## Retour P64-L05V - ne pas confondre smoke et capacite (2026-07-22)

Le retour Fusion est positif pour l insertion dans le vide global de la fixture, la premiere persistance atomique du witness et l absence de cache revendique. La fixture est volontairement simple : elle ne mesure pas la profondeur de recherche et ne valide pas la reconstruction de `Mon insert.bgig.json`.

La prochaine action unique est humaine et courte : produire un SolverCaseBundle DEV representatif du projet complexe apres une manipulation reelle, puis fournir son chemin et son digest. En parallele, recharger le witness sur le meme projet pour observer un warm start accepte. Aucun bundle personnel n entre dans le depot avant anonymisation et revue.

La prochaine mission de code, non demarree, sera P64-L06A : anonymiser, rejouer et classifier ce premier cas reel avant de proposer une amelioration ciblee du solveur. Aucune promesse de capacite ou de vitesse n est faite avant cette preuve.

## Apres P64-L05V-R1 - recapture fidele du cas reel (2026-07-23)

Les trois bundles reels sont valides et prouvent le delta exact puis l echec global, mais le clic DEV 0.1.58 ecrasait la raison du refus incremental avant l export. R1 corrige cette instrumentation sans modifier le solveur.

Historique : cette recapture manuelle était l action demandée avant ADR-0080. Elle est maintenant remplacée par le journal automatique local.

P64-L06A est désormais prête : elle inventorie les cas réels et les journaux, puis lance le benchmark sans attendre une nouvelle manipulation humaine.

### Installation P64-L05V-R1 terminee

Historique : le commit e817432 avait été installé dans Fusion 0.1.58. La manipulation manuelle alors demandée est annulée par ADR-0080 et remplacée par le journal automatique 0.1.59.

## Cadrage de la suite P64-L06 (2026-07-23)

Le programme de benchmark et le registre des horizons produit sont désormais
documentés. Ils n'écrasent pas la prochaine action unique :

1. inventorier les cas réels et les journaux locaux ;
2. exécuter P64-L06A en lecture contrôlée : anonymisation, replay et
   classification, sans changement de solveur ;
3. seulement ensuite ouvrir L06B/L06C pour les oracles, générateurs et
   comparateurs offline ;
4. lancer une campagne autonome L06D avant de sélectionner une seule
   amélioration L06E.

Les formes complexes, couvercles avancés, couleurs, aperçu 3D et compositeur
manuel restent des horizons différés. Ils ne sont pas injectés dans le benchmark
rectangulaire T0/T1.

## Préparation P64-L06P — Goal autonome

Le paquet de reprise fixe la matrice P45/P64, les splits regression/discovery/
tuning/holdout, un oracle exact interne sans dépendance, le tournoi progressif,
les budgets, la pause sûre et les arrêts. Le premier Goal intègre au maximum une
amélioration validée ; il peut conclure sans diff si aucune hypothèse ne passe.

Cette préparation est `done-documentation`. ADR-0080 lève ensuite la gate R1 sans changer le solveur ni les règles du benchmark.

<!-- P64-L09S-0167-NEXT -->
## Prochaine action canonique corrective

1. Suite automatisee autorisee terminee : `833/833`, sans benchmark, holdout ni corpus.
2. Correctif integre dans `main` au commit `832c9d5`.
3. Package Fusion `0.1.67` prepare et installe ; marqueurs locaux verifies.
4. Arreter l'autonomie a la gate humaine P64-L09S-V et faire rejouer le cas complexe recent par Thomas.
5. Ne declarer `fusion-validated` qu'apres observation humaine conforme ; conserver `print-validated=false`.

<!-- P64-L09S-0169-NEXT -->
## Historique clos P64-L09S-V 0.1.69

1. Ne plus executer le package `0.1.69` : `human-KO`, `do-not-run`.
2. Conserver ses acquis partiels et la preuve
   `docs/P64_L09S_V_0169_HUMAN_KO_EVIDENCE.md`.
3. Suivre uniquement l'action courante P64-L09T en tete de ce document.
4. Conserver `fusion-validated=false`, `print-validated=false`.
