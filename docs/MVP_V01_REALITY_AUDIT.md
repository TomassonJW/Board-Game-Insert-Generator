# Audit de realite - MVP V0.1

Date : 2026-07-12
Statut : correctif de pilotage, pas une livraison produit.

## Conclusion

Le MVP V0.1 n est pas accepte. Le depot contient des fondations reutilisables,
mais la promesse utilisateur canonique n est pas prouvee de bout en bout.

La confirmation `Fusion P43 OK` prouve seulement que la scene preparee peut etre
observee dans Fusion. Elle ne prouve pas que la personne peut saisir facilement
son jeu ni que le resultat par defaut est un rangement utile et comprehensible.

## Evidence observee

### 1. Palette Fusion inutilisable dans le cas observe

Le retour humain montre les trois cartes `Design`, `Scene Fusion` et
`Fabrication` bloquees sur `Chargement...`. Aucun champ de saisie ne peut y etre
utilise. Le code HTML initialise ces trois valeurs ainsi et depend d un unique
message `refresh` venant de Fusion ; il n affiche ni etat de secours, ni action
de reprise claire quand ce message n arrive pas.

La palette n est donc pas une surface de conception utilisable. C est coherent
avec la vision canonique : le Studio doit etre la surface principale, Fusion un
adaptateur de materialisation. Le produit actuel ne rend toutefois pas cette
separation claire pour la personne qui ouvre Fusion.

### 2. Studio present dans le code, UX non prouvee

`frontend/src/App.tsx` contient une boite, un tableau de pieces, un tableau de
plateaux/livrets, des bacs, des complements et des reglages. Les tests P38 sont
cependant des controles de texte source et de build ; ils ne prouvent pas le
parcours visuel, la lisibilite, les interactions reelles ou la qualite de la
mise en page. L inspection visuelle automatisee locale etait indisponible dans
le sandbox Windows ; ce manque de preuve interdit de qualifier cette UI de
terminee.

### 3. Critere P43 insuffisant pour la qualite de resultat

Le test du jeu temoin P43 n exige que trois bacs de rangement, au moins un
remplissage creux et plein, et au plus 24 composants. Il accepte donc 20 pieces
sans determiner si elles sont utiles, compréhensibles ou evitables.

Le constructeur CAD fusionne seulement des cellules libres face a face si elles
ont exactement la meme classification. Il n explore pas l agrandissement d un
bac utile, ne compare pas des plans selon le nombre de pieces utiles et ne refuse
pas de materialiser un residu peu exploitable. Les petits volumes observes sont
donc le comportement actuel attendu du code, pas un incident isole de Fusion.

### 4. Erreur de qualification

P42/P43 ont confondu trois niveaux distincts :

| Niveau | Etat reel |
| --- | --- |
| Validite geometrique | Partiellement couverte : collisions et conservation de volume sont testees. |
| Materialisation Fusion | Observee pour le jeu temoin P43. |
| MVP produit utilisable | Non accepte : saisie, acces a la bonne UI, resultat par defaut et lisibilite ne sont pas prouves. |

## Elements reutilisables

- contrat projet V0.1 (boite, pieces, groupes, plateaux/livrets, remplissages,
  parois et jeux) ;
- moteur pur de derivation, reservation et controle de collisions ;
- CAD IR et adaptateur Fusion ;
- premieres tables de saisie du Studio ;
- fixture P43 comme test de non-regression geometrique, jamais comme seul
  critere de qualite produit.

## Elements a reprendre avant toute V0.2

1. acces explicite a la surface de conception et etat fiable de la palette
   Fusion ;
2. parcours Studio visuellement teste, lisible et sans texte mal encode ;
3. apercu et resultat issus du vrai plan resolu, pas d un dessin indicatif ;
4. objectif de rangement utile : extension de bacs, choix de complements,
   limitation et justification des volumes automatiques ;
5. nouvelle acceptance V0.1 fondee sur des scenarios produit, puis un smoke
   Fusion de la scene effectivement choisie.

## Consequence de pilotage

P43 est reouvert. P44 a P50 restent bloques. P51 est absorbe dans la reprise
complete de la qualite des resultats : corriger uniquement la fusion de cellules
ne suffirait pas.
