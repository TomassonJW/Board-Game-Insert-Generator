# 2026-07-17 — P64-H07 beam 3D et portefeuille Auto

## Mission

Livrer un beam 3D borné, des efforts monotones et un portefeuille interne qui
ne sélectionne que des plans complets certifiés, sans ouvrir l'UI P64-H08.

## Réalisation

- ajout de `free_3d_beam` : plusieurs états EP/EMS, enveloppes finales,
  rotations XY, budgets durs, timeout et annulation ;
- ajout d'un adaptateur produit fail-closed pour cavités, enveloppes,
  réservations, appuis, retrait et conservation ;
- renforcement du certificat par correspondance exacte candidat/plan ;
- ajout de `portfolio_auto`, des profils Rapide/Normal/Approfondi monotones,
  du fast path stage, de la déduplication et du classement certifié ;
- chemin public, schéma, UI, CAD IR, scène et valeurs physiques inchangés.

## Preuves

- tests H07 beam, arrêt, adaptateur, portfolio, déduplication et snapshot ;
- corpus H04 simple/dense/réservations ;
- benchmark local de neuf combinaisons H01/H02/H03R × trois efforts : environ
  40 s au total, toutes avec une proposition Auto certifiée ;
- validations globales consignées dans le commit de mission.

## Limites

Le beam est une heuristique incomplète. Sur H01/H02/H03R, la baseline certifiée
reste mieux classée ; cela est attendu et évite une régression. Les réglages ne
sont pas encore visibles dans Fusion. Aucune preuve Fusion ou impression n'est
ajoutée ; `print-validated: false`.

## Suite

P64-H08 uniquement : réglages Fusion, diagnostic secondaire, stabilité du
focus et préparation de P64-V2.
