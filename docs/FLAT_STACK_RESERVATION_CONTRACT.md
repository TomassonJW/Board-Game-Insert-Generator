# Contrat de reservation de pile plateaux et livrets V0.1

## But

`bgig.flat_stack_reservation.v1` reserve la pile des plateaux, livrets et autres
elements plats au sommet de la boite. Il recalcule les bacs P39 sous la hauteur
restante, puis transmet un besoin de support a P41.

## Regles de pile

- Une ligne ayant `stack_order` est placee avant une ligne sans ordre explicite.
- Dans une ligne, l epaisseur est `dimensions_mm.z * quantity`.
- Les lignes sont alignees sur la plus grande empreinte XY de la pile.
- Le jeu `layout_clearance_mm` est reserve autour de l empreinte et sous la pile
  pour la separer des bacs.
- La hauteur disponible aux bacs est `usable_height_mm - hauteur_reservation`.

Les livres et plateaux restent des objets reserves, non imprimables. Leur
position XY definitive reste la responsabilite de P41.

## Sortie

La sortie contient :

- `flat_stack` : empreinte physique, taille reservee, hauteur laissée aux bacs,
  ordre et origine Z de chaque ligne ;
- `container_plan` : bacs P39 recalcules sous cette hauteur ;
- `support_requirement` : empreinte et aire de support requises, aire candidate
  des sommets de bacs, et statut honnete ;
- `blockers` : depassement de largeur, profondeur, hauteur ou bac qui ne tient
  plus sous la pile.

## Statut de support

| Statut | Signification |
| --- | --- |
| `not_required` | Aucun plateau ou livret n est reserve. |
| `area_budget_sufficient_pending_placement` | La somme des sommets de bacs suffit en aire, mais P41 doit encore prouver une surface continue. |
| `support_extension_required` | Les sommets de bacs ne suffisent pas encore ; P41 doit agrandir un bac ou ajouter support/remplissage. |
| `blocked` | Une mesure de pile ou de bac est impossible. |

Un statut autre que `blocked` n est pas une preuve physique de support, ni une
preuve Fusion ou impression.

## Suite

P41 place bacs et reservation dans la boite, applique le jeu global, ferme le
volume, puis prouve collisions et support. P42 materialise seulement le resultat
retenu.
