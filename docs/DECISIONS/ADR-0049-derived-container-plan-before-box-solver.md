# ADR-0049 - Plan de bacs derive avant le solveur de boite

## Statut

Acceptee, decision reversible de la mission P39 du MVP V0.1.

## Date

2026-07-12

## Carte liee

- `P39 - Derivation des bacs et logements`.

## Contexte

Le projet utilisateur `bgig.project.v1` exprime les pieces, leur quantite et le
bac qu elles doivent partager. Il ne demande volontairement aucune dimension de
bac a l utilisateur. Les anciens candidats P13/P21 sont des objets techniques
historiques et ne peuvent pas redevenir la saisie principale.

P39 doit cependant produire un resultat concret au bouton `Construire` avant la
reservation des plateaux (P40), la fermeture de volume (P41) et la geometrie
(P42).

## Options

1. Reutiliser directement les candidats P13/P21 comme resultat utilisateur.
2. Attendre P41 et ne rien montrer avant le solveur complet.
3. Introduire un plan intermediaire pur : bacs requis et logements derives,
   sans placement dans la boite.

## Decision

Retenir l option 3 avec `bgig.container_derivation.v1`.

Le module pur `container_derivation.py` normalise le projet V1 ou migre P23,
puis produit un bac par `container_group_id` avec :

- logements par famille de pieces ;
- jeux internes, parois, fond, dimensions internes et externes minimales ;
- piles comptees pour rond, carre, rectangle, cube, pion et sur mesure ;
- paquet de cartes dont `z` reste l epaisseur totale declaree ;
- diagnostics explicables pour les bacs trop grands ou trop hauts.

Les formes non rectangulaires utilisent pour V0.1 une enveloppe rectangulaire
sure. Les arrondis, prises et formes ergonomiques restent V0.2. Le plan ne
place aucun bac dans la boite, n utilise pas le jeu entre bacs et ne genere ni
CAD, ni Fusion, ni promesse d impression.

La route locale `POST /api/project-v1/derive-containers` et le Studio affichent
ce resultat comme une etape intermediaire honnete.

## Consequences

- Le bouton `Construire mes bacs` a maintenant un resultat immediat et lisible.
- P40 consommera les dimensions derivees pour reserver plateaux et livrets.
- P41 reste l unique etape autorisee a fermer le volume global et appliquer le
  jeu entre bacs.
- Un bac impossible est bloque avec la mesure qui depasse au lieu d etre force.
- Il n y a pas de limite metier codee pour les quantites ; la recherche de
  grille de piles est bornee en temps.

## Alternatives refusees

- Montrer les candidats/layers historiques : retour du jargon et des dimensions
  techniques dans le parcours principal.
- Pretendre qu un bac derive est deja place ou imprimable : faux resultat.
- Ajouter maintenant des cavites rondes ou des formes ergonomiques : scope V0.2.
