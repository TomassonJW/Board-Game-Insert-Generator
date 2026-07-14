# ADR-0061 - Sequencement post-MVP et quarantaine des complements

## Statut

Acceptee le 2026-07-13 par clarification produit explicite.

## Date

2026-07-13

## Cartes liees

- P66-M000 - Quarantaine des complements experimentaux
- P66-M001 / P66-V - Preparation et gate du MVP V0.1
- P67 - Atelier humain de priorisation post-MVP
- P44 a P50 - V0.2 formes/ergonomie puis V0.3 couvercles/calibration
- P68 - Premiers retours d usage et d impression
- P69 - Revue UI/UX exhaustive apres P44-P50

## Contexte

P44 a P50 ont deja une signification canonique dans ADR-0047, les contrats MVP,
la roadmap, le backlog et les gates. Les renumeroter apres P70 casserait cette
trace sans changer le produit.

Le retour humain confirme aussi que les actions Bac vide, Bloc plein / cale et
Separateur ne portent pas encore le comportement attendu. Les supprimer du
schema ou du moteur casserait inutilement les projets historiques ; les laisser
au premier niveau du MVP promettrait une fonction non acceptee.

Enfin, deux besoins humains distincts existent apres le MVP : prioriser les
briques V0.2/V0.3 a partir d un usage reel, puis conduire une revue UI/UX
exhaustive une fois ces briques fonctionnelles disponibles.

## Options

### Option A - Renumeroter P44 a P50 apres P70

Avantage : ordre numerique apparent.

Inconvenients : migration de nombreuses references, perte de lisibilite
historique et aucun gain fonctionnel.

### Option B - Conserver P44 a P50 et ajouter des gates de pilotage

Avantages : historique stable, priorites humaines explicites et aucune confusion
entre lot fonctionnel, observation physique et revue UX.

Inconvenient : l ordre d execution n est pas strictement croissant numeriquement.

### Option C - Supprimer les complements du modele

Avantage : surface et moteur simplifies.

Inconvenients : migration destructive, perte de compatibilite et fermeture
prematuree d une fonction qui pourra etre redefinie correctement plus tard.

## Decision

Retenir l option B et refuser l option C.

1. P44 a P50 conservent leurs identifiants canoniques. Les numeros de lots sont
   des identifiants de pilotage, pas un ordre Git.
2. P66-M000 retire provisoirement la creation de Bac vide, Bloc plein / cale et
   Separateur du parcours normal de la palette.
3. Le schema, le loader, le coeur et la materialisation des complements
   explicitement presents dans un ancien projet restent compatibles.
4. Aucun complement automatique n est autorise et la fixture d acceptation P66
   contient zero complement.
5. P66-M001 prepare ensuite la gate P66-V sans modifier le produit.
6. Apres P66 OK, P67 conduit un atelier humain de priorisation. P44-M001 ne
   devient `ready` qu apres cette decision.
7. P68 recueille les premiers retours d usage et d impression sans modifier les
   tolerances globales.
8. P44-P46 portent la V0.2 formes/ergonomie ; P47-P50 portent la V0.3
   couvercles/calibration.
9. Apres P50, P69 conduit la revue UI/UX exhaustive et tres commentee qui cadre
   les versions suivantes.

## Consequences

### Positives

- les references historiques restent stables ;
- le MVP ne montre plus une fonction de complement non acceptee ;
- les anciens projets ne sont pas casses ;
- les premieres impressions peuvent nourrir les choix V0.2 ;
- la revue de priorite et la revue UI/UX finale ne sont plus confondues.

### Negatives

- la sequence P66 -> P67 -> P44 n est pas numeriquement croissante ;
- le code des complements reste present comme compatibilite dormante ;
- une future reactivation exigera un nouveau contrat produit et des tests.

## Alternatives refusees

- Renumeroter P44-P50 : cout documentaire et historique disproportionne.
- Laisser les actions visibles mais marquees experimentales : surcharge et
  promesse confuse dans le MVP.
- Supprimer les complements du coeur : changement destructif non necessaire.
- Fusionner P67 et P69 : les decisions n interviennent pas au meme moment et ne
  disposent pas des memes preuves.

## Suivi

- P66-M000 implemente seulement la quarantaine de surface et sa compatibilite.
- P66-M001/P66-V restent le chemin de fermeture du MVP.
- P67, P68 et P69 sont documentes par des contrats separes.
- Toute reactivation des complements exige une decision humaine issue de P67 ou
  d une ADR ulterieure.

## Suivi P67 du 2026-07-14

P67 est en revue. ADR-0062 propose de placer une fondation UX bornee dans P44
avant les geometries P45, sans renumeroter P44-P50 et sans avancer P69. Cette
reorientation reste soumise a P67-V. La quarantaine des complements reste
pleinement active ; aucune toolbar ne peut les reactiver sans contrat accepte.

## Decision P67-V du 2026-07-14

P67 accepte l option C d ADR-0062 : P44 commence par une fondation UX bornee,
P45 conserve les geometries ergonomiques et P46 reste la gate V0.2 complete.
Les identifiants P44-P50 ne changent pas.

La quarantaine des complements est confirmee `pour maintenant`. Bac vide, Bloc
plein / cale et Separateur ne reviennent ni dans la toolbar ni dans les cartes
normales. Cette decision reste revisitable seulement par un futur contrat
separe ; la compatibilite historique demeure.
