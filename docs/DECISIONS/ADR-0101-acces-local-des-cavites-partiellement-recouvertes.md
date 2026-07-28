# ADR-0101 — Accès local des cavités partiellement recouvertes

## Statut

Acceptée comme correction directe du défaut humain observé dans Fusion 0.1.75.

Cette décision ne vaut ni validation Fusion, ni validation d'impression.

## Contexte

ADR-0100 impose une continuité sans matière entre une cavité et la découpe
locale d'un plateau amovible. La version 0.1.75 satisfait cette règle sous le
plateau, mais abaisse toute la cavité dès qu'une partie seulement de son
empreinte est recouverte.

La portion hors plateau reste alors surmontée par le volume plein du conteneur.
La cavité est géométriquement présente, mais son accès fonctionnel est presque
fermé.

## Décision

L'ancrage Z de la cavité reste unique et déterministe. Il est fixé par la
découpe locale recouvrante la plus profonde, sans changer la profondeur
calibrée.

Après cet ancrage, l'accès supérieur est résolu par régions XY :

1. dans une région recouverte, le vide rejoint le dessous exact de la découpe
   locale ;
2. dans une région non recouverte, le vide rejoint le sommet fonctionnel local
   du corps ;
3. si plusieurs paliers existent, chaque région rejoint son propre dessous de
   découpe ;
4. chaque prolongement vertical est limité à l'intersection entre la cavité et
   le prisme composite concerné.

Les prolongements d'accès ne retirent aucune matière en dehors de l'empreinte
de la cavité. Les parois XY, le fond, les bandes d'appui du plateau et les
épaisseurs canoniques voisines restent donc inchangés.

## Ordre géométrique

L'ordre logique et CAD est :

1. unir les prismes du conteneur composite ;
2. soustraire la cavité calibrée ;
3. soustraire ses accès verticaux locaux ;
4. soustraire les encastrements exacts des plateaux et livrets.

Les accès s'arrêtent au dessous des encastrements. Ils ne doublent donc pas
leur volume de coupe.

## Preuve attendue

Le certificat de matérialisation expose :

- `cavity_vertical_access_open=true` ;
- le nombre exact d'accès verticaux requis ;
- des coupes `frozen_cavity_vertical_access` bornées à la cavité ;
- un ordre CAD où les accès suivent la cavité et précèdent les encastrements.

La CAD IR et le plan Fusion doivent transporter les mêmes coupes.

## Compatibilité

ADR-0101 complète ADR-0100 sans modifier :

- le solveur et le plan minimal ;
- la pose X/Y, l'orientation ou les dimensions de cavité ;
- la profondeur calibrée ;
- les valeurs de paroi, de fond, de jeu ou de tolérance ;
- les réservations virtuelles ;
- le chemin BRep transitoire, les budgets et le rollback.

## Alternatives refusées

- remonter toute la cavité au sommet du conteneur ;
- allonger sa profondeur ;
- ouvrir tout le conteneur hors plateau ;
- retirer les parois autour de la cavité ;
- étendre arbitrairement la découpe du plateau ;
- conserver la fermeture et demander une prise latérale non prévue.
