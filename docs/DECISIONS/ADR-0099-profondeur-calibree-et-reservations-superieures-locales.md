# ADR-0099 — Profondeur calibrée et réservations supérieures locales

## Statut

Acceptée par la clarification humaine de Thomas le 2026-07-28.

Cette décision corrige uniquement la sémantique verticale de finalisation et
la composition de plusieurs réservations supérieures. Elle ne vaut ni
validation Fusion, ni validation d'impression.

## Contexte

La gate humaine 0.1.73 confirme que la matérialisation BRep transitoire est
rapide, progressive et fidèle à l'aperçu. Elle révèle cependant deux erreurs
fonctionnelles :

- une cavité calibrée à `10,6 mm` peut mesurer `18,2 mm` après finalisation ;
- deux plateaux de dimensions différentes paraissent produire une découpe
  globale à profondeur cumulée.

ADR-0093 et ADR-0098 ont utilisé l'expression « cavité figée » pour empêcher la
finition de redistribuer les contenus. Cette expression ne doit pas imposer de
conserver une origine Z locale devenue incorrecte lorsque le corps gagne de la
hauteur ou reçoit une découpe supérieure.

## Décision

### 1. Le calibre est figé, pas l'origine Z locale

Le plan minimal fige :

- l'identité de la cavité et de son contenu ;
- ses dimensions X, Y et Z calibrées ;
- sa pose X/Y et son orientation ;
- les jeux effectifs qui ont produit ses dimensions ;
- son propriétaire.

La finalisation ne peut ni redimensionner, ni recentrer, ni redistribuer cette
cavité. Elle résout toutefois à nouveau son origine Z locale par une règle
déterministe, car le repère final du propriétaire peut être plus haut que son
enveloppe minimale.

Cette résolution Z n'est pas une liberté du solveur et ne sert pas à faciliter
la fermeture. Elle est une conséquence géométrique certifiée du corps final.

### 2. Une cavité sans découpe supérieure reste calibrée et ouverte

Lorsqu'aucune réservation supérieure ne recouvre sa projection XY :

- la profondeur de cavité reste inchangée ;
- son plafond coïncide avec la face supérieure fonctionnelle du corps final ;
- le surplus Z devient de la matière sous la cavité ;
- le fond restant est mesuré et certifié.

### 3. Une cavité sous une découpe supérieure descend sans s'allonger

Lorsqu'une réservation supérieure recouvre la cavité :

- la profondeur de cavité reste inchangée ;
- son plafond est placé sous l'intervalle Z local de cette découpe ;
- la séparation minimale réutilise l'épaisseur de paroi canonique déjà résolue
  pour le conteneur ;
- le fond restant et la séparation supérieure sont tous deux certifiés ;
- si ces deux contraintes ne tiennent pas, le plan est refusé explicitement.

L'ancienne compensation qui ajoutait la profondeur d'encastrement à la
profondeur de cavité est supprimée.

### 4. Chaque réservation supérieure reste locale

Chaque plateau ou livret conserve :

- son identifiant stable ;
- son empreinte et sa pose XY résolues ;
- son épaisseur physique et ses jeux ;
- son ordre vertical ;
- son propre intervalle Z ;
- ses intersections exactes avec les corps porteurs.

Une coupe est créée uniquement sur l'intersection entre l'empreinte de cette
réservation et le corps concerné.

### 5. Le cumul vertical dépend du recouvrement réel

- Des empreintes disjointes partagent le même niveau disponible et ne cumulent
  pas leur hauteur.
- Des empreintes partiellement recouvrantes ne cumulent leurs hauteurs que
  dans leur intersection.
- Des éléments réellement empilés produisent une géométrie en paliers conforme
  à leurs empreintes et à leur ordre.
- Un rectangle englobant, une profondeur maximale globale ou la somme totale
  des éléments plats ne peut pas remplacer cette composition locale.

### 6. Les certificats portent la nouvelle sémantique

Le plan final, l'aperçu, la CAD IR et le plan Fusion exposent et vérifient :

- profondeur calibrée source et finale ;
- origine Z minimale et origine Z finale ;
- motif d'ancrage : `open_top` ou `below_top_inset` ;
- réservation locale éventuellement responsable ;
- épaisseur de fond restante ;
- séparation supérieure restante ;
- correspondance exacte des coupes par réservation.

## Compatibilité avec les décisions précédentes

Cette ADR supersède uniquement :

- ADR-0093 §5 lorsque « cavités figées » interdisait toute résolution Z finale ;
- ADR-0098 §1 et ses conséquences lorsqu'elles imposaient une pose monde Z
  identique entre minimum et final.

Restent inchangés :

- aucune modification X/Y, rotation ou dimension de cavité ;
- aucune redistribution des assets ;
- aucun déplacement opportuniste pour fermer le volume ;
- plateaux et livrets toujours virtuels et non imprimables ;
- paroi minimale issue des paramètres canoniques ;
- corps BRep transitoire et matérialisation progressive ;
- `fusion-validated=false`, `print-validated=false` avant nouvelle gate.

## Alternatives refusées

- Augmenter la profondeur de cavité de l'épaisseur du plateau.
- Conserver une origine Z minimale puis découper jusqu'au sommet final.
- Appliquer la somme des plateaux comme profondeur globale.
- Inventer une nouvelle épaisseur de séparation.
- Déplacer une cavité en X/Y pour faciliter la finition.
