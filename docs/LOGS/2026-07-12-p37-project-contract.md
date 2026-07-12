# 2026-07-12 - P37 contrat projet V0.1

## Resultat

Le coeur Python expose maintenant `bgig.project.v1`, un contrat utilisateur
strict et local pour la boite, les pieces, les groupes de bacs, les
plateaux/livrets et les remplissages.

## Preuves

- validation native V1 ;
- migration non destructive de `bgig.local_composer.v0` ;
- conservation des options P33/P34 comme donnees differees ;
- cas 72 lignes de pieces, 50 groupes et 25 elements plats valide sans limite
  metier codee en dur ;
- API locale de nouveau projet et de normalisation/migration ;
- tests Python et build TypeScript/Vite.

## Limites assumees

P37 ne calcule pas encore la taille d'un bac, la pile haute, un remplissage ou
un placement. Les routes P21 historiques restent fonctionnelles sur V0 ; P39
les reconnectera a V1 apres derivation honnete des bacs.

## Suite

P38 remplace le parcours Studio P23 par les tableaux V1 et masque les controles
apparence/couvercle hors du flux V0.1.
