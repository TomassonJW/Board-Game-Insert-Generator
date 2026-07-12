# ADR-0045 - Contrat de couvercle coulissant V0

## Statut

`superseded-for-product` par ADR-0047. Le choix C du 2026-07-11 reste historique, mais le contrat a deux rails exterieurs n est pas la specification V0.3 canonique.

## Contexte

Les bacs ouverts P31 sont observes dans Fusion mais ne sont pas encore valides
par impression. Un couvercle coulissant ajoute deux rails, du frottement, une
hauteur supplementaire et un jeu XY dependant de l'imprimante. Le produit doit
le representer sans le faire passer pour une piece fonctionnelle.

## Decision

Le premier mecanisme ferme de BGIG est un couvercle coulissant experimental :

- deux pieces separees a terme : bac et capot ;
- un axe de glisse `x` ou `y` explicite ;
- des parametres locaux et versionnes : epaisseur de capot, hauteur de rail,
  jeu de glisse et recouvrement aux extremites ;
- une evaluation de faisabilite par module et des refus explicites ;
- un apercu et un transport CAD IR metadata avant toute operation CAD.

Les valeurs V0 sont bornees pour preparer un coupon, pas pour redefinir les
tolerances globales : 0.8 a 3.0 mm pour capot/rail, 0.15 a 0.6 mm de jeu et 6 a
20 mm de recouvrement.

## Consequences

P34-M001 n'ajoute aucun rail, aucune rainure, aucun capot et aucune operation
Fusion. Il sauvegarde `bgig.mechanism.v0`, garde le digest P21 identique et
marque les modules `planned_for_coupon`, `refused` ou `not_requested`.

La materialisation P34-M002 devra produire deux corps explicitement lies au
contrat, etre observee dans Fusion, puis etre suivie d'un coupon imprime et
mesure. Aucun statut `print-validated` ne peut preceder ces mesures.

## Alternatives ecartees

- Aucun couvercle : utile comme valeur par defaut, mais ne repond pas au choix
  de fermeture.
- Couvercle pose : plus simple, mais non retenu par le choix humain.
- Clip ou charniere : trop dependant de la flexion, du materiau et de
  l'orientation pour un premier mecanisme.

## ADR liee

ADR-0044 est `not-retained` : elle documente l'option B proposee avant la
decision humaine et reste conservee pour l'historique.
