# 2026-07-29 — P64-L09U-R9-B déduplication des rangs plats

## Décision

Le premier incrément R9-B supprime les classements plats strictement répétés
dans un même appel, sans modifier la recherche beam ni son ensemble de
candidats.

L'essai qui terminait le front Normal est rejeté : il réduisait le calcul à
`6,618 s`, mais changeait le digest autoritaire en `269f…009`.

## Changement

- cache de rang limité à un seul appel de résolution automatique ;
- clé : signature géométrique exacte déjà utilisée pour la déduplication ;
- contexte boîte, placements, sommet de conception et mode capturé par
  l'appel, donc aucune réutilisation entre candidats ou runs ;
- rectangles matériels et utiles préparés une seule fois par appel ;
- copie superficielle en lecture seule pendant le classement, copie profonde
  finale inchangée pour la réservation publiée ;
- compteurs de demandes, rangs uniques et réutilisations exposés dans la
  télémétrie de recherche automatique.

## Mesures

Sur la première lane Approfondie exacte :

- `CasLimite02+` : `10,341 s`, digest `a3ef…bc46` ;
- `CasLimite02++` : `9,288 s`, digest `a3ef…bc46` ;
- recherche beam : environ `2,30 s` ;
- SHA personnels avant/après : identiques.

La suite R9 doit encore éviter les deux appels SCIP initiaux et les huit lanes
internes inutiles. Aucun gain Fusion n'est encore revendiqué.
