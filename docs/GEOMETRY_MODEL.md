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
- `PrimitiveVolume`, `CompositeModule`, `Cavity` et `Feature` existent comme
  concepts, mais ne pilotent pas encore une generation complete.

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

### Cell

Portion theorique d'espace reservee a un module dans le layout.

Une cellule sert a raisonner sur l'organisation. Elle n'est pas directement le
corps imprime. Deux cellules peuvent se toucher sans que les corps imprimables se
touchent, car les jeux sont appliques ensuite.

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

Volume retire a l'interieur d'un module pour contenir un objet.

Exemples :

- logement de cartes sleevees ;
- bac a tokens ;
- compartiment a meeples ;
- casier a des ;
- gorge de couvercle.

Les cavites ont leurs propres jeux. Le jeu autour d'une carte sleevee n'est pas
le meme que le jeu entre deux modules voisins.

### Feature

Detail ajoute ou retire sur un corps imprimable.

Exemples :

- encoche de doigt ;
- chanfrein ;
- arrondi ;
- embossage ;
- gravure ;
- texte ;
- texture ;
- trou ;
- poignee ;
- charniere ;
- couvercle.

## Faces

Une face peut etre :

- peripherique contre la boite ;
- voisine d'un autre module ;
- libre dans une zone non occupee ;
- interne a un module composite ;
- fonctionnelle pour une cavite ou un couvercle.

Le type de face determine le jeu applique. Le systeme ne doit jamais reduire
aveuglement tous les volumes avec une seule valeur globale.

## Etat actuel

Implemente :

- boite ;
- modules demandes ;
- cellules rectangulaires ;
- corps imprimables rectangulaires ;
- offsets par face pour cas simples ;
- representation conceptuelle des primitives et composites.

Experimental :

- detection de voisinage par contact de cellules ;
- concepts `Cavity` et `Feature` presents mais non generes ;
- `CompositeModule` present mais non exploite par le layout.

Prevu :

- cavites ;
- features ;
- unions de primitives ;
- coupes ;
- arrondis ;
- chanfreins ;
- sorties Fusion 360 ;
- validation par impression reelle.

## Criteres de qualite geometrique

- Une dimension negative ou nulle est invalide.
- Une cavite ne doit pas casser les parois minimales.
- Une feature est CAD-agnostic tant qu'elle reste dans le moteur.
- Une operation Fusion future doit mapper un concept deja resolu, pas inventer un
  nouveau modele metier.
- Les modules composites doivent conserver de la matiere continue sur leurs faces
  internes soudees.
