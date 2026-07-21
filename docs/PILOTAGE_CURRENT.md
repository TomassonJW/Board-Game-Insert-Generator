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
- ADR-0074 et P64-L03R-A sont architecture-accepted ; P64-L03R-B est désormais
  `implemented-core`, `automated-validated`, et P64-L03R-C devient la seule
  prochaine mission runtime.

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
| Ready — bridge et scène | P64-L03R-C | Matérialisation minimale/finalisée, digests exacts et remplacement sûr de scène. |
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
`no_solution_within_budget`. P64-L03R-C est `ready` ; aucune revue humaine n'est
requise avant sa clôture automatisée. `fusion-validated: false`,
`print-validated: false`.
