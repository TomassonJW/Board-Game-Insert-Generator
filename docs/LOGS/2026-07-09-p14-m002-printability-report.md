# 2026-07-09 - P14-USABLE-ASSET-TRAY-M002 printability report V0

Mission interne 2 du sprint `P14-USABLE-ASSET-TRAY-SPRINT`.

Changement : ajout de `printability_report_v0` aux modules asset-first generes et placements CAD IR. Le rapport expose murs externes, paroi interne, fond, profondeur de cavite, profondeur d'encoche, hauteur module et warnings.

Fusion UI : `quick_asset_box_summary` affiche `printability_checked: yes`, `printability_validated_by_print: no`, `printability_report_v0` et `printability_warning`.

Limite maintenue : aucun changement de tolerances, aucune validation physique, aucun export STL/3MF. `print-validated: false` reste obligatoire.