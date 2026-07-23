# 2026-07-23 - P64-L05V-R2 journal automatique

## Décision humaine

Thomas demande de supprimer le bouton DEV, de journaliser automatiquement le parcours complet utile et de rendre le benchmark P64-L06 autonome sans dépendre d'une paire de clics réalisée au bon instant.

## Livraison

- add-in porté à 0.1.59 ;
- bouton et style DEV retirés ;
- route de journal séparée du traitement projet ;
- événements JSON Lines append-only ;
- états complets dédupliqués par SHA-256 ;
- chemins et secrets refusés ;
- ADR-0080, contrat, preuve et pilotage mis à jour.

## Effet sur P64-L06

La recapture R1 devient une preuve complémentaire, non une gate. L06A inventorie et classe les cas disponibles ; L06B à L06E peuvent ensuite utiliser le corpus versionné, les générateurs T0/T1 et les oracles internes sans nouvelle action humaine.

## Clôture

Suite complète 685/685, préparateur 83/83, commit fonctionnel `31b867e` intégré dans `main` et add-in 0.1.59 installé localement. Le manifest et le journal sont présents ; le bouton DEV est absent.

## Invariants

Aucun changement de solveur, budget, délai, certificat, schéma métier, géométrie, finalisation, CAD, scène ou valeur physique. Aucun journal personnel n'est promu automatiquement.

fusion-validated: false. print-validated: false.
