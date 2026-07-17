# Pilotage courant

Ce document est le point d’entrée court de reprise. Il indique l’état actif et les renvois canoniques ; il ne remplace ni les contrats, ni les ADR, ni les preuves archivées.

## En 60 secondes

1. Vérifier `git status --short --branch`, `HEAD` et la relation avec `origin/main`.
2. Lire cette fiche, puis [Next actions](NEXT_ACTIONS.md) et les [gates humaines](HUMAN_GATES.md).
3. Lire le contrat et les ADR directement liés à la mission sélectionnée.
4. Ouvrir les sources de détail seulement lorsqu’une question reste non résolue : [statut](STATUS.md), [capabilities](CAPABILITY_MAP.md), [roadmap](ROADMAP.md) ou [backlog](BACKLOG.md).

## État actif

- Dernière preuve : `P64-H01 Fusion OK 0.1.42 - commit 5865645` ; P64-H01 est `fusion-validated`.
- `print-validated: false` ; aucune valeur physique n'est calibrée par cette preuve.
- P44-VH01 corrige la hauteur cachée ; le cas originel est calculable, sans retour formel de gate ni revendication fusion-validated.
- Code produit : P64-H01 ajoute la recherche dense adaptative et l'équilibre spatial X/Y/Z dans le package 0.1.42.
- Code produit : P44-VH02 ajoute suppression directe, confirmation transactionnelle et noms incrementaux ; P44-VH02H01 aligne la croix avec le menu.
- Code produit : P64-H02 ajoute la reprise diversifiée seulement après un cul-de-sac canonique, dans le package 0.1.44.
- Prochaine action : gate humaine P64-H02V ; P44-V et P45 restent bloques.

## Vue de séquence

| État | Élément | Rôle |
| --- | --- | --- |
| Terminé | P44-M007H03 / H03V | UX et calcul sleeves observés dans Fusion 0.1.40. |
| Terminé | P44-VP | Dossier global préparé ; le retour P44-V 0.1.40 est un KO contextuel. |
| Supersédé | P44-VH01V | Le cas Z originel passe, mais la densité a révélé P64-H01 ; aucune fusion-validation formelle n'est revendiquée. |
| Terminé | P64-H01 / H01V | Recherche dense et répartition progressive X/Y/Z observées dans Fusion 0.1.42. |
| KO contextuel | P44-VH02V | Le reste est observe comme OK, mais la croix passait sur une nouvelle ligne ; supersede par P64-H02V. |
| Pret | P64-H02V | Verifier la croix a droite de ... et le projet laisse ouvert, complet en 2 niveaux dans Fusion 0.1.44. |
| KO contextuel | P44-V | Reprendre après P64-H02V ; P45 reste bloqué. |
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
