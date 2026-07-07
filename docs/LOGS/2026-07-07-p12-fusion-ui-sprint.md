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

Statut : `implemented-fusion`, validation Fusion manuelle requise, `print-validated: false`.
