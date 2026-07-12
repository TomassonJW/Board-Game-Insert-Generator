# Contrat de fermeture de volume V0.1

`bgig.volume_closure.v1` est le plan complet, avant CAD, d un insert V0.1.

## Sortie

- `placements[]` : bacs imprimables places en X/Y/Z ;
- `reservations[]` : pile de plateaux/livrets non imprimable ;
- `fill_placements[]` : volumes exacts demandes ;
- `free_regions[]` : chaque region restante est classifiee ;
- `support` : support de la pile superieure ;
- `validation` : collisions et conservation exacte du volume ;
- `summary.status` : `constructed_plan` ou `impossible`.

Les volumes creux sont proposes par defaut. Un volume plein n apparait comme
candidat que si l utilisateur a choisi `solid`. Un remplissage `exact` est place
ou le plan devient `impossible` avec une raison lisible.

Le plan n est ni de la geometrie CAD, ni une validation Fusion ou impression.
