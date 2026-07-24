# ADR-0087 — Support matériel réel et finalisation couplée bornée

- Statut : acceptée
- Date : 2026-07-24
- Mission : P64-L09A

## Contexte

La gate humaine P64-L08LV confirme que la correction SCIP 0.1.62 supprime le
plafond artificiel observé en 0.1.61 : le cas préparé termine en environ
25 secondes, puis une variante réelle avec un bac de cartes très compliqué
termine en environ 34 secondes. Cette preuve valide la recherche de faisabilité,
pas toute la sémantique géométrique du plan.

Deux limites distinctes sont maintenant observées :

1. un petit conteneur peut être placé au-dessus de l'ouverture d'un conteneur
   plus grand alors qu'il pourrait tomber dans cette ouverture ;
2. l'ajout d'un plateau peut faire échouer le calcul avant SCIP, car
   `_prepare_product_problem` refuse actuellement tout `problem.top_inset_zones`
   avec `top_inset_reservations_not_supported`.

Le certificat d'appui courant calcule encore largement l'intersection des
enveloppes XY. Il ne distingue pas la matière porteuse du rebord et le vide de
la cavité. Le refus des réservations signifie par ailleurs qu'un échec avec
plateau ne prouve aucune impossibilité géométrique.

Enfin, ADR-0069, ADR-0071 et ADR-0074 décrivent surtout une finalisation
optionnelle après un placement minimal. Cette séparation reste utile pour les
projets simples, mais elle est insuffisante lorsque l'expansion des enveloppes,
les réservations supérieures et les futures enveloppes de couvercles se
contraignent mutuellement.

## Décision

### 1. Limiter explicitement la portée de P64-L08LV

P64-L08LV est positive pour la correction de temps et l'obtention d'un premier
plan SCIP dans Fusion 0.1.62. Elle ne certifie ni les appuis matériels sur des
conteneurs ouverts, ni les réservations supérieures dans SCIP, ni l'impression.

### 2. Remplacer l'appui par enveloppe par un certificat de matière porteuse

Chaque placement inférieur doit exposer des régions porteuses réelles dans le
plan XY de son sommet :

- rebords et parois supérieures pour un conteneur ouvert ;
- surface pleine pour un corps réellement plein ;
- surface de fermeture uniquement si un mécanisme distinct la certifie comme
  porteuse ;
- aucune matière dans une ouverture ou une cavité.

Un placement supérieur hors sol est admissible seulement si :

1. il ne peut pas descendre dans une ouverture connectée à sa verticale ;
2. l'union des régions matérielles en contact fournit une aire d'appui minimale ;
3. la projection de stabilité requise est contenue dans l'enveloppe des appuis ;
4. les jeux Z, collisions, retraits et autres contraintes restent satisfaits.

Un pontage sur plusieurs rebords est autorisé lorsqu'il satisfait ces quatre
conditions. Une préférence de classement « grandes ouvertures vers le haut /
petits XY plutôt dessous » peut réduire les mauvais essais, mais ne remplace
jamais le certificat.

### 3. Interdire toute sémantique implicite de couvercle

`has_lid` ne crée ni surface pleine, ni nouvelle pose globale. Un futur
certificat de fermeture devra porter au minimum :

- la fermeture et la rétention des contenus ;
- l'enveloppe extérieure fermée et son épaisseur ;
- les surfaces porteuses et leur domaine de charge ;
- la stabilité, l'accès et les directions de retrait ;
- les poses globales autorisées.

Ce certificat appartient aux mécanismes P47-P50 et à l'horizon
`F-CLOSED-CONTAINER-POSE`. P64 ne pourra consommer que ses résultats certifiés.

### 4. Faire entrer les réservations supérieures dans le problème produit

Les plateaux et livrets ne sont ni ignorés, ni arrondis en une réduction globale
de hauteur. Leur empreinte, profondeur, ordre de retrait, prise et intersections
doivent être représentés exactement ou refusés honnêtement.

Le statut `top_inset_reservations_not_supported` reste un refus de capacité
temporaire. Il ne peut jamais être présenté comme une impossibilité de placement.

### 5. Utiliser une boucle bornée de placement et de fermeture

La cible devient :

1. obtenir avec SCIP un incumbent 3D minimal faisable ;
2. introduire les réservations plateaux/livrets et les futures enveloppes de
   mécanismes déjà certifiées ;
3. optimiser conjointement les dimensions extérieures finales et la
   distribution du volume résiduel ;
4. réparer localement placements et hauteurs lorsqu'une expansion crée un
   conflit ;
5. répéter les étapes 2 à 4 sous un nombre d'itérations et un budget uniques ;
6. rejouer un certificat global complet ;
7. matérialiser uniquement depuis ce plan final certifié.

L'incumbent SCIP est conservé comme point de départ. Une réparation locale est
tentée avant tout nouveau placement global. Le solveur global n'est rappelé que
si la réparation locale échoue et seulement avec le budget restant.

### 6. Préserver les cavités et l'objectif de remplissage

Les cavités d'assets, leurs jeux et leurs poses restent fixes pendant la
fermeture. Une réservation supérieure peut imposer une augmentation de Z, mais
la coupe résultante ne doit jamais percer une cavité, une paroi minimale ou un
fond minimal.

Après retrait des jeux et réservations, les conteneurs demandés absorbent le
volume imprimable restant par leurs faces admissibles. Aucun corps automatique,
micro-bac ou vide oublié n'est créé.

### 7. Ne pas publier un seed incomplet

Pour un projet sans réservation ni enveloppe de mécanisme active, un placement
minimal certifié peut rester matérialisable conformément à ADR-0074.

Pour un projet qui exige la boucle couplée, le premier placement SCIP est un
incumbent interne. Il ne devient ni `minimal_layout` courant, ni plan
matérialisable tant que les réservations actives et le certificat global final
ne sont pas satisfaits.

## Conséquences

- ADR-0074 reste normative pour la matérialisation minimale des projets dont
  toutes les contraintes actives sont déjà certifiées.
- ADR-0069 et les clauses de finalisation d'ADR-0071/ADR-0074 sont amendées :
  la fermeture n'est plus forcément une postproduction unique.
- Le validateur commun doit connaître la matière porteuse avant que le solveur
  puisse revendiquer un appui.
- La prise en charge des plateaux dans SCIP et le moteur de fermeture restent
  deux lots distincts et testables.
- Aucun changement de runtime, de schéma, de tolérance ou de valeur physique
  n'est autorisé par cette mission documentaire.

## Découpage accepté

1. `P64-L09B` — certificat de support matériel et anti-chute ;
2. `P64-L09C` — réservations supérieures fidèles dans la lane SCIP produit ;
3. `P64-F01B` — boucle bornée de fermeture, expansion et réparation locale ;
4. `P64-F02B` — objectifs équilibrés, proportionnels puis modulaires ;
5. `P64-L09V` — observation Fusion combinée après preuves automatisées.

`P64-L09B` est la prochaine mission unique. Aucun benchmark ni nouveau holdout
n'est requis pour cette correction de vérité géométrique.
