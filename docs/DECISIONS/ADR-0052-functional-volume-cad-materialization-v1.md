# ADR-0052 - Materialisation CAD fonctionnelle du volume V0.1

## Statut

Acceptee, decision reversible de la mission P42 du MVP V0.1.

## Date

2026-07-12

## Carte liee

- `P42 - Geometrie fonctionnelle V0.1`.

## Contexte

P41 produit un plan complet et controle du volume de la boite, mais ce plan ne
contient encore aucun corps CAD. Le Studio ne doit pas presenter ce resultat
comme un insert fonctionnel tant que les parois, fonds, logements, supports et
remplissages ne peuvent pas etre lus par Fusion.

## Options etudiees

1. Generer directement les corps dans Fusion depuis le projet utilisateur.
2. Reutiliser les bacs P31 issus de l ancien portefeuille P21.
3. Materialiser le plan P41 dans une CAD IR pure, puis laisser Fusion la
   consommer.

## Decision

L option 3 est retenue.

`build_functional_cad()` produit `bgig.functional_cad_build.v1` a partir du
projet V0.1 normalise et du plan P41. Quand le plan est constructible, il emet
une scene `cad_ir.v0` :

- un corps rectangulaire ouvert par bac place ;
- une cavite ouverte par logement de famille de pieces ;
- les remplissages exacts demandes ;
- les bacs vides et supports automatiques qui conservent les parois minimales ;
- les remplissages pleins et separateurs demandes.

Les cellules automatiques compatibles sont d abord fusionnees de maniere deterministe, puis le jeu commun est conserve autour des regions resultantes. Une region
automatique trop petite apres ce retrait reste un jeu technique explique. A
l inverse, un bac vide exact demande par l utilisateur est refuse si ses parois
ou son fond minimaux ne tiennent pas : BGIG ne le rend jamais plus fin en
silence.

La rotation XY appliquee par P41 est egalement appliquee aux logements locaux.
Fusion ne recalcule ni les positions, ni les dimensions, ni les tolerances.

## Consequences

- Le coeur Python reste sans dependance Fusion.
- Le bouton `Construire mon insert` peut annoncer une geometrie fonctionnelle
  prete a observer dans Fusion, sans annoncer une validation Fusion ou une
  impression.
- La commande experte `export-project-v1-cad` produit une scene reproductible
  pour la preparation du smoke Fusion.
- Les corps V0.1 restent strictement rectangulaires : arrondis, encoches et
  couvercles restent dans les versions suivantes.

## Alternatives refusees

- Fusion comme solveur : casse la source de verite Python et rend les tests
  hors Fusion impossibles.
- Promouvoir P31 : son vocabulaire de selection P21 ne correspond pas aux
  groupes de bacs, plateaux et volumes P37-P41.
- Materialiser toute region libre sans retrait : ferait toucher les bacs entre
  eux ou la boite et violerait le jeu commun.
