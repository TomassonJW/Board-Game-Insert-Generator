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

Depuis `P3-M002`, le moteur represente explicitement les six faces d'un corps
rectangulaire simple puis transforme chaque classification en application de
tolerance testable. Cette etape n'ajoute pas de nouvelles valeurs par defaut et
ne change pas les dimensions imprimables des exemples existants.

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

Regles appliquees en `P3-M002` :

| Role | Faces typiques | Offset applique | Recoit un jeu ? | Statut |
| --- | --- | ---: | --- | --- |
| `peripheral` | X/Y contre la boite | `peripheral_clearance_mm + printer_compensation_mm` | oui | implemente |
| `neighbor` | X/Y contre une cellule voisine | `module_gap_mm / 2 + printer_compensation_mm` | oui | implemente |
| `exposed` | X/Y libre | `printer_compensation_mm` seulement si non nul | non | implemente |
| `functional` | `z_min` | `0.0` | non | implemente |
| `functional` | `z_max` | `vertical_lid_clearance_mm` | oui | implemente |
| `internal` | future face interne | `0.0` | non | regle testee, detection future |
| `welded` | future jonction soudee | `0.0` | non | regle testee, detection future |

Si deux modules voisins recoivent chacun `module_gap_mm / 2`, le jeu total entre
leurs corps imprimables est `module_gap_mm`. Une face `internal` ou `welded` ne
recoit aucun jeu inter-module et aucune compensation imprimante, afin de
preserver la matiere continue d'un futur module composite.

Les rapports Markdown et JSON exposent les tolerances appliquees par face :
offset, source, identifiant de regle et raison.

## Clearances de cavites abstraites

Depuis P5-M002/P5-M003, certaines cavites peuvent omettre `clearance_mm` dans la
configuration. Le loader resout alors la valeur depuis le profil actif et expose
la source dans les rapports et la CAD IR :

| Type de cavite | Source de clearance | Statut |
| --- | --- | --- |
| `cards` | `card_clearance_mm` | implemente, non valide physiquement |
| `sleeved_cards` | `sleeved_card_clearance_mm` | implemente, non valide physiquement |
| `tokens` | `token_clearance_mm` | implemente, non valide physiquement |
| `dice` | `token_clearance_mm` | provisoire, non calibre comme valeur dediee |
| `meeples` | `meeple_clearance_mm` | implemente, non valide physiquement |

Les cavites `free` et `other` doivent garder un `clearance_mm` explicite. Aucune
nouvelle valeur par defaut n'est ajoutee pour les des tant qu'une calibration
physique ne justifie pas un champ dedie.

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

## Profils d'impression

Depuis `P3-M003`, le JSON V0 accepte un champ racine optionnel `print_profile`.
Le loader resout ce profil en `ToleranceProfile`, puis applique les champs
explicites de `tolerances` comme overrides champ par champ.

Profils implementes :

| Profil | Role | Statut |
| --- | --- | --- |
| `default` | valeurs V0 historiques | implemente, non valide physiquement |
| `pla_standard` | point de depart PLA standard | experimental |
| `petg_standard` | point de depart PETG standard | experimental |
| `fast_draft` | point de depart impression rapide | experimental |
| `fine_detail` | point de depart detail fin | experimental |

Un profil ne cache jamais ses valeurs finales : les rapports Markdown/JSON
exposent le profil et la table `tolerances` resolue. Les profils ne sont pas une
validation physique ; ils doivent etre calibres par impression reelle avant toute
promesse utilisateur.

## Statuts

Implemente :

- offsets simples sur X/Y/Z pour corps rectangulaires ;
- profils d'impression explicites et surchargeables ;
- classification explicite des faces rectangulaires simples ;
- moteur de regles de tolerance par role de face ;
- distinction peripherie, voisin, face exposee, face fonctionnelle, face interne
  et face soudee dans les regles ;
- exposition des classifications et tolerances appliquees dans les rapports ;
- clearances de cavites abstraites resolues depuis le profil actif pour cartes,
  cartes sleevees, tokens, des et meeples ;
- validation que les offsets ne rendent pas le corps non positif.

Experimental :

- detection automatique des roles `internal` et `welded` pour modules composites
  futurs ;
- valeurs de tolerance non calibrees physiquement.

Prevu :

- calibration physique des profils ;
- ergonomie avancee des cavites ;
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

Le protocole `docs/CALIBRATION_PROTOCOL.md` decrit les coupons, mesures et
criteres d'interpretation attendus avant toute modification des valeurs par
defaut ou declaration de profil stable.

## P39 - Application des jeux V0.1

P39 applique `content_clearance_mm` de chaque famille, ou le jeu global de
contenu, dans le logement derive. `layout_clearance_mm` reste volontairement
absent de ce calcul : ce jeu est entre bacs et sera applique une seule fois par
P41 lors du placement global.