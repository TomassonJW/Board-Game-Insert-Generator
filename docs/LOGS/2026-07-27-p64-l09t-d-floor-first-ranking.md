# Journal — P64-L09T-D classement plancher d'abord

Date : 2026-07-27.

## Décision appliquée

Le portefeuille minimal classe désormais les plans complets certifiés par
conteneurs élevés, bases Z, volume élevé et gêne sous les réservations avant
empreinte, piles et compacité.

La lane de piles réservées conserve son exploration intermédiaire historique,
puis classe plusieurs états complets selon cette politique. Une pile nécessaire
reste donc trouvable ; la préférence basse ne devient pas une contrainte
gloutonne.

Les axes sont exposés dans les métriques, la provenance de recherche, le
candidat retenu, le pool de finition et le witness.

## Validation

- gate ciblée : `107/107`, OK ;
- lane SCIP : `19/19`, OK avec une intégration native ignorée ;
- contrats documentaires : `10/10`, OK ;
- gate globale autorisée : `863/863` en `286.898 s`, un test ignoré ;
- onze modules benchmark/corpus/tournoi exclus, aucun artefact recalculé.

Statut : `P64-L09T-D-automated-validated`.

`fusion-validated=false`, `print-validated=false`.

Prochaine mission : P64-L09T-E, fermeture hybride réelle.
