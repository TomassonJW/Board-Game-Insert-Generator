# Volumetric Layout Strategy

## Objectif

BGIG doit evoluer d'un layout 2D de rectangles vers une organisation du volume
complet de la boite. Le moteur devra raisonner en X/Y/Z, en etages, en volumes
libres, en empilement, en reservations de boards/livrets et en ordre de retrait.

## Etat actuel

- `row_fill` et `grid` placent des cellules XY simples.
- Z sert surtout a verifier la hauteur du module et la hauteur utile.
- Les cavites et features sont locales aux modules mais restent abstraites.
- P8-M001 ajoute un socle declaratif `volumetric_grid` dans le coeur Python pur : unites X/Y/Z, size_units, layers, placements de modules, zones reservees/interdites et cellules libres reportees.
- P8-M002 enrichit ce socle avec ordre de retrait abstrait, directions d'acces,
  reservations typées et surfaces de support abstraites.
- Aucun solveur volumetrique 3D n'est implemente.

## Concepts cibles

- `VolumetricCell` : unite ou reservation X/Y/Z dans la boite, serialisee comme cellule `free`, `occupied`, `reserved` ou `forbidden` dans les rapports P8-M001.
- `Layer` : tranche de hauteur avec regles de support et retrait.
- `Reservation` : espace non imprime reserve a un board, livret, plateau ou vide fonctionnel.
- `FreeVolume` : volume restant exploitable ou a documenter.
- `StackRule` : contrainte d'empilement, support et poids.
- `RemovalOrder` : ordre dans lequel l'utilisateur peut retirer modules et couches.

## Invariants

- Le moteur pur decide le volume ; Fusion ne recompose pas le layout.
- Les cellules 2D existantes restent compatibles comme cas de base `single_layer`.
- Une reservation de board/livret est un volume non imprimable explicite.
- Une proposition volumetrique doit expliquer ses volumes libres et ses collisions refusees.

## Prochaines missions possibles

1. `P8-M001 - Specifier et implementer le socle de grille volumetrique 3D` : done, modele pur, config, validation, rapports et metadata CAD IR.
2. `P8-M002 - Approfondir reservations, layers et ordre de retrait` : modele pur, sans solveur complet.
3. `P8-M003 - Preparer les collisions X/Y/Z issues d'un futur planner` : moteur pur.

## Gates

- Gate architecture si le format de configuration public change de maniere incompatible.
- Gate impression reelle avant toute promesse de support/empilement physique.
- Gate Fusion si une vue 3D volumetrique cree une geometrie nouvelle dans Fusion.

## Socle P8-M001

Le bloc racine optionnel `volumetric_grid` represente une grille discrete qui
couvre exactement le volume utile : X/Y correspondent aux dimensions internes de
boite, Z correspond a `usable_height_mm`. Cette convention garde la reservation
sous couvercle hors grille utile.

Le moteur accepte uniquement des placements explicites. Il ne cherche pas encore
ou placer les modules. Il calcule :

- nombre total de cellules ;
- cellules occupees par module ;
- cellules reservees ;
- cellules interdites ;
- cellules libres ;
- volume libre approximatif en `mm^3`.

Les collisions simples entre placements, reservations et zones interdites sont
refusees par la validation. Cela reste un controle declaratif, pas un solveur.
## Enrichissement P8-M002

P8-M002 garde le modele declaratif : la configuration dit ce qui occupe, reserve
ou supporte une zone, mais le moteur ne cherche pas encore automatiquement une
solution. Les ajouts sont :

- `removal_order` sur placements et reservations amovibles ;
- `access_direction` pour rendre l'ordre de retrait explicable ;
- `reservation_kind` et `asset_kind` sur les zones reservees ;
- `support_surfaces` pour decrire une intention de support portee par le fond de
  boite, un placement de module ou une zone.

Les surfaces de support sont `abstract_only` et `physical_validation:
not_validated` dans les rapports/CAD IR. Elles ne prouvent pas la portance ou la
qualite d'impression.