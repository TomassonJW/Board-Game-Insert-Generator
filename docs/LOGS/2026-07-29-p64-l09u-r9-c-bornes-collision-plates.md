# 2026-07-29 — P64-L09U-R9-C bornes de collision plates

## Changement

- les bornes XYZ immuables des corps sont préparées une fois par appel de
  résolution automatique ;
- les milliers de classements réutilisent ces bornes sans reconstruire les
  mêmes dimensions ;
- une réservation candidate copie seulement le sous-payload de migration
  qu'elle modifie ; la copie profonde finale publiée reste inchangée ;
- le certificat matériel lit directement les rectangles numériques déjà
  normalisés.

## Mesures

- `CasLimite02+` : `8,916 s` ;
- `CasLimite02++` : `8,240 s` ;
- digest `a3ef…bc46` ;
- SHA personnels inchangés.

Les 27 tests ciblés des réservations plates passent. Aucun ordre, candidat,
budget, pas de grille ou certificat n'est modifié.
