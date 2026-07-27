# Pilotage courant

<!-- P64-L09U-CURRENT -->
## Reprise canonique P64-L09U-R3

- `0.1.73` est `human-KO`, `do-not-run` pour une utilisation finale.
- Acquis humains à préserver : calcul rapide, finalisation utilisable,
  matérialisation en quelques secondes, progressive, réactive et fidèle à
  l'aperçu, sans `ALL_TOOL_BODY_REFERENCE_LOST`.
- Défaut bloquant 1 : une cavité attendue à `10,6 mm` mesure `18,2 mm` après
  finalisation. Le corps gagne de la hauteur et la cavité est allongée au lieu
  de conserver son calibre et de résoudre son origine Z finale.
- Défaut bloquant 2 : les deux plateaux différents de `CasLimite02+` produisent
  un encastrement apparemment global et cumulé au lieu de découpes locales et
  étagées par empreinte.
- Défaut complémentaire : une variante locale non sauvegardée a affiché environ
  `24 s` pour un plafond annoncé à `20 s`.
- ADR-0099 fige dimensions, X/Y, orientation et identité de la cavité, mais
  impose une résolution Z finale déterministe : ouverte au sommet hors
  réservation, ou sous la découpe locale avec paroi canonique.
- P64-L09U-R3 corrige ces trois points sans modifier le nouveau chemin BRep
  transitoire, le rendu progressif, le rollback ni la session vierge.
- Cible initiale : `0.1.74`.
- Prochaine action unique : exécuter
  `docs/P64_L09U_R3_END_TO_END_RUNBOOK.md`, puis préparer une nouvelle gate
  humaine.
- Aucun benchmark/holdout ; projets personnels en lecture seule ;
  `fusion-validated=false`, `print-validated=false`.

Autorités R3 :

- `docs/P64_L09U_R2_V_0173_HUMAN_KO_EVIDENCE.md` ;
- `docs/DECISIONS/ADR-0099-profondeur-calibree-et-reservations-superieures-locales.md` ;
- `docs/P64_L09U_R3_END_TO_END_RUNBOOK.md`.

### Historique R2 clôturé en human-KO

#### Reprise canonique P64-L09U-R2

- `0.1.70`, `0.1.71` et `0.1.72` sont `human-KO`, `do-not-run`.
- 0.1.72 confirme le démarrage vierge, le calcul explicite et une
  matérialisation minimale possible, mais pas la fidélité ni la robustesse du
  plan final.
- Les faits humains bloquants sont : aperçu final différent de Fusion, cavités
  hautes apparemment agrandies ou approfondies, fermeture sans plateau arrêtée
  avant budget, `CasLimite01++` non résolu, matérialisation très longue et
  `Combine1 / ALL_TOOL_BODY_REFERENCE_LOST`.
- R2 finalise uniquement le plan minimal sélectionné. Aucun candidat minimal
  alternatif n'est substitué silencieusement.
- L'aperçu composite projette les vrais prismes CAD et les poses monde exactes
  des cavités gelées ; les accès verticaux restent visuellement distincts.
- La fermeture attribue toutes les cellules couvertes, distingue les jeux
  externes XY et Z du résiduel imprimable et scinde leurs jonctions si
  nécessaire. Elle ne déplace ni ne redimensionne les cavités.
- Le solveur de piles sait insérer tardivement un support plus large sous une
  pile déjà construite. `CasLimite01++` calcule et finalise ainsi sans sélection
  manuelle de variante.
- Fusion ne crée plus de features paramétriques Combine pour les unions et
  coupes rectangulaires : un corps BRep transitoire complet est booléenné puis
  persisté une seule fois par module dans une BaseFeature.
- L'adaptateur rend la main à l'interface entre les modules et conserve le
  rollback global après erreur. Cette respiration n'est pas encore une jauge
  déterminée ni une annulation utilisateur.
- Candidate corrective : `0.1.73`.
- Preflight source :
  `e8392bc12c69074e654d1d9cecf99656df5fe9ac187eb17d1b981a713584b6fd`.
- Le préparateur sec passe avec `109/109` tests ciblés et six replays exacts en
  lecture seule. La suite globale autorisée passe `886/886` en `363.209 s`,
  avec une intégration SCIP native ignorée et douze modules interdits exclus.
- Le package 0.1.73 du commit `b5fb15b` est installé et vérifié dans Fusion ;
  la session démarre sans projet courant et les artefacts de recette sont prêts.
- Les jobs annulables, miniatures de variantes et épaisseur distincte de
  séparateur restent cadrés par ADR-0095 à ADR-0097 et hors de R2.
- Prochaine action unique : gate humaine P64-L09U-R2-V selon
  `docs/P64_L09U_R2_V_0173_FUSION_GATE_RECIPE.md`.
- Aucun benchmark/holdout, aucune valeur physique nouvelle ;
  `fusion-validated=false`, `print-validated=false`.

Autorités R2 :

- `docs/P64_L09U_R1_V_0172_HUMAN_KO_EVIDENCE.md` ;
- `docs/DECISIONS/ADR-0098-plan-minimal-exact-et-corps-fusion-transitoire.md` ;
- `docs/P64_L09U_R2_0173_CORRECTIVE_EVIDENCE.md` ;
- `docs/P64_L09U_R2_V_0173_FUSION_GATE_RECIPE.md`.

### Historique R1 supersédé

#### Reprise canonique P64-L09U-R1

- `0.1.70` et `0.1.71` sont `human-KO`, `do-not-run`.
- 0.1.71 confirme le démarrage vierge, le calcul explicite et la finalisation.
- Sa matérialisation échoue en moins d'une seconde sur
  `ALL_TOOL_BODY_REFERENCE_LOST` et laisse des volumes outils visibles.
- La cause est précise : après `BaseFeature.finishEdit`, l'adaptateur passait
  encore les corps sources au Combine au lieu des corps résultats exposés par
  `baseFeature.bodies`.
- R1 relit et vérifie les corps résultats avant Join/Cut.
- Toute erreur de génération déclenche désormais un rollback de tous les objets
  BGIG du job ; un nettoyage incomplet est signalé explicitement.
- Les acquis réservation, paroi, priorité plancher, cavités figées, fermeture
  composite et opérations CAD logiques restent inchangés.
- Les six variantes personnelles exactes repassent en lecture seule.
- `CasLimite01++` est logeable : 18 variantes locales sont générées, 7 retenues
  et une restriction contrôlée en mémoire à la variante canonique trouve un
  plan complet en environ `15,8 s`.
- Cette preuve motive ADR-0096, mais la sélection visuelle n'est pas livrée
  dans le correctif atomique 0.1.72.
- ADR-0095 cadre les vrais jobs annulables et la progression Fusion par lots.
- ADR-0097 sépare la future épaisseur de séparateur sans choisir de nouvelle
  valeur physique.
- Candidate corrective : `0.1.72`.
- Preflight source :
  `b3f8c6cfc183c4a929516d46d44e03e4cbb22cafd6f2c1f9a35a958cc80e555b`.
- Validation : `149/149` tests ciblés, six replays exacts en lecture seule,
  puis suite globale autorisée `881/881` en `408.131 s`.
- Une intégration SCIP native est ignorée ; douze modules
  benchmark/corpus/tournoi sont exclus.
- Prochaine action unique : gate humaine P64-L09U-R1-V selon
  `docs/P64_L09U_R1_V_FUSION_GATE_RECIPE.md`.
- Aucun benchmark/holdout, aucune valeur physique nouvelle ;
  `fusion-validated=false`, `print-validated=false`.

Autorités :

- `docs/P64_L09U_V_0171_HUMAN_KO_EVIDENCE.md` ;
- `docs/DECISIONS/ADR-0094-session-vierge-et-materialisation-fusion-par-lots.md` ;
- `docs/P64_L09U_R1_RELEASE_GATE_EVIDENCE.md` ;
- `docs/P64_L09U_R1_V_FUSION_GATE_RECIPE.md` ;
- `docs/DECISIONS/ADR-0095-operations-cancellables-et-progression-fusion-par-lots.md` ;
- `docs/DECISIONS/ADR-0096-selection-explicite-des-agencements-locaux-certifies.md` ;
- `docs/DECISIONS/ADR-0097-epaisseur-minimale-distincte-des-separateurs-d-assets.md`.

<!-- P64-L09T-CURRENT -->
## Reprise canonique P64-L09T

- Le package `0.1.69` est `human-KO`, `do-not-run`, avec trois acquis
  conserves : jauge fluide, minima des cas de base et cavite orientee corrigee.
- Les variantes locales `CasLimite01+` et `CasLimite02+` calculent, finalisent
  et produisent une CAD IR materialisable en profil Normal, avec cavites
  figees et residuel nul. Les fichiers personnels sont restes inchanges.
- ADR-0093 est acceptee. Elle impose un recalcul explicite apres toute edition,
  des reservations plateau/livret automatiquement placees, une priorite globale
  aux couches basses et une paroi minimale entre cavite et encoche.
- La seule finition automatique immediate est hybride : extensions
  rectangulaires, puis annexes soudables sans jeu interne, avec jeux externes,
  cavites, reservations, unions, coupes et residuel nul certifies.
- Les cales separees, separateurs sans fond et conteneurs de finition generes
  sont inscrits dans P64-F03 et restent differes.
- P64-L09T est lance. Les missions A, B, C, D, E, F et G sont
  automatisees-validees. A rend
  toute edition geometrique explicite : elle rend
  minimal, final et scene obsoletes ; aucun placement n'est republie avant un
  clic explicite sur `Calculer`.
- Le cache certifie exact et le witness restent limites au calcul explicite ;
  la palette et le journal courant ne transportent plus les anciens statuts de
  reutilisation.
- B attache a chaque tentative de finition un diagnostic stable : nature du
  verdict, phase, temps ecoule, plafond, candidats, rejets et raison technique.
  Le resultat solveur, l'activite de palette et le volet technique transportent
  la meme preuve.
- La palette ne presente une impossibilite que si
  `proof_of_impossibility=true`. Une strategie bornee epuisee reste
  explicitement `inconnu, pas impossible`.
- C remplace l'origine XY manuelle par une recherche automatique bornee et
  deterministe. Les reservations sont placees conjointement, leur Z reste le
  plus haut admissible et la pose certifiee appartient au plan minimal.
- Les anciens projets avec origine XY sont lus sans reecriture, normalises vers
  le placement automatique et leur etat derive redevient a calculer.
- Le certificat reutilise l'epaisseur de paroi deja resolue par conteneur. Il
  rejette les bandes de matiere trop minces entre une cavite et une coupe,
  sans reduire ni translater la cavite.
- La finition recharge exactement la pose du plan minimal ; elle ne recentre
  plus les plateaux ou livrets.
- D remplace le classement compact-first entre plans complets certifies. Il
  minimise d'abord les conteneurs eleves, la somme de leurs bases Z, leur
  volume eleve et la gene sous les reservations, puis seulement empreinte,
  piles et compacite.
- Ce classement n'est pas une contrainte gloutonne : les etats intermediaires
  diversifies restent explores et une pile necessaire reste admissible.
- Les composantes du rang sont exposees dans les metriques, le portefeuille,
  le candidat selectionne, les candidats de finition et le witness.
- E reprend le pre-remplissage continu reel sans exiger une partition brute
  complete. Elle decompose le residuel selon les faces canoniques, tente les
  extensions rectangulaires avant les annexes et fige les poses de cavite.
- Le certificat composite v2 attribue chaque cellule imprimable a un
  proprietaire unique, supprime seulement le jeu interne et conserve les
  corridors externes et les reservations comme vides techniques.
- F publie directement la fermeture hybride v2 : le pont temporaire vers la
  fermeture v1 est retire. Le finaliseur recertifie les placements minimaux
  exacts, puis attache les vrais prismes composites au plan produit.
- Chaque cavite recoit une pose monde figee et une empreinte stable. La CAD IR
  cree le coeur, unit les annexes, coupe seulement les cavites et acces de leur
  proprietaire, puis applique les reservations superieures.
- `bgig.xy_composite_cad_materialization_certificate.v2` certifie volumes,
  unions, poses, acces, parois et residuel nul. Les divergences de geometrie ou
  de pose sont refusees avant le plan Fusion.
- G migre les witnesses anterieurs au rang plancher d'abord sans les traiter
  comme des caches : ils amorcent un calcul explicite, sont recertifies et la
  recherche continue.
- Pour douze corps ou plus sous reservation haute, la fermeture essaie d'abord
  la partition rectangulaire certifiable avec coupe differee, puis transmet le
  temps restant au repli par annexes.
- La matrice publique couvre un cas 01+ dense, les quatre variantes isolees de
  02, reservations, couches, fermetures, rejets, stale et arrets.
- La candidate `0.1.70`, son preflight public et son preparateur Fusion sont
  prets. La gate reste `prepared-not-human-observed`.
- Validation A : `912/912` en `329.039 s`, un test SCIP natif ignore sous
  Python 3.10, aucun benchmark/holdout solveur invoque.
- Validation B : `99/99` tests cibles, syntaxe JavaScript `node --check`
  verte, puis suite complete `922/922` en `299.3 s`, avec un test SCIP natif
  ignore sous Python 3.10.
- Validation C : `135/135` tests reservation/migration/palette/minimal/finition,
  `17/17` solveur par etages et `47/47` CAD/resultat. La gate globale autorisee
  passe `859/859` en `282.881 s`, avec un test SCIP natif ignore. Les onze
  modules benchmark/corpus/tournoi restent exclus par le contrat du Goal.
- Validation D : `107/107` tests cibles, puis `19/19` pour la lane SCIP avec
  une integration native ignoree. La gate globale autorisee passe `863/863`
  en `286.898 s`, avec un test ignore et les onze modules interdits exclus.
- Validation E : `45/45` tests cibles, une regression produit `1/1`, puis gate
  globale autorisee `860/860` en `280.807 s`, avec un test ignore. Douze
  modules interdits sont exclus, dont l'adaptateur benchmark devenu non
  canonique avec l'identite v9 et non regenere.
- Validation F : `157/157` tests cibles, puis gate globale autorisee `866/866`
  en `285.542 s`, avec un test ignore. Les douze modules interdits restent
  exclus et aucun artefact associe n'est regenere.
- Validation G : `158/158` tests cibles, six replays locaux exacts en lecture
  seule, puis gate globale autorisee `873/873` en `374.311 s`, avec un test
  ignore. Les douze modules interdits restent exclus.
- Preflight 0.1.70 :
  `f78017e31ff18ad81d0a2aef6e9e1e7d52e624372779f56482ad472ec069fa65`.
- Prochaine action : P64-L09T-V, observation Fusion humaine selon
  `docs/P64_L09T_V_FUSION_GATE_RECIPE.md`.
- Aucun benchmark/holdout, aucune valeur physique nouvelle ;
  `fusion-validated=false`, `print-validated=false`.

Autorites :

- `docs/DECISIONS/ADR-0093-recalcul-explicite-reservations-optimisees-et-fermeture-hybride.md` ;
- `docs/P64_L09S_V_0169_HUMAN_KO_EVIDENCE.md` ;
- `docs/P64_L09T_END_TO_END_GOAL_RUNBOOK.md` ;
- `docs/P64_L09T_A_EXPLICIT_RECALCULATION_EVIDENCE.md` ;
- `docs/P64_L09T_B_EXPLAINABLE_FINALIZATION_STOPS_EVIDENCE.md` ;
- `docs/P64_L09T_C_AUTOMATIC_TOP_RESERVATIONS_EVIDENCE.md` ;
- `docs/P64_L09T_D_FLOOR_FIRST_RANKING_EVIDENCE.md` ;
- `docs/P64_L09T_E_HYBRID_COMPOSITE_CLOSURE_EVIDENCE.md` ;
- `docs/P64_L09T_F_COMPOSITE_CAD_EVIDENCE.md` ;
- `docs/P64_L09T_G_RELEASE_GATE_EVIDENCE.md` ;
- `docs/P64_L09T_V_FUSION_GATE_RECIPE.md`.

<!-- P64-L09S-0168-CURRENT -->
## Reprise canonique corrective 0.1.68

- Le package `0.1.67` est `human-KO`, non accepte et `do-not-run`.
- `CasLimite01` exige une projection sans reservations hautes, un unique solve SCIP puis une recertification obligatoire contre les vrais plateaux.
- `CasLimite02` exige un pool borne de plans minimaux certifies et la reconstruction des variantes avant finition.
- Minima et axes fixes sont invariants ; aucun plateau ne fabrique un support.
- Correctifs et tests cibles termines. La cloture exige la suite autorisee complete, l integration dans `main`, l installation `0.1.68`, puis l observation humaine.
- Prochaine frontiere unique : P64-L09S-V sur `CasLimite01` et `CasLimite02`.
- Aucun benchmark/holdout/corpus ; `fusion-validated=false`, `print-validated=false`.

Les sections suivantes conservent le journal historique des missions et packages precedents.

<!-- P64-L09S-F -->
## Reprise canonique a la gate P64-L09S-V

- A a F sont implementees, testees et documentees.
- Package cible : 0.1.67 ; ancien 0.1.65 `human-KO` et `do-not-run`.
- Le preparateur reel a installe 0.1.67 au commit `12c9f93`, la fixture recente et ses reglages ; statut `prepared-not-human-observed`.
- Prochaine et unique action : observation humaine Fusion selon `P64_L09S_V_FUSION_GATE_RECIPE.md`.
- Aucun benchmark/holdout ; `print-validated=false`.


<!-- P64-L09S-E -->
## Reprise canonique apres P64-L09S-E

- A a E sont implementees, testees, documentees et integrees dans le parcours produit.
- Le cas plateau recent atteint un plan final composite courant, un CAD IR fidele et un plan Fusion pur.
- Prochaine mission unique : P64-L09S-F, durcissement de bout en bout et preparation locale de la gate V.
- Aucun benchmark/holdout ; aucune installation Fusion avant la preparation V ; `print-validated=false`.


<!-- P64-L09S-D -->
## Reprise canonique apres P64-L09S-D

- A, B, C et D sont implementees et testees.
- D certifie la fermeture composite XY bornee du cas plateau recent, mais la garde non materialisable.
- Prochaine mission unique : P64-L09S-E, traduction CAD IR, unions par proprietaire et encoches exactes.
- Aucun package Fusion installe ; aucun benchmark/holdout ; `print-validated=false`.


## Carte active - P64-L09S-D

- A terminee : reservations minimales.
- B terminee : cycle honnete.
- C terminee : partition rectangulaire globale complete par construction.
- D active apres integration : annexes XY composites bornees.
- Prochaine gate humaine : V apres A a F.

## Carte active - P64-L09S-C

- A terminee : reservations minimales sans support artificiel.
- B terminee : cycle honnete, budgets reactifs et couleurs.
- C active apres integration : fermeture rectangulaire globale.
- Prochaine gate humaine : V apres A a F.

## Carte active - P64-L09S-B

- Goal P64-L09S en cours.
- A terminee : calcul minimal sans support artificiel.
- B suivante : verite du cycle, budgets reactifs et couleurs.
- Prochaine gate humaine : P64-L09S-V apres A a F.
- `print-validated=false`.

Ce document est le point d'entrée court de reprise. Il indique l'état actif et
les renvois canoniques ; il ne remplace ni les contrats, ni les ADR, ni les
preuves archivées.

## En 60 secondes

1. Vérifier git status --short --branch, HEAD et la relation avec origin/main.
2. Lire cette fiche, puis [Next actions](NEXT_ACTIONS.md) et les [gates humaines](HUMAN_GATES.md).
3. Lire le contrat et les ADR directement liés à la mission sélectionnée.
4. Ouvrir les sources de détail seulement lorsqu'une question reste non résolue :
   [statut](STATUS.md), [capabilities](CAPABILITY_MAP.md),
   [roadmap](ROADMAP.md) ou [backlog](BACKLOG.md).

## État actif

**État autoritaire du 2026-07-25 :** P64-L09R-V 0.1.65 est un KO humain et ne
doit pas être reprise avec l'architecture courante. Le rafraîchissement du
budget est corrigé, mais le calcul minimal allonge arbitrairement un petit
conteneur de 6,8 mm pour en faire un support à seulement 0,75 % du plateau. La
finition laisse ensuite 775 266,384 mm³ de résiduel et ne publie aucun plan
final, tandis que l'interface annonce à tort un succès.

ADR-0089 est proposée. Elle conserve SCIP pour le solve minimal 3D, interdit
toute croissance de support liée aux plateaux, transforme les réservations en
prismes à respecter, puis impose une fermeture globale complète et équilibrée.
Des annexes XY soudées et certifiées sont permises seulement en repli. Le Goal
P64-L09S est préparé mais non lancé. Sa prochaine action unique est le lancement
explicite par Thomas dans le clavardage de reprise ; ce lancement acceptera
ADR-0089. Aucun code, benchmark ou package Fusion ne commence avant ce
déclencheur. `print-validated=false`.

- Dernière preuve : P64-V2H03V Fusion OK 0.1.55 ; P64-V2H03 est
  fusion-validated pour la coordination des variantes internes.
- print-validated: false ; aucune valeur physique n'est calibrée par cette preuve.
- P64-H03R 0.1.47 conserve les gains de recherche dirigée déjà automatisés.
- P64-H07 0.1.50 livre le beam et le portefeuille interne ; P64-H08 0.1.51
  expose Auto intelligent, Étages et piles, Placement 3D libre et les efforts.
- P64-V2 0.1.51 est un KO contextuel : le cas dense réel reste faussement sans
  solution et l'harmonisation visuelle reste insuffisante.
- P64-V2H01 0.1.52 a séparé faisabilité minimale et fermeture continue, mais le
  nouveau cas réel à 11 conteneurs et 34 contenus produit encore un KO contextuel ;
  aucune preuve Fusion OK 0.1.52 ne doit être émise.
- P64-V2H02R 0.1.54 est fusion-validated : capacité, vérité, budgets, méthodes, occlusion et repère Y sont observés dans Fusion.
  Le cas dense reste honnêtement non certifié ; une marge volumique positive ne
  prouve toujours pas une disposition.
- P64-V2H03A accepte ADR-0070 et le contrat de coordination : P45 possède les
  sémantiques et le certificat local ; P64 possède la recherche et le certificat
  global.
- P64-V2H03B et P64-V2H03C sont `implemented-core` et
  `automated-validated` : frontière locale, sélection globale paresseuse,
  certificats, fixtures et caps.
- Le cul-de-sac minimal est résolu ; le mécanisme dense 11 × 34 reste
  honnêtement `no_solution_within_budget` jusque dans la lane Deep.
- P64-V2H03V est fusion-validated par le retour humain `P64-V2H03V Fusion OK
  0.1.55` : solution multi-cavités, variantes non canoniques, diagnostic
  replié, contrôle canonique et absence de scène automatique sont observés.
- Le cas dense 11 × 34 reste honnêtement `no_solution_within_budget` ; la gate
  ne le déclare ni soluble ni impossible.
- P44-V est fusion-validated avec réserve de charge ; P45-M001V est acceptée ;
  P64-L01, P64-L02 et P64-L03 restent automated-validated pour leurs acquis.
- P64-L03V est un KO contextuel 0.1.56 : expansion déjà réalisée au solve,
  finalisation sans transformation et mise à jour de scène mal détectée.
- ADR-0074 et P64-L03R-A sont architecture-accepted ; P64-L03R-B et
  P64-L03R-C sont `implemented-core`, `automated-validated`.
- L’observation exploratoire humaine du package 0.1.57 est positive avec
  réserves, mais ne vaut pas le retour formel `P64-L03R-V Fusion OK`.
- ADR-0075 et le contrat P64-L04 sont acceptés. P64-L04A est
  `implemented-core`, `implemented-fusion-bridge`, `implemented-fusion-ui` et
  `automated-validated` dans 0.1.58.
- P64-L04B et P64-L04C sont automated-validated.
- Le retour humain P64-L04V est globalement KO mais partiellement positif :
  l’insertion interne fonctionne, le nouveau conteneur et la reconstruction
  depuis zéro restaient en défaut.
- P64-L04R1 et P64-L05A sont automated-validated. L05A insère exactement un
  nouveau conteneur à voisins figés puis recertifie le plan complet sans solve
  global. P64-L05B, P64-L05C et P64-L05D1/D2 sont automated-validated.
  L05D1 fournit un corpus anonymise, un replay borne et une gate A/B.
  P64-L05D2 reduit les evaluations inutiles sans regression fonctionnelle.
  P64-L05V-R2 remplace la recapture manuelle par un journal local automatique
  dans l'add-in 0.1.59. ADR-0080 ferme la gate humaine. L06A, L06B et L06C sont terminées :
  13/13 bundles classés, un cas réel anonymisé, 192 cas T0/T1, deux comparateurs
  offline et un petit oracle exact. L06D et L06E sont terminées : 904 exécutions, trois hypothèses sans gain, holdout sans contradiction et décision finale `no_algorithm_change_v1`.
- Cette clôture ne constitue pas une comparaison de l'état de l'art. ADR-0081
  ouvre P64-L07 : audit d'au moins huit solutions existantes, benchmark d'au
  moins trois concurrents externes distincts, nouveau holdout et intégration
  mesurée d'un à trois gagnants complémentaires.
- P64-L07A est terminé et automated-validated : dix candidats ont été audités ;
  PackingSolver, LAFF, OR-Tools CP-SAT, SCIP et HiGHS restent en lice dans cinq
  familles distinctes.
- P64-L07B est terminé et automated-validated : le manifest V2 conserve huit
  régressions, ajoute 192 cas BGIG, huit contrôles publics issus de deux sources
  et scelle un nouveau holdout indépendant dont les recettes restent hors dépôt.
- P64-L07C est terminé et automated-validated : OR-Tools, HiGHS, SCIP et LAFF
  ont réellement exécuté 12 contrôles sur 12 avec recertification BGIG. SCIP et
  LAFF restent benchmark-only ; aucun moteur n'était adopté à ce stade.
- P64-L07D est terminé et automated-validated : quatre moteurs externes
  sont comparés, HiGHS est scellé seul puis certifie 5/7 cas représentables du
  holdout. Le holdout est consommé et ne sera jamais rouvert.
- P64-L07E est conservée comme preuve d'une lane HiGHS de sol rectangulaire.
  ADR-0083 requalifie cependant L07 : ses quatre candidats ont été comparés sur
  un seul niveau et ne répondent pas à la gate de solvage 3D réel.
- P64-L07V est suspendue. P64-L08A à L08H sont terminées. Le tournoi a
  réellement comparé OR-Tools, SCIP, PackingSolver et LAFF sur les cas limites
  X/Y/Z, puis ouvert le holdout neuf une seule fois après sélection scellée.
  SCIP reste le gagnant benchmark avec 18 gains et 0 perte face au vrai
  comportement BGIG ; le portefeuille est rejeté à +5/−3 face à SCIP seul.
- L08H corrige le blocage ABI : le wheel officiel PySCIPOpt 6.2.1 `cp314`
  charge SCIP 10.0.2 et résout un contrôle exact hors ligne dans Python 3.14,
  mais son paquet natif reste refusé pour redistribution incomplète.
- P64-L08I et ADR-0084 sont terminées. Le worker scellé reste un vrai MIP 3D :
  variables entières/binaires, collisions X/Y/Z, étages, appuis, réservations,
  régions, variantes et retraits. Les sources SCIP 10.0.2, SoPlex 8.0.2,
  PySCIPOpt 6.2.1 et la toolchain `cp314` sont verrouillées avant build.
- P64-L08J est terminée et automated-validated : le runtime minimal SCIP
  `cp314` fait 56 491 565 octets, contient 26 binaires, n'a aucune dépendance
  manquante ou interdite et repasse les six contrôles publics 3D sans perte. Une
  reconstruction indépendante confirme la configuration et le comportement ;
  les sorties MSVC ne sont pas promises identiques bit à bit.
- P64-L08K a intégré SCIP dans 0.1.61, mais sa première gate humaine est KO :
  Approfondi s’arrêtait vers 30 s sans plan sur le cas public 18x20 et le vrai
  projet local 28x30. `bounded_portfolio_exhausted` masquait l’état SCIP.
- P64-L08L corrige cette limite : emphase faisabilité, arrêt au premier plan,
  plafond Approfondi de 120 s et remplissage certifié des petites familles
  répétées. Le vrai projet local 28x30 produit 28 placements recertifiés en
  environ 20 s, sans donnée privée ajoutée au dépôt.
- La régression publique 28x30 dérivée du cas revu produit également 28
  placements, moteur `hybrid_anchor_and_fill`, un appel SCIP et zéro voie
  interne. L’add-in devient 0.1.62.
- P64-L08LV est positive dans Fusion : environ 25 s sur le cas préparé, puis
  34 s avec un bac de cartes très compliqué. La correction de performance est
  `fusion-validated`; `print-validated=false`.
- P64-L09A et ADR-0087 cadrent les limites révélées : appui sur matière réelle,
  anti-chute, réservations plateaux dans SCIP et boucle bornée de fermeture.
- P64-L09B est implemented-core et automated-validated : solides, rebords
  ouverts, chute, couverture matérielle et stabilité utilisent une seule autorité
  dans les voies internes, la fermeture continue, SCIP et le certificat commun.
  Les plans historiques non conformes sont rétrogradés sans faux impossible.
  Suite complète : 843/843.
- P64-L09C est implemented-product et automated-validated : les réservations
  supérieures représentables atteignent le worker SCIP avec coordonnées entières,
  fonds et cavités par rotation. Le contrôle natif CPython 3.14 trouve un corps
  porteur au sommet en une invocation. Les formes non représentables restent
  fail-closed ; benchmark et holdout non exécutés.
- P64-F01B est implemented-product et automated-validated : l’incumbent minimal
  alimente une fermeture bornée, les réservations précèdent l’expansion, une
  réparation locale précède tout solve global et seul le plan final recertifié
  devient matérialisable. Un échec rend no_solution_within_budget sans plan
  partiel. Suite complète : 851/851.
- La partie admissible de P64-F02B est implemented-product et
  automated-validated : le volume ajouté puis le ratio d’expansion sont des
  objectifs secondaires déterministes ; le plan F01B certifié reste prioritaire
  sans amélioration stricte. Suite complète : 853/853.
- P64-L09V 0.1.63 reste archivée sans observation. P64-L09R-B à F sont
  `implemented-product` et `automated-validated`, mais leur gate 0.1.65 est KO :
  compensation Z non viable, finalisation incomplète et message de succès faux.
  P64-L09S est `ready-for-user-goal-launch`. Son périmètre composite est limité
  aux annexes XY de fermeture décrites par ADR-0089.

## Vue de séquence

| État | Élément | Rôle |
| --- | --- | --- |
| Terminé | P44-M007H03 / H03V | UX et calcul sleeves observés dans Fusion 0.1.40. |
| Terminé | P44-VP | Dossier global préparé ; P44-V 0.1.40 est un KO contextuel. |
| Terminé | P64-H01 / H01V | Recherche dense et répartition progressive X/Y/Z observées dans Fusion 0.1.42. |
| KO contextuel | P44-VH02V | Fonctions acceptées contextuellement, croix corrigée ensuite. |
| KO contextuel | P64-H02V | Alignement UX accepté, mais faux impossible sur 0.1.44. |
| Terminé, KO contextuel | P64-H03R | Baseline dirigée conservée ; autre cas dense non résolu. |
| Terminé | P64-A01 | Contrat programme et ADR multi-solveurs/finition acceptés. |
| Terminé | P64-H04 à H06 | Résultats honnêtes, contrat commun et greedy EP/EMS. |
| Terminé | P64-H07 | Beam, profils monotones et portefeuille Auto interne. |
| Terminé | P64-H08 | Réglages Fusion et diagnostic secondaire 0.1.51. |
| KO contextuel | P64-V2 | Contrôles visibles, mais cas dense réel sans solution. |
| KO contextuel | P64-V2H01 | Le projet réel étendu dépasse la fixture 0.1.52. |
| Terminé — gate Fusion | P64-V2H02R | Fusion OK 0.1.54 commit 42e8993 ; pas de validation physique. |
| Terminé — contrat | P64-V2H03A | ADR-0070, propriété P45/P64 et découpage H03B/H03C acceptés. |
| Terminé — automatisé | P64-V2H03B | Frontière locale certifiée, fixtures 1 à 8 et caps mesurés. |
| Terminé — automatisé | P64-V2H03C | Sélection globale paresseuse, lanes monotones, certificat global et fixtures 4 à 10. |
| Terminé — gate Fusion | P64-V2H03V | Fusion OK 0.1.55 : variantes internes visibles, diagnostic replié, contrôle canonique et aucune scène automatique. |
| Terminé — gate Fusion | P44-V | Fusion OK 0.1.55 avec réserve de charge explicitement non observée. |
| Terminé — décision | P45-M001V | Contrat accepté avec Pile / Basculer unifiés ; aucun runtime. |
| Terminé — automatisé | P64-L01 | États, digests, invalidation ciblée, cache borné et stale fail-closed. |
| Terminé — automatisé | P64-L02 | Annotations contextuelles, sous-scores, Pareto et résumé progressif non normatif. |
| Terminé — automatisé, sémantique à corriger | P64-L03 | Solve explicite et stale acquis ; géométrie minimal/final supersédée par ADR-0074. |
| KO contextuel | P64-L03V | Fusion 0.1.56 révèle expansion au solve et scène non réactivable normalement. |
| Terminé — contrat | P64-L03R-A | ADR-0074 et contrat minimal/matérialisation duale acceptés. |
| Terminé — automatisé | P64-L03R-B | Solve minimal multi-graines certifié, résiduel non attribué, sans finition ni scène. |
| Terminé — automatisé | P64-L03R-C | Matérialisation minimale/finalisée, digests exacts et remplacement sûr de scène simulé. |
| Revue exploratoire, non formelle | P64-L03R-V | Plan minimal prometteur observé dans 0.1.57 ; réserves reprises par L04, aucune promotion fusion-validated. |
| Terminé — automatisé | P64-L04A | Insertion locale à enveloppe fixe, recertification globale sans solve et UX compacte dans 0.1.58. |
| Terminé — automatisé | P64-L04B | Préfixe Normal incumbent, extension Deep anytime sous deadline commune de 30 s. |
| Terminé — automatisé | P64-L04C | Identité, lifecycle, étape et temps écoulé honnêtes ; doublons sémantiques bloqués. |
| Retour humain globalement KO | P64-L04V | Insertion interne positive ; nouveau conteneur et reconstruction depuis zéro encore insuffisants. |
| Terminé — automatisé | P64-L04R1 | Cache réservé aux plans certifiés et temps recherche/restitution distincts. |
| Terminé — automatisé | P64-L05A | Nouveau conteneur inséré à voisins figés, plan complet recertifié sans solve global. |
| Termine — automatise | P64-L05B | Bouton DEV rouge et SolverCaseBundle local, versionne, filtre et sans effet metier. |
| Termine - automatise | P64-L05C | Sidecar exact et incumbent recertifie, recherche courante conservee. |
| Termine - automatise | P64-L05D1 | Corpus anonymise, replay borne et gate A/B fonctionnelle prioritaire. |
| Termine - automatise | P64-L05D2 | Elagage sous ordre explicite, -44,355 % essais sur corpus, 0 regression fonctionnelle. |
| Termine - automatise | P64-L05V-A | Preflight, add-in 0.1.58 et fixture installes et verifies. |
| Supersédée | P64-L05V-R1 | La recapture manuelle est remplacée par le journal automatique ADR-0080. |
| Terminé — Goal interne | P64-L06 | Runbook exécuté ; chaîne de mesure livrée, aucune comparaison externe, aucune amélioration intégrée. |
| Terminé — automatisé | P64-L06A | 13/13 bundles classés ; un cas réel anonymisé et rejoué, 12 non promus. |
| Terminé — automatisé | P64-L06B | 192 cas T0/T1, cinq familles, oracles vérifiés et holdout fermé. |
| Terminé — automatisé | P64-L06C | Deux comparateurs sans dépendance, recertification fraîche et petit oracle exact 6/6 dans sa portée. |
| Terminé — résultat négatif | P64-L06D/E | 904 exécutions internes ; aucune amélioration intégrée ; holdout L06 consommé. |
| Terminé — automatisé | P64-L07A | Dix candidats audités ; cinq moteurs et cinq familles passent la première gate, sans adoption. |
| Terminé — automatisé | P64-L07B | Corpus V2 déterministe, deux sources publiques et nouveau holdout scellé, sans run candidat. |
| Terminé — automatisé | P64-L07C | Quatre moteurs externes, quatre familles et 12/12 contrôles réels recertifiés. |
| Terminé — automatisé | P64-L07D | Quatre moteurs comparés ; HiGHS scellé seul, holdout 5/7 dans sa portée. |
| Historique, portée corrigée | P64-L07E | HiGHS 1.15.1 est une lane de sol rectangulaire, pas un gagnant 3D global. |
| Supersédée | P64-L07V | Observation Fusion suspendue par ADR-0083 : elle ne teste pas la gate réelle. |
| Terminé — diagnostic | P64-L08A/B | Gate 3D définie ; HiGHS de sol quarantiné hors Auto après mesure. |
| Terminé — audit | P64-L08C | Shortlist 3D conditionnelle ; aucun gagnant ni build lourd. |
| Terminé — corpus | P64-L08D | 41 cas ouverts, 40 privés scellés, témoins 3D et bornes négatives. |
| Terminé — adaptateurs | P64-L08E | Quatre moteurs/familles exécutés en X/Y/Z ; contrôles recertifiés, refus explicites, holdout fermé. |
| Terminé — gagnant benchmark | P64-L08F | SCIP retenu : +18/−0 face à BGIG ; portefeuille rejeté à +5/−3 face à SCIP. |
| Terminé — résultat produit négatif | P64-L08G | ABI `cp310/cp314` incompatible et redistribution native incomplète ; aucun runtime ni gate Fusion. |
| Terminé — ABI réparée, paquet refusé | P64-L08H | SCIP `cp314` fonctionne hors ligne ; avis natifs et autorités Intel/Microsoft incomplets, aucune intégration. |
| Terminée — audit pré-build | P64-L08I | ADR-0084, modèle MIP 3D, sources et toolchain verrouillés ; aucune intégration produit. |
| Terminée — build et équivalence | P64-L08J | Runtime SCIP minimal qualifié deux fois, 26 binaires résolus, six contrôles publics 3D sans perte. |
| Terminée — intégration produit automatisée | P64-L08K | SCIP prioritaire dans 0.1.61 ; première gate humaine KO sur les vrais cas limites. |
| Terminée — correction automatisée | P64-L08L | Faisabilité d’abord, plafond 120 s, remplissage répété ; cas local et public 28x30 recertifiés. |
| Terminée — gate Fusion de performance | P64-L08LV | Environ 25 s puis 34 s dans Fusion 0.1.62 ; plafond corrigé, portée géométrique limitée. |
| Terminée — architecture | P64-L09A | ADR-0087 : matière porteuse, réservations SCIP et fermeture couplée bornée. |
| Terminée — automatisée | P64-L09B | Chute interdite ; rebords, faces pleines et pontage stable certifiés sur matière réelle. |
| Terminée — automatisée | P64-L09C | Réservations exactes dans SCIP, fonds et cavités protégés, preuve native CPython 3.14. |
| Terminée — automatisée | P64-F01B | Fermeture bornée, réparation locale, échec honnête et certificat final avant CAD. |
| Terminée — automatisée | P64-F02B admissible | Volume ajouté égal puis ratio d’expansion égal ; fallback F01B certifié et modularité différée. |
| Supersédée sans observation | P64-L09V | Gate 0.1.63 annulée par ADR-0088 ; ne pas l’exécuter. |
| Terminée — décision | P64-L09R-A | Support enveloppe, finition optionnelle, budgets visibles et jauge active seulement pendant les opérations. |
| Terminée — automatisée | P64-L09R-B | Support enveloppe, réservations, plan minimal matérialisable, préférence souple et deadlines totales 3/10/20/60/180 s. |
| Terminée — automatisée | P64-L09R-C | Finition facultative à budget indépendant ; timeout, rejet et résultat obsolète conservent le plan minimal. |
| Terminée — automatisée | P64-L09R-D | Trois actions permanentes, activation exacte, budgets séparés et durées adjacentes. |
| Terminée — automatisée | P64-L09R-E | Jauge temporaire pleine largeur, cadence 1 s, worker pur, matérialisation sur thread Fusion et stale fail-closed. |
| Terminée — automatisée | P64-L09R-F | Reçu public 28x30, plateau, préférence souple, timeouts et conservation du minimal durcis ; package 0.1.64 préparé sans installation. |
| KO humain | P64-L09R-V | 0.1.65 allonge arbitrairement un conteneur sous plateau et la finition échoue avec un succès UI trompeur. |
| Prochaine action — lancement humain | P64-L09S | Thomas lance le Goal préparé ; A à F s’enchaînent ensuite sans nouveau GO, puis V reste humaine. |
| Bloqué | P45 runtime, P46-P50, P69 | Dépendances et gates de version non satisfaites. |
| Disponible sans recalibrage | P68 | Recueillir des faits d'impression réels sans modifier les defaults. |

## Autorité documentaire

- PILOTAGE_CURRENT.md : état minimal et chemin de lecture.
- NEXT_ACTIONS.md : une seule prochaine action recommandée.
- P64_MULTI_SOLVER_PORTFOLIO_PROGRAM.md : ordre, contrats et interdits P64.
- P64_V2H03_INTERNAL_VARIANT_COORDINATION_CONTRACT.md : propriété, identité,
  certificats, budgets, fixtures et découpage des variantes internes.
- P64_V2H03B_LOCAL_VARIANT_EVIDENCE.md : mesures, caps et fixtures automatisées.
- P64_V2H03C_GLOBAL_SELECTION_EVIDENCE.md : fallback, benchmarks, certificats et limites denses.
- P64_L01_INCREMENTAL_STATE_EVIDENCE.md : identités, cache et invalidation.
- P64_L02_CONTEXTUAL_LOCAL_ANALYSIS_EVIDENCE.md : annotations, scores, Pareto,
  résumé progressif et absence de solve global.
- P64_F01B_COUPLED_FINALIZATION_EVIDENCE.md : fermeture, réparation, budget,
  certificat final et non-publication des plans partiels.
- P64_F02B_BALANCED_PROPORTIONAL_EVIDENCE.md : objectifs secondaires, score,
  budget partagé, fallback F01B et modularité différée.
- P64_L09R_CALCUL_FINITION_PROGRESS_CONTRACT.md : calcul minimal, finition
  optionnelle, budgets, boutons, invalidation, jauge et découpage L09R.
- P64_L09R_B_MINIMAL_CALCULATION_EVIDENCE.md : support enveloppe, plan minimal
  matérialisable, compensation Z, préférence souple et deadlines totales.
- P64_L09R_F_REPRESENTATIVE_HARDENING_EVIDENCE.md : cas publics, mesures séparées, contrôles négatifs et préparation 0.1.64 sans installation.
- P64_L09R_V_0165_HUMAN_KO_EVIDENCE.md : faits Fusion, causes du support arbitraire, échecs de finition et faux succès UI.
- ADR-0089-reservations-minimales-et-fermeture-globale-composee.md : décision proposée, acceptée seulement par le lancement explicite du Goal.
- P64_L09S_END_TO_END_GOAL_RUNBOOK.md : missions A à F, gate V, certificats, interdits et prompt canonique.
- P64_L09R_V_FUSION_GATE_RECIPE.md : recette 0.1.65 archivée, `do-not-run`.
- ADR-0088 : acquis du retour sélectif et de l’UX staged, avec amendement proposé par ADR-0089.
- P64_L09V_FUSION_GATE_PREPARATION.md : preuve historique 0.1.63 supersédée ;
  aucune action humaine à exécuter.
- P64_L09A_MATERIAL_SUPPORT_AND_COUPLED_FINALIZATION_CONTRACT.md : matière
  porteuse, anti-chute, réservations SCIP, boucle bornée et lots L09/F01B/F02B.
- P64_L09B_MATERIAL_SUPPORT_EVIDENCE.md : surfaces porteuses, chute, pontage,
  parité des voies et changements de vérité historiques.
- P64_L09_VALIDATION_UNIFIEE.md : matrice canonique des preuves automatisées et
  des observations Fusion de toute la chaîne L09.
- P64_L03R_MINIMAL_LAYOUT_AND_MATERIALIZATION_CONTRACT.md : invariant minimal,
  portfolio multi-graines, matérialisation duale et remplacement de scène.
- P64_L03R_B_MINIMAL_SOLVER_EVIDENCE.md : solveur minimal, certificats,
  portefeuille, couches locales, budgets et non-régression dense.
- P64_L03R_C_DUAL_MATERIALIZATION_EVIDENCE.md : sélection duale, CAD IR,
  identité exacte et remplacement borné de scène.
- P64_L04_INCREMENTAL_LOCAL_REUSE_CONTRACT.md : insertion pré-finalisation,
  enveloppe fixe, caps, certificats, fallback et lots B/C/V.
- P64_L04A_INCREMENTAL_LOCAL_REUSE_EVIDENCE.md : preuves cœur, staged, bridge
  et DOM de localité sans solve global.
- P64_L04B_DEEP_ANYTIME_CONTRACT.md : préfixe Normal, deadline Deep, sélection
  monotone, annulation stale et observabilité.
- P64_L04B_DEEP_ANYTIME_EVIDENCE.md : preuves d’incumbent, expiration,
  télémétrie et non-régression automatisée.
- ADR-0075 : réutilisation locale interne à enveloppe fixe.
- ADR-0076 : insertion bornée d’un nouveau conteneur dans le vide global.
- P64_L05A_GLOBAL_VOID_CONTAINER_REUSE_CONTRACT.md : éligibilité, caps,
  certificat et fallback L05A.
- P64_L05A_GLOBAL_VOID_CONTAINER_REUSE_EVIDENCE.md : preuves cœur, staged,
  bridge et DOM de L05A.
- ADR-0077 : capture locale versionnee, semantique et sans auto-apprentissage.
- ADR-0080 : journal local automatique, états dédupliqués et fin de la gate par bouton DEV.
- P64_L05B_SOLVER_CASE_BUNDLE_CONTRACT.md : schema, filtrage, lifecycle et invariants.
- P64_L05B_SOLVER_CASE_BUNDLE_EVIDENCE.md : preuves producteur, staged, bridge et DOM.
- ADR-0078 : sidecar exact, recertification et recherche sans court-circuit.
- P64_L05C_CERTIFIED_PLAN_WITNESS_CONTRACT.md : identite, persistance, warm start et invariants.
- P64_L05C_CERTIFIED_PLAN_WITNESS_EVIDENCE.md : preuves coeur, Deep, staged, bridge et DOM.
- P64_L06B_BENCHMARK_CORPUS_CONTRACT.md : manifest, recettes, oracles, splits et holdout fermé.
- P64_L06B_BENCHMARK_CORPUS_EVIDENCE.md : couverture réelle, audits P45 et reconstruction exacte.
- P64_L06C_OFFLINE_ADAPTER_AND_EXACT_ORACLE_CONTRACT.md : protocole commun, portée exacte, caps et refus.
- P64_L06C_OFFLINE_ADAPTER_AND_EXACT_ORACLE_EVIDENCE.md : deux candidats, 6/6 vérités et recertification fraîche.
- P64_L06_SOLVER_BENCHMARK_CAMPAIGN.md : tiers T0/T1, oracles, comparateurs,
  métriques, protocole goal et lots L06A à L06V.
- P64_L06_AUTONOMOUS_GOAL_RUNBOOK.md : préflight R1, matrice P45/P64, splits,
  budgets 36 h, checkpoints, arrêts et prompt `/goal` canonique.
- ADR-0081 : tournoi externe libre, minimum de concurrence réelle, licences et
  règle d'intégration d'un à trois gagnants.
- P64_L07_OPEN_SOLVER_TOURNAMENT_PROGRAM.md : correction explicite de L06,
  recherche de l'état de l'art, corpus V2, mesures équitables et missions L07.
- P64_L07_AUTONOMOUS_GOAL_RUNBOOK.md : enveloppe 36 h, acquisition isolée,
  tournoi progressif, holdout neuf et prompt `/goal` canonique.
- P64_L07A_EXTERNAL_SOLVER_AUDIT_EVIDENCE.md : dix candidats, shortlist de
  cinq familles, licences, limites de modèle et absence de formes 3D arbitraires.
- P64_L08J_MINIMAL_SCIP_RUNTIME_BUILD_EVIDENCE.md : build minimal, dépendances,
  avis, reconstruction indépendante et équivalence publique 3D.
- ADR-0085 et P64_L08K_SCIP_PRODUCT_INTEGRATION_EVIDENCE.md : lane SCIP
  prioritaire, paquet 0.1.61, preuves 3D, régression 18x20 et limites honnêtes.
- P64_L08K_FUSION_GATE_CHECKLIST.md : gate séparant chargement réel, valeur sur
  le projet limite et validation d'impression.
- ADR-0086 et P64_L08L_HUMAN_GATE_CORRECTION_EVIDENCE.md : faisabilité,
  remplissage répété, preuves publiques et privées sans données privées versionnées.
- P64_L08L_FUSION_GATE_CHECKLIST.md : nouvelle gate 0.1.62 sur les cas 28x30.
- P64_L07B_CORPUS_V2_EVIDENCE.md : corpus V2, sources publiques, petits
  contrôles exacts, séparation des splits et nouveau holdout scellé.
- ADR-0082 : HiGHS 1.15.1 CLI comme lane produit Windows hors ligne.
- P64_L07E_HIGHS_PRODUCT_INTEGRATION_EVIDENCE.md : gate produit, paquet,
  équivalence CLI, fallback et limites de l'intégration.
- P64_L07_SCOPE_CORRECTION.md : requalification de L07 et limites exactes de
  la lane de sol ; il prévaut sur toute formule de victoire globale.
- ADR-0083 et P64_L08_REAL_3D_SOLVER_BENCHMARK_PROGRAM.md : gate obligatoire
  de solvage 3D des cas limites, portefeuille et critères de sélection.
- P64_L08D_REAL_3D_CORPUS_EVIDENCE.md : familles adversariales, témoins,
  bornes négatives et reçu public du holdout privé encore fermé.
- FUTURE_PRODUCT_HORIZONS.md : registre différé des formes, mécanismes,
  visualisations et du futur compositeur manuel 3D.
- ADR-0074 : supersession partielle d'ADR-0071 après le KO Fusion 0.1.56.
- STATUS.md : faits réalisés, validations et limites.
- CAPABILITY_MAP.md : capability et niveau de preuve.
- ROADMAP.md : trajectoire et verrouillage de version.
- BACKLOG.md : mission, dépendances, livrables et statut.
- HUMAN_GATES.md : action humaine réellement requise.
- docs/LOGS/ : preuve et contexte d'une mission terminée.

## Règle de mise à jour

À la fin d'une mission, synchroniser cette fiche, NEXT_ACTIONS.md et le statut
dans BACKLOG.md. Ajouter ensuite le fait vérifiable à STATUS.md,
CAPABILITY_MAP.md, ROADMAP.md et au journal, sans recopier le récit complet.
Ne jamais effacer une preuve historique : la lier, l'archiver ou la marquer
comme supersédée.


## Amendement P64-A02 — boucle étagée et capacité réutilisable (2026-07-21)

L'arbitrage produit est accepté comme architecture future, sans modifier le
runtime 0.1.55. ADR-0071 remplace la cible « tout recalculer après chaque
édition » par cinq états explicites : source, analyse locale, agencement global,
plan finalisé et scène matérialisée. Les analyses locales rapides peuvent se
mettre à jour par asset ou conteneur ; le solve global et la finalisation restent
deux actions utilisateur distinctes.

ADR-0072 accepte une carte de capacité post-solve strictement éphémère. Elle
distingue les opportunités internes, situées dans l'enveloppe finale d'un
conteneur existant, des baies de boîte volontairement réservées pour un futur
conteneur autonome. Une zone libre technique ou un EMS résiduel n'est jamais
promu implicitement en réserve utile.

Documents d'autorité ajoutés :

- P64_STAGED_CALCULATION_AND_FINISHING_PROGRAM.md : états, invalidation, scores,
  UX, finalisation et séquence L01 à F03 ;
- P64_POST_SOLVE_CAPACITY_REUSE_CONTRACT.md : détection, mémoire courte,
  insertion locale, recertification et séquence C01 à CV ;
- ADR-0071 et ADR-0072 : décisions structurantes et alternatives refusées.

P64-A02 est done-documentation et architecture-accepted. Aucune carte runtime
nouvelle n'est active : P64-V2H03V reste l'unique prochaine gate, P44-V/P45/P46
restent verrouillées, le cas dense 11 × 34 reste no_solution_within_budget et
print-validated reste false.


## P44-V requalification 0.1.55

Preparation terminee : package 0.1.55, invariants DOM P44 et H03V controles. Gate humaine suivante ; P45 reste bloque. Aucun comportement runtime ou physique ne change.


## Mise a jour P44-V - gate acceptee

P44-V est fusion-validated pour la fondation UX 0.1.55 par le retour humain du 2026-07-21. La charge d environ 50 conteneurs reste non observee et ne vaut aucune revendication de capacite. P45-M001 peut etre cadre ; P45 ne doit pas absorber le solveur P64.


## P45-M001V — contrat accepté avec interface unifiée

ADR-0073 et le contrat P45-M001 distinguent constitution de pile, pose physique,
disposition locale et placement global. `Pile` et `Basculer` forment un composant
commun aux cartes et aux autres assets ; seul le sleeving reste spécialisé. Le
côté choisi est le côté d'appui, Z ne change jamais sans action explicite, P45
certifie les variantes locales et P64 choisit globalement.

P64-L01, P64-L02 et P64-L03 sont `implemented-core` et `automated-validated`
pour leurs acquis. P64-L03V, préparée ensuite, est désormais un KO contextuel ;
ADR-0074 et P64-L03R-A portent la correction. Tout runtime ou schéma P45 reste
bloqué jusqu'à son contrat additif. Aucune valeur physique n'est modifiée.

## P64-L01 — état incrémental automatisé

Le cœur Python possède désormais des snapshots et clés versionnés, une
invalidation ciblée asset/conteneur/contexte, un cache LRU borné, des jetons de
requête à usage unique et des statuts `current` / `stale`. Une édition locale ne
lance aucun solveur dans cette API et une réponse tardive ne peut pas remplacer
l'état courant.

La preuve automatisée L01 couvre 16 fixtures ciblées, un corpus de cinquante
conteneurs et la parité de dérivation. L02 ajoute l'analyse contextuelle locale et
le résumé progressif sans modifier le solveur public. P64-L03 reste
automated-validated pour l'orchestration ; L03V est désormais un KO contextuel.
Aucune preuve Fusion ou impression n'est revendiquée pour la correction.

## P64-L02 — analyse contextuelle automatisée

- État : implémenté et couvert par les tests automatisés ; aucune gate Fusion ou impression ouverte.
- Le moteur pur consomme P64-L01 pour produire les annotations compatible, conditional, incompatible et unknown sans promouvoir unknown.
- Les sous-scores restent séparés et explicables ; la frontière Pareto moteur demeure complète et déterministe.
- La palette expose Compact, Équilibré et Bas comme représentants UX non normatifs, avec détails et options expertes repliés par défaut.
- Une édition locale invalide uniquement la chaîne concernée et ne lance aucun solve global.
- P64-L03 est désormais automated-validated ; aucun solve global, remplissage, cale, finalisation ou matérialisation ne faisait partie de L02.

## P64-L03 — cycle explicite automatisé (2026-07-21)

Le timer global est retiré. La palette impose Calculer, Finaliser, puis
Matérialiser. Le cœur conserve provenance, cache borné, stale et raisons
d'arrêt. La finalisation de compatibilité ne change aucune géométrie.
Preuve : docs/P64_L03_EXPLICIT_STAGED_CYCLE_EVIDENCE.md.
P64-L03V est ensuite devenue `contextual-KO` ; ADR-0074 supersède la sémantique
minimal/final. Les validations Fusion et impression restent false.

## P64-L03R-A — recadrage minimal/final (2026-07-21)

La revue humaine du package 0.1.56 clôt P64-L03V en KO contextuel. Le cycle
explicite et l'absence d'auto-solve restent acquis, mais le solve global courant
distribue déjà les surplus et la finalisation de compatibilité ne transforme
pas la géométrie. L'UI peut aussi confondre un ancien digest matérialisé avec le
nouvel artefact courant.

ADR-0074 et le contrat P64-L03R imposent un `minimal_layout` sans surplus, une
recherche bornée multi-graines par rareté de placement, des couches de support
locales, puis deux branches : matérialiser minimal ou finaliser. Une scène BGIG
est courante seulement par égalité des digests exacts.

P64-L03R-A est done-documentation et architecture-accepted. P64-L03R-B est
`implemented-core` et `automated-validated`. P64-L03R-C devient la seule
prochaine mission. Aucun schéma projet, valeur physique, CAD IR, finalisation
ou scène n'est modifié par B. `fusion-validated: false`,
`print-validated: false` pour la correction.

## P64-L03R-B — solveur minimal multi-graines livré

Le cœur pur expose désormais `solve_minimal_layout`. Il consomme les frontières
locales certifiées de L01/L02, ou les dérive sous le même budget en fallback,
puis compare des préfixes Rapide / Normal / Approfondi de graines, ordres,
ancres et propagations déterministes. Les lanes EMS historiques restent des
comparateurs isolés.

Le certificat `bgig.minimal_layout_certificate.v1` impose les dimensions
minimales exactes, six surplus nuls, le support, les réservations et la
conservation avec résiduel classifié mais non attribué. Le groupe compact est
recentré lorsque le monde final le permet. Les corps hauts peuvent traverser
plusieurs intervalles à côté de piles fines certifiées.

Aucune finalisation, CAD IR, scène Fusion, valeur physique ou mutation du
solveur public historique n'est incluse. Le cas dense 11 × 34 reste
`no_solution_within_budget`. P64-L03R-C est désormais clôturé automatiquement ;
la gate humaine P64-L03R-V devient active. `fusion-validated: false`,
`print-validated: false`.
## P64-L03R-C — matérialisation duale livrée

Le cycle staged sélectionne maintenant le `minimal_layout` certifié par défaut.
La CAD IR est construite sans relancer le solveur historique, sans distribuer le
résiduel et sans exiger de plan finalisé. Une finition reste un artefact distinct,
optionnel et absent de ce lot.

La sélection et la scène transportent `artifact_kind`, `artifact_digest`,
`partition_plan_digest`, `cad_ir_digest` et `source_revision`. Le digest CAD est
revalidé avant génération. La palette ne considère la scène courante que si
toute l'identité correspond ; sinon elle expose `Mettre à jour la scène`.

Le remplacement refuse toute scène BGIG ambiguë avant suppression et reste borné
à l'unique racine possédée. Les tests simulés couvrent stale, ancien digest,
absence de doublon et préservation des objets utilisateur. Preuve :
`docs/P64_L03R_C_DUAL_MATERIALIZATION_EVIDENCE.md`.

À la clôture de L03R-C, P64-L03R-V était la prochaine gate humaine sur
Fusion 0.1.57 ; ADR-0075 la supplante désormais par L04V. C ne revendique
aucune observation Fusion ou impression, ne livre aucune méthode de finition et
ne change ni solveur public, ni budget, ni schéma, ni valeur physique. Le cas
dense 11 × 34 reste `no_solution_within_budget`.

## P64-L04A — insertion locale pré-finalisation (2026-07-22)

L’observation Fusion 0.1.57 reste exploratoire et ne vaut pas le retour formel
L03R-V. ADR-0075 la supplante par L04A/B/C puis une gate combinée L04V.

L04A conserve le plan monde et tente d’insérer les nouvelles cavités dans
l’enveloppe exacte du conteneur déjà placé. Le plan source, les variantes locales
et le plan reconstruit sont recertifiés ; aucun solve global, finaliseur ou
adaptateur Fusion n’est appelé. Un refus laisse le plan stale et demande un
calcul minimal explicite.

Le cœur, le lifecycle staged, le bridge validate_project et la palette sont
automated-validated dans le package 0.1.58. Une réussite crée un nouvel artefact
minimal ; le plan finalisé et la scène précédente deviennent obsolètes sans
mutation automatique. L04B et L04C sont désormais acquis ; L04V suit.
fusion-validated: false, print-validated: false.

## P64-L04B — Approfondi anytime (2026-07-22)

L04B exécute le préfixe Normal exact avant toute lane propre à Deep. Son meilleur
plan certifié devient l’incumbent initial. Les trois lanes supplémentaires
partagent une seule deadline de 30 000 ms ; chaque beam reçoit le temps restant.
Une expiration conserve l’incumbent, tandis qu’une annulation de validité reste
fail-closed.

Le tuple de classement nommé reste inchangé et une égalité ne déplace pas
gratuitement l’incumbent. Les provenances de phases, budgets, temps, lanes,
frontières, digests et raisons d’arrêt sont observables. Le plan retenu repasse
par le certificat minimal commun.

Validation : 14/14 tests ciblés et 639/639 suite complète. Aucun manifest Fusion,
schéma, budget historique par lane, valeur physique, finalisation, CAD ou scène
n’est modifié. Le cas dense 11 × 34 ne reçoit aucune nouvelle revendication.
P64-L04C est automated-validated ; P64-L04V devient la prochaine gate humaine.
`fusion-validated: false`, `print-validated: false`.

## P64-L04C — activité opérationnelle honnête (2026-07-22)

L04C introduit un état dérivé pur et déterministe pour analyse, calcul minimal,
finalisation et matérialisation. Chaque lancement explicite possède une identité,
une étape courante et un temps écoulé ; aucun pourcentage ni ETA ne sont inventés.

La palette affiche l'activité immédiatement, conserve les détails repliés et
bloque seulement un second lancement du même type sémantique. Le bridge réapplique
le même verrou. La matérialisation inclut la synchronisation réelle de la scène
dans son temps terminal. Aucune action Annuler n'est exposée :
stale_or_cancelled reste une invalidation de validité, pas une annulation
utilisateur générique.

Validation : 5/5 tests purs, 85/85 palette/bridge/CAD ciblés et 648/648
suite complète. Ruff ciblé, py_compile et syntaxe JavaScript passent. Aucun
solveur, budget, schéma, géométrie, valeur physique, CAD IR ou scène automatique
n'est modifié. P64-L04V devient la prochaine gate distincte.
fusion-validated: false, print-validated: false.

## P64-L04V preparation de gate Fusion (2026-07-22)

Le preparateur borne, la baseline portable et la checklist L04V sont versionnes.
Le preflight couvre une reussite locale sans solveur global et un fallback explicite sans solve automatique. La suite complete est verte (650/650).
La promotion Fusion reste humaine ; print-validated: false.

Preuves : P64_L04V_FUSION_GATE_CHECKLIST.md et P64_L04V_FUSION_GATE_PREPARATION_EVIDENCE.md.

## P64-L04R1 — cache négatif corrigé (2026-07-22)

Le retour L04V est partiellement positif : l'insertion d'asset dans un conteneur
existant fonctionne, mais l'ajout d'un nouveau conteneur dans le vide global et
la reconstruction depuis zéro restent KO. R1 supprime la réutilisation des
échecs par le cache et distingue temps de recherche initiale et restitution d'un
succès certifié. Validation automatisée : 651/651. L05A devient la prochaine
mission du programme correctif accepté ; fusion-validated: false,
print-validated: false.

## P64-L05A — nouveau conteneur dans le vide global (2026-07-22)

ADR-0076 et le contrat L05A sont implémentés. Un delta strictement borné à un
nouveau groupe peut conserver bit-à-bit les placements monde existants,
énumérer des positions de contact pour ses variantes locales certifiées et
republier un plan minimal entièrement recertifié. Les zones résiduelles ne sont
pas une preuve. Aucun solve global, finaliseur, CAD ou scène n’est déclenché.

Statut : implemented-core, implemented-fusion-bridge,
implemented-fusion-ui, automated-validated. fusion-validated: false,
print-validated: false. P64-L05B est la prochaine mission.


## P64-L05B — SolverCaseBundle et capture DEV (2026-07-22)

ADR-0077 et le contrat L05B sont implementes. Le bouton rouge explicite capture
un bundle local `bgig.solver_case_bundle.v1` : projet normalise, etat staged
observe positif ou negatif, frontieres P45, provenance, budgets, raison d'arret,
trace semantique sans valeurs et identite de scene allowlistee.

La capture est atomique, bornee a 256 evenements et n'appelle ni solveur,
finalisation, CAD ou Fusion. Elle ne modifie pas automatiquement l'algorithme.
Le manifest reste 0.1.58 ; fusion-validated: false, print-validated: false.
P64-L05C est la prochaine mission unique.

## P64-L05C - temoin certifie persistant automatise

ADR-0078 autorise un sidecar local distinct du cache et de la source projet. Il
est compatible uniquement avec le projet normalise et le jeu exact de frontieres
P45, puis recertifie comme incumbent dans le coeur. Les lanes, caps, prefixe
Normal et deadline Deep restent inchanges ; la recherche ne revendique jamais un
cache hit.

P64-L05C est implemented-core, implemented-fusion-bridge,
implemented-fusion-ui et automated-validated. Le manifest reste 0.1.58,
fusion-validated: false et print-validated: false. P64-L05D devient la prochaine
mission unique : corpus, replay, baseline et optimisation mesuree.

## P64-L05D1 - corpus et gate A/B automatises (2026-07-22)

Sept cas anonymises sont versionnes dans un manifest exact : cinq CI et deux
extended. Le replay separe un digest fonctionnel deterministe des temps mur non
normatifs. La comparaison A/B refuse perte de solution, certificat absent,
prefixe de lanes modifie, qualite degradee ou attente violee avant de regarder
la vitesse.

Le projet personnel indique par Thomas a ete observe en lecture seule et son
SHA-256 est reste identique. Rapide, Normal et Approfondi n'y produisent aucune
completion geometrique ; cela confirme une limite de profondeur sans promouvoir
le fichier dans le corpus.

P64-L05D1 est implemented-core et automated-validated.
fusion-validated: false. print-validated: false. P64-L05D2 est la prochaine
mission unique : optimisation interne bornee, baselined puis comparee.

## P64-L05D2 - premiere optimisation mesuree (2026-07-22)

Sous ordre explicite, le quota de participants non vides definit un prefixe que
les participants ulterieurs ne peuvent plus rejoindre. Leur evaluation est
omise ; la voie heuristique sans ordre reste inchangee.

Sur sept cas, les essais passent de 57 329 a 31 901, les etats de 2 581 a 3 333
sous les memes caps, et aucune regression fonctionnelle n'est observee. Les
temps cumules varient de +2,883 % : aucun gain global de vitesse n'est revendique.

Le projet personnel reste sans completion geometrique et son SHA-256 demeure
identique apres replay en lecture seule. P64-L05D2 est implemented-core et
automated-validated ; fusion-validated: false, print-validated: false.

P64-L05V-A devient la prochaine mission unique : preparer et installer la gate
Fusion, puis faire capturer explicitement un SolverCaseBundle reel.

## P64-L05V-A - gate Fusion preparee et installee (2026-07-22)

Le commit 261f7cc est installe dans l'add-in Fusion 0.1.58. Les marqueurs L05,
le runtime, le settings et le commit installe sont verifies ; la fixture globale
est ecrite dans Documents/BGIG/projects. P64-L05 est maintenant ready-human-gate.

fusion-validated: false. print-validated: false. La capture DEV reste locale et
ne modifie pas automatiquement le solveur.

## P64-L05V - retour Fusion positif partiel (2026-07-22)

Thomas observe dans Fusion 0.1.58 le plan minimal a deux conteneurs, dont le nouveau `Bac 888`, avec `Recherche poursuivie : Oui`, aucun cache revendique et une ecriture atomique du plan temoin. Aucune scene BGIG n est trouvee pendant l inspection read-only, comme attendu sans materialisation.

La fixture confirme le mecanisme, pas la capacite sur un cas difficile. Le retour affiche `Warm start : non fourni` et `no_initial_incumbent` : seule la premiere persistance est observee, pas un rechargement compatible. Aucun bundle DEV reel n est encore fourni. La prochaine preuve humaine est donc de recharger ce witness et de capturer localement un cas representatif de `Mon insert` ; P64-L06A ne commencera qu apres anonymisation et revue du bundle.

fusion-validated reste false globalement. print-validated: false.

## P64-L05V-R1 - fidelite du bouton DEV (2026-07-23)

Trois bundles reels valides etablissent la sequence plan certifie, ajout d exactement un conteneur, puis echec global borne. Ils revelent que la requete DEV ecrasait le rapport de refus incremental par dependencies_unchanged avant l export.

Historique R1 : le bridge figeait le snapshot observé avant resynchronisation et les 682 tests passaient. La demande de deux captures manuelles a depuis été remplacée par le journal automatique décidé dans ADR-0080 ; P64-L06A n est plus verrouillé par cette preuve.

fusion-validated: false. print-validated: false.

### Installation P64-L05V-R1

Historique : le commit e817432 avait été installé dans l add-in 0.1.58 et vérifié. ADR-0080 remplace maintenant la recapture manuelle par le journal automatique 0.1.59.

## Cadrage P64-L06 et horizons produit (2026-07-23)

La vision différée distingue désormais les capacités locales P45, le placement
global P64, les mécanismes P47-P50 et les futures surfaces P69/P70+. Cercles,
polygones, formes composites, poses inclinées, conteneurs fermés réorientables,
plateaux-couvercles, cloisons spécialisées, finitions, couleurs, aperçu 3D et
compositeur manuel sont conservés sans élargir le runtime.

Le programme P64-L06 définit une campagne autonome reprenable : cas T0/T1
actuels, oracles certifiés, adapters offline, tiers CI/extended/soak et gate A/B.
Il exclut l'auto-modification et ne rend aucune dépendance externe acceptable.
L06A à L06D sont désormais terminées. La campagne progressive a retenu une
décision négative sans modifier le solveur ; L06E a clôturé ce premier Goal.

## P64-L06P — runbook Goal prêt (2026-07-23)

Le futur Goal est borné à 36 h, 2 Gio, deux workers fonctionnels et une seule
amélioration intégrée. Le corpus sépare regression, discovery, tuning et holdout ;
le holdout reste fermé avant la sélection d'une hypothèse. Un petit oracle exact
interne évite toute dépendance externe bloquante.

Historique : ce lot était documentaire et attendait encore la paire R1. ADR-0080 a levé cette attente. L06A à L06E sont terminées sans modifier les frontières produit ; le premier Goal est clôturé.

## P64-L05V-R2 — journal automatique et Goal débloqué (2026-07-23)

Sur décision explicite de Thomas, le bouton DEV est supprimé. L'add-in 0.1.59 écrit automatiquement un fichier chronologique par session et conserve chaque état complet du projet une seule fois par empreinte. Les clics, champs, demandes, résultats, erreurs, documents et actions Fusion deviennent analysables sans manipulation spéciale.

Les chemins personnels et secrets sont refusés. Les journaux et projets restent locaux, sans promotion automatique. Le journal ne lance aucun solveur, finaliseur, CAD ou changement de scène et une erreur d'écriture ne bloque pas le produit.

ADR-0080 ferme la gate de recapture R1. L06A a classé 13 bundles et intégré un seul cas anonymisé. L06B a ensuite livré le corpus généré ; le corpus versionné, les générateurs T0/T1 et les oracles internes restent la base du Goal.

Statut : implemented-fusion-bridge, implemented-fusion-ui, automated-validated, integrated-main, installed-local 0.1.59. fusion-validated: false. print-validated: false.

## P64-L06A — inventaire réel terminé (2026-07-23)

Treize bundles locaux sur treize sont valides. La paire récente retenue décrit honnêtement un ajout de contenu : plan stale puis échec global frais sur le même projet, sans cache négatif. Elle ne remplace pas artificiellement l'ancien cas d'ajout de conteneur.

Un seul état final 18 conteneurs / 20 contenus est anonymisé, renormalisé et versionné au tier étendu. Deux replays sont fonctionnellement identiques et satisfont les attentes. Les douze autres bundles restent locaux ; aucun journal personnel n'est promu.

Statut : P64-L06A à P64-L06E done, automated-validated ; premier Goal clôturé par un résultat négatif accepté. fusion-validated: false. print-validated: false.

## P64-L06B — corpus T0/T1 généré (2026-07-23)

Le manifest L06 conserve les huit cas de régression et ajoute 192 recettes :
64 discovery, 64 tuning et 64 holdout. Chaque split couvre les cinq familles,
les cardinalités P45/P64, un à trois étages, les densités, réservations,
rotations et ordres adversariaux prévus. Les cas possibles possèdent un témoin
local/global vérifié ; les cas impossibles une borne exacte de volume ou hauteur.

Les fronts P45 réellement observés couvrent 1, 2, 4 et 8 variantes. Tous les cas
faisables de discovery et tuning ont au moins une variante certifiée. Le holdout
reste fermé et aucun solveur n'y a été exécuté. Le schéma projet ne sachant pas
interdire une rotation globale, cette politique reste une contrainte explicite
du benchmark et un adapter incapable doit répondre unsupported.

Statut : P64-L06B à P64-L06E done, automated-validated ; premier Goal clôturé.
fusion-validated: false. print-validated: false.

## P64-L06C — comparateurs offline et petit oracle exact (2026-07-23)

Deux candidats sont exposés sans dépendance externe : le solveur BGIG courant et
un petit oracle exact interne. Les rapports ont une forme commune, un digest
stable et ne publient une solution qu'après une nouvelle certification BGIG.

Le modèle exact se limite à un niveau, sans réservation, une variante locale et
au plus quatre conteneurs. Il retrouve 4 cas faisables et 2 impossibles sur les
6 cas discovery de sa portée. Tout étage, réservation, variante multiple, cap ou
interdiction de rotation non représentable reçoit un refus honnête. Le holdout
reste fermé.

Statut : P64-L06C à P64-L06E done, automated-validated ; premier Goal clôturé.
fusion-validated: false. print-validated: false.

## P64-L06D — campagne progressive terminée (2026-07-23)

Le runner écrit un résultat et un checkpoint atomiques après chaque couple cas/comparateur, reprend sans double exécution et refuse les digests incohérents. La campagne versionnée totalise 904 exécutions avec un worker et aucune dépendance externe.

Les huit régressions passent. Trois contrôles d'entrée montrent l'effet des rotations et réservations. Trois variantes de lanes Rapide, à budget constant, restent identiques à la baseline sur discovery et tuning. Le choix `no_algorithm_change_v1` est scellé avant holdout ; le holdout confirme zéro gain et zéro contradiction d'oracle. Aucun soak ni changement du solveur produit.

Statut : P64-L06D et P64-L06E done, automated-validated, negative-result-accepted ; premier Goal clôturé. fusion-validated: false. print-validated: false.

## P64-L06E — décision négative et Goal clôturé (2026-07-23)

La gate finale refuse les trois variantes de lanes faute de gain objectif. La décision `no_algorithm_change_v1` est enregistrée : aucun changement du solveur, des budgets, des certificats ou du produit.

Le premier Goal P64-L06 est terminé. Son résultat utile est la chaîne de mesure autonome et la classification des lacunes, pas une revendication de capacité supplémentaire. Le holdout est consommé ; un futur programme devra en créer un nouveau.

Statut : P64-L06A à P64-L06E done, automated-validated, negative-result-accepted. Aucune action humaine requise. fusion-validated: false. print-validated: false.

## P64-L07 — vrai benchmark externe en cours (2026-07-23)

P64-L07 corrige explicitement la portée insuffisante du premier Goal : les trois
variantes internes de L06 ne comptent pas comme des concurrents externes.

ADR-0081 et le nouveau runbook imposent :

- audit d'au moins huit solutions depuis leurs sources officielles ;
- contrôle de licence, Windows hors ligne, packaging et maintenance ;
- au moins trois concurrents externes réellement distincts ;
- corpus BGIG V2, sources publiques et nouveau holdout indépendant ;
- même validateur, mêmes ressources et statuts honnêtes ;
- intégration du meilleur moteur et de deux compléments au maximum, seulement
  si chacun gagne une famille distincte et si le portefeuille bat le meilleur
  moteur seul.

Le solveur courant reste la baseline. L07A à L07D sont terminés : dix
candidats sont audités, quatre moteurs de quatre familles sont exécutés et le
holdout neuf est consommé après une sélection scellée. HiGHS, meilleur candidat
produit, certifie 5/7 cas représentables du holdout ; deux restent
`bounded_unknown`.

SCIP et LAFF restent `benchmark-only`. OR-Tools ne gagne aucune famille face à
HiGHS et aucun portefeuille n'est retenu. Les cas de sélection interdisent tous
la rotation par une propriété absente du schéma produit ; ce constat a imposé
la gate produit distincte L07E. Cette gate donne ensuite deux gains de qualité,
aucune perte et autorise l'intégration de HiGHS seul.

Statut : Goal clôturé ; P64-L07A/B/C/D/E done et automated-validated. HiGHS
1.15.1 est intégré seul dans l'add-in 0.1.60, avec certificat BGIG commun et
fallback interne. P64-L07V est une observation Fusion humaine facultative.
fusion-validated: false. print-validated: false.

## Addendum 2026-07-24 — L07 requalifié, L08 actif

Les sections historiques L07 de cette carte décrivent une lane de sol et ne
doivent plus être lues comme une clôture du benchmark externe. ADR-0083 suspend
L07V et ouvre P64-L08 : la gate réelle porte sur les cas limites 3D BGIG,
notamment l'empilement, les appuis, les réservations et la forte cardinalité.

<!-- P64-L09S-0167-CORRECTIVE -->
## Correctif P64-L09S-V 0.1.67

- la gate humaine `0.1.66` est `human-KO` et `do-not-run` ;
- la reduction d'une enveloppe minimale canonique est interdite et corrigee ;
- le rejeu exact du projet complexe recent passe le calcul et la finalisation avec un residuel de `0.0 mm3` ;
- la suite automatisee autorisee est verte : `833/833`, avec `68` exclusions benchmark/holdout/corpus et `1` test SCIP natif ignore sous Python 3.10 ;
- la gate Fusion `0.1.67` est `prepared-not-human-observed` au commit `832c9d5`, preflight `85c578d`, et la prochaine frontiere est l'observation humaine ;
- `fusion-validated=false` et `print-validated=false`.

<!-- P64-L09S-0169-CURRENT -->
## Historique clos du correctif P64-L09S-V 0.1.69

- `0.1.69` est maintenant `human-KO`, `do-not-run`, supersede par P64-L09T.
- `0.1.68` reste `human-KO` et `do-not-run`.
- Le calcul traite les plateaux/livrets comme des reservations virtuelles
  superieures et ajoute une voie bornee de piles posees au sol pour les grands
  cas.
- Les cavites orientees conservent leur profondeur canonique ; le bac de cartes
  debout passe de `63.6 mm` a `67.6 mm` avec la compensation locale, jamais a
  `24 mm`.
- Le repli composite repart du plan minimal certifie original et la jauge
  n'interroge plus Python toutes les secondes.
- Rejeux locaux exacts : `CasLimite01` calcule, finalise avec residuel nul et
  produit 18 composants CAD ; `CasLimite02` calcule, finalise et conserve tous
  ses minima.
- Validation finale : `910/910` en `329.251 s`, un test SCIP natif ignore sous
  Python 3.10, aucun solveur de holdout invoque.
- Package observe : `0.1.69`. Preuve du KO :
  `docs/P64_L09S_V_0169_HUMAN_KO_EVIDENCE.md`.
- Prochaine frontiere : Goal P64-L09T, puis gate Fusion humaine P64-L09T-V.
- `fusion-validated=false`, `print-validated=false`.
