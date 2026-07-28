# ADR-0103 — Placement automatique canonique et ordre de pile

## Statut

Acceptée dans le périmètre P64-L09U-R7 à partir du verdict humain 0.1.77.

Cette décision ne vaut ni validation Fusion, ni validation d'impression.

## Contexte

Le plan automatique actuel sait proposer plusieurs poses XY et composer leurs
intervalles Z locaux. Il ne connaît toutefois pas toute la structure finale :

- il pénalise les recouvrements entre éléments plats ;
- il certifie la distance aux cavités, mais pas toutes les parois externes,
  séparations et frontières des corps finalisés ;
- il accepte des positions au bord de boîte ;
- il suit d'abord le `stack_order` historique ;
- la finalisation peut alors produire des fragments de coupe de `0,5 mm`.

La profondeur R6 et les cavités figées sont correctes. Le correctif porte sur
la pose des réservations, leur ordre et leur recertification finale.

## Options comparées

### Option A — centrage simple

- Simplicité : très bonne.
- Robustesse : faible dès que les conteneurs sont dissymétriques.
- Maintenance : faible coût initial, nombreux correctifs particuliers ensuite.
- Testabilité : simple, mais ne couvre pas les cas réels.
- Recherche : minimale.

Option refusée : un centre de boîte n'est pas nécessairement un centre utile.

### Option B — grille exhaustive de 0,1 mm

- Simplicité : moyenne.
- Robustesse : bonne si le certificat est complet.
- Maintenance : coût élevé et risque de budgets variables.
- Testabilité : bonne mais matrice très volumineuse.
- Recherche : jusqu'à plusieurs millions de couples XY par élément.

Option refusée : la précision produit ne justifie pas une exploration
exhaustive.

### Option C — ancres bornées, certificats durs et score lexicographique

- Simplicité : moyenne, sans nouveau solveur.
- Robustesse : forte grâce aux rejets avant classement et à la recertification.
- Maintenance : règles centralisées et observables.
- Testabilité : chaque composante du certificat et du score est isolable.
- Recherche : bornée par les limites existantes, avec déduplication sur grille.

Option retenue.

### Option D — déplacer seulement pendant la finalisation

Option refusée : les conteneurs sous l'empreinte ne seraient plus ceux que le
calcul minimal a certifiés.

## Décision

### 1. Les candidats restent bornés

Le moteur conserve une recherche déterministe par ancres, sans balayage complet.
Les ancres proviennent :

- des marges canoniques de boîte ;
- des centres de matière et de cavités finalisables ;
- des bords de corps/cavités, décalés de la paroi minimale ;
- des positions de recouvrement ou de centrage avec les autres éléments plats ;
- des poses déjà certifiées lorsque leur réutilisation reste exacte.

Toutes les ancres sont converties sur la grille produit avant déduplication.

### 2. Les contraintes dures précèdent le score

Une pose candidate est refusée si l'une des règles suivantes échoue :

- l'empreinte avec jeu sort de la boîte ou laisse moins que la paroi canonique
  par rapport à son bord ;
- deux zones plates réellement séparées laissent entre elles une bande de
  matière inférieure à la paroi canonique ;
- une coupe, une prise ou leur intersection avec un corps final crée un
  fragment de matière positif mais inférieur à la paroi minimale ;
- une paroi externe de conteneur ou séparation interne tombe sous son minimum ;
- la pose perce un fond, modifie une cavité figée ou exige un support
  artificiel ;
- un intervalle/corps/coupe sort de l'enveloppe finale certifiée.

Deux vides qui doivent communiquer peuvent fusionner sans paroi intermédiaire,
conformément à ADR-0100 et ADR-0101. Cette exception doit être explicite ; elle
ne transforme pas un fragment de matière en paroi valide.

### 3. Score automatique

Entre poses entièrement certifiées, le classement est lexicographique :

1. maximiser la couverture intérieure utile par les empreintes de conteneurs et
   cavités finalisables ;
2. maximiser le recouvrement sain entre éléments plats lorsqu'une vraie pile
   est possible ;
3. maximiser la plus petite marge de matière au-delà du minimum ;
4. minimiser la distance entre le centre de chaque encoche et le centre de sa
   couverture utile ;
5. minimiser la distance résiduelle au centre de boîte ;
6. départager par la signature canonique : identifiant, rotation, X, Y.

Une composante et sa valeur sont publiées dans la trace de recherche. Une
égalité ne déplace pas gratuitement l'incumbent.

### 4. Ordre automatique de pile

L'ordre est calculé après résolution de la rotation, à partir de l'empreinte
réellement orientée avec jeu.

Du bas vers le haut, la clé est :

1. aire orientée croissante ;
2. plus grand côté croissant ;
3. plus petit côté croissant ;
4. `stack_order` historique uniquement comme départage si les trois valeurs
   précédentes sont égales ;
5. identifiant stable.

Ainsi, un petit élément est toujours sous un grand élément. La rotation peut
modifier la clé lorsque les jeux X/Y orientés diffèrent.

### 5. Compatibilité de `stack_order`

Les anciens fichiers sont lus sans réécriture :

- `stack_order` est conservé comme donnée source ;
- l'ordre effectif automatique est publié séparément ;
- si l'ordre source contredit la règle automatique, le résultat porte
  `legacy_stack_order_normalized` et les dérivations antérieures deviennent
  obsolètes ;
- aucun ancien witness ou plan final ne peut être réutilisé sous l'ancienne
  sémantique.

Le futur mode manuel pourra introduire une politique explicite distincte. R7
n'ajoute ni champ d'édition, ni UI, ni comportement manuel implicite.

### 6. Même pose du minimum à Fusion

Le calcul minimal publie :

- la pose choisie ;
- la clé d'ordre effective ;
- le score détaillé ;
- les enveloppes de paroi attendues ;
- un certificat de compatibilité avec la frontière finale.

La finalisation reconstruit la géométrie finale et recertifie exactement cette
pose. Elle peut la conserver ou refuser le plan. Elle ne peut jamais la
déplacer silencieusement.

L'aperçu, la CAD IR et le plan Fusion transportent la même pose, le même ordre
et les mêmes intervalles Z.

## Conséquences

- Le nombre de rejets peut augmenter.
- Une position auparavant « réussie » peut devenir un refus explicite.
- Le score favorise une encoche réellement utile au lieu d'éviter les
  recouvrements.
- Le futur mode manuel reste possible via une politique séparée.
- L'identité fonctionnelle du plan minimal, du finaliseur et des artefacts CAD
  doit changer.

## Alternatives refusées

- Accepter une paroi résiduelle inférieure au minimum parce que la coupe touche
  une cavité.
- Ajouter une tolérance métier spéciale pour les micro-fragments.
- Recentrer en finalisation.
- Transformer les réservations en plaques imprimables.
- Laisser `stack_order` inverser la règle automatique.
- Implémenter immédiatement une UI manuelle.
