# Tolerance Model

## Objectif

Le modele de tolerance evite de confondre volume theorique et volume imprime.

Un insert qui remplit exactement le volume interieur d'une boite en CAO ne rentrera pas toujours dans la boite reelle. A l'inverse, reduire tous les volumes uniformement peut creer des jeux inutiles, des parois trop fines ou des modules mal ajustes.

## Jeux a distinguer

Le projet distingue au minimum :

- jeu peripherique contre la boite ;
- jeu entre modules voisins ;
- jeu vertical sous le couvercle ;
- jeu autour des cartes ;
- jeu autour des cartes sleevees ;
- jeu autour des tokens ;
- jeu autour des meeples ou pieces irregulieres ;
- jeu pour couvercles coulissants ;
- jeu pour charnieres ;
- compensation liee au filament et a l'imprimante ;
- arrondis et chanfreins de confort.

## Valeurs V0 par defaut recommandees

Ces valeurs sont prudentes et doivent etre ajustees selon l'imprimante :

| Champ | Valeur typique | Role |
| --- | ---: | --- |
| `peripheral_clearance_mm` | 0.8 | Eviter que l'insert force contre la boite |
| `module_gap_mm` | 0.6 | Laisser un jeu total entre deux modules voisins |
| `vertical_lid_clearance_mm` | 1.0 | Eviter la pression sous couvercle |
| `card_clearance_mm` | 0.5 | Jeu autour de cartes non sleevees |
| `sleeved_card_clearance_mm` | 1.0 | Jeu autour de cartes sleevees |
| `token_clearance_mm` | 0.6 | Jeu pour tokens carton |
| `meeple_clearance_mm` | 1.0 | Jeu pour pieces irregulieres |
| `sliding_lid_clearance_mm` | 0.35 | Jeu fonctionnel de couvercle coulissant |
| `hinge_clearance_mm` | 0.4 | Jeu fonctionnel de charniere simple |
| `printer_compensation_mm` | 0.0 | Correction profil imprimante |
| `default_corner_radius_mm` | 1.5 | Rayon de confort par defaut |
| `default_chamfer_mm` | 0.4 | Chanfrein de manipulation |

## Application par face

En V0 :

- une face contre la boite recoit le jeu peripherique ;
- une face partagee avec un module voisin recoit la moitie du jeu entre modules ;
- une face libre recoit seulement la compensation imprimante si elle existe ;
- la face superieure recoit le jeu vertical sous couvercle ;
- la face basse reste a Z=0, sauf evolution future explicite.

Si deux modules voisins recoivent chacun `module_gap_mm / 2`, le jeu total entre leurs corps imprimables est `module_gap_mm`.

## Modules composites

Pour un module composite, les primitives internes sont fusionnees.

Les faces internes entre primitives du meme module ne recoivent aucun jeu. Les tolerances s'appliquent seulement :

- aux faces exposees au monde exterieur ;
- aux faces fonctionnelles ;
- aux cavites ;
- aux interfaces de couvercles ou charnieres.

Cette regle est une contrainte d'architecture. Elle evite de casser un module soude en appliquant un jeu la ou il devrait exister une matiere continue.

## Profils d'impression futurs

Le modele doit permettre des profils comme :

- PLA standard ;
- PETG ;
- impression rapide ;
- impression fine ;
- imprimante calibree ;
- imprimante non calibree ;
- buse large ;
- couche epaisse.

Un profil ne doit pas cacher ses valeurs. Il doit produire un ensemble explicite de champs de tolerance.

## Validation par impression

Aucune valeur de tolerance ne doit etre presentee comme universelle. Les rapports doivent rappeler que les jeux doivent etre valides par impression reelle, surtout pour les couvercles, charnieres et cartes sleevees.
