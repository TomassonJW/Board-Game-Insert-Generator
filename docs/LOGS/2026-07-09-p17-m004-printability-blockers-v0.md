# 2026-07-09 - P17-M004 printability blockers V0

Mission : `P17-M004 - Printability blockers V0`.

Implementation : `printability_report_v0` expose maintenant `printability_status`, `printability_export_allowed`, `issue_counts` et `issues[]` avec severites.

Blockers V0 : mur externe/interne sous minimum, fond sous minimum, cavite supprimant toute la hauteur module. Warnings V0 : encoche profonde, module haut, cavite non planifiee et absence de validation physique.

Fusion : le resume `quick_asset_box` affiche le statut et `printability_export_allowed`. `print_validated: false` reste obligatoire.

Suite : `P17-M005 - Calibration coupon / preprint check V0`.
