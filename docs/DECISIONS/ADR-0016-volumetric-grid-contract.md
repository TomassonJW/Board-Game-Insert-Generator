# ADR-0016 - Volumetric grid contract

## Statut

Accepte

## Date

2026-07-06

## Carte liee

- `P8-M001 - Specifier et implementer le socle de grille volumetrique 3D et layers`

## Contexte

La North Star demande un moteur capable de raisonner sur tout le volume X/Y/Z de
la boite : etages, volumes libres, reservations de boards/livrets, zones
interdites et modules multi-hauteurs. Le projet possede deja un layout 2D simple
et une CAD IR, mais aucun socle discret 3D testable hors Fusion.

## Options

1. Garder P8-M001 documentaire uniquement.
2. Ajouter directement un solveur volumetrique.
3. Ajouter un contrat declaratif `volumetric_grid` sans solveur ni Fusion.

## Decision

Retenir l'option 3.

Le coeur Python accepte un bloc racine optionnel `volumetric_grid` qui decrit :

- `unit_mm` et `size_units` ;
- des `layers` ;
- des `module_placements` explicites ;
- des zones `reserved` ou `forbidden` ;
- une synthese de cellules libres, occupees, reservees et interdites.

La grille doit couvrir exactement X/Y de la boite et Z de `usable_height_mm`.
Fusion ne consomme cette information que comme metadata CAD IR additive et ne
cree aucune geometrie volumetrique nouvelle.

## Consequences

Positives :

- le modele volumetrique devient testable sans Fusion ;
- un module peut occuper plusieurs unites X/Y/Z ;
- les reservations et volumes libres deviennent visibles dans Markdown/JSON/CAD IR ;
- le futur solveur aura un contrat stable a consommer.

Negatives et risques :

- le schema JSON public s'elargit ;
- les placements restent manuels et peuvent donner une impression de solveur qui
  n'existe pas encore ;
- le volume libre est approximatif car base sur des cellules discretes.

## Alternatives refusees

- Documentation seule : insuffisante pour tester les invariants de grille.
- Solveur complet : premature, plus risque, et hors scope P8-M001.
- Generation Fusion directe : interdite par la gate humaine de cette mission.

## Suivi

- `P8-M002` peut enrichir reservations, ordre de retrait et surfaces de support
  abstraites.
- Toute generation Fusion volumetrique ou vue 3D reste sous gate humaine.
- Toute validation de support physique ou empilement reste sous gate impression.