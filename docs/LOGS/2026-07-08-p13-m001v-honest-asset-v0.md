# 2026-07-08 - P13-M001V KO partiel, correction V0 honnete

## Contexte

Le smoke test Fusion apres `859bc7b` ne plante plus et `quick_asset_box` genere une scene, mais la validation humaine est refusee : le module visible `24 x 24 x 4 mm` peut etre compris comme un logement pour `30` tokens `20 x 20 x 2 mm` plus `20` tokens `18 x 18 x 2 mm`, alors que P13-M001 V0 ne genere ni assets individuels, ni cavites, ni sizing count-aware.

## Cause

Le pipeline existant `assets -> module_candidates -> executable_asset_plan` transporte le `count` dans les metadonnees (`quantity.count`, `contained_asset_count`), mais le sizing du candidat utilise seulement l enveloppe representative du ou des assets du groupe : plus grand X/Y/Z, clearance asset, murs et plancher. Le comportement est coherent avec une V0 report-only/representative, mais le reporting et la scene Fusion etaient trop ambigus pour une validation produit.

## Correction

- Ajout du reporting explicite `asset_items_visualized: no`.
- Ajout du reporting explicite `asset_cavities_generated: no`.
- Ajout du reporting explicite `count_aware_storage_sizing: no`.
- Ajout de diagnostics `asset_sizing` par asset : count lu, dimensions lues, contribution reelle, warning si count non utilise.
- Ajout de diagnostics `module_candidate_sizing` : source assets, count lu, asset fit, module size, formule de sizing et warning de capacite non garantie.
- Ajout d outlines XY bas/haut du volume boite comme repere visuel non imprimable.

## Limites restantes

P13-M001 reste une V0 honnete, non count-aware. Elle ne visualise pas les assets comme objets Fusion individuels et ne genere pas de cavites/logements. La mission suivante logique, apres decision sur P13-M001V, est P13-M002 pour sizing count-aware borne et debug visuel asset si le produit le confirme.

## Gate

`P13-M001V` doit etre rejouee dans Fusion. Ne pas declarer `fusion-validated` avant validation humaine.