# 2026-07-28 — P64-L09U-R7 — décisions placement, pile et grille

## Décisions

ADR-0103 retient :

- une recherche bornée par ancres ;
- des contraintes de paroi dures avant le score ;
- un score favorisant couverture utile, pile saine et centrage ;
- un ordre automatique fondé sur l'empreinte orientée ;
- la normalisation explicite d'un `stack_order` historique contradictoire ;
- aucune relocalisation silencieuse en finalisation.

ADR-0104 retient :

- une grille produit de `0,1 mm` ;
- des ticks entiers aux frontières de disposition ;
- un epsilon numérique interne distinct ;
- des arrondis conservateurs pour jeux et minima ;
- aucune réécriture automatique des projets ;
- une invalidation explicite des anciens artefacts ;
- des mesures avant/après sans promesse de performance.

## Option retenue

La combinaison « ancres bornées + certificat dur + score lexicographique » est
préférée au centrage simple et au balayage exhaustif de la grille.

## Compatibilité

Le futur mode manuel reste possible par une politique explicite distincte, mais
aucune UI ou édition manuelle n'est ajoutée dans R7.

## Suite

R7-C1 introduit les primitives de grille et la quantification des candidats
avant les changements de géométrie finale.
