# ADR-0054 - Cavites calibrees et enveloppes de bacs extensibles

## Statut

Accepte le 2026-07-12 par clarification produit explicite.

## Date

2026-07-12

## Cartes liees

- `P53 - Contrat de volume absorbe par les bacs`
- `P55 - Contrat executable cavite/minimum/final`
- `P57 - Solveur de partition et expansion des bacs`

## Contexte

Le premier plan P41/P42 traite les regions libres comme des candidats de
remplissage et peut les materialiser en petits bacs automatiques. Le jeu temoin
P43 produit ainsi quinze corps residuels sans fonction demandee par la personne.

Cette interpretation est contraire au besoin produit. Les mesures, quantites et
jeux des assets definissent le volume interieur necessaire de leurs logements.
Elles ne demandent pas que l enveloppe exterieure du bac reste au minimum autour
de ces logements.

## Options

1. Conserver les bacs a leurs dimensions minimales et imprimer les residus sous
   forme de corps automatiques.
2. Laisser du vide non attribue dans la boite.
3. Fixer les cavites utiles puis agrandir les enveloppes des bacs demandes pour
   absorber le volume disponible dans leurs parois et leurs fonds.

## Decision

Retenir l option 3.

Le solveur distingue desormais deux geometries :

- la `cavity envelope`, minimale et calibree depuis les assets, leur quantite et
  leur jeu ;
- la `container outer envelope`, variable, calculee pour participer a une
  partition complete du volume disponible.

La cavite ne grandit pas quand le bac absorbe du volume. Le surplus X/Y devient
de la matiere autour des cavites. Le surplus Z devient principalement de la
matiere sous les cavites, donc un fond plus epais. Les parois et fonds minimaux
restent des bornes basses, pas des epaisseurs finales imposees.

Apres reservation de la pile de plateaux/livrets et des jeux obligatoires, le
volume imprimable restant doit etre partitionne entre les bacs demandes. Un
projet avec un seul bac peut donc produire un grand corps exterieur et une petite
cavite calibree. Un projet avec plusieurs bacs repartit ce volume entre eux selon
un plan explicable et regulier.

Aucun bac vide, bloc plein ou separateur n est cree automatiquement. Ces corps
n existent que s ils sont demandes explicitement dans l editeur. Les jeux entre
bacs et contre la boite restent des vides techniques intentionnels ; ils ne sont
pas materialises.

## Politique de repartition par defaut

Le solveur doit privilegier, dans cet ordre :

1. une partition simple et lisible du volume disponible ;
2. le respect de toutes les cavites calibrees ;
3. le moins de corps possible, exactement ceux demandes par les groupes de bacs
   et les complements explicites ;
4. des alignements de faces et hauteurs qui supportent les plateaux/livrets ;
5. une repartition equilibree du surplus, sans lamelles ni micro-volumes ;
6. un diagnostic impossible si aucune partition ne respecte les contraintes.

Les futurs reglages avances pourront modifier la preference de repartition
(agrandir plutot en X/Y, epaissir davantage les fonds, aligner certaines faces,
verrouiller une dimension exterieure), sans changer la taille utile des cavites.

## Consequences

- Le chemin automatique `free region -> filler body` de P41/P42 est obsolete
  pour le MVP et doit etre retire du resultat par defaut.
- P39 reste reutilisable pour calculer les cavites et enveloppes minimales.
- P40 reste reutilisable pour reserver la pile superieure.
- P41 doit etre remplace par un solveur de partition et d expansion conjointe.
- P42 doit materialiser les enveloppes finales et soustraire les cavites fixes.
- La conservation de volume porte sur les enveloppes finales, les reservations
  et les jeux techniques, pas sur une collection de remplissages automatiques.

## Alternatives refusees

- Option 1 : elle produit exactement les micro-bacs rejetes dans P43.
- Option 2 : elle ne remplit pas proprement la boite et ne respecte pas la
  promesse d insert complet.

## Suivi

La vision, le modele geometrique, le contrat MVP et P53-P60 sont alignes sur
cette decision avant toute nouvelle implementation.
