# P64-F02B — preuve des objectifs équilibrés et proportionnels

Date : 2026-07-24
Statut : implemented-product, automated-validated, fusion-validated=false,
print-validated=false.

## Périmètre livré

La partie admissible de P64-F02B ajoute deux objectifs secondaires explicites à
la fermeture couplée P64-F01B :

1. réduire l'écart de volume ajouté entre conteneurs extensibles ;
2. puis réduire l'écart de ratio d'expansion entre ces conteneurs.

Les trames, cellules et l'harmonisation modulaire restent différées jusqu'aux
contrats de faces P45/P46. Aucun benchmark, tuning, holdout, changement d'UI,
de schéma produit, de pose ou de valeur physique n'a été introduit.

## Algorithme certifié

Le finaliseur produit d'abord le plan P64-F01B fermé et certifié. Il calcule
ensuite le budget encore disponible dans les mêmes caps, repart du même
incumbent minimal et génère des candidats distincts de partage d'un espace entre
deux faces Auto/Target compatibles.

Chaque candidat est classé après les contraintes dures et la fermeture complète,
avec le score déterministe suivant :

1. étendue du volume ajouté ;
2. écart absolu moyen du volume ajouté ;
3. étendue du ratio d'expansion ;
4. écart absolu moyen du ratio d'expansion.

Le candidat secondaire n'est publié que s'il est entièrement fermé, accepté par
le certificat produit commun et strictement meilleur que le plan P64-F01B. Sinon,
le plan P64-F01B certifié est conservé exactement. Aucun solve global
supplémentaire n'est invoqué.

## Preuves automatisées

- objectif volume ajouté égal : partage symétrique d'un espace, écart final nul ;
- objectif ratio d'expansion égal : partage proportionnel aux volumes initiaux,
  écart final nul ;
- déterminisme : digest identique à entrée et budget identiques ;
- axes Fixed, collisions, jeux, support matériel, boîte et réservations restent
  contrôlés par le même validateur commun ;
- fallback : sans amélioration stricte, la provenance reste
  `f01b_certified_baseline` ;
- budget : les compteurs cumulés des deux tentatives restent sous les caps
  partagés ;
- tests ciblés : fermeture 5/5, staged 14/14, palette 29/29 ;
- suite complète : 853/853 en 224,573 s, avec un test SCIP natif ignoré sous
  Python 3.10 ;
- qualité : Ruff ciblé OK, `git diff --check` OK.

## Limites honnêtes

- l'harmonisation modulaire n'est pas implémentée ;
- aucune validation Fusion ou impression réelle n'est revendiquée ;
- la gate produit combinée reste P64-L09V ;
- les couvercles ne créent toujours aucune surface porteuse ou pose implicite.
