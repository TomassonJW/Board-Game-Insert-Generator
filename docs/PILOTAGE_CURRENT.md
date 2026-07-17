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

- Dernière preuve : P64-V2H02R Fusion OK 0.1.54 - commit 42e8993 ; P64-V2H02R est
  fusion-validated.
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
- P64-V2H03B est `implemented-core` et `automated-validated` :
  frontière locale, certificats, fixtures et caps, sans branchement public.
- P64-V2H03C devient la seule mission `ready` ; sa gate Fusion éventuelle
  reste séparée.
- P44-V et P45 restent bloquées pendant ce chemin correctif.

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
| Prêt | P64-V2H03C | Sélection globale paresseuse, lanes monotones et certificat global. |
| KO contextuel | P44-V | À requalifier séparément après arbitrage ; P45 reste bloqué. |
| Bloqué | P45 à P50, P69 | Dépendances et gates de version non satisfaites. |
| Disponible sans recalibrage | P68 | Recueillir des faits d'impression réels sans modifier les defaults. |

## Autorité documentaire

- PILOTAGE_CURRENT.md : état minimal et chemin de lecture.
- NEXT_ACTIONS.md : une seule prochaine action recommandée.
- P64_MULTI_SOLVER_PORTFOLIO_PROGRAM.md : ordre, contrats et interdits P64.
- P64_V2H03_INTERNAL_VARIANT_COORDINATION_CONTRACT.md : propriété, identité,
  certificats, budgets, fixtures et découpage des variantes internes.
- P64_V2H03B_LOCAL_VARIANT_EVIDENCE.md : mesures, caps et fixtures automatisées.
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
