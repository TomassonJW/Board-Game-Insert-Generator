# P42a - Regroupement des remplissages automatiques

## Declencheur

Le jeu temoin P43 etait constructible mais decomposait un espace libre en 111
petites pieces CAD. Cette decomposition est correcte pour conserver le volume,
mais elle n est pas une liste de pieces imprimables utile ni lisible dans Fusion.

## Correction

Avant materialisation, P42 fusionne de maniere deterministe les cellules libres
qui ont la meme signification, le meme remplissage demande et une face complete
commune. La provenance de toutes les cellules fusionnees reste dans la metadata
CAD. Une forme en L n est jamais transformee abusivement en parallelepipede.

## Resultat

Le jeu temoin passe de 111 a 20 pieces CAD, dont 15 remplissages automatiques
coherents. Les parois minimales, le jeu commun, la validation Fusion hors API et
la grande cardinalite restent testes. L export accepte aussi les JSON UTF-8 avec
BOM ecrits par Windows.

## Suite

P43 peut reprendre la preparation du smoke Fusion avec une scene lisible.
