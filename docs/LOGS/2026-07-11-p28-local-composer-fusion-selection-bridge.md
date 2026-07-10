# P28 - Pont Fusion de la selection locale

Date : 2026-07-11

## Decision

La validation humaine P28 autorise un raccord borne entre la selection explicite P21 du Studio local et le pipeline CAD IR/Fusion existant. ADR-0041 fixe le choix : une enveloppe `rectangular_blank` CAD IR est creee par module deja resolu, sans recalcul ou logique P21 dans Fusion.

## Implementation

- `local_composer.export_from_draft` remplit maintenant `cad_ir.components` avec les modules selectionnes et conserve la trace de variante.
- `export-local-composer-selection` produit une scene de smoke reproductible depuis un starter local.
- `prepare_local_composer_selection_test.ps1` exporte le scenario, installe l add-in et precharge les settings Fusion.
- Le controle reste volontairement limite a trois volumes de module pour le starter `mixed-box` ; aucune cavite, paroi, tolerance, impression ou export imprimable n est ajoutee.

## Preuves hors Fusion

- Tests de contrat local composer et CLI : la CAD IR P28 est acceptee par `generation_plan_from_cad_ir`.
- Export reel hors Fusion : trois composants et un plan Fusion de trois blanks, sept objets crees au plan.
- Dry run du preparateur Fusion : chemins, installation et settings verifies sans ecriture AppData.

## Gate restante

Une observation humaine dans Fusion est obligatoire avant tout statut `fusion-validated`. La gate impression reste fermee.