# P31 - Gate bacs fonctionnels

## Constat

P28 est un raccord complet mais produit des blocs. P30 rend cette limite visible dans le Studio. Les primitives necessaires a un premier bac existent deja : enveloppe rectangulaire, cavite CAD IR, validation de murs/fond et coupe Fusion top-open.

## Recommandation

`open_top_tray_from_selected_module.v0` : une cavite `free` par module P21, ouverte en haut, avec parois et fond existants. Les allocations restent informatives ; aucun compartiment ou notch n est introduit.

## Decision attendue

`P31 approuve` pour autoriser le code, ses tests et la preparation de la gate Fusion suivante.