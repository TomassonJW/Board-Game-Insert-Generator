# 2026-07-09 - P17-M002 export_printables action

Mission : `P17-M002 - Action Fusion export_printables`.

Implementation : la commande Fusion accepte maintenant `export_printables`. L'action inspecte la scene BGIG active, exige une seule racine BGIG, selectionne uniquement les bodies tagues `module_body`, exporte chaque body en STL via `design.exportManager.createSTLExportOptions(...)/execute(...)`, et affiche un rapport d'export.

Rapport V0 : politique `fusion_only_stl_per_printable_module_v0`, format `stl`, dossier export, compteurs detectes/exportes/refuses, fichiers exportes, refus avec raisons, `manifest_json: not generated in P17-M002`, `manifest_markdown: not generated in P17-M002`, `print_validated: false`.

Limites : pas encore de manifeste JSON/Markdown complet, pas de 3MF, pas de validation Fusion humaine, pas d'impression 3D validee.

Suite : `P17-M003 - Export manifest V0`.
