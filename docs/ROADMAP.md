# Roadmap

## V0 - Repo fondateur et moteur de layout minimal

Objectifs :

- documentation complete du modele mental ;
- structure Python minimale ;
- exemples JSON ;
- validation de base ;
- layout rectangulaire trivial ;
- application simple des tolerances ;
- rapport Markdown/JSON ;
- tests unitaires hors Fusion.

Critere de reussite :

- un developpeur comprend la vision et peut executer un exemple local.

## V1 - Generation de blanks Fusion 360

Objectifs :

- add-in Python Fusion 360 ;
- creation de composants rectangulaires ;
- dimensions tolerancees ;
- noms propres ;
- boite de reference ;
- rayons parametriques simples.

Critere de reussite :

- une configuration V0 produit des composants Fusion 360 inspectables.

## V2 - Layout semi-automatique

Objectifs :

- strategies grille, lignes, colonnes ;
- decoupe guillotine simple ;
- rotation autorisee ;
- rapport de score basique ;
- detection plus fine des impossibilites.

Critere de reussite :

- le moteur propose plusieurs layouts simples et reproductibles.

## V3 - Modules creuses

Objectifs :

- bacs ;
- compartiments cartes ;
- logements tokens ;
- encoches de doigt ;
- fonds arrondis ;
- separateurs.

Critere de reussite :

- les premiers modules fonctionnels sont imprimables avec cavites simples.

## V4 - Modules composites

Objectifs :

- modules constitues de plusieurs primitives ;
- union logique de volumes ;
- absence de jeu interne entre primitives soudees ;
- detection des faces exposees ;
- rapport des primitives et interfaces.

Critere de reussite :

- un module en L ou T est genere sans rupture de tolerance interne.

## V5 - Couvercles et fermetures

Objectifs :

- couvercles simples ;
- couvercles coulissants ;
- rainures ;
- languettes ;
- jeux fonctionnels ;
- charnieres simples.

Critere de reussite :

- un module avec couvercle peut etre imprime, assemble et teste.

## V6 - Surcouche esthetique

Objectifs :

- embossage ;
- gravure ;
- texte ;
- pictogrammes ;
- textures ;
- motifs ;
- ajourages ;
- coins stylises.

Critere de reussite :

- l'apparence peut etre parametree sans casser la logique fonctionnelle.

## V7 - Assistant de conception

Objectifs :

- description utilisateur plus libre ;
- generation de plusieurs propositions ;
- notation selon compacite, ergonomie, facilite d'impression, rapidite de setup et lisibilite ;
- aide a la decision.

Critere de reussite :

- l'utilisateur choisit entre des propositions expliquees, pas entre des boites opaques.
