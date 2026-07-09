# ADR-0033 - Tray storage semantics V0

## Statut

Accepte - 2026-07-09.

## Contexte

`P14-USABLE-ASSET-TRAY-SPRINT-V` a montre que le moteur fonctionne techniquement, mais que le resultat n'est pas encore "usable" pour un utilisateur. Le preset P14 complet lit correctement les assets, genere des modules, compartiments, encoches, rapports de printability et registry OK. Le probleme est semantique : les assets tokens, dice, meeples et generic sont dimensionnes comme des piles verticales cherchant a utiliser presque toute la hauteur disponible, ce qui produit des modules trop hauts et visuellement surprenants.

Le sprint P15 realigne le modele produit sans introduire de solveur global, de nouvelle geometrie complexe ou de validation d'impression.

## Semantique actuelle auditee

- `tokens`, `dice`, `meeples`, `generic` : `z_mm` est une epaisseur/hauteur unitaire d'un item. `count` est utilise pour calculer `capacity_per_stack`, `pile_count`, `items_per_pile`, `stack_height_mm` et l'enveloppe de stockage.
- `cards`, `sleeved_cards` : `z_mm` est la hauteur totale fournie du paquet/deck. `count` est reporte mais non multiplie.
- `count` : quantite declaree lue pour le sizing count-aware des types itemises ; pour cartes, information reportee seulement.
- `grid_unit_mm` : taille d'une cellule de grille discrete issue de `volumetric_grid.unit_mm`.
- `grid span` / `theoretical_grid_extent_mm` : espace reserve par le placement dans la grille ; ce n'est pas une taille de body Fusion.
- `asset_fit` / `asset_fit_size_mm` : enveloppe utile des assets avec clearance interne, consommee par les cavites.
- `printable body` / `module body` : corps imprimable reel genere par Fusion, incluant murs et fond.
- `cavity` : volume soustrait au body, derive de `asset_fit` ou de compartiments asset-specific.
- Grouping actuel : les assets compatibles sont groupes par `kind`, `containment_intent` et `dimension_confidence`; les compartiments restent par source asset dans un module groupe quand le layout tient.

## Decision

1. Conserver la semantique `z_mm` actuelle, mais la rendre explicite dans les rapports.
2. Introduire une semantique de rangement V0 : `storage_orientation`.
3. Le defaut pour `tokens`, `dice`, `meeples` et `generic` devient `flat_tray`.
4. `flat_tray` limite la hauteur de pile par une valeur `max_stack_height_mm` et force l'expansion XY avant l'expansion Z.
5. `vertical_stack` conserve l'ancien comportement consistant a utiliser la hauteur disponible, mais il doit etre demande explicitement.
6. `auto` reste autorise comme alias prudent vers `flat_tray` tant qu'aucun solveur de choix automatique n'est valide.
7. Les cartes et cartes sleevees restent separees : `z_mm` est la hauteur totale du deck.
8. La grille reste une `placement_reservation_lattice_v0` : elle reserve l'espace et place les modules, mais les bodies ne sont pas snaps au millimetre a la grille.
9. Le reporting doit dire explicitement : `grid_semantics`, `body_snap_to_grid`, `grid_span_is_reserved_space` et `body_size_may_be_smaller_than_grid_span`.

## Valeurs V0 retenues

Les valeurs P15 sont des heuristiques produit, pas des tolerances d'impression :

- tokens : `max_stack_height_mm = 12.0` par defaut ;
- dice : `max_stack_height_mm = 20.0` par defaut ;
- meeples : `max_stack_height_mm = 24.0` par defaut ;
- generic : `max_stack_height_mm = 16.0` par defaut.

Une valeur globale `max_stack_height_mm` peut override ces defaults dans les configs temporaires `quick_asset_box`. Une future version pourra ajouter des overrides par type ou par asset si le schema public est elargi.

## Consequences

- Les modules tokens/dice/meeples/generic ne doivent plus devenir automatiquement tres hauts dans les presets usuels.
- A count eleve, le moteur creera plus de piles XY avant d'augmenter Z.
- Les modules peuvent occuper plus de surface XY ; un rejet de placement est preferable a une tour trompeuse.
- Le rapport devient plus pedagogique : il explique la hauteur cible, la hauteur utilisee, l'expansion XY/Z et la nature de la grille.
- Fusion continue de consommer la CAD IR existante ; aucun import `adsk` n'est ajoute au coeur Python.

## Alternatives refusees

- Garder le comportement P14 par defaut : refuse car non usable visuellement.
- Ajouter un solveur global de packing : refuse en P15, trop large.
- Changer immediatement le schema public assets : refuse, pas necessaire pour une V0.
- Snapper les bodies a la grille physique : refuse, cela melangerait reserve de placement et geometrie imprimable.
- Visualiser chaque item Fusion : refuse, hors scope et potentiellement lourd.

## Suivi

- P15-M002/P15-M003 : implementer `storage_orientation` et `max_stack_height_mm` dans le sizing V0 et le reporting.
- P15-M004 : rendre explicite la semantique de grille dans CAD IR/report/Fusion summary.
- P15-M005 : preparer un preset smoke P15 realiste et reinstaller l'add-in pour validation humaine Fusion.
