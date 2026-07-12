# Contrat d acceptation du MVP V0.1

Statut : actif apres la remise a plat du 2026-07-12.

Ce document ne change pas la vision canonique. Il rend testable ce que signifie
`saisir, organiser, remplir et construire` avant toute acceptation V0.1.

## Regle de sortie

La V0.1 n est acceptable que si les six axes suivants sont tous vrais pour des
projets simples et complexes. Une scene Fusion visible ou un nombre de composants
borne ne peut pas compenser un axe manquant.

| Axe | Preuve attendue | Refus explicite |
| --- | --- | --- |
| Acces | La personne identifie immediatement ou creer/modifier son projet. Depuis Fusion, la palette explique son role et ouvre ou indique clairement le Studio. | Palette bloquee sur `Chargement`, palette prise pour un editeur alors qu elle ne l est pas. |
| Saisie | Boite, pieces, bac cible, plateaux/livrets, complements et reglages sont editables dans des listes dynamiques sans JSON ni jargon. | Champs caches, table non interactive, limite metier arbitraire, texte mal encode. |
| Controle | Les erreurs sont localisees et dites en langage courant avant construction. | Erreur technique generique, calcul lance avec des donnees incoherentes. |
| Construction | Le bouton produit un plan complet, explique ou impossible avec une cause et une correction. | Resultat nominal sans explication, ou echec incomprehensible. |
| Qualite du rangement | Les bacs utiles sont privilegies ; chaque volume automatique imprime est necessaire, utile ou choisi. | Multiplication de petits bacs automatiques sans fonction compréhensible. |
| Passage Fusion | Fusion materialise exactement le plan choisi et affiche un etat non bloque. | Scene differente du plan, doublons, etat eternel de chargement. |

## Scenarios obligatoires

Chaque scenario doit etre verifie au niveau moteur, API et interface. Le dernier
seulement demande un smoke Fusion humain lorsque la scene change.

1. Boite vide : la personne peut saisir ses mesures, comprendre ce qui manque et
   ajouter une premiere ligne.
2. Une famille de pieces, aucun element plat : un seul bac utile est propose ;
   aucun remplissage parasite n est imprime par defaut.
3. Plusieurs familles partageant un bac : les logements sont differencies mais
   restent dans un unique corps quand les contraintes le permettent.
4. Familles separees, plusieurs plateaux/livrets : la pile superieure est
   reservee, le support est explique et aucune hauteur ne depasse.
5. Complements explicites : bac vide, remplissage plein et separateur respectent
   le choix et les dimensions de la personne.
6. Projet de grande cardinalite : dizaines de lignes possibles sans limite
   metier arbitraire ; le calcul est borne et son diagnostic lisible.
7. Projet impossible : aucun corps trompeur n est exporte ; la contrainte qui
   bloque et l action utile sont affichees.

## Politique de volumes automatiques

Le remplissage complet ne signifie pas imprimer toute cellule libre de la
decomposition interne. Le moteur doit d abord, dans cet ordre :

1. agrandir un bac existant si cela cree une utilite de rangement explicable ;
2. assembler des regions rectangulaires compatibles en un complement utile ;
3. creer un support indispensable sous un plateau/livret ;
4. proposer un bac vide, un remplissage plein ou un separateur avec un nom, une
   taille et une raison visibles ;
5. conserver le reste comme jeu technique classe si aucune piece imprimable
   utile ne peut etre justifiee.

Une piece automatique ne peut jamais etre acceptee uniquement parce qu elle
ferme un residu de grille. Sa justification doit etre visible dans le resultat.
Le nombre de corps n a pas de plafond arbitraire : il doit etre la consequence
de besoins reels, et non de la decomposition du solveur.

## Resultat visible avant Fusion

Avant tout export ou passage dans Fusion, le Studio montre :

- la liste des bacs, leur contenu, leurs dimensions et leur role ;
- les plateaux/livrets reserves et la hauteur disponible ;
- les complements choisis ou proposes, separes des bacs utiles ;
- un apercu issu des positions resolues, avec legendes et avertissements ;
- le statut clair `construit`, `partiel` ou `impossible` ;
- le chemin suivant en langage courant : modifier, accepter le plan ou ouvrir
  Fusion.

## Tests non negociables

- tests moteur sur les sept scenarios ;
- tests API sur le contrat complet ;
- tests d interaction UI sur ajout, modification, suppression, groupes,
  validations et resultat ;
- test de contrat de la palette Fusion : un etat est affiche ou une erreur
  explicite remplace le chargement ;
- build frontend et controle d encodage des textes affiches ;
- smoke Fusion du scenario de reference final ;
- aucune revendication `print-validated` sans impression et mesure reelles.
