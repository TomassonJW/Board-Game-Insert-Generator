# Journal P64-H01 - Recherche dense et équilibre spatial

Date : 2026-07-17

## Déclencheur

Après P44-VH01, le projet réel devient calculable mais reste fragile : environ
30 conteneurs, 77 éléments, un petit asset supplémentaire et un faux
`NO_STAGE_COMPOSITION_FITS` malgré environ 40 % de volume minimal. Le mode
Équilibré conserve aussi un seul étage tant qu'un arrangement XY existe.

## Diagnostic

- les groupes par étages sont contigus et de taille uniforme ;
- les piles de plus de dix corps sont elles aussi principalement contiguës ;
- l'ajout du petit asset agrandit une seule enveloppe de 198,9 × 221,2 à
  198,9 × 233,6 mm et supprime le seul candidat historique ;
- une partition déterministe non contiguë trouve immédiatement deux groupes
  valides et environ 97,5 % de support ;
- le classement favorise la famille de recherche avant la qualité ;
- le sous-solveur XY pénalise systématiquement les rangées supplémentaires sans
  tenir compte de la hauteur Z de l'étage.

## Décision

ADR-0065 retient une recherche adaptative bornée et un score d'équilibre
spatial explicite. Aucun solveur externe, changement de schéma ou recalibrage
physique n'est introduit.

## Implémentation

- partitions LPT selon l'empreinte minimale cumulée ;
- huit nombres d'étages adaptatifs au maximum par ordre ;
- borne Z optimiste avant calcul XY ;
- familles adaptatives évaluées avant les groupes contigus ;
- arrangements XY `balanced` comparés à leur hauteur d'étage ;
- score X/Y/Z moyen complété par l'équilibre des charges d'étage ;
- léger coût de simplicité pour les compositions hybrides par intervalles ;
- mode compact inchangé dans son ordre de préférence.

## Preuves automatisées

- 2, 8 et 32 corps homogènes : 1, 2 et 3 étages en mode balanced ;
- 8 corps homogènes : 1 étage en mode compact ;
- fixture dense de 30 corps : solution complète adaptative en 2 étages ;
- projet réel augmenté : solution complète en environ 1,8 seconde ;
- tests solveur volumétrique et partition ciblés verts avant suite complète.

## Limites

La recherche reste heuristique, déterministe et bornée ; aucune optimalité
globale n'est revendiquée. fusion-validated: false et print-validated: false
jusqu'aux preuves correspondantes.

## Suite

Le package 0.1.42 a été observé positivement dans Fusion :
`P64-H01 Fusion OK 0.1.42 - commit 5865645`. P64-H01 est fusion-validated ;
P44-VH02 est le seul lot de code suivant et P45 reste bloqué.
