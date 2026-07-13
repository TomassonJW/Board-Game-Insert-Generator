# Contrat d acceptation du MVP V0.1 Fusion-only

Statut : actif selon ADR-0055.

## Regle de sortie

Le MVP est accepte uniquement si le parcours complet fonctionne dans l add-in
Fusion 360 installe. Une app web externe, un serveur loopback ou une scene CAD
isolee ne constitue pas le produit.

| Axe | Preuve attendue | Refus explicite |
| --- | --- | --- |
| Acces | Le bouton BGIG ouvre une palette utilisable dans Fusion. | Navigateur externe, serveur local requis ou palette bloquee. |
| Saisie | Boite, pieces, bacs, plateaux/livrets et reglages sont editables dans la palette. | JSON manuel, chemins techniques ou CommandInputs comme parcours normal. |
| Controle | Les erreurs sont localisees en langage courant avant construction. | Erreur generique ou calcul lance avec donnees incoherentes. |
| Construction | Les cavites sont calibrees et les bacs demandes absorbent le volume. | Cavite agrandie, corps automatique, micro-bac ou vide oublie. |
| Resultat | La palette montre le plan moteur reel avant materialisation. | Dessin indicatif presente comme solution. |
| Fusion | La scene contient exactement le plan accepte, sans doublon. | Scene differente, objets orphelins ou chargement permanent. |
| Packaging | L add-in fonctionne sans Vite, localhost ou repo de developpement. | Dependances de developpement requises par l utilisateur. |

## Scenarios obligatoires

Chaque scenario est verifie au niveau coeur, bridge de palette et resultat
Fusion quand une materialisation est attendue.

1. Projet vide : la palette guide vers la mesure de boite et le premier asset.
2. Une famille, aucun element plat : un bac occupe le volume imprimable ; sa
   petite cavite reste calibree.
3. Plusieurs familles dans le meme bac : plusieurs cavites fixes dans un seul
   corps extensible.
4. Plusieurs bacs et plusieurs plateaux/livrets : partition complete sous la
   pile, support coherent et aucun depassement.
5. Complement explicite : bac vide, volume plein ou separateur existe seulement
   parce que la personne l a ajoute.
6. Grande cardinalite : dizaines de lignes et de bacs, calcul borne et diagnostic.
7. Projet impossible : aucun corps trompeur, cause et correction visibles.
8. Regeneration : projet modifie, meme scene BGIG remplacee sans doublon.
9. Reouverture : projet sauvegarde, add-in relance et saisie restauree.
10. Installation propre : parcours sans serveur local ni navigateur externe.

## Cavites fixes et enveloppes extensibles

Pour chaque groupe de bac, le coeur calcule :

1. cavites depuis formes, dimensions, quantites et jeux ;
2. arrangement local ;
3. enveloppe exterieure minimale ;
4. enveloppe finale participant a la partition.

L expansion ne modifie jamais la taille ni l arrangement local des cavites. Les
jeux restent du vide. Le nombre de corps final est exactement le nombre de
groupes constructibles plus les complements explicitement demandes.

## Editeur embarque obligatoire

La palette Fusion fournit :

- mesures de boite et hauteur utile ;
- table dynamique des pieces ;
- table plateaux/livrets ;
- cartes de bacs ;
- complements explicites ;
- tolerances et preferences ;
- mode simple et avance ;
- sauvegarde, import, validation et construction ;
- resultat et actions de scene.

La commande CommandInputs reste un secours expert. Elle ne remplace pas la
palette dans les preuves MVP.

## Resultat avant CAD

La palette montre depuis le plan moteur :

- bacs et contenus ;
- pile superieure ;
- cavites ;
- enveloppes minimale et finale ;
- surplus parois/fond ;
- placements reels ;
- complements explicites ;
- construit, partiel ou impossible ;
- zero corps automatique.

La materialisation ne peut partir que de ce plan courant.

## Tests non negociables

- tests moteur sur les scenarios ;
- invariant zero corps automatique ;
- invariant cavites immuables pendant expansion ;
- tests de bridge JSON palette/coeur ;
- tests DOM sur edition dynamique, erreurs, sauvegarde et resultat ;
- controle UTF-8 ;
- absence de localhost, Vite et navigateur dans le runtime add-in ;
- timeout et retry de palette ;
- correspondance exacte projet -> plan -> CAD IR -> scene Fusion ;
- generate/regenerate/clear sans doublon et preservation non-BGIG ;
- installation add-in verifiee par scripts ;
- observation humaine finale dans Fusion ;
- aucune revendication print-validated sans impression reelle.

## Gate P66

Codex prepare automatiquement l add-in, le projet temoin et les settings. Thomas
ouvre Fusion, lance BGIG et confirme uniquement le parcours final visible et la
scene selon docs/P66_TERRA_EXECUTION_CONTRACT.md. Cette observation P66 est la
seule gate humaine produit restante pour V0.1.
