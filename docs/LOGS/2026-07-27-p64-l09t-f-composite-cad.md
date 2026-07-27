# Journal — P64-L09T-F certificat et CAD composites

## Date

2026-07-27.

## Décision d'exécution

La géométrie hybride v2 devient directement la géométrie produit et CAD. Le
pont temporaire vers la fermeture v1 est supprimé.

Les cavités restent figées dans leur pose monde minimale. Leur ouverture
verticale est une coupe du composant propriétaire exécutée après ses unions,
pas un vide imposé à tous les propriétaires pendant la fermeture.

## Livrables

- finaliseur borné `v10` et publication directe de la fermeture hybride v2 ;
- contrats de pose monde des cavités avec empreinte stable ;
- certificat de matérialisation composite v2 et sous-codes de rejet ;
- CAD IR cœur, annexes, unions, cavités, accès puis réservations ;
- politique Fusion pure `hybrid_xy_composite_v2` ;
- refus des divergences de géométrie et de pose.

## Validation

- gate ciblée : `157/157`, OK ;
- gate globale autorisée : `866/866` en `285.542 s`, un test ignoré ;
- scénario multi-propriétaires P66 : finalisation, CAD IR et adaptation Fusion
  pure réussies ;
- douze modules interdits exclus ; aucun benchmark ou holdout.

Statut : `P64-L09T-F-automated-validated`.

`fusion-validated=false`, `print-validated=false`.

Prochaine mission : P64-L09T-G, durcissement, package candidat, installation et
préparation automatique de la gate Fusion.
