# ADR-0044 - Contrat de couvercle amovible V0

## Statut

`proposed` - en attente de la validation P34.

## Contexte

BGIG sait produire des bacs ouverts, mais aucune piece mobile ou fermante n est encore calibree par impression. Une fermeture ajoute des jeux, une hauteur, une friction et un comportement dependant du materiau. Le produit doit choisir un premier mecanisme avant implementation.

## Options

1. Aucun couvercle.
2. Couvercle pose amovible, sans clip.
3. Couvercle coulissant sur rails.
4. Clip ou charniere integree.

## Proposition

Choisir le couvercle pose amovible V0 : une seconde piece qui couvre le bac et se pose par gravite, sans verrouillage ni element flexible.

## Invariants si accepte

- le bac reste un corps separe du capot ;
- le plan et les tolerances existants ne changent pas ;
- un jeu de couvercle est declare explicitement, jamais deduit silencieusement ;
- le contrat refuse les dimensions incompatibles ;
- Fusion consomme une CAD IR deja resolue ;
- le statut reste experimental puis `a valider par impression reelle`.

## Consequences

Cette option est plus robuste et plus facile a expliquer qu un rail ou un clip, mais elle ne garantit ni tenue en transport ni ajustement avant une mesure reelle. Les mecanismes coulissants, clips et charnieres restent hors scope.