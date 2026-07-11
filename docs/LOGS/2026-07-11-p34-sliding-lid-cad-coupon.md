# P34-M002 - Coupon CAD IR coulissant a deux pieces

## Resultat

Le moteur conserve l'organisation P21 et ajoute seulement un coupon a cote de
la boite quand le coulissant est demande : un bac et un capot. Le capot est une
plaque rectangulaire avec deux glissieres laterales jointes par la nouvelle
operation limitee `join_rectangular_prism`.

## Garanties

- un seul coupon pour le premier module compatible, jamais un capot sur tous les bacs ;
- aucun changement de solveur, de digest P21 ou de tolerance globale ;
- refus conserves pour les modules incompatibles ;
- Fusion reste un adaptateur et `print-validated` reste faux.

## Preuves hors Fusion

- calcul pur de geometrie et refus P34 ;
- export Local Composer/CLI avec contrat de coupon ;
- plan Fusion hors API avec deux joins ;
- tests Python, compilation add-in et preparateur Fusion local.

## Gate suivante

Le smoke Fusion humain doit confirmer le capot unique et ses deux glissieres.
L'impression mesuree reste une gate physique distincte.
