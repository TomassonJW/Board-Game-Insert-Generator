# Journal P64-L09R-E — progression et réactivité

Date : 2026-07-25

## Changement produit

La jauge d’activité est maintenant une zone temporaire pleine largeur juste au-dessus de `Calculer`, `Finaliser` et `Matérialiser`. Calcul et finition montrent le temps écoulé sur leur budget total ; la matérialisation reste indéterminée. La zone disparaît entièrement dès qu’aucune opération n’est active.

## Exécution sûre

Calcul minimal et finition passent par un worker Python pur alimenté uniquement par une copie JSON et des chemins texte. Le callback Fusion conserve le polling, la publication HTML et toute synchronisation CAD. La voie longue est unique, les accès concurrents au pont partagé sont rejetés sans course, puis les validations, sauvegardes et réglages différés sont repris.

Un résultat n’est publié que si la révision et le digest du projet, du profil de calcul et du profil de finition correspondent encore. Sinon il est marqué obsolète et ignoré.

## Validation

- 130/130 tests ciblés ;
- JavaScript `node --check` OK ;
- compilation Python OK ;
- suite complète 867/867 en 243,972 s, un test natif ignoré ; tests documentaires 2/2 et diff check OK.

## Suite

P64-L09R-F devient la prochaine mission unique : cas 28x30, plateau, empilement au-dessus d’une ouverture, collisions et réservations négatives, fins anticipées, deadlines, mesures séparées et préparation du dossier P64-L09R-V sans installation Fusion.