# P64-V2H01 — Fermeture continue et réservations supérieures conditionnelles

Statut : implemented, automated-validated dans le package 0.1.52 ; validation
Fusion requise. Ce lot corrige le KO contextuel observé sur P64-V2 0.1.51.

## Problème confirmé

Le projet Fusion laissé ouvert contient 9 conteneurs, 26 éléments, deux
réservations supérieures et une boîte de 250 x 180 x 70 mm.

La reproduction automatisée de la 0.1.51 établit trois faits :

- Étages et piles ne trouve aucun arrangement dans son budget ;
- le greedy 3D pouvait proposer une géométrie minimale mais elle était rejetée
  dès qu'un espace maximal vide imprimable subsistait ;
- le beam mélangeait placement de faisabilité et gonflement final des enveloppes,
  puis élaguait des états encore utiles avant d'avoir placé tous les corps.

Les trois modes existaient réellement, mais leurs limites convergeaient vers le
même résultat utilisateur : aucun plan matérialisable sur ce cas pourtant
faisable.

## Objectif borné

Rétablir un résultat certifié sans changer :

- le nombre de corps demandé ;
- les assets, cavités, parois, fonds, jeux ou valeurs physiques ;
- le schéma projet ;
- le caractère explicite de Matérialiser dans Fusion ;
- la frontière cœur Python sans import adsk.

## Décision d'algorithme

La chaîne free-3D devient :

1. préparation des minima et des contraintes supérieures ;
2. placement de faisabilité sur enveloppes minimales ;
3. recherche beam multi-états, bornée et déterministe hors cutoff temporel ;
4. fermeture continue des seuls axes Auto ou Cible ;
5. reconstruction produit et certificat commun ;
6. classement du portefeuille entre candidats certifiés seulement.

Le beam n'agrandit plus un corps jusqu'aux limites d'un EMS pendant la recherche
de faisabilité. Cette expansion prématurée favorisait un bon remplissage local
mais détruisait les solutions denses suivantes.

## Réservations plateau et livret

Une réservation supérieure n'est pas un obstacle plein. Un corps peut :

- rester entièrement sous son plan d'appui ; ou
- atteindre le sommet, recevoir la coupe localisée et conserver assez de matière
  sous ses cavités.

Pendant la recherche, une zone conditionnelle refuse seulement les corps qui ne
peuvent satisfaire aucun de ces deux cas. Les grands corps trop profonds sont
donc routés hors de l'empreinte concernée ; un corps compatible peut encore
monter au sommet et porter l'encastrement.

Le validateur commun reste l'autorité finale sur les coupes, compensations de
cavité, fonds, supports et séquence de retrait.

## Fermeture continue minimale

La fermeture :

- ne crée aucun corps ;
- ne change aucun axe Fixe ;
- ne déplace aucune cavité ;
- agrandit une enveloppe par face entière jusqu'à la prochaine limite utile ;
- conserve les jeux entre corps et le jeu périphérique ;
- revalide collision, support, réservations et contrat produit ;
- s'arrête honnêtement avec un résiduel si la topologie ne peut pas être fermée
  dans le budget.

Le score primaire réduit les EMS restants. À égalité, les faces alignées sont
favorisées puis la croissance relative la plus faible. Cette étape améliore la
cohérence visuelle, mais ne prétend pas implémenter l'harmonisation modulaire
P64-F02.

## Critères d'acceptation automatisés

- le cas anonymisé du KO P64-V2 conserve 9 conteneurs et les deux réservations ;
- Étages et piles reste honnêtement sans solution dans son budget ;
- Placement 3D libre trouve un plan certifié et matérialisable ;
- Auto sélectionne le même candidat libre certifié sur ce cas ;
- le plan utilise plusieurs niveaux ;
- le résiduel imprimable final est nul ;
- la télémétrie expose statut, itérations, candidats évalués et alignements de la
  fermeture ;
- aucune coupe supérieure ne perce un fond ou une cavité ;
- les tests de déterminisme, budgets, annulation et frontières adsk restent verts.

## Harmonisation restante

P64-V2H01 tire en avant uniquement la fermeture nécessaire à la correction de
faisabilité. P64-F01 conserve le travail de finition plus large sur plusieurs
topologies et objectifs. P64-F02 reste la mission d'harmonisation modulaire :
trames candidates globales/locales, régularité des dimensions et résultat
total, partiel ou rejeté avec fallback.

Aucune grille dure, aucun GCD flottant et aucune cale automatique ne sont ajoutés
ici.

## Gate Fusion

Préparation : scripts/fusion/prepare_p64_v2h01_continuous_closure_test.ps1.

Retour attendu :

P64-V2H01 Fusion OK 0.1.52 - commit <sha>

Un retour positif valide le comportement logiciel observé seulement. Il ne
calibre aucune valeur physique et ne vaut pas impression réelle.
print-validated: false.