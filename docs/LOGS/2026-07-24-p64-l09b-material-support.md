# 2026-07-24 — P64-L09B support matériel

## Décision appliquée

Le support 3D est désormais certifié sur la matière réelle au plan supérieur :
face pleine pour un solide, rebords pour un conteneur ouvert, sans effet de
`has_lid`.

## Effets

- chute dans une ouverture : rejet dur ;
- pontage : accepté seulement avec au moins 25 % de contact matériel et un
  polygone d'appui stable ;
- même calcul pour les voies internes, la fermeture continue, SCIP et le
  certificat commun ;
- plan historique non conforme : résultat borné non matérialisable, sans crash.

## Validation

- tests ciblés : OK ;
- suite complète : 843/843 ;
- benchmark et holdout : non exécutés, hors périmètre ;
- Fusion et impression : non exécutées.

## Suite

P64-L09C devient la prochaine mission unique : représenter fidèlement les
réservations supérieures dans SCIP et supprimer le refus générique actuel.
