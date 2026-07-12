# Contrat d acceptation du MVP V0.1

Statut : actif apres les clarifications produit du 2026-07-12.

Ce document rend testable `saisir, organiser, remplir et construire`. Une scene
Fusion visible ou un nombre de composants borne ne compense jamais un axe
produit manquant.

## Regle de sortie

| Axe | Preuve attendue | Refus explicite |
| --- | --- | --- |
| Acces | La personne identifie immediatement ou creer et modifier son projet. Depuis Fusion, la palette conduit clairement au Studio. | Palette bloquee sur `Chargement` ou prise pour un editeur incomplet. |
| Saisie | Boite, assets, bac cible, plateaux/livrets, complements explicites, tolerances, parois et fonds sont editables dans des listes dynamiques. | JSON, jargon moteur, champs caches ou limite metier arbitraire. |
| Controle | Les erreurs sont localisees et dites en langage courant avant construction. | Erreur technique generique ou calcul lance avec des donnees incoherentes. |
| Construction | Les cavites sont calibrees puis les enveloppes des bacs demandes absorbent le volume disponible. | Cavite agrandie, corps automatique, micro-bac residuel ou vide non explique. |
| Resultat | Le plan reel est visible avant Fusion, avec contenu, dimensions et surplus absorbe par bac. | Dessin indicatif presente comme solution ou corps sans raison. |
| Passage Fusion | Fusion materialise exactement le plan choisi et affiche un etat non bloque. | Scene differente, doublons ou chargement permanent. |

## Scenarios obligatoires

Chaque scenario est verifie au niveau moteur, API et interface. Seul le dernier
smoke CAD demande une observation humaine Fusion.

1. Boite vide : saisie des mesures et ajout d une premiere ligne d asset.
2. Une famille, aucun element plat : un seul bac occupe le volume imprimable ;
   sa petite cavite reste calibree et son enveloppe absorbe le surplus.
3. Plusieurs familles dans le meme bac : plusieurs cavites calibrees dans un
   seul corps exterieur extensible.
4. Plusieurs bacs et plusieurs plateaux/livrets : partition complete sous la
   pile, support coherent, aucun depassement.
5. Complement explicite : bac vide, remplissage plein ou separateur existe
   uniquement parce que la personne l a ajoute.
6. Grande cardinalite : dizaines de lignes et de bacs representables, calcul
   borne et diagnostic lisible.
7. Projet impossible : aucun corps trompeur exporte, contrainte et correction
   affichees.
8. Scene finale : meme nombre de corps dans le resultat accepte et dans Fusion,
   sans corps automatique ni doublon.

## Politique cavites fixes / enveloppes extensibles

Pour chaque groupe de bac, le moteur calcule dans cet ordre :

1. les cavites depuis formes, dimensions, quantites et jeux des assets ;
2. leur arrangement interne ;
3. l enveloppe exterieure minimale avec cloisons, parois et fond minimaux ;
4. l enveloppe exterieure finale participant a la partition de la boite.

L expansion X/Y ajoute de la matiere autour des cavites. L expansion Z ajoute de
la matiere sous les cavites. Elle ne modifie jamais la taille utile des cavites.
Les jeux externes et internes restent du vide.

Le nombre de corps final est exactement le nombre de groupes de bacs
constructibles, plus les complements explicitement demandes. Une cellule libre,
une reservation ou un jeu technique ne devient jamais un corps imprimable. Si
aucune partition complete ne respecte les contraintes, le resultat est
`impossible` avec une explication.

## Editeur premium obligatoire

Le Studio fournit une interface unique, belle, fluide et responsive :

- mesures de la boite et hauteur utile ;
- tableau dynamique des assets avec forme, mesures, quantite, bac cible et jeu ;
- tableau dynamique des plateaux/livrets avec mesures, quantite et ordre ;
- cartes des bacs avec paroi/fond minimaux et surcharges ;
- complements explicites, jamais ajoutes silencieusement ;
- tolerances et preferences globales ;
- mode avance pour verrous dimensionnels, axes extensibles et repartition du
  surplus ;
- sauvegarde, import, validation, construction et reprise de saisie.

Le mode simple reste comprehensible par un debutant. Le mode avance expose le
controle sans changer d outil ni afficher le vocabulaire interne du moteur.

## Resultat visible avant Fusion

Le Studio montre :

- la liste des bacs et les assets contenus ;
- la pile plateaux/livrets et la hauteur reservee ;
- pour chaque bac : cavites, enveloppe minimale, enveloppe finale et surplus
  absorbe dans parois/fond ;
- les seuls complements explicitement choisis ;
- un apercu dessus et coupe issu des placements resolus ;
- le statut `construit`, `partiel` ou `impossible` ;
- les actions modifier, recalculer, accepter et ouvrir dans Fusion.

## Tests non negociables

- tests moteur sur les huit scenarios ;
- invariant zero corps automatique ;
- invariant aucune modification de cavite pendant l expansion ;
- tests API sur le contrat complet ;
- tests d interaction UI sur ajout, modification, suppression, groupes,
  validations, sauvegarde et resultat ;
- controle d encodage des textes affiches ;
- palette Fusion : etat ou erreur explicite, jamais chargement permanent ;
- correspondance exacte plan Studio / CAD IR / Fusion ;
- aucune revendication `print-validated` sans impression et mesure reelles.
