# ADR-0001 - Core engine before Fusion 360

## Statut

Accepte.

## Contexte

Le projet vise une integration Fusion 360, mais les decisions importantes concernent le layout, les tolerances, les volumes utiles et la representation des modules.

Mettre cette logique directement dans un add-in Fusion rendrait les tests difficiles, ralentirait le debug et couplerait le produit a une API CAD.

## Options

1. Construire directement un script Fusion 360.
2. Construire un moteur pur Python, puis un adaptateur Fusion.
3. Utiliser un autre noyau CAD des la V0.

## Decision

Construire d'abord un moteur pur Python testable hors Fusion 360.

Fusion 360 sera une cible de sortie. L'adaptateur recevra une representation intermediaire deja validee.

## Consequences

Positives :

- tests rapides ;
- architecture plus claire ;
- debug local ;
- possibilite de sorties futures ;
- separation des responsabilites.

Negatives :

- il faut maintenir une representation intermediaire ;
- certaines contraintes Fusion ne seront decouvertes qu'en V1 ;
- la V0 ne produit pas encore de fichier imprimable.

## Alternatives refusees

Le script Fusion direct est refuse parce qu'il transforme un probleme de conception parametrique en automatisation CAD fragile.
