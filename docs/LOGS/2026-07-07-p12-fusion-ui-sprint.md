# Log - P12 UI Fusion sprint

Date : 2026-07-07

## Gate P12-UI

Gate humaine validee pour un sprint autonome limite a l'UI Fusion, aux parametres de generation et a la regeneration par relance. Le perimetre interdit reste : nouveau solveur, nouvelle geometrie Fusion, modules composites, fillets/conges, export STL/3MF, changement de tolerances et dependance `adsk` dans le coeur Python.

## P12-M001 - Toolbar relancable

Mission : stabiliser le lancement UI Fusion par bouton toolbar et commande relancable.

Changements :

- ajout d'un plan UI testable dans `fusion_skeleton.py` ;
- centralisation des constantes toolbar/commande ;
- message Fusion enrichi avec la politique `toolbar_button_reopens_command_without_addin_restart` ;
- documentation d'une strategie `Fusion UI Strategy` ;
- correction d'un artefact de statut P11 et d'une incoherence de smoke test P11.

Statut avant smoke test : `implemented-fusion`, validation Fusion manuelle requise, `print-validated: false`.
## Validation P12-M001V

Validation humaine Fusion confirmee apres le commit `a12ef42` :

- add-in recopie depuis le repo vers le dossier Fusion AddIns : OK ;
- commande `Generate Board Game Insert` visible : OK ;
- bouton visible dans `Design workspace > Utilities > Add-Ins` : OK ;
- la commande s'ouvre au lancement de l'add-in : OK ;
- apres fermeture / perte de focus, le bouton toolbar permet de rouvrir BGIG sans redemarrer l'add-in : OK ;
- CAD IR `simple_asset_product_scene` chargee via l'UI : OK ;
- mode `compact_and_exploded` utilise : OK ;
- generation Fusion : OK ;
- `Body sizing report` present : OK ;
- occurrences liees conservees : OK ;
- ligne `UI reopen policy: toolbar_button_reopens_command_without_addin_restart` presente : OK ;
- impression 3D : non validee.

Statut : `fusion-validated`, `print-validated: false`. Prochaine action : gate produit avant palette persistante, generation depuis config BGIG, nettoyage automatique ou regeneration plus ambitieuse.
