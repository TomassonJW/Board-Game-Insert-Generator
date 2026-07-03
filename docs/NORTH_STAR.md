# North Star

Board Game Insert Generator vise a devenir un generateur semi-intelligent
d'inserts parametriques pour boites de jeux de societe.

La promesse long terme n'est pas de dessiner rapidement quelques boites
rectangulaires. La promesse est de formaliser une logique robuste de conception
parametrique, tolerancee, imprimable et explicable.

## Formulation courte

Transformer des contraintes de rangement mesurees en geometries imprimables,
modulaires, tolerancees, comprehensibles et iterables, sans enfermer la logique de
conception dans Fusion 360.

## Ambition produit

Un utilisateur doit pouvoir decrire :

- les dimensions internes reelles de sa boite ;
- les contraintes verticales liees au couvercle, aux plateaux, aux livrets et aux
  regles ;
- les assets a ranger : cartes, cartes sleevees, tokens, meeples, des, figurines
  simples, sacs, livrets ;
- ses intentions : setup rapide, rangement vertical, modules separables, maintien
  en place, lisibilite, economie de filament ;
- son profil d'impression : PLA standard, PETG, impression rapide, impression
  fine, imprimante bien calibree ou non.

Le systeme doit ensuite produire une ou plusieurs propositions d'organisation,
puis des corps imprimables coherents.

## Definition du succes

Le projet reussit quand :

- les donnees d'entree sont suffisamment simples pour un utilisateur motive ;
- les decisions de layout et de tolerance sont visibles ;
- les modules generes sont testables hors Fusion 360 ;
- l'adaptateur Fusion 360 peut produire des composants inspectables ;
- les impressions reelles permettent d'ajuster les profils ;
- un futur agent peut continuer le travail sans reinventer la roadmap.

## Philosophie

Le coeur du projet doit rester un moteur de conception, pas un script Fusion 360.

Fusion 360 est une cible de generation importante parce que son API Python permet
de creer des composants parametriques, de les inspecter et de les exporter. Mais
les decisions de layout, de tolerance et de validation doivent rester testables
hors Fusion.

## Ce que le projet doit apprendre a faire

A court terme :

- calculer des volumes rectangulaires simples ;
- appliquer des tolerances explicites ;
- produire un rapport de layout lisible ;
- preparer une sortie Fusion 360.

A moyen terme :

- creer des modules creuses ;
- generer des bacs a tokens, logements de cartes, casiers a des et zones libres ;
- ajouter des encoches de doigt, fonds arrondis, parois et separateurs ;
- proposer plusieurs layouts simples.

A long terme :

- composer des modules en L, T ou formes composites ;
- ajouter couvercles, rainures, languettes, charnieres et fermetures ;
- integrer texte, embossage, gravure, pictogrammes, textures et ajourages ;
- assister la conception par evaluation multi-criteres.

## Limites assumees

Le projet ne pretend pas resoudre l'optimisation parfaite du rangement en V0. Il
ne pretend pas non plus que des tolerances generiques suffisent pour toutes les
imprimantes. Les valeurs par defaut doivent rester prudentes, visibles et
ajustables.

Le vrai critere de qualite sera la capacite a passer progressivement du modele
theorique a des objets imprimes verifiables.
