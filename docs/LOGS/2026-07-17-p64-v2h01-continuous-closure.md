# 2026-07-17 — P64-V2H01 fermeture continue corrective

## Déclencheur

Retour Fusion contextuel sur 0.1.51 : les méthodes semblent identiques, un cas
dense visiblement faisable reste en Calcul impossible et la répartition manque
d'harmonie.

## Reproduction

Projet local laissé ouvert : 250 x 180 x 70 mm, 9 conteneurs, 26 éléments,
plateau et livret.

- stage_stack/deep : no_solution_within_budget ;
- free_3d/deep 0.1.51 : greedy géométrique rejeté pour résiduel, beam sans
  complétion certifiée ;
- cause complémentaire : les réservations supérieures ne sont ni des obstacles
  pleins ni des zones libres ; elles demandent un corps sous le plan d'appui ou
  un corps au sommet compatible avec la profondeur de coupe.

## Correction

- beam v2 sur enveloppes minimales ;
- un seul participant le plus contraint branché par niveau, avec plusieurs états ;
- réservations supérieures conditionnelles pendant la recherche ;
- fermeture continue Auto/Cible avant certificat ;
- score secondaire par faces alignées et croissance relative ;
- aucun corps, axe Fixe, asset, cavité, paroi, fond, jeu ou défaut modifié.

## Preuve automatisée

La fixture anonymisée issue du cas réel conserve les minima et réservations
structurantes. En effort Approfondi :

- Étages et piles : pas de solution dans le budget ;
- Placement 3D libre : solution certifiée, 9 corps, plusieurs niveaux ;
- Auto : même candidat libre certifié ;
- résiduel imprimable : 0 ;
- erreurs de coupe/cavité : 0.

Package : 0.1.52. Statut : implemented, automated-validated,
ready-for-human-fusion-check.

## Limites

La fermeture améliore l'alignement des faces mais n'est pas la grille modulaire
adaptative P64-F02. Aucune validation Fusion ni impression n'est revendiquée.
print-validated: false.