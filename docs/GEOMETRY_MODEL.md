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
- `Layer` : tranche de hauteur ou etage logique dans la boite.
- `VolumetricCell` : reservation X/Y/Z, distincte d'un corps imprimable.
- `FreeVolume` : volume restant disponible ou volontairement laisse libre.
- `StackRule` : relation de support, empilement ou interdiction de charge.
- `RemovalOrder` : ordre de retrait attendu pour eviter de bloquer l'acces.

Ces concepts ne sont pas un solveur 3D implemente. Ils cadrent les futures
missions de Phase 8 et Phase 9.
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

Invariants P5-M004 :

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
- grille volumetrique 3D ;
- layers et reservations ;
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
- Une feature P5-M004 est CAD-agnostic, locale a une cavite et non executable par Fusion.
- Une coupe Fusion P6-M001 doit rester une soustraction rectangulaire verticale issue de la CAD IR.
- Une operation Fusion future doit mapper un concept deja resolu, pas inventer un
  nouveau modele metier.
- Les modules composites doivent conserver de la matiere continue sur leurs faces
  internes soudees.
