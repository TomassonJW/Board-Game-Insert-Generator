# ADR-0069 — Finition continue et harmonisation modulaire du volume

## Statut

Acceptée le 2026-07-17 comme trajectoire post-faisabilité. Cette ADR ne vaut pas
implémentation et ne rend pas la finition bloquante pour P64-V2 ou P46.

## Contexte

Une solution faisable peut laisser des vides fragmentés, des faces peu alignées
ou des dimensions de conteneurs visuellement hétérogènes. Produire
automatiquement des cales ajouterait des corps, des problèmes de manipulation et
des affirmations physiques non validées.

L'idée d'une unité de slot 3D empirique est utile pour harmoniser les enveloppes,
mais une grille globale choisie trop tôt peut rendre insoluble une disposition
qui était valide. Le plus petit volume commun, une médiane ou un GCD flottant ne
capturent pas à eux seuls la topologie, les réservations ou la contrainte plus
forte de Z.

La faisabilité et la finition doivent donc être séparées. La finition reçoit une
solution certifiée et ne peut jamais transformer son propre échec en
`proven_impossible`.

## Options

1. Laisser tous les résiduels tels quels.
2. Créer automatiquement des cales pour tout volume restant.
3. Redistribuer continûment le résiduel à topologie fixe.
4. Imposer une grille 3D globale avant la recherche.
5. Enchaîner une fermeture continue puis une harmonisation modulaire adaptative,
   avec fallback vers la solution certifiée.

## Décision

Retenir l'option 5, par incréments.

`P64-F01` introduit d'abord une fermeture continue sur le graphe d'adjacence :
les enveloppes extensibles absorbent du résiduel par faces entières sans changer
la topologie. `P64-F02` peut ensuite inférer plusieurs trames vectorielles
`(u_x, u_y, u_z)` à partir des dimensions de boîte, plans de coupe, minima et
réservations. Il arrondit seulement les enveloppes extérieures vers des multiples
compatibles et répartit les cellules restantes par dalles de face.

Le registre de recherche reste léger : espaces maximaux vides, plans de coupe,
spectre d'alignements, trames candidates et composantes résiduelles. Il ne prend
pas la forme d'une matrice de voxels globale.

Chaque finition est revalidée par le validateur commun. Les résultats possibles
sont : totalement harmonisé, partiellement harmonisé avec résiduel intentionnel,
ou finition rejetée avec conservation exacte de la solution de base.

Le mode produit `Auto` ne conserve une finition que si elle améliore un score
explicite sans dégrader contraintes, usage ou budget. Une harmonisation stricte
reste un choix avancé.

Les cales sont reportées à `P64-F03`, toujours proposées explicitement et sous
préconditions physiques. Aucun corps n'est généré automatiquement.

## Conséquences

- la recherche de faisabilité reste libre de toute grille dure prématurée ;
- les conteneurs peuvent converger vers des dimensions plus régulières sans
  modifier assets, cavités, parois minimales, fonds, jeux ou réservations ;
- la topologie des cellules est comptée correctement : une unité ajoutée sur une
  face consomme toute la dalle correspondante ;
- des trames locales, notamment en Z, peuvent être préférées à une trame globale ;
- la finition ajoute un coût de calcul mesurable et doit avoir son propre budget ;
- P64-F01/F02 sont planifiés après P46 et ne bloquent pas le rétablissement du
  solveur critique ;
- les cales, nervures ou géométries auxiliaires restent hors scope sans contrat
  et preuve physique.

## Alternatives refusées

- L'option 1 reste un fallback valide mais pas la finition cible.
- L'option 2 est refusée par défaut : elle crée des pièces et une dette physique.
- L'option 3 seule est insuffisante pour obtenir une modularité explicite.
- L'option 4 est refusée : elle peut détruire la faisabilité et croît
  cubiquement si elle est voxelisée.
- Un GCD, une médiane ou un ratio unique comme source exclusive de trame est
  refusé ; plusieurs candidats doivent être scorés et revalidés.

## Suivi

- Contrat détaillé : `docs/P64_MULTI_SOLVER_PORTFOLIO_PROGRAM.md`.
- P64-F01 après P46 : fermeture continue par graphe d'adjacence.
- P64-F02 après P64-F01 : harmonisation modulaire adaptative.
- P64-F03 après retours physiques suffisants : résiduel utile et cales
  explicites.

## Amendement P64-V2H01 — 2026-07-17

Le KO contextuel de P64-V2 montre que la séparation initiale était placée un
cran trop tard : le certificat produit exige un résiduel imprimable nul, donc
une géométrie minimale faisable ne peut pas être certifiée avant une fermeture
bornée.

La séquence normative devient :

faisabilité géométrique -> fermeture continue minimale -> certificat produit.

Le sous-ensemble de P64-F01 nécessaire à cette chaîne est avancé dans
P64-V2H01. Il reste strictement topologique, sans corps ajouté, sans axe Fixe
modifié et avec rejet honnête si la fermeture échoue. Le reste de P64-F01
(optimisation de plusieurs fermetures et objectifs de finition) demeure
planifié. P64-F02 reste entièrement distinct et futur : aucune modularité
globale ou locale n'est revendiquée par le package 0.1.52.

Les réservations supérieures sont en outre des contraintes conditionnelles, pas
des obstacles pleins : un corps reste sous le plan d'appui ou atteint le sommet
avec une coupe et des fonds valides. Cette précision évite à la fois les
intersections invalides et l'exclusion abusive de solutions réelles.

## Amendement P64-V2H02 — 2026-07-17

La prévalidation d'une réservation supérieure est localisée. Pour une
orientation candidate donnée, elle compare chaque cavité transformée à
l'empreinte XY de la réservation. Une cavité profonde sans recouvrement ne peut
plus interdire globalement le conteneur. Le validateur final reste autoritaire
sur coupe, matière résiduelle, fonds et support.

Les points extrêmes initiaux incluent en outre les frontières droite et arrière
des réservations. Cette règle permet de placer directement un corps haut hors de
leur empreinte sans transformer la réservation en obstacle plein.

Ces précisions corrigent la faisabilité ; elles ne constituent ni
l'harmonisation modulaire P64-F02, ni une autorisation d'ajouter des cales ou de
modifier des valeurs physiques.
