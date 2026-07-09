# ADR-0034 - Packing 2D ergonomique des piles flat tray V0

## Statut

Accepte

## Date

2026-07-09

## Carte liee

- `P16-M001 - Documenter la strategie flat_tray_2d`
- `P16-ERGONOMIC-2D-TRAY-PACKING-SPRINT`

## Contexte

P15 a corrige le probleme des modules asset-first qui montaient automatiquement en tours hautes. Pour les assets simples (`tokens`, `dice`, `meeples`, `generic`), `storage_orientation = auto` se resout maintenant en `flat_tray` avec `max_stack_height_mm`.

La validation humaine P15 a confirme que les modules restent bas, mais a ouvert une dette produit : le layout `flat_tray` V0 etale encore les piles principalement en ligne X. Le resultat est mathematiquement coherent mais peu ergonomique : des des, cubes ou tokens deviennent des barres longues alors qu'un vrai insert devrait utiliser plusieurs rangees/colonnes.

## Options

1. Conserver `flat_tray_linear_v0` comme defaut et documenter seulement la limite.
   - Simple et sans risque technique.
   - Mauvais alignement produit : le systeme reste peu utilisable.
2. Ajouter directement un solveur global de packing/optimisation.
   - Plus puissant a long terme.
   - Trop large pour le MVP, plus difficile a tester, et contraire au scope sans backtracking.
3. Introduire `flat_tray_2d_v0` comme heuristique deterministe bornee.
   - Corrige l'intuition principale sans dependance lourde.
   - Reste explicable et testable.
   - Ne cherche pas un optimum global.

## Decision

Pour `tokens`, `dice`, `meeples` et `generic`, le defaut produit devient `flat_tray_2d_v0`.

`flat_tray_linear_v0` designe l'ancien comportement P15 : apres calcul de `items_per_pile` et `pile_count`, les piles sont disposees surtout sur une seule rangee X.

`flat_tray_2d_v0` dispose les piles sur une grille 2D locale :

- `items_per_pile` : nombre d'items empilables verticalement dans une pile selon `max_stack_height_mm` et `z_mm` ;
- `pile_count` : nombre de piles necessaires pour contenir `count` items ;
- `pile_grid_columns` : nombre de colonnes de piles dans le module ;
- `pile_grid_rows` : nombre de rangees de piles dans le module ;
- `pile_pitch_x_mm` / `pile_pitch_y_mm` : pas local entre piles, derive de la taille asset et du clearance ;
- `target_aspect_ratio` : ratio cible largeur/profondeur du rectangle utile ;
- `max_module_length_mm` : contrainte souple pour eviter les barres longues ;
- `max_stack_height_mm` : plafond de hauteur de pile deja expose par P15.

La grille volumetrique BGIG reste distincte : `grid_semantics = placement_reservation_lattice_v0`, `body_snap_to_grid: no`, `grid_span_is_reserved_space: yes`. Le packing 2D est un layout interne au module, pas un snap physique du body sur les cellules de grille.

`vertical_stack` reste un mode explicite et futur/legacy pour produire volontairement des modules hauts. Il ne redevient pas le defaut.

## Consequences

Positives :

- Les modules simples deviennent plus proches d'un bac utilisable.
- Les cas comme 8 des ou 24 cubes peuvent former des grilles 4x2, 3x3 ou 4x3 plutot que des lignes 8x1 ou 12x1.
- Le comportement reste deterministe et facile a tester.
- Le reporting peut expliquer pourquoi une disposition est 2D ou pourquoi le fallback reste lineaire.

Negatives / risques :

- Ce n'est pas un solveur global : le resultat peut rester sous-optimal.
- Les compartiments restent rectangulaires par asset source, pas par pile ni par item.
- La notion de ratio cible est heuristique et devra etre ajustee par validation humaine.
- Une contrainte `max_module_length_mm` trop stricte peut forcer un refus ou un layout moins compact.

## Alternatives refusees

- `flat_tray_linear_v0` comme defaut durable : refuse parce que la validation P15 l'a explicitement identifie comme peu ergonomique.
- Solveur global/backtracking : refuse pour P16 afin de garder un increment borne, testable et compatible avec le MVP.
- Visualisation de chaque item ou cavites par pile : refuse hors scope P16 ; la generation reste module/compartiment V0.

## Suivi

P16-M002 doit implementer l'heuristique moteur et ses tests.

P16-M003 doit verifier que `asset_fit`, compartiments, cavites et notches suivent les nouvelles dimensions.

P16-M004 doit exposer dans le rapport : `tray_packing_policy: flat_tray_2d_v0`, `pile_grid_columns`, `pile_grid_rows`, `target_aspect_ratio`, `max_module_length_mm`, `linear_layout_avoided: yes/no` et warnings si le module reste long faute de place.

P16-M005/P16-M006 doivent preparer le preset Fusion `p16_ergonomic_tray_packing` et la gate humaine P16. `Print validation: false` reste obligatoire.