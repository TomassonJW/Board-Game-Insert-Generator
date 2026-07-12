# Vision produit canonique - V0.1, V0.2 et V0.3

## Statut

Cette vision est acceptee par Thomas le 2026-07-12. Elle est la reference
produit prioritaire de BGIG. En cas de conflit avec un ancien lot P29 a P35,
ce document et ADR-0047 prevalent.

## Promesse simple

Une personne mesure sa boite, decrit ce qu'elle veut ranger dans des tableaux
simples, indique quelles pieces doivent partager le meme bac, puis clique sur
`Construire mon insert`. BGIG produit un rangement complet qui tient dans le
volume disponible, explique ce qui a ete fait et refuse clairement ce qui est
physiquement impossible.

L'interface parle de boite, pieces, bacs, plateaux, livrets, parois et jeu. Les
termes `asset`, `candidate`, `layer`, `policy`, `CAD IR` et `digest` restent dans
le moteur, les exports techniques ou le mode expert.

## Ordre des versions non negociable

1. `V0.1 - MVP fonctionnel complet` : saisir, organiser, remplir et construire.
2. `V0.2 - Formes et ergonomie` : arrondis, encoches, fonds faciles a vider.
3. `V0.3 - Couvercles` : encastrable puis coulissant interieur.

La V0.2 ne commence pas avant l'acceptation fonctionnelle de la V0.1. La V0.3
ne commence pas avant l'acceptation de la V0.2. Une exploration technique plus
avancee peut rester dans l'historique, mais elle ne doit ni guider le backlog ni
apparaitre dans le parcours principal.

## V0.1 - MVP fonctionnel complet

### 0. Add-in Fusion 360 comme produit unique

Le produit est installe et utilise dans Fusion 360. Le bouton BGIG ouvre une
palette HTML embarquee dans l add-in ; cette palette porte tout le parcours de
creation et de resultat. Aucun navigateur externe, serveur loopback, processus
Vite ou application separee n est requis.

La palette parle de boite, pieces, bacs, plateaux, livrets, parois et jeux. Un
mode avance expose progressivement les axes extensibles, dimensions verrouillees,
preferences de surplus et diagnostics. La commande Fusion CommandInputs reste
un recours expert et de smoke, pas le parcours normal.

Le moteur Python pur reste hors adsk et source de verite. La palette transmet un
projet versionne au bridge ; le coeur calcule ; l adaptateur Fusion materialise.
La scene CAD ne devient jamais le projet canonique.

### 1. Mesurer la boite principale

L'ecran principal demande en langage courant :

- largeur interieure ;
- profondeur interieure ;
- hauteur interieure reellement disponible ;
- jeu minimal commun entre les volumes imprimes et contre la boite ;
- epaisseur minimale par defaut des parois et du fond.

Toutes les dimensions metier sont en millimetres. Le jeu entre bacs et le jeu
autour des pieces sont deux notions distinctes : le premier gouverne le plan de
boite ; le second gouverne l'ajustement des logements et reste un reglage de
fabrication explicite.

### 2. Decrire les pieces du jeu

Un tableau dynamique permet d'ajouter et supprimer autant de lignes que
necessaire. Chaque ligne contient au minimum :

| Champ UI | Sens produit |
| --- | --- |
| Nom | Nom humain de la piece ou famille de pieces |
| Forme courante | Rond, carre, rectangle, cartes, cube/de, pion ou sur mesure |
| Dimensions | Champs adaptes a la forme, toujours normalises en enveloppe X/Y/Z |
| Quantite | Nombre d'exemplaires a ranger |
| Bac cible | `Nouveau bac`, `Bac 1`, `Bac 2`, etc. |
| Jeu autour des pieces | Valeur par defaut, avec surcharge experte possible |

Le menu `Bac cible` est la traduction simple du regroupement. Deux lignes qui
pointent vers `Bac 2` doivent etre rangees dans le meme corps imprimable, avec
des logements distincts si necessaire. Une ligne pointant vers un autre numero
doit produire un autre bac. Le moteur conserve des identifiants stables, mais
l'utilisateur voit des noms et numeros lisibles.

Les presets de forme n'inventent pas un modele 3D detaille de chaque piece. Ils
definissent une enveloppe et une geometrie de logement fiable : cylindrique pour
un rond, prismatique pour carre/rectangle/cube, enveloppe rectangulaire explicite
pour `sur mesure` dans le MVP. Les formes libres detaillees restent ulterieures.

### 3. Regler les bacs demandes

Une liste de bacs est derivee des choix du tableau des pieces. Pour chaque bac,
l'utilisateur peut nommer le bac et surcharger l'epaisseur minimale de paroi.
Par defaut, le fond reprend la meme epaisseur minimale ; un reglage expert peut
les dissocier plus tard sans changer le parcours novice.

Le moteur derive les cavites calibrees et les dimensions exterieures minimales
depuis les pieces, leurs quantites et leurs jeux. Ces dimensions minimales ne
sont pas les dimensions finales du bac. Le solveur agrandit ensuite l enveloppe
exterieure du bac pour participer au remplissage complet de la boite, sans
agrandir les cavites. Le surplus devient de la matiere dans les parois autour des
cavites et dans le fond sous les cavites. Il ne demande pas a l utilisateur de
dessiner manuellement un `module candidat`.

### 4. Ajouter plateaux et livrets

Un second tableau dynamique, separe du contenu a ranger, gere les elements poses
au-dessus des bacs :

| Champ UI | Sens produit |
| --- | --- |
| Nom | Plateau principal, livret de regles, aide de jeu, etc. |
| Type | Plateau, livret ou autre element plat |
| Largeur et profondeur | Encombrement replie reel |
| Epaisseur unitaire | Epaisseur d'un exemplaire |
| Quantite | Nombre d'exemplaires |
| Ordre dans la pile | Automatique par defaut, ajustable en mode avance |

BGIG calcule la hauteur totale de cette pile et la reserve au sommet. Les bacs
situes dessous sont ajustes pour ne jamais depasser. Leurs faces superieures
doivent former un support coherent sous les plateaux et livrets, avec des
encastrements ou retraits correspondant aux empreintes reelles lorsqu'ils sont
necessaires. Une reservation n'est jamais un bac imprimable.

### 5. Absorber le volume dans les bacs demandes

Apres reservation des plateaux/livrets et des jeux obligatoires, les bacs demandes
se partagent tout le volume imprimable restant. Les cavites restent calibrees sur
les assets. Les enveloppes exterieures grandissent pour former une partition
simple et complete : surplus X/Y dans les parois, surplus Z sous les cavites dans
les fonds.

Le moteur ne cree aucun bac de remplissage automatique. Un `Bac vide`, un
`Remplissage plein` ou un `Separateur` existe uniquement si l utilisateur l ajoute
explicitement dans l editeur. Ces elements explicites participent alors a la
partition comme les autres corps demandes.

Un projet avec un seul bac peut donc remplir presque toute la boite avec un seul
grand corps et une petite cavite calibree. Un projet avec plusieurs bacs repartit
le volume entre eux. Les seuls vides externes autorises sont les jeux demandes
entre les bacs, contre la boite et sous le couvercle.
### 6. Construire

Le bouton principal s'appelle `Construire mon insert`. Il lance, dans cet ordre :

1. validation des mesures et quantites ;
2. creation des groupes de bacs ;
3. calcul des logements et de leur capacite ;
4. reservation de la pile plateaux/livrets ;
5. partition du volume entre les bacs demandes et calcul de leurs enveloppes finales ;
6. repartition du surplus dans les parois et fonds sans modifier les cavites ;
7. controle des parois, jeux, collisions, couverture et hauteur totale ;
8. production d'une ou plusieurs solutions expliquees ;
9. materialisation CAD/Fusion de la solution choisie.

Le calcul peut etre plus couteux qu'un apercu. Les changements de saisie mettent
a jour immediatement les controles simples et l'aperçu ; le solveur complet part
sur action explicite ou apres une temporisation claire.

### 7. Definition verifiable de "boite remplie"

Un plan V0.1 est complet seulement si :

- 100 % des quantites de pieces sont affectees a un logement ;
- 100 % des plateaux/livrets sont reserves dans la hauteur disponible ;
- chaque bac respecte ses parois et son fond minimaux ;
- le meme jeu minimal est respecte entre bacs et contre la boite ;
- aucune collision ni sortie de boite n'existe ;
- chaque corps imprimable correspond a un bac demande par un groupe d assets ou
  a un complement ajoute explicitement ;
- aucun corps automatique n est cree depuis une region libre du solveur ;
- l union des enveloppes finales, des reservations et des jeux techniques couvre
  exactement le volume disponible ;
- la somme des hauteurs, couvercles exclus en V0.1, ne depasse jamais la boite ;
- le resultat indique clairement `construit`, `partiel` ou `impossible`.

"Rempli" signifie que les bacs demandes occupent tout le volume imprimable par
leurs enveloppes exterieures. Les cavites utiles et les jeux necessaires restent
vides ; le surplus est absorbe par la matiere des parois et des fonds, pas par des
micro-boites ajoutees.

### 8. Cardinalite et limites honnetes

Le schema, l'UI et le moteur ne fixent aucun nombre metier arbitraire de lignes,
de bacs ou de plateaux. Un projet avec 1 piece et aucun plateau comme un projet
avec des dizaines de familles doit etre representable.

BGIG ne promet cependant pas qu'une solution physique existe pour toute entree,
ni qu'une recherche exhaustive est instantanee. Le moteur doit :

- detecter les impossibilites dimensionnelles avant la recherche ;
- annoncer les limites de temps ou de complexite ;
- conserver la meilleure solution complete connue ;
- ne jamais presenter un resultat partiel comme un insert termine ;
- proposer des corrections concretes : regrouper autrement, reduire une marge,
  changer l'orientation ou retirer un element.

## V0.2 - Formes et ergonomie, apres la V0.1

La V0.2 ajoute dans le meme add-in Fusion des parametres visibles en direct et ayant un
effet reel sur la geometrie :

- coins exterieurs droits, arrondis ou chanfreines ;
- rayons et chanfreins bornes par l'epaisseur disponible ;
- encoches de prise ;
- fonds et angles interieurs arrondis ou en pente pour recuperer facilement des
  pieces en vrac ;
- labels et finitions non destructives ;
- valeurs globales avec surcharge par bac lorsque cela reste compréhensible.

Chaque option doit recalculer le volume utile, la resistance minimale et la
fabricabilite. Un simple effet graphique ne suffit pas. P33 est conserve comme
prototype de preview, mais ne constitue pas une V0.2 et reste hors du parcours
principal tant que la V0.1 n'est pas acceptee.

## V0.3 - Couvercles, apres la V0.2

### Couvercle encastrable

Le couvercle vient par-dessus le bac. Un profil interieur legerement conique
reprend la forme interieure du bac pour le centrer et le retenir. La hauteur
ajoutee par le couvercle participe au calcul global : aucun bac ferme ne peut
faire depasser la pile de la boite principale.

La demande "sans tolerance" est traduite comme un contact nominal dans le
modele CAD, pas comme une garantie physique de jeu nul. Une impression reelle
varie avec machine, matiere et orientation. La V0.3 devra donc separer le profil
nominal de la compensation de fabrication et valider cette derniere par coupons.

### Couvercle coulissant interieur

Le mecanisme canonique est le suivant :

- le couvercle est une piece separee legerement plus large que l'ouverture utile
  afin de s'engager dans les rainures ;
- trois cotes du bac portent des glissieres creusees dans les parois interieures ;
- le quatrieme cote est ouvert en partie haute sur l'epaisseur necessaire a
  l'introduction du couvercle ;
- les bords inferieurs du couvercle sont chanfreines ;
- les rainures epousent ce profil avec un jeu reglable de 0 a 0,2 mm maximum ;
- l'engagement, la butee, la prise et l'orientation d'impression sont verifies
  avant toute promesse de fonctionnement ;
- l'epaisseur du couvercle et la hauteur des rainures participent au solveur
  volumetrique global.

Le coupon P34 a deux rails exterieurs ne correspond pas a ce mecanisme. Il est
archive comme exploration technique de primitive additive, pas comme base
produit V0.3.

## Frontiere produit et technique

L add-in Fusion 360 est le produit MVP et sa palette embarquee est l interface
principale. Le moteur Python pur reste la source de verite et ne depend pas
d adsk. La palette ne recalcule aucune decision metier : elle edite le projet,
appelle le coeur par messages JSON versionnes et affiche ses resultats.

L adaptateur Fusion materialise et exporte un plan resolu ; il ne choisit ni
groupes, ni dimensions, ni positions. frontend/ et le serveur local P23 sont des
prototypes historiques hors MVP, non packages et non requis au runtime. Les
statuts implemente, fusion-validated et print-validated restent strictement
distincts.
