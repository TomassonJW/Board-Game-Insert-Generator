# Volumetric Layout Strategy

## Objectif

BGIG doit evoluer d'un layout 2D de rectangles vers une organisation du volume
complet de la boite. Le moteur devra raisonner en X/Y/Z, en etages, en volumes
libres, en empilement, en reservations de boards/livrets et en ordre de retrait.

## Etat actuel

- `row_fill` et `grid` placent des cellules XY simples.
- Z sert surtout a verifier la hauteur du module et la hauteur utile.
- Les cavites et features sont locales aux modules mais restent abstraites.
- Aucun solveur volumetrique 3D n'est implemente.

## Concepts cibles

- `VolumetricCell` : unite ou reservation X/Y/Z dans la boite.
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

1. `P8-M001 - Specifier le modele de grille volumetrique 3D` : docs/tests de contrat seulement.
2. `P8-M002 - Representer les layers et reservations non imprimables` : modele pur, sans solveur.
3. `P8-M003 - Valider les collisions X/Y/Z dans une fixture simple` : moteur pur.

## Gates

- Gate architecture si le format de configuration public change de maniere incompatible.
- Gate impression reelle avant toute promesse de support/empilement physique.
- Gate Fusion si une vue 3D volumetrique cree une geometrie nouvelle dans Fusion.
