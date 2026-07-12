# Gate report - P43 smoke Fusion V0.1 (gate rouverte)

## Declencheur

P42 produit maintenant la geometrie fonctionnelle du projet V0.1 : bacs,
logements, support sous plateaux, remplissages et separateurs. La seule preuve
qui ne peut pas etre automatisee est leur observation dans Fusion.

## Etat actuel

- jeu temoin : `examples/p43_v01_functional_project.json` ;
- scene CAD preparee : 20 pieces fonctionnelles et 19 cavites ;
- scene compacte seule : pas de vue eclatee ni de limite de nombre de pieces ;
- add-in installe dans Fusion et reglages locaux ecrits ;
- tests Python, API, CLI, scene Fusion hors API et build Studio passes ;
- impression, ajustement reel des pieces et slicer : hors gate P43.

## Ce qui doit etre observe dans Fusion

1. La commande s ouvre sans erreur et lance la scene compacte preconfiguree.
2. La scene comporte la boite de reference, trois bacs nommes, un bac vide de
   support, un separateur et des remplissages automatiques regroupes.
3. Les logements sont ouverts par le dessus, avec parois et fond visibles.
4. Aucun doublon BGIG n apparait apres ce premier lancement.

## Options

1. `Fusion P43 OK` : tous les points visibles sont presents et aucune erreur ne
   s affiche.
2. `Fusion P43 KO` : une erreur, une piece manquante, une cavite incorrecte ou
   un doublon est observe ; le message ou une capture est joint.

## Recommandation

Confirmer `Fusion P43 OK` si la scene correspond aux quatre points ci-dessus.
Ce smoke ne valide qu une scene Fusion. Il ne vaut pas acceptance du MVP logiciel ni validation d impression.

## Risques et limites

- le smoke ne prouve pas la resistance, l ajustement des vraies pieces ou la
  qualite d impression ;
- V0.2 formes/ergonomie et V0.3 couvercles restent bloques jusqu a P58,
  puis a P46 ;
- toute erreur Fusion visible doit etre corrigee avant acceptation.

## Validation demandee

Retour humain unique : `Fusion P43 OK`, ou le texte/capture de l ecart observe.

## Observation humaine recue

Le 2026-07-12, Thomas a confirme : `Fusion P43 OK`.

## Decision corrigee

Le smoke Fusion est accepte pour la geometrie du jeu temoin uniquement. Il est
`fusion-validated-geometry-only`. Le MVP V0.1 reste reouvert et
`product-mvp-rejected` jusqu a P58 ; `print-validated: false` reste obligatoire.

## Suivi de reprise

La scene P43 contient 20 pieces, dont 15 remplissages automatiques residuels.
Ils sont corrects pour le volume et les collisions, mais leur fragmentation et la
palette bloquee sur `Chargement...` montrent que la qualite produit n est pas
acceptee. P51 est absorbe par P56 ; P58 demandera un nouveau smoke Fusion de la
scene finale retenue.
