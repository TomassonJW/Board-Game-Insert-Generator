# Clarification V0.1 - Le surplus devient de la matiere dans les bacs

## Retour produit

Thomas confirme que l editeur premium doit permettre de saisir la boite, les
assets, leurs quantites et regroupements, les plateaux/livrets, les jeux, parois,
fonds et autres parametres utiles.

Les mesures des assets calibrent les cavites. Elles ne doivent pas limiter les
dimensions exterieures des bacs a leur minimum.

## Correction

Le volume restant doit etre absorbe intelligemment en agrandissant les enveloppes
des bacs demandes : parois plus larges autour des cavites et fonds plus epais sous
les cavites. Les cavites restent calibrees.

Les petits corps automatiques observes dans P43 sont une erreur de modele. Aucun
bac vide, remplissage plein ou separateur n est cree sans demande explicite.

## Impact

- ADR-0054 porte le nouvel invariant ;
- P39 et P40 restent des fondations reutilisables ;
- P41/P42 doivent etre repris ;
- V0.2 et V0.3 restent bloques jusqu a la nouvelle acceptance P60.
