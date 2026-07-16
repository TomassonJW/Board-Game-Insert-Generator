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
## P40 - Jeu autour de la pile superieure

P40 applique `layout_clearance_mm` autour de l empreinte de pile et une fois sous
la pile, entre les plateaux/livrets et les bacs. La marge sous couvercle reste
integree a `usable_height_mm` et n est pas ajoutee une seconde fois.
## P53 - Epaisseurs minimales et epaisseurs finales

Les epaisseurs de paroi et de fond saisies dans l editeur sont des minima de
fabrication. Elles servent a construire `minimum_outer_envelope`. Elles ne sont
pas des valeurs finales quand le bac doit absorber du volume.

L expansion de `final_outer_envelope` ajoute de la matiere apres application des
jeux de cavite et des jeux externes. Elle ne modifie jamais :

- le jeu autour des assets ;
- le jeu total entre deux bacs ;
- le jeu peripherique contre la boite ;
- la marge sous couvercle.

Les jeux restent du vide et ne sont pas absorbes. Le surplus de matiere est
trace separement pour chaque face et pour le fond, afin que le mode avance puisse
plus tard verrouiller ou ponderer sa repartition sans changer les valeurs de
tolerance.

## Revue P60 - Presentation sans changement de valeurs

Les jeux sont regroupes dans l ecran Reglages et chaque libelle precise `par
cote` ou `jeu total`. La hauteur de conception est derivee de la hauteur
interieure moins le jeu superieur ; `usable_height_mm` ne doit plus apparaitre
comme une seconde mesure novice contradictoire.

La proposition utilisateur de 0,1 mm n est pas adoptee comme valeur generale :
elle peut etre insuffisante en FDM, notamment comme jeu total entre corps. Les
defaults existants restent experimentaux jusqu aux coupons et toute modification
reste soumise a la gate humaine du modele de tolerance.

## P65 - Jeux anisotropes entre conteneurs

Le projet distingue layout_clearance_mm, presente dans l interface
comme jeu X-Y entre conteneurs, et container_z_clearance_mm, jeu vertical entre
deux enveloppes empilees. Un ancien projet sans champ Z herite de sa valeur X-Y ;
un nouveau projet ecrit les deux valeurs explicitement, toutes deux a 0,6 mm par
defaut. Aucun nouveau calibrage physique n est revendique.

Le jeu Z consomme le budget de hauteur entre deux corps, reste un vide technique
non imprimable et n ajoute aucune cale ni support automatique. Le contrat d appui
reconnait l alignement des faces separees par ce vide configure ; il ne pretend pas
a un contact physique. Ces valeurs restent experimentales et a valider par
impression reelle.
## P65-M002 planifie - Frontieres boite et voisinage

Le MVP doit exposer quatre roles distincts, sans les additionner deux fois :

| Interface | Champ | Semantique |
| --- | --- | --- |
| conteneur / boite X-Y | `container_box_xy_clearance_mm` | marge par cote sur le perimetre X-Y |
| conteneur / conteneur X-Y | `layout_clearance_mm` | ecart total entre deux corps voisins |
| conteneur / conteneur Z | `container_z_clearance_mm` | ecart total entre deux corps empiles |
| conteneur / boite Z haut | `box.lid_clearance_mm` | marge unique sous le haut interieur/couvercle |

La face basse reste ancree a `Z=0` et ne recoit pas de jeu. Un jeu inferieur
necessiterait une geometrie porteuse explicite et reste hors MVP. Pour conserver
les anciens projets, l absence de `container_box_xy_clearance_mm` doit heriter de
`layout_clearance_mm`. Le zero est une valeur saisissable, pas un nouveau default.

Le solveur doit utiliser le jeu boite X-Y uniquement pour reduire son rectangle
interieur et positionner sa premiere/derniere enveloppe. Il doit utiliser le jeu
inter-conteneurs X-Y uniquement entre voisins. En Z, la marge superieure reduit
la hauteur de conception une seule fois ; le jeu inter-conteneurs est reserve
uniquement entre etages.

## P67-V - Jeux herites et overrides par objet

La revue humaine P67-V accepte le besoin produit suivant, sans changer encore le
schema, les formules ou les valeurs numeriques : chaque plateau, livret, asset
et conteneur doit afficher un jeu effectif herite d un default pertinent, puis
permettre un override facultatif et independant en X, Y et Z.

Le motif UX est commun, mais les roles physiques restent distincts :

| Objet | Interface physique | Source actuelle | Cible planifiee |
| --- | --- | --- | --- |
| Asset | asset / cavite interne | `default_content_clearance_mm`, puis `content_clearance_mm` scalaire optionnel | default de cavite par role, override X/Y/Z par asset |
| Plateau ou livret | element plat / top inset | `layout_clearance_mm` reutilise en X/Y, aucun override par objet, aucun jeu Z explicite | default d encastrement, override X/Y/Z par element plat |
| Conteneur | corps / boite ou corps voisin | defaults globaux P65, separes par cote/total et par interface | override externe X/Y/Z par conteneur, resolu sans double comptage |

Pour chaque axe, une absence d override signifie `Herite du projet`. La sortie
derivee doit exposer la valeur effective et sa source : default de role, profil,
override de l objet ou compatibilite historique. Un zero explicite reste
different d une valeur absente.

La presentation ne doit jamais laisser croire qu un meme nombre a le meme sens
partout. Pour un asset ou un element plat, X/Y decrivent le jeu de logement
autour de la piece. Pour un conteneur, le jeu est une interface externe et doit
rester compatible avec les notions P65 `par cote` contre la boite et `total`
entre voisins. Le jeu Z d un top inset augmente la profondeur utile de
l encastrement ; sa composition entre elements plats superposes doit etre
specifiee avant implementation.

P67-V ne change aucun default et ne promeut pas la valeur observee
0,2 / 0,2 / 0 mm en valeur universelle. Les choix suivants restent a figer par
P44-M008 et une gate humaine de tolerance :

- nom et forme exacte des champs additifs ;
- semantique par cote ou totale de chaque axe ;
- regle de resolution entre deux conteneurs ayant des overrides differents ;
- interaction avec boite, voisins, etages et marge sous couvercle ;
- composition Z de plusieurs plateaux/livrets superposes ;
- migration des scalaires historiques sans changement de resultat ;
- defaults affiches pour chaque role et protocole de calibration P68.

P44-M008 est une mission de contrat et d ADR, sans code. P44-M009 pourra
implementer le schema, le loader, le coeur, la palette, les rapports et la CAD
IR uniquement apres acceptation de ces regles. `print-validated: false` reste
obligatoire.

## P44-M008 - Proposition de jeux par role (2026-07-15)

Le contrat P44_M008_TOLERANCE_OVERRIDE_CONTRACT propose asset-cavite,
plat-encastrement et conteneur externe, avec zero explicite, sources effectives
et semantiques P65 preservees. Gate humaine obligatoire avant P44-M009. Aucun
default, formule executable ou resultat existant ne change.

## P44-M009 - Jeux effectifs par role (2026-07-16)

P44-M009 implemente l option B acceptee : asset_cavity, flat_inset et
external_container. Les valeurs se resolvent par axe : override objet,
scalaire historique compatible, puis default de role. Null herite ; zero est
effectif. Les conteneurs externes portent between_mm (voisinage total) et
box_per_side_xy_mm (perimetre par cote). Chaque paire utilise max, jamais une
somme, y compris les interfaces d etage. Le schema est additif et les rapports,
palette et CAD IR portent valeurs et provenance. fusion-validated: false ;
print-validated: false.

## P44-M009H01 - Édition horizontale commune dans la palette

Le moteur conserve ses vecteurs X/Y/Z et leur provenance pour la compatibilité,
mais la palette 0.1.32 n’autorise plus deux saisies horizontales indépendantes.
Chaque override unitaire utilise un champ X/Y commun et un champ Z distinct
lorsqu’il existe. Les champs sont rangés dans un volet replié par objet.

Les projets anisotropes existants restent inchangés jusqu’à une nouvelle saisie
X/Y, qui unifie alors les deux axes. Aucun jeu par défaut ni aucune formule
physique ne change. print-validated: false.
