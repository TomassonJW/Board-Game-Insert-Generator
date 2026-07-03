# Tolerance Model

## Objectif

Le modele de tolerance evite de confondre volume theorique et volume imprime.

Un insert qui remplit exactement le volume interieur d'une boite en CAO ne
rentrera pas toujours dans la boite reelle. A l'inverse, reduire tous les volumes
uniformement peut creer des jeux inutiles, des parois trop fines ou des modules
mal ajustes.

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

## Valeurs actuelles par defaut

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

Depuis `P3-M001`, le moteur represente explicitement les six faces d'un corps
rectangulaire simple avant de calculer les offsets. Cette etape est preparatoire :
elle n'ajoute pas de nouvelles valeurs par defaut et ne change pas les dimensions
imprimables des exemples existants.

Faces nommees :

- `x_min` ;
- `x_max` ;
- `y_min` ;
- `y_max` ;
- `z_min` ;
- `z_max`.

Roles actuels :

- `peripheral` : face contre la limite interieure mesuree de la boite ;
- `neighbor` : face en contact avec une autre cellule theorique ;
- `exposed` : face libre dans une zone non occupee ;
- `functional` : face reservee a une contrainte fonctionnelle, comme le dessous
  ancre a Z=0 ou le dessus sous couvercle ;
- `internal` : role reserve pour une future face interne ;
- `welded` : role reserve pour une future jonction soudee de module composite.

Regle d'offset V0 preservee :

- une face `peripheral` recoit le jeu peripherique ;
- une face `neighbor` recoit la moitie du jeu entre modules ;
- une face `exposed` recoit seulement la compensation imprimante si elle existe ;
- `z_max` recoit le jeu vertical sous couvercle ;
- `z_min` reste a Z=0.

Si deux modules voisins recoivent chacun `module_gap_mm / 2`, le jeu total entre
leurs corps imprimables est `module_gap_mm`.

## Modules composites

Pour un module composite, les primitives internes sont fusionnees.

Les faces internes entre primitives du meme module ne recoivent aucun jeu. Les
tolerances s'appliquent seulement :

- aux faces exposees au monde exterieur ;
- aux faces fonctionnelles ;
- aux cavites ;
- aux interfaces de couvercles ou charnieres.

Cette regle est une contrainte d'architecture. Elle evite de casser un module
soude en appliquant un jeu la ou il devrait exister une matiere continue.

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

Un profil ne doit pas cacher ses valeurs. Il doit produire un ensemble explicite
de champs de tolerance.

## Statuts

Implemente :

- offsets simples sur X/Y/Z pour corps rectangulaires ;
- classification explicite des faces rectangulaires simples ;
- distinction peripherie, voisin, face exposee et face fonctionnelle dans les cas
  simples ;
- exposition des classifications dans les rapports ;
- validation que les offsets ne rendent pas le corps non positif.

Experimental :

- roles `internal` et `welded` reserves pour modules composites futurs ;
- valeurs de tolerance non calibrees physiquement.

Prevu :

- application dimensionnelle plus avancee a partir des roles de faces ;
- profils d'impression ;
- tolerances de cavites ;
- jeux de couvercles, rainures, charnieres et clips ;
- protocole de calibration par coupons imprimes.

A valider par impression reelle :

- toutes les valeurs par defaut ;
- toutes les interfaces fonctionnelles ;
- tous les mecanismes ;
- les modules composites et unions Fusion.

## Validation par impression

Aucune valeur de tolerance ne doit etre presentee comme universelle. Les rapports
doivent rappeler que les jeux doivent etre valides par impression reelle, surtout
pour les couvercles, charnieres et cartes sleevees.
