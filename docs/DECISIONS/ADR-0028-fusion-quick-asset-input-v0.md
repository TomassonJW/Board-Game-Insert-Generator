# ADR-0028 - Fusion quick_asset_box input V0

Date : 2026-07-08

## Statut

Acceptee pour implementation P13-M001. Validation Fusion humaine requise via P13-M001V.

## Contexte

Apres P12-M004V, la commande Fusion persiste ses champs et supporte `cad_ir_file`, `config_file` et `quick_parametric_box`. Le prochain besoin produit est de saisir quelques assets depuis Fusion sans ecrire de JSON a la main, tout en gardant le coeur Python pur et le pipeline asset-first deja teste.

## Decision

Ajouter un mode `quick_asset_box` dans la commande Fusion classique. La saisie assets V0 est un champ texte editable au format `asset_id,type,count,x_mm,y_mm,z_mm,fit`, avec entrees separees par `;` ou saut de ligne.

La commande construit une config temporaire conforme au schema existant, puis reutilise le pipeline moteur : assets, candidats, variante recommandee, plan executable, CAD IR et generation Fusion. Les assets invalides sont reportes comme refuses et ne bloquent pas si au moins un asset valide reste. `metadata.quick_asset_box` est ajoute de facon additive au CAD IR genere pour le reporting Fusion.

## Options refusees

- Palette HTML persistante : trop large pour P13-M001 et gatee.
- Tableau assets avance : meilleur UX futur, mais trop couteux pour une V0 smoke-testable.
- Nouveau solveur ou optimisation : hors scope, deja gate par P10.
- Extension du schema JSON public : inutile, la config temporaire reste compatible avec le schema existant.

## Consequences

- `quick_asset_box` est `implemented-fusion` mais non `fusion-validated` avant P13-M001V.
- Le coeur `src/board_game_insert_generator` reste independant de `adsk`.
- Le profil UI legacy `draft` est mappe vers le profil moteur existant `fast_draft` uniquement dans la config temporaire `quick_asset_box`.
- L'UI reste une commande Fusion classique, non une palette persistante.
