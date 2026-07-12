# Hotfix P61 - synchronisation de scene Fusion

## Declencheur

Le retour humain du 2026-07-13 indique que la modelisation ne part plus depuis
la palette P61. Le CAD IR de l essai est bien produit avec trois composants : le
defaut se situe donc entre la demande de materialisation et la scene Fusion.

## Cause

`materialize_project` utilisait toujours l action Fusion stricte `generate`.
Cette action refuse volontairement un document qui contient deja une scene
BGIG afin d eviter les doublons. L utilisateur devait alors decouvrir une
seconde action `regenerate_project`, alors que le bouton principal promettait
de mettre Fusion a jour.

Le bridge considerait aussi toute execution non explicitement refusee comme
`synchronized`, sans verifier que la scene generee etait retrouvable dans le
registre BGIG.

## Correction

- creation si aucune scene BGIG n existe ;
- regeneration si exactement une scene BGIG taguee et saine existe ;
- blocage sans suppression pour toute scene multiple ou ambigue ;
- inspection obligatoire apres execution et nombre exact de corps avant le
  statut `synchronized` ;
- rapport Fusion conserve dans `Details techniques` en cas de blocage.

## Validation

Les 392 tests automatises passent et couvrent notamment creation, remplacement
sur scene saine, refus ambigu et absence de faux succes. La validation manuelle
dans Fusion reste requise ; aucune validation impression n est revendiquee.
