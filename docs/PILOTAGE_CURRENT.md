# Pilotage courant

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
  dans l'add-in 0.1.59. ADR-0080 ferme la gate humaine. L06A et L06B sont terminées :
  13/13 bundles classés, un cas réel anonymisé, puis 192 cas T0/T1 générés ;
  L06C est la prochaine mission.

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
| Autorisé — Goal | P64-L06 | Runbook 36 h, matrice T0/T1, splits et checkpoints ; exécution débloquée par ADR-0080. |
| Terminé — automatisé | P64-L06A | 13/13 bundles classés ; un cas réel anonymisé et rejoué, 12 non promus. |
| Terminé — automatisé | P64-L06B | 192 cas T0/T1, cinq familles, oracles vérifiés et holdout fermé. |
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
- P64_L06_SOLVER_BENCHMARK_CAMPAIGN.md : tiers T0/T1, oracles, comparateurs,
  métriques, protocole goal et lots L06A à L06V.
- P64_L06_AUTONOMOUS_GOAL_RUNBOOK.md : préflight R1, matrice P45/P64, splits,
  budgets 36 h, checkpoints, arrêts et prompt `/goal` canonique.
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
La première mission runtime reste P64-L06A après confirmation des captures R1 ;
ce cadrage documentaire ne lève aucune gate.

## P64-L06P — runbook Goal prêt (2026-07-23)

Le futur Goal est borné à 36 h, 2 Gio, deux workers fonctionnels et une seule
amélioration intégrée. Le corpus sépare regression, discovery, tuning et holdout ;
le holdout reste fermé avant la sélection d'une hypothèse. Un petit oracle exact
interne évite toute dépendance externe bloquante.

Historique : ce lot était documentaire et attendait encore la paire R1. ADR-0080 a levé cette attente ; L06A est désormais prête sans modifier solveur, budget, schéma, géométrie, Fusion ou manifest.
## P64-L05V-R2 — journal automatique et Goal débloqué (2026-07-23)

Sur décision explicite de Thomas, le bouton DEV est supprimé. L'add-in 0.1.59 écrit automatiquement un fichier chronologique par session et conserve chaque état complet du projet une seule fois par empreinte. Les clics, champs, demandes, résultats, erreurs, documents et actions Fusion deviennent analysables sans manipulation spéciale.

Les chemins personnels et secrets sont refusés. Les journaux et projets restent locaux, sans promotion automatique. Le journal ne lance aucun solveur, finaliseur, CAD ou changement de scène et une erreur d'écriture ne bloque pas le produit.

ADR-0080 ferme la gate de recapture R1. L06A a classé 13 bundles et intégré un seul cas anonymisé. L06B a ensuite livré le corpus généré ; le corpus versionné, les générateurs T0/T1 et les oracles internes restent la base du Goal.

Statut : implemented-fusion-bridge, implemented-fusion-ui, automated-validated, integrated-main, installed-local 0.1.59. fusion-validated: false. print-validated: false.

## P64-L06A — inventaire réel terminé (2026-07-23)

Treize bundles locaux sur treize sont valides. La paire récente retenue décrit honnêtement un ajout de contenu : plan stale puis échec global frais sur le même projet, sans cache négatif. Elle ne remplace pas artificiellement l'ancien cas d'ajout de conteneur.

Un seul état final 18 conteneurs / 20 contenus est anonymisé, renormalisé et versionné au tier étendu. Deux replays sont fonctionnellement identiques et satisfont les attentes. Les douze autres bundles restent locaux ; aucun journal personnel n'est promu.

Statut : P64-L06A et P64-L06B done, automated-validated ; P64-L06C prochaine. fusion-validated: false. print-validated: false.

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

Statut : P64-L06B done, automated-validated ; P64-L06C prochaine mission.
fusion-validated: false. print-validated: false.
