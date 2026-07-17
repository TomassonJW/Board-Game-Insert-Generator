# 2026-07-17 — P64-H02, reprise diversifiée et actions d’élément alignées

## Faits observés

- Le projet laissé par Thomas contient 8 conteneurs, 11 éléments, une boîte de
  250 × 180 × 70 mm et 12 mm de réservations supérieures localisées.
- Le portefeuille canonique évalue 96 groupements et retourne 8 candidats, tous
  rejetés par `TOP_INSET_PIERCES_CAVITY_FLOOR`.
- Le volume n’est pas la cause : un ordre différent des mêmes participants
  construit une solution complète en deux niveaux.
- La croix de suppression était un item de grille supplémentaire ; elle passait
  donc seule sur la ligne suivante au lieu de rester à droite du menu `...`.

## Correction

- le menu et la croix partagent désormais une cellule flex de 85 px ;
- le solveur ne diversifie les ordres qu’après un cul-de-sac canonique ;
- six portefeuilles supplémentaires au maximum sont autorisés ;
- le cas exact est construit après 3 portefeuilles au total, avec 19 candidats
  faisables agrégés et 8 conteneurs sur 2 niveaux ;
- package cible : 0.1.44, gate P64-H02V.

## Limites

Aucune valeur physique, dimension, tolérance, cavité, réservation, géométrie ou
scène automatique ne change. La recherche reste heuristique et non globalement
optimale. `fusion-validated: false`, `print-validated: false` jusqu’au retour humain.
