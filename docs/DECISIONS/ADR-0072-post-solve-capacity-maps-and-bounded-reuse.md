# ADR-0072 — Cartes de capacité post-solvage et réutilisation bornée

## Statut

Acceptée le 2026-07-21 comme architecture future, après challenge de la
proposition humaine. Cette décision ne vaut ni implémentation, ni autorisation de
créer automatiquement des assets, cavités, séparateurs, cales ou conteneurs.

## Date

2026-07-21

## Cartes liées

- `P64-A02 — Calcul étagé et réutilisation de capacité` ;
- `P64-C01 — Carte de capacité en lecture seule` ;
- `P64-C02 — Insertion locale d'asset et recertification` ;
- `P64-C03 — Baie réservée et insertion d'un conteneur autonome` ;
- `P64-CV — Gate Fusion de réutilisation bornée` ;
- `P64-F01` à `P64-F03` pour la topologie du résiduel et les réserves utiles ;
- `P45` pour les cavités, cloisons et futures formes.

## Contexte

Après un solvage et une finalisation, une enveloppe de conteneur peut être plus
grande que le strict nécessaire à ses cavités. Le surplus est actuellement de la
matière autour ou sous les cavités. Le plan peut aussi conserver, si une future
politique l'autorise explicitement, une baie rectangulaire utile dans la boîte.

Ces volumes peuvent aider une personne qui ajoute ensuite un asset ou un
conteneur de taille voisine. Relancer immédiatement toute la recherche globale
peut être inutile lorsque la nouvelle demande tient dans une enveloppe monde
déjà certifiée et ne déplace aucun corps existant.

Mais trois objets différents ne doivent pas être confondus :

1. une nouvelle cavité dans un conteneur existant ;
2. un nouveau séparateur ou une réorganisation interne du même corps ;
3. un nouveau conteneur autonome, donc un nouveau corps avec placement, appui et
   ordre de retrait propres.

Le premier cas peut parfois réutiliser le placement global. Le troisième ne le
peut que si une baie de boîte a été explicitement préservée et certifiée. Toute
autre promesse de « zéro recalcul » serait fausse.

## Options

### Option A — Toujours relancer le solveur complet

- Avantage : un seul chemin de certification.
- Inconvénient : coût et instabilité inutiles pour une insertion strictement
  contenue dans une enveloppe inchangée.

### Option B — Modifier directement le plan final sans recertification

- Avantage : retour immédiat.
- Inconvénient : certificats, digests, supports, fonds et réservations deviennent
  faux.
- Risque : géométrie non constructible présentée comme valide.

### Option C — Carte de capacité dérivée, tentative locale et fallback global

- Avantage : réutilisation sûre du plan quand les invariants restent vrais.
- Inconvénient : nouvelle couche de diagnostic et deux chemins d'insertion.
- Risque : interpréter une opportunité comme une garantie avant validation.

## Décision

Retenir l'option C.

### Deux familles de capacité

#### Zone d'opportunité interne

Une `InternalOpportunityZone` est une région orthogonale située dans
`final_outer_envelope` mais hors :

- cavités existantes et leurs jeux ;
- parois, cloisons et fond minimaux ;
- features et accès réservés ;
- coupes de plateau/livret ;
- surfaces nécessaires au support et au retrait ;
- intervalles techniques globaux.

Elle décrit un volume potentiellement convertible en nouvelle cavité ou en
réorganisation interne. Elle n'est ni une cavité, ni un asset, ni un corps.

#### Baie de réserve de boîte

Une `BoxReserveBay` est un volume de boîte laissé intentionnellement libre par
la finalisation, nommé, borné et certifié. Elle peut accueillir plus tard un
conteneur autonome sans déplacer les placements existants, sous réserve de
validation du nouveau corps, de ses jeux, appuis, réservations et retrait.

Une région résiduelle accidentelle ou non certifiée n'est jamais promue en baie.

### Carte dérivée et mémoire courte

La « mémoire courte » devient une `CapacityOpportunityMap` interne et dérivée.
Elle porte :

- digest du projet source ;
- digest du placement global ;
- digest et politique de finalisation ;
- version du détecteur ;
- zones, origine locale ou monde et dimensions maximales ;
- orientations autorisées ;
- accès et direction d'insertion ;
- parois/fonds disponibles ;
- compatibilité plateau/réservation ;
- codes de rejet et limites du calcul.

Elle n'est pas persistée comme choix utilisateur ni comme vérité géométrique.
Toute modification d'une dépendance la rend obsolète. Une session peut la mettre
en cache par digest ; une réouverture peut la reconstruire depuis le plan courant.

### Détection bornée

Le détecteur utilise les faces utiles des cavités, enveloppes, réservations et
plans de coupe pour produire des AABB maximales puis les dédupliquer par
inclusion. Il ne voxelise pas la boîte et ne cherche pas toutes les formes
possibles.

Une zone est conservée seulement si elle dépasse des minima explicites. Les
tailles « similaires » servent à classer les suggestions à partir des assets,
cavités et conteneurs existants ; elles n'inventent jamais une nouvelle mesure.
La personne choisit un asset réel, un preset ou des dimensions explicites avant
toute mutation.

### Insertion d'un asset dans une enveloppe inchangée

Le chemin rapide est autorisé seulement si :

1. la nouvelle cavité tient entièrement dans une zone courante ;
2. l'enveloppe extérieure finale et le placement monde restent identiques ;
3. la pose de l'asset, ses jeux et la cloison sont explicites ;
4. le certificat local du conteneur est reconstruit ;
5. le certificat global commun est rejoué sur le plan inchangé ;
6. la CAD IR et la scène restent obsolètes jusqu'à matérialisation explicite.

Ajouter l'asset modifie bien la source et invalide l'ancien certificat. Le gain
est l'absence de recherche de placement, jamais l'absence de validation.

Si une condition échoue, la mutation est refusée atomiquement ou conservée comme
édition non résolue avec proposition de `Calculer l'agencement`. Aucun autre
conteneur n'est déplacé silencieusement.

### Insertion d'un conteneur autonome

Un nouveau conteneur peut suivre un chemin incrémental seulement dans une
`BoxReserveBay` courante. Le moteur teste variantes autorisées, orientations,
jeux globaux, support, retrait et réservations dans cette baie, sans bouger les
corps existants.

Sans baie compatible, le nouveau conteneur entre dans le projet source mais le
plan devient obsolète et exige le solveur global. Une zone interne à un corps ne
peut pas être renommée « nouveau conteneur » pour contourner cette règle.

### Séparateurs, cales et formes

- un séparateur modifie la géométrie interne du conteneur et relève du certificat
  local P45 ;
- une cale est un corps explicite relevant de P64-F03 et de préconditions
  physiques ;
- une forme spéciale d'encastrement ne peut être inventée par la carte de
  capacité ; elle exige un producteur géométrique P45/P46 ;
- aucun objet n'est créé automatiquement parce qu'une zone existe.

### UX cible

Dans un conteneur finalisé, un contrôle discret peut afficher :

- `Capacité disponible` ;
- dimensions maximales et limites ;
- `Ajouter un élément ici` ;
- `Ajouter une séparation`, seulement quand P45 l'autorise ;
- motif d'indisponibilité ou nécessité d'un recalcul global.

Au niveau du plan global, une baie de réserve peut proposer
`Ajouter un conteneur dans cette réserve`.

Ces contrôles restent cachés par défaut. Les zones techniques, digests et codes
de rejet vivent dans le diagnostic secondaire.

## Conséquences

### Positives

- des ajouts locaux peuvent réutiliser un placement sans relancer la recherche ;
- les volumes d'expansion deviennent inspectables et utiles ;
- les réserves futures sont intentionnelles plutôt que des vides oubliés ;
- le fallback vers le solveur global reste honnête et explicite.

### Négatives

- le plan porte un nouvel artefact dérivé et davantage de digests ;
- convertir de la matière en cavité peut dégrader rigidité ou imprimabilité ;
- la différence entre cavité, séparateur et conteneur autonome doit être très
  claire dans l'interface.

### Risques et mitigations

- faux volume disponible : calcul fail-closed et certificat local reconstruit ;
- ancien plan réutilisé à tort : digests source/placement/finalisation exacts ;
- perte de résistance : minima contractés, gate physique et aucune promesse
  d'impression ;
- baie qui bloque le retrait : validateur global autoritaire ;
- explosion des régions : AABB adaptatives, déduplication et caps ;
- suggestion absurde : comparaison seulement à des dimensions sources connues.

## Alternatives refusées

- ajouter sans invalider ni recertifier ;
- traiter le surplus solide comme une cavité déjà disponible ;
- créer automatiquement un asset, séparateur, cale ou conteneur ;
- utiliser une zone interne comme nouveau corps autonome implicite ;
- promettre qu'un nouveau conteneur n'exige jamais de solvage global ;
- conserver une carte de capacité après changement de ses digests.

## Suivi

- Contrat détaillé : `docs/P64_POST_SOLVE_CAPACITY_REUSE_CONTRACT.md`.
- P64-C01 reste read-only et ne modifie ni projet, ni géométrie, ni scène.
- P64-C02 dépend de P64-C01, P45 et de la finalisation certifiée.
- P64-C03 dépend d'une politique de baie acceptée et de P64-F03.
- Les mutations visibles exigent une gate Fusion P64-CV ; toute revendication de
  résistance ou de qualité physique exige une impression réelle.
- `fusion-validated: false`, `print-validated: false`.
