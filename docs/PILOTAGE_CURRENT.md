# Pilotage courant

Ce document est le point d’entrée court de reprise. Il indique l’état actif et les renvois canoniques ; il ne remplace ni les contrats, ni les ADR, ni les preuves archivées.

## En 60 secondes

1. Vérifier `git status --short --branch`, `HEAD` et la relation avec `origin/main`.
2. Lire cette fiche, puis [Next actions](NEXT_ACTIONS.md) et les [gates humaines](HUMAN_GATES.md).
3. Lire le contrat et les ADR directement liés à la mission sélectionnée.
4. Ouvrir les sources de détail seulement lorsqu’une question reste non résolue : [statut](STATUS.md), [capabilities](CAPABILITY_MAP.md), [roadmap](ROADMAP.md) ou [backlog](BACKLOG.md).

## État actif

- Dernière preuve : `P44-M007H03 Fusion OK 0.1.40 - commit 92f07c8` ; P44-M007H03 est `fusion-validated`.
- `print-validated: false` ; aucune valeur physique n’est calibrée par cette preuve.
- Code produit : P44-VH01 corrige la hauteur cachée transmise au solveur dans le package 0.1.41.
- Prochaine action : gate humaine P44-VH01V. Après son OK, P44-VH02 est le seul lot de code ; P45 reste bloqué.

## Vue de séquence

| État | Élément | Rôle |
| --- | --- | --- |
| Terminé | P44-M007H03 / H03V | UX et calcul sleeves observés dans Fusion 0.1.40. |
| Terminé | P44-VP | Dossier global préparé ; le retour P44-V 0.1.40 est un KO contextuel. |
| Prêt | P44-VH01V | Vérifier que Z pilote réellement la hauteur multi-étages dans Fusion 0.1.41. |
| KO contextuel | P44-V | Reprendre après P44-VH01V puis P44-VH02. |
| Bloqué | P45 à P50, P67 à P69 | Dépendances et gates de version non satisfaites. |

## Autorité documentaire

- `PILOTAGE_CURRENT.md` : état minimal et chemin de lecture.
- `NEXT_ACTIONS.md` : une seule prochaine action recommandée.
- `STATUS.md` : faits réalisés, validations et limites.
- `CAPABILITY_MAP.md` : capability et niveau de preuve.
- `ROADMAP.md` : trajectoire et verrouillage de version.
- `BACKLOG.md` : mission, dépendances, livrables et statut.
- `HUMAN_GATES.md` : action humaine réellement requise.
- `docs/LOGS/` : preuve et contexte d’une mission terminée.

## Règle de mise à jour

À la fin d’une mission, synchroniser cette fiche, `NEXT_ACTIONS.md` et le statut de la mission dans `BACKLOG.md`. Ajouter ensuite le fait vérifiable à `STATUS.md`, `CAPABILITY_MAP.md`, `ROADMAP.md` et au journal, sans recopier le récit complet. Ne jamais effacer une preuve ou décision historique : la lier, l’archiver ou la marquer comme supersédée.
