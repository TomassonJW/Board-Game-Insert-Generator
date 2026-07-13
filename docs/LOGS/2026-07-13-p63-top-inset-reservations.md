# 2026-07-13 - P63 reservations superieures encastrees

## Resultat

P63 remplace la reduction globale de hauteur P40/P57 par des encastrements
rectangulaires locaux depuis le plan superieur de conception. Les conteneurs et
complements demandes conservent leur hauteur complete hors empreinte ; aucun
corps automatique n est cree.

## Contrat livre

- placement centre automatique ou origine XY explicite, rotation 0/90 ;
- composition verticale uniquement entre empreintes qui se chevauchent ;
- ordre de retrait et plan d appui explicites ;
- zone de prise rectangulaire simple, sans ergonomie courbe V0.2 ;
- refus d une coupe qui perce le fond d un corps ou descend sous le fond d une
  cavite intersectee ;
- operations CAD IR distinctes des cavites de contenu ;
- generation Fusion des coupes d empreinte et de prise avec controle du sommet,
  de la profondeur retenue et des bornes locales ;
- vue de dessus et coupe X/Z des reservations dans l Apercu.

## Compatibilite

Le payload historique `flat_stack` reste expose aux consommateurs existants,
mais sa hauteur de rangement vaut maintenant la hauteur de conception complete
et sa semantique est `localized_top_insets`. Le fixture P60 a ete migre de
63,4 mm a 66 mm : le livret retire localement 2 mm au lieu de raboter tous les
corps.

## Preuves

- 408 tests automatises passent ;
- tests dedies au calcul, aux intersections, au non-percement, a la
  determinisme, aux vues, a la CAD IR et au plan Fusion ;
- package Fusion 0.1.13 ;
- coeur Python sans import `adsk` ;
- `print-validated: false` ;
- observation Fusion differee a P66 : `fusion-retest-required`.

## Suite

P64 devient `ready` pour remplacer le placement XY a Z = 0 par un solveur
volumetrique borne par etages, conformement a ADR-0059.
