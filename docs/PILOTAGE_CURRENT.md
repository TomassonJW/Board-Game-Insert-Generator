# Pilotage courant

Ce document est le point d'entrée court de reprise. Il indique l'état actif et
les renvois canoniques ; il ne remplace ni les contrats, ni les ADR, ni les
preuves archivées.

## En 60 secondes

1. Vérifier `git status --short --branch`, `HEAD` et la relation avec `origin/main`.
2. Lire cette fiche, puis [Next actions](NEXT_ACTIONS.md) et les [gates humaines](HUMAN_GATES.md).
3. Lire le contrat et les ADR directement liés à la mission sélectionnée.
4. Ouvrir les sources de détail seulement lorsqu'une question reste non résolue : [statut](STATUS.md), [capabilities](CAPABILITY_MAP.md), [roadmap](ROADMAP.md) ou [backlog](BACKLOG.md).

## État actif

- Dernière preuve : `P64-H01 Fusion OK 0.1.42 - commit 5865645` ; P64-H01 est `fusion-validated`.
- `print-validated: false` ; aucune valeur physique n'est calibrée par cette preuve.
- P64-H03R (package 0.1.47) conserve la recherche dirigée H03 au-dessus de H04 ;
  un autre cas dense reste un KO contextuel, sans remettre en cause les cas
  supplémentaires déjà résolus.
- P64-H03R est `automated-validated`, mais ni `fusion-validated` ni `print-validated`.
- P64-A01 accepte la trajectoire multi-solveurs des ADR-0068/0069 ; aucun runtime
  n'est modifié par cette mission documentaire.
- P64-H05 (package 0.1.48) encapsule la baseline H03R derrière le contrat commun ; ses références H04 restent identiques.
- Prochaine action unique : `P64-H06`, placement 3D libre greedy EP/EMS. P44-V et P45 restent bloqués.

## Vue de séquence

| État | Élément | Rôle |
| --- | --- | --- |
| Terminé | P44-M007H03 / H03V | UX et calcul sleeves observés dans Fusion 0.1.40. |
| Terminé | P44-VP | Dossier global préparé ; le retour P44-V 0.1.40 est un KO contextuel. |
| Terminé | P64-H01 / H01V | Recherche dense et répartition progressive X/Y/Z observées dans Fusion 0.1.42. |
| KO contextuel | P44-VH02V | Fonctions acceptées contextuellement, croix corrigée ensuite. |
| KO contextuel | P64-H02V | L'alignement UX est accepté contextuellement, mais un nouveau faux impossible empêche toute preuve globale 0.1.44. |
| Terminé, KO contextuel | P64-H03R | Baseline dirigée conservée sur H04 ; un cas dense reste à dépasser par H06/H07. |
| Terminé | P64-A01 | Contrat programme et ADR multi-solveurs/finition acceptés. |
| Terminé | P64-H04 | Résultats honnêtes, télémétrie versionnée et corpus automatisé ; aucune nouvelle stratégie. |
| Terminé | P64-H05 | Contrat commun, certificat et baseline `Étages et piles` préservée. |
| Prêt | P64-H06 | Placement 3D libre greedy EP/EMS. |
| KO contextuel | P44-V | Reprendre seulement après P64-V2 ; P45 reste bloqué. |
| Bloqué | P45 à P50, P69 | Dépendances et gates de version non satisfaites. |
| Disponible sans recalibrage | P68 | Recueillir des faits d'impression réels sans modifier les defaults. |

## Autorité documentaire

- `PILOTAGE_CURRENT.md` : état minimal et chemin de lecture.
- `NEXT_ACTIONS.md` : une seule prochaine action recommandée.
- `P64_MULTI_SOLVER_PORTFOLIO_PROGRAM.md` : ordre, contrats et interdits P64.
- `STATUS.md` : faits réalisés, validations et limites.
- `CAPABILITY_MAP.md` : capability et niveau de preuve.
- `ROADMAP.md` : trajectoire et verrouillage de version.
- `BACKLOG.md` : mission, dépendances, livrables et statut.
- `HUMAN_GATES.md` : action humaine réellement requise.
- `docs/LOGS/` : preuve et contexte d'une mission terminée.

## Règle de mise à jour

À la fin d'une mission, synchroniser cette fiche, `NEXT_ACTIONS.md` et le statut
de la mission dans `BACKLOG.md`. Ajouter ensuite le fait vérifiable à `STATUS.md`,
`CAPABILITY_MAP.md`, `ROADMAP.md` et au journal, sans recopier le récit complet.
Ne jamais effacer une preuve ou décision historique : la lier, l'archiver ou la
marquer comme supersédée.
