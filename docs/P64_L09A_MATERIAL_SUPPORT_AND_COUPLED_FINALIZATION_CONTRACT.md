# P64-L09A — Contrat de support matériel et de finalisation couplée

## 1. Portée

Ce contrat transforme les observations humaines postérieures à P64-L08LV en
lots exécutables. Il ne modifie aucun solveur. Il précise :

- ce qui constitue un appui réel ;
- quand un conteneur peut tomber dans une ouverture ;
- comment les réservations supérieures entrent dans SCIP ;
- comment la fermeture du volume devient une boucle bornée ;
- ce qu'un futur couvercle devra certifier avant d'autoriser une pose.

## 2. Vérité géométrique commune

### 2.1 Régions porteuses

Un participant placé expose zéro ou plusieurs `load_bearing_regions` dans son
plan supérieur. Chaque région possède :

- une géométrie XY dans le repère monde ;
- une altitude Z ;
- une provenance : paroi, rebord, corps plein ou fermeture certifiée ;
- l'identité du participant propriétaire ;
- les limites mécaniques disponibles lorsqu'elles existent.

Une enveloppe extérieure seule ne produit jamais une région porteuse.

Pour le premier incrément rectangulaire :

- un bac ouvert expose le rectangle de ses rebords, soit l'enveloppe extérieure
  moins les ouvertures de cavité au niveau concerné ;
- un corps plein expose sa face supérieure pleine ;
- un couvercle non certifié n'expose rien.

### 2.2 Certificat anti-chute

Pour chaque placement supérieur hors sol, le validateur doit construire :

1. son empreinte de contact ;
2. les ouvertures connectées situées immédiatement dessous ;
3. l'union des régions matérielles réellement en contact ;
4. la couverture d'appui ;
5. l'enveloppe de stabilité des contacts.

Le placement est rejeté si son empreinte peut descendre dans une ouverture avec
les jeux applicables. Il est également rejeté si la couverture ou la stabilité
est insuffisante.

Le certificat doit distinguer au minimum :

- `supported_on_material` ;
- `bridged_on_material` ;
- `falls_through_opening` ;
- `insufficient_material_support` ;
- `unstable_support_polygon`.

La valeur historique de couverture minimale reste une contrainte logicielle
existante, pas une calibration physique universelle. Aucun nouveau seuil
physique n'est décidé par L09A.

### 2.3 Classement non normatif

Le solveur peut préférer :

- les grandes ouvertures plus haut ;
- les petites empreintes plus bas ;
- les corps pleins comme supports avant les corps ouverts.

Ces préférences ordonnent les essais. Elles ne peuvent ni accepter un placement,
ni contourner le certificat anti-chute.

## 3. Réservations plateaux et livrets

Une `top_inset_reservation` transporte déjà empreinte, profondeur, orientation,
ordre de retrait, prise et intersections. La lane SCIP produit doit recevoir une
représentation exacte de ces contraintes.

Un problème avec réservation peut avoir trois sorties honnêtes :

- solution finale certifiée ;
- absence de solution prouvée dans un modèle exact ;
- résultat borné ou contrainte non encore représentable.

Le refus `top_inset_reservations_not_supported` appartient à la troisième
catégorie. Il ne doit jamais être converti en impossibilité géométrique.

## 4. Boucle bornée de fermeture

```text
incumbent minimal SCIP
  -> ajouter les contraintes de réservations et mécanismes certifiés
  -> choisir des expansions de faces admissibles
  -> distribuer le résiduel
  -> réparer localement placements et hauteurs
  -> recertifier
  -> répéter sous budget si nécessaire
  -> publier le plan final certifié
```

### 4.1 Budget

La boucle possède :

- un nombre maximal d'itérations ;
- un budget de temps unique ;
- des caps de candidats d'expansion et de réparations ;
- une raison d'arrêt explicite.

Une relance globale consomme le temps restant. Elle n'ouvre jamais un second
budget silencieux.

### 4.2 Incumbent et réparations

Le placement SCIP initial est l'incumbent. La fermeture essaie successivement :

1. expansion sans déplacement ;
2. ajustement local d'un placement ou d'une hauteur ;
3. réparation d'un petit voisinage borné ;
4. rappel du placement global uniquement si les étapes précédentes échouent.

Chaque étape reconstruit les appuis matériels, les collisions, les réservations,
les espaces, les retraits et le bilan de volume.

### 4.3 Cavités et épaisseurs

Une cavité d'asset conserve dimensions, pose et jeux. L'expansion ne porte que
sur les faces déclarées admissibles du corps extérieur.

Lorsqu'un plateau retire une profondeur depuis le dessus, une augmentation de Z
doit préserver simultanément :

- la cavité exacte ;
- la paroi minimale ;
- le fond minimal ;
- la profondeur de coupe ;
- la hauteur utile de boîte.

Une transformation qui ne satisfait pas ces cinq points est rejetée, pas
compensée par une approximation.

## 5. Couvercles et poses futures

`has_lid` reste une information descriptive insuffisante. Une
`closed_container_pose_certificate` future devra lier :

- mécanisme et version ;
- état fermé ;
- rétention des contenus ;
- enveloppe extérieure fermée ;
- épaisseurs et surfaces porteuses ;
- poses autorisées ;
- stabilité ;
- accès et ordre de retrait.

Sans ce certificat, P64 garde uniquement les poses actuelles du conteneur
ouvert. Un plateau à double rôle suit la même règle et reste dans
`F-DUAL-ROLE-TRAY-LID`.

## 6. Lots et critères d'acceptation

### P64-L09B — Support matériel réel

- fixture négative : petit conteneur entièrement contenu dans une grande
  ouverture ;
- fixture positive : pontage sur plusieurs rebords avec appui et stabilité
  suffisants ;
- fixture négative : aire suffisante mais stabilité insuffisante ;
- parité entre plans SCIP directs, remplissage hybride et solveurs internes ;
- certificat commun obligatoire avant publication ;
- aucune valeur de tolérance ou de résistance recalibrée.

### P64-L09C — Réservations dans SCIP

- un projet avec `top_inset_zones` atteint réellement la lane SCIP ;
- empreinte, profondeur, prise et ordre de retrait restent exacts ;
- aucune coupe ne perce cavité, paroi ou fond ;
- les statuts bornés et non représentables restent distincts d'une impossibilité ;
- le cas plateau observé reçoit une fixture publique minimale, sans donnée
  personnelle.

### P64-F01B — Fermeture couplée

- incumbent préservé ;
- cavités bit-à-bit inchangées ;
- expansions seulement sur faces admissibles ;
- réparation locale avant solve global ;
- budget unique et itérations bornées ;
- résiduel, réservations et bilan de volume certifiés ensemble ;
- aucun plan intermédiaire incomplet matérialisable.

### P64-F02B — Objectifs de finition

- égalité des volumes ajoutés et égalité des ratios restent deux objectifs
  distincts ;
- les contraintes dures priment toujours sur le score ;
- l'harmonisation modulaire vient seulement après les contrats de faces P45/P46 ;
- le plan de base reste disponible si l'objectif secondaire échoue.

### P64-L09V — Gate Fusion

La gate combinée n'est préparée qu'après L09B, L09C et F01B automatisés. Elle
observe au minimum :

- absence du placement qui tombe dans une ouverture ;
- pontage valide conservé ;
- projet avec plateau réellement résolu par la voie attendue ;
- cavités préservées après compensation Z ;
- plan final unique, certifié et matérialisable ;
- aucune réorientation de couvercle implicite.

`print-validated=false` reste obligatoire.

## 7. Interdits

- accepter un appui sur la seule enveloppe XY ;
- traiter une préférence de classement comme une preuve ;
- transformer `has_lid` en pose ou surface porteuse ;
- ignorer une réservation puis couper après solve ;
- déplacer ou réduire une cavité pour fermer le volume ;
- relancer silencieusement un budget global complet ;
- matérialiser un incumbent qui n'a pas encore intégré ses réservations actives.
