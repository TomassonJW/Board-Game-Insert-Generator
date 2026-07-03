# Geometry Model

## Axes

Toutes les dimensions sont en millimetres.

- X : largeur gauche-droite de la boite.
- Y : profondeur avant-arriere de la boite.
- Z : hauteur verticale.

L'origine V0 est le coin interieur bas-gauche-avant de la boite.

## Concepts

### Box

Volume interieur reel mesure dans la boite de jeu. Il represente la contrainte physique maximale, pas l'espace automatiquement imprimable.

### Usable volume

Volume disponible apres prise en compte des contraintes non imprimables :

- marge sous couvercle ;
- livrets ou regles conserves au-dessus ;
- plateaux ou materiel non modelise ;
- hauteur utile souhaitee.

En V0, cette notion est representee par les dimensions internes de boite et `usable_height_mm`.

### Cell

Portion theorique d'espace reservee a un module dans le layout.

Une cellule sert a raisonner sur l'organisation. Elle n'est pas directement le corps imprime. Deux cellules peuvent se toucher sans que les corps imprimables se touchent, car les jeux sont appliques ensuite.

### PrimitiveVolume

Volume rectangulaire de base. Il est utile pour representer une partie simple d'un module.

### CompositeModule

Module logique compose de plusieurs `PrimitiveVolume` fusionnes.

Exemples :

- module en L ;
- module en T ;
- deux bacs relies par un pont ;
- volume avec excroissance ;
- module qui contourne une zone libre.

Regle fondamentale : les primitives d'un meme module composite sont soudees. Aucun jeu ne doit etre applique entre leurs faces internes communes.

### PrintableBody

Geometrie finale imprimable apres application des tolerances externes et fonctionnelles.

En V0, un `PrintableBody` est encore un volume rectangulaire simple issu d'une cellule. A terme, il pourra etre le resultat d'une union de primitives et de features.

### Cavity

Volume retire a l'interieur d'un module pour contenir un objet.

Exemples :

- logement de cartes sleevees ;
- bac a tokens ;
- compartiment a meeples ;
- casier a des ;
- gorge de couvercle.

Les cavites ont leurs propres jeux. Le jeu autour d'une carte sleevee n'est pas le meme que le jeu entre deux modules voisins.

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

Le type de face determine le jeu applique. Le systeme ne doit jamais reduire aveuglement tous les volumes avec une seule valeur globale.

## Etat V0

Implemente :

- boite ;
- modules demandes ;
- cellules rectangulaires ;
- corps imprimables rectangulaires ;
- offsets par face ;
- representation conceptuelle des primitives et composites.

Prevu :

- cavites ;
- features ;
- unions de primitives ;
- coupes ;
- arrondis ;
- chanfreins ;
- sorties Fusion 360.
