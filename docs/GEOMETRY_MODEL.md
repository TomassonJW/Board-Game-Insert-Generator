# Geometry Model

## Axes et unites

Toutes les dimensions sont en millimetres.

- X : largeur gauche-droite de la boite.
- Y : profondeur avant-arriere de la boite.
- Z : hauteur verticale.

L'origine actuelle est le coin interieur bas-gauche-avant de la boite.

## Regle centrale

Le modele distingue :

- volume interieur reel ;
- volume utile ;
- cellule theorique ;
- corps imprimable ;
- primitive ;
- module composite ;
- cavite ;
- feature.

Cette separation evite de confondre organisation, impression et operations CAD.

## Concepts

### Concepts volumetriques cibles

La cible long terme ajoute des concepts encore majoritairement documentaires :

- `Asset` : objet reel du jeu a ranger, mesure exactement ou approximativement.
- `Reservation` : volume non imprimable reserve pour board, livret, plateau,
  couvercle ou espace de retrait.
- `Layer` : tranche de hauteur ou etage logique dans la boite ; P8-M001 le charge depuis `volumetric_grid.layers`.
- `VolumetricCell` : reservation X/Y/Z, distincte d'un corps imprimable ; P8-M001 expose les cellules `free`, `occupied`, `reserved` et `forbidden`.
- `FreeVolume` : volume restant disponible ou volontairement laisse libre ; P8-M001 le calcule approximativement par nombre de cellules libres.
- `StackRule` : relation de support, empilement ou interdiction de charge ; P8-M002 represente les premieres surfaces de support abstraites.
- `RemovalOrder` : ordre de retrait attendu pour eviter de bloquer l'acces ; P8-M002 le reporte sur placements et reservations.

Ces concepts ne constituent toujours pas un solveur 3D. P8-M001 implemente le
socle declaratif et les controles simples, P8-M002 ajoute les metadata de
support/retrait/accessibilite, mais le moteur ne place pas automatiquement les
modules.
### Contrat des dataclasses Phase 1

Les dataclasses du coeur Python sont des objets de valeur legers. Elles portent
les champs du domaine, mais ne cherchent pas a valider seules toute la
configuration.

Regle actuelle :

- les dimensions metier sont toujours exprimees en millimetres ;
- `Dimension3D` et `Point3D` representent des valeurs numeriques, sans unite
  alternative ;
- `BoxSpec` decrit le volume interieur et la hauteur utile demandee ;
- `ModuleRequest` decrit une demande utilisateur avant placement ;
- `Cell` represente uniquement une reservation theorique de layout ;
- `PrintableBody` represente un corps imprimable deja reduit par les offsets de
  tolerance ;
- `FaceName`, `FaceRole` et `FaceClassification` portent les metadonnees de
  classification de faces ;
- `PrimitiveVolume` et `CompositeModule` existent comme concepts ;
- `Cavity` et `Feature` pilotent maintenant des intentions abstraites validees,
  reportees et exportees en CAD IR, sans generation Fusion reelle.

La validation agregee reste dans `validation.py` afin de produire plusieurs
messages d'erreur actionnables en une seule passe. Les constructeurs ne doivent
donc pas devenir le lieu principal de validation sans decision explicite.

### Box

Volume interieur reel mesure dans la boite de jeu. Il represente la contrainte
physique maximale, pas l'espace automatiquement imprimable.

### Usable volume

Volume disponible apres prise en compte des contraintes non imprimables :

- marge sous couvercle ;
- livrets ou regles conserves au-dessus ;
- plateaux ou materiel non modelise ;
- hauteur utile souhaitee.

En V0, cette notion est representee par les dimensions internes de boite et
`usable_height_mm`.
La cible volumetrique decrit aussi les layers, reservations et volumes libres dans `docs/VOLUMETRIC_LAYOUT_STRATEGY.md`.

### Cell

Portion theorique d'espace reservee a un module dans le layout.

Une cellule sert a raisonner sur l'organisation. Elle n'est pas directement le
corps imprime. Deux cellules peuvent se toucher sans que les corps imprimables se
touchent, car les jeux sont appliques ensuite.

### Contrat de layout rectangulaire simple

Le layout Phase 2 manipule des rectangles theoriques dans le plan XY. Il ne
calcule pas de tolerance, ne choisit pas de cavite et ne produit pas de corps
CAD.

Strategies implementees :

- `row_fill` trie les modules par priorite descendante, puis par ordre de
  declaration ;
- chaque quantite de module devient une instance separee ;
- le placement remplit une ligne sur X, puis commence une nouvelle ligne sur Y ;
- la profondeur d'une ligne est la plus grande dimension Y des cellules de cette
  ligne ;
- la rotation est decidee module par module selon `allow_rotation` et seulement
  pour faire tenir la cellule dans la ligne ou dans la boite.
- `grid` trie les modules avec la meme regle, calcule une cellule reguliere XY
  depuis la plus grande empreinte de module orientee, puis place les instances
  ligne par ligne ;
- `grid` garde une hauteur Z par module, meme si la reservation XY est reguliere
  pour toutes les cellules ;
- `grid` refuse la configuration si le nombre de cellules regulieres depasse la
  profondeur disponible de la boite.

Identifiant reserve :

- `columns` : colonnes explicites futures pour regroupements par type ou usage.

Cet identifiant reserve est connu du contrat interne, mais il reste refuse par la
validation tant qu'une mission dediee ne l'implemente pas.

### PrimitiveVolume

Volume rectangulaire de base. Il est utile pour representer une partie simple
d'un module.

### CompositeModule

Module logique compose de plusieurs `PrimitiveVolume` fusionnes.

Exemples :

- module en L ;
- module en T ;
- deux bacs relies par un pont ;
- volume avec excroissance ;
- module qui contourne une zone libre.

Regle fondamentale : les primitives d'un meme module composite sont soudees.
Aucun jeu ne doit etre applique entre leurs faces internes communes.

### PrintableBody

Geometrie finale imprimable apres application des tolerances externes et
fonctionnelles.

Dans l'etat actuel, un `PrintableBody` est encore un volume rectangulaire simple
issu d'une cellule. A terme, il pourra etre le resultat d'une union de primitives
et de features.

### Cavity

Volume rectangulaire retire a l'interieur d'un module pour contenir un objet.
Depuis P5-M001/P5-M002/P5-M003, une cavite simple porte :

- un identifiant stable ;
- un type fonctionnel ;
- une origine locale dans le module ;
- des dimensions internes ;
- une clearance fonctionnelle ;
- une source de clearance (`explicit` ou profil de tolerance) ;
- un commentaire optionnel.

Exemples :

- logement de cartes sleevees ;
- bac a tokens ;
- compartiment a meeples ;
- casier a des ;
- gorge de couvercle.

Les cavites ont leurs propres jeux. Le jeu autour d'une carte sleevee n'est pas
le meme que le jeu entre deux modules voisins. Depuis P5-M001, la validation
porte sur l'enveloppe externe du module, les parois X/Y minimales et le fond
minimal. Depuis P5-M002/P5-M003, les cavites `cards`, `sleeved_cards`,
`tokens`, `dice` et `meeples` peuvent omettre `clearance_mm` : le moteur
utilise alors la valeur de profil active correspondante et refuse une valeur
explicite inferieure. Les des utilisent provisoirement `token_clearance_mm`
tant qu'aucune calibration ne justifie un champ dedie. La cavite est transportee
dans la CAD IR. Depuis P6-M001, les cavites rectangulaires simples peuvent etre
coupees dans Fusion par l'adaptateur, avec validation manuelle requise. Cette
generation ne couvre pas les features ergonomiques, les arrondis ou les booleans
complexes.

Depuis P5-M004, une cavite peut aussi porter des `Feature` ergonomiques
abstraites. Depuis P6-M002, une partie limitee de ces features peut etre consommee
par l'adaptateur Fusion : les encoches simples de paroi sont executees comme
coupes rectangulaires. Les autres features restent des intentions abstraites.

### Feature

Feature abstraite associee a une cavite ou, plus tard, a un corps imprimable.
Depuis P5-M004, les features implementees sont limitees aux intentions
ergonomiques de cavites :

- `finger_notch` : encoche de doigt simple ;
- `side_notch` : encoche laterale ;
- `center_notch` : encoche centrale ;
- `half_moon_notch` : encoche en demi-lune decrite abstraitement ;
- `rounded_floor` : intention de fond arrondi ou rayon de fond ;
- `grip_aid` : aide abstraite de prise en main.

Chaque feature porte un identifiant, un kind, un placement humain, une position
locale dans la cavite, une taille optionnelle, un rayon optionnel et un
commentaire. Les encoches et aides de prise en main requierent une taille. Les
demi-lunes et fonds arrondis requierent un rayon.

Taxonomie P6-M003 :

- `top_open_rectangular_notch` : morsure rectangulaire ouverte par le haut,
  `fusion-validated`, `print-validated: false` ;
- `top_open_half_moon_notch` : intention de demi-lune courbe, fallback Fusion
  rectangulaire top-open ;
- `through_wall_window` : fenetre fermee, explicitement distincte d'une encoche
  utilisable ;
- `blind_internal_thumb_scoop` : creux interne non traversant avec peau externe
  a preserver ;
- `side_relief_notch` : degagement lateral pour cartes, tuiles ou assets plats ;
- `dual_side_card_access` : acces bilateral a un paquet de cartes ou tuiles.

Invariants P5-M004/P6-M003 :

- la feature reste dans les dimensions locales de la cavite ;
- le rayon reste abstrait et borne par la taille XY de la cavite ;
- le statut reste `abstract_only` ;
- par defaut, `fusion_generation` reste `not_implemented` ;
- P6-M002 autorise seulement le mapping des encoches simples de paroi vers une
  coupe rectangulaire Fusion top-open issue de la CAD IR ;
- une `half_moon_notch` executee par P6-M002 reste une approximation
  rectangulaire top-open de bounding box, pas une demi-lune courbe reelle ;
- aucune coupe courbe, fond arrondi, boolean complexe, fillet ou conge n'est
  genere dans Fusion.

Exemples futurs hors perimetre P5-M004 :

- chanfrein ;
- embossage ;
- gravure ;
- texte ;
- texture ;
- trou ;
- poignee ;
- charniere ;
- couvercle.

## Faces

Une face rectangulaire est identifiee par son nom geometrique : `x_min`, `x_max`,
`y_min`, `y_max`, `z_min` ou `z_max`.

Elle porte un role explicite :

- `peripheral` : contre la boite ;
- `neighbor` : voisine d'un autre module ;
- `exposed` : libre dans une zone non occupee ;
- `functional` : liee a une contrainte fonctionnelle comme le dessous ancre ou le
  dessus sous couvercle ;
- `internal` : interne a un futur module composite ;
- `welded` : jonction soudee future entre primitives du meme module.

Depuis `P3-M002`, cette classification pilote une application de tolerance
explicite et testee par role de face. Elle ne valide pas physiquement les jeux
et ne change pas les valeurs de tolerance par defaut. Les exemples existants
gardent leurs dimensions imprimables attendues.

## Etat actuel

Implemente :

- boite ;
- modules demandes ;
- cellules rectangulaires ;
- corps imprimables rectangulaires ;
- offsets par face pour cas simples ;
- classification explicite des faces pour corps rectangulaires simples ;
- regles de tolerance appliquees par role de face ;
- representation conceptuelle des primitives et composites ;
- cavites rectangulaires simples abstraites dans la configuration, la validation,
  les rapports et la CAD IR ;
- features ergonomiques abstraites de cavites dans la configuration, la
  validation, les rapports et la CAD IR ;
- generation Fusion codee de cavites rectangulaires simples depuis la CAD IR,
  encore sous validation manuelle Fusion.

Experimental :

- detection automatique des roles `internal` et `welded` non exploitee par le
  layout ;
- concepts `Feature` exportes comme intentions abstraites mais non generes dans
  Fusion ;
- cavites rectangulaires Fusion codees mais non encore validees manuellement pour
  P6-M001 ;
- `CompositeModule` present mais non exploite par le layout.

Prevu :

- modele d'assets ;
- solveur volumetrique 3D ;
- reservations derivees d'assets ;
- ordre de retrait et accessibilite ;
- unions de primitives ;
- coupes avancees ;
- arrondis ;
- chanfreins ;
- sorties Fusion 360 ;
- validation par impression reelle.

## Criteres de qualite geometrique

- Une dimension negative ou nulle est invalide.
- Une cavite ne doit pas casser les parois minimales.
- Une feature P6-M003 est CAD-agnostic, locale a une cavite et porte une taxonomie resolue.
- Une grille P8-M001/P8-M002 est CAD-agnostic, declarative, discrete en X/Y/Z et ne genere aucune geometrie Fusion.
- Une surface de support P8-M002 est `abstract_only` et non validee physiquement.
- Une coupe Fusion P6-M001 doit rester une soustraction rectangulaire verticale issue de la CAD IR.
- Une operation Fusion future doit mapper un concept deja resolu, pas inventer un
  nouveau modele metier.
- Les modules composites doivent conserver de la matiere continue sur leurs faces
  internes soudees.

## P39 - Enveloppes de logements derivees

Les dimensions P39 sont des enveloppes internes minimales : elles incluent le
jeu autour des pieces, les cloisons internes, les parois externes et le fond.
Elles ne constituent pas encore une cavite materialisee. Les formes non
rectangulaires sont representees par une enveloppe rectangulaire sure en V0.1 ;
les formes ergonomiques restent V0.2.

## P40 - Reservation de pile superieure

La pile plateaux/livrets est une `Reservation` non imprimable : son empreinte et
sa hauteur diminuent le volume de stockage disponible. Son support est une
contrainte de placement, pas une feature geometrique ou un corps imprimable.
P41 devra prouver la continuite de cette surface apres placement.

## P41/P42 - Comportement historique rejete

P41 decompose le volume libre et P42 peut materialiser certaines regions en bacs
vides automatiques. Ce comportement reste dans le code comme fondation
experimentale, mais il est `superseded-for-product` par ADR-0054. Une cellule
libre n est jamais un corps imprimable par nature.

## P53 - Cavite calibree et enveloppe exterieure extensible

Chaque bac distingue obligatoirement :

- `cavity_envelopes` : volumes utiles calibres depuis assets, quantites et jeux ;
- `minimum_outer_envelope` : borne basse incluant cavites, cloisons, parois et
  fond minimaux ;
- `final_outer_envelope` : dimensions et position choisies par le solveur global ;
- `absorbed_material` : surplus entre minimum et final, reparti autour et sous
  les cavites.

Invariants :

- les cavites gardent leurs dimensions pendant l expansion de l enveloppe ;
- le surplus X/Y reste de la matiere autour des cavites ;
- le surplus Z reste sous les cavites, sauf contrainte explicite differente ;
- chaque enveloppe finale reste un parallelepipede V0.1 constructible ;
- le nombre de corps provient des groupes et complements explicites, jamais des
  regions libres ;
- les jeux contre la boite et entre bacs sont des vides techniques.

La CAD IR transporte minimum, final, cavites et repartition du surplus. Fusion ne
recalcule aucune de ces decisions.

## P55 - Repere stable des cavites et enveloppes extensibles

Une cavite P55 est exprimee dans le repere minimum_outer_envelope.local. Son
origine locale, ses dimensions et son jeu sont figes par la derivation P39.
L enveloppe finale contient ce repere sans le deformer : le surplus X/Y est
distribue autour de lui et le surplus Z sous lui.

La translation du repere minimal dans l enveloppe finale est reportee separement
par minimum_envelope_origin_in_final_mm. Cette translation ne constitue pas un
recalcul de l arrangement local. P57 choisira conjointement enveloppes finales et
placements ; P59 materialisera ensuite exactement ce plan.

## P57 - Partition complete sans corps automatique

Le plan bgig.partition_plan.v1 utilise des partitions rectangulaires en rangees.
Chaque placement porte origine monde, taille monde, rotation Z, enveloppe finale
locale, cavites P55 et repartition du surplus. Une solution `constructed` prouve :

- tous les corps restent dans la boite et sous la reservation P40 ;
- les corps ne se chevauchent pas et les jeux demandes sont respectes ;
- chaque volume imprimable hors jeux appartient a un corps explicitement demande ;
- les enveloppes finales sont revalidees par P55 ;
- les cavites et leur repere local ne changent pas ;
- `unassigned_printable_volume_mm3 = 0` et `automatic_body_count = 0`.

Les complements exacts sont des participants fixes. Un complement `auto` ou de
hauteur incompatible est refuse ; le solveur ne cree jamais une lamelle pour
fermer la partition. Le score de simplicite compare une famille bornee de
candidats et ne revendique pas l optimalite mathematique globale.

## Dimensions physiques et orientation P62

Pour un element carte, `base_dimensions_mm` decrit le paquet physique avant
orientation. `dimensions_mm` est l enveloppe XYZ resolue que consomment le
dimensionnement de cavite et le solveur. Une orientation ne modifie jamais la
mesure physique source ; elle permute seulement son enveloppe de rangement.

Une surcharge manuelle (`dimension_source = explicit`) est prioritaire sur le
format catalogue. `auto` choisit deterministiquement l empreinte minimale parmi
les orientations compatibles avec la hauteur disponible courante. P64 compose
ensuite ces envelopes par etages et conserve les cavites P55 dans leur repere
local ; P62 ne recalcule pas les dimensions physiques source.


## P63 - Reservations superieures localisees

Une reservation `bgig.top_inset_reservations.v1` est un volume de soustraction
non imprimable ouvert sur le plan superieur de conception. Elle ne devient ni
une cavite de contenu ni un corps. Hors de son empreinte, chaque corps demande
conserve son sommet au plan de conception.

Pour chaque plateau ou livret, le contrat fixe : empreinte physique, jeu XY,
rotation 0/90, origine XY, epaisseur cumulee, profondeur depuis le sommet, ordre
de retrait, plan d appui et prise rectangulaire. Deux empreintes qui se
chevauchent se composent en Z selon leur ordre ; deux empreintes disjointes
partagent le meme plan superieur.

La coupe locale doit rester dans le blank, laisser au moins le fond minimal du
corps et ne jamais descendre sous le fond d une cavite intersectee. Les surfaces
de cavite presentes au plan d appui sont retranchees de la couverture support.
La CAD IR transporte les operations `subtract_top_inset_reservation` et
`subtract_top_inset_grip` dans le repere `body.local`. Fusion execute ces
operations sans recalculer placement, profondeur ou support.

## P64 - Composition volumetrique par etages

Un `Stage` P64 est une tranche logique calculee, pas un corps automatique. Il
porte `origin_z_mm`, `height_mm`, les corps demandes et un etat XY. Les corps
restent les seuls volumes imprimables : leurs origines monde, rotations et
cavites sont ensuite transportees vers la CAD IR.

Pour chaque axe d un conteneur, `Auto` accepte la taille calculee, `Cible`
exprime un objectif souple et `Fixe` impose une taille dure. Un etage superieur
doit atteindre un recouvrement d appui minimal sur l etage immediatement
inferieur ; le retrait est ordonne du sommet vers le bas. Aucune surface d appui
ni cale n est inventee.

`complete` ferme le volume technique avec les seuls corps demandes et jeux ;
`proposal_with_residuals` transporte des zones non imprimables et une suggestion
optionnelle ; `impossible` ne fournit pas de projection de solution. Une
reservation superieure P63 ne s applique qu au corps de l etage le plus haut
qu elle intersecte, jamais aux corps inferieurs qui partagent son empreinte.
## P64 - Intervalles Z hybrides et profondeur utile sous plateau

Le solveur conserve les etages XY historiques, puis peut construire des piles
verticales independantes. Les bornes Z de tous les corps produisent des
intervalles globaux de lecture ; un corps haut peut traverser plusieurs
intervalles pendant qu une pile voisine change de corps. Chaque corps reste un
corps explicitement demande, sans cale ni remplissage automatique.

Pour une cavite de contenu recouverte par une reservation superieure, la
profondeur de coupe finale est :

    profondeur_finale = profondeur_asset_de_base + profondeur_encastrement_cumulee

La compensation retenue est le maximum des profondeurs depuis le sommet parmi
les reservations qui recouvrent la cavite. Le fond restant du corps doit rester
superieur ou egal au fond minimal ; sinon la proposition est bloquee avant CAD.
Le contrat conserve separement les dimensions de base et la compensation.

## P65 - Intervalle technique Z entre etages

Deux conteneurs empiles ne partagent plus implicitement une face Z. Leur pose est
separee par container_z_clearance_mm. Cet intervalle appartient au volume
technique reserve : il reduit la hauteur distribuable aux corps, apparait dans les
origines CAD IR et ne constitue ni un PrintableBody, ni une Reservation de
plateau, ni un etage fonctionnel supplementaire. Les etages de sortie restent les
tranches ou au moins un corps commence.
## P65-M002 planifie - Enveloppe de placement distincte

Le solveur doit construire une enveloppe de placement X-Y de la boite en
retirant `container_box_xy_clearance_mm` sur chacun des quatre cotes. Les corps
sont ensuite places dans cette enveloppe avec `layout_clearance_mm` uniquement
entre voisins. Ces deux reductions sont independantes et doivent etre validees
separement.

En Z, l origine du premier corps reste `0`. La hauteur de conception integre deja
`box.lid_clearance_mm` au sommet ; `container_z_clearance_mm` ne s applique
qu entre deux enveloppes empilees. Aucun intervalle de boite ne doit etre
reclasse comme etage, reservation, support ou corps imprimable.

## P64-V2H03 - Variantes locales certifiées

Une variante interne de conteneur n'est ni un nouveau corps, ni une forme P45,
ni une rotation globale. Elle associe, dans le repère
`minimum_outer_envelope.local`, une enveloppe minimale et un layout complet de
cavités dont dimensions, quantités, formes résolues et jeux sont inchangés.

Le certificat local vérifie couverture des contenus, non-recouvrement, parois,
cloisons, fond, repère, digest et absence de corps automatique. Il ne certifie
pas la boîte, les jeux externes, les réservations supérieures, l'appui ou le
retrait : ces contraintes restent au certificat global P64 après choix de la
variante et du placement.

P45 possède les futures sémantiques `standard/auto`, `rangée`, `colonne
verticale` et les formes ergonomiques. P64-V2H03 peut seulement produire des
relayouts techniques rectangulaires des cavités existantes. Une rotation XY de
90 degrés reste une option de placement globale et ne crée pas une variante
locale supplémentaire.

Voir ADR-0070 et
`docs/P64_V2H03_INTERNAL_VARIANT_COORDINATION_CONTRACT.md`.

## Implémentation P64-V2H03B

Une variante certifiée contient enveloppe minimale, paroi, fond, repère local,
cavités triées, origines, dimensions, quantités, jeux effectifs et leurs
sources. Le digest exclut provenance producteur, origine boîte et rotation
globale ; les miroirs restent distincts.

Le certificat vérifie couverture, invariants de contenus, valeurs physiques,
géométrie finie, cloisons, non-recouvrement, enveloppe serrée, axes Fixe,
absence de corps automatique et digest. Cible reste préférentiel et Auto libre.


## P64-A02 — géométrie des capacités dérivées

InternalOpportunityZone est une AABB ou union orthogonale conservatrice située
dans l'enveloppe extérieure finale d'un conteneur. Elle décrit du surplus solide
qui pourrait être reconverti par une nouvelle dérivation P45. Elle n'est pas une
cavité existante et ne doit pas être soustraite par Fusion à sa seule présence.

BoxReserveBay est une région monde explicitement volontaire, extérieure aux
corps imprimables et intérieure à l'enveloppe utile de boîte. Elle doit respecter
jeux globaux, réservations, accès et insertion. Un EMS, un canal technique ou un
résiduel fortuit ne devient jamais une BoxReserveBay sans décision de
finalisation et certificat.

Les deux classes portent bornes, repère, provenance, contraintes admissibles et
digests. Elles ne possèdent ni forme ergonomique, ni asset, ni conteneur. P45
reste propriétaire de la géométrie locale créée après une action utilisateur ;
P64 vérifie ensuite la compatibilité monde.
