# 2026-07-09 - P16-M001 flat_tray_2d strategy

P16-M001 documente la strategie `flat_tray_2d_v0` via ADR-0034.

Decision : `flat_tray_linear_v0` nomme le comportement P15 lineaire ; `flat_tray_2d_v0` devient la cible par defaut pour tokens/dice/meeples/generic ; `vertical_stack` reste explicite ; la grille globale reste `placement_reservation_lattice_v0` avec `body_snap_to_grid: no`.

Aucun moteur ni add-in n'est modifie dans cette mission. P16-M002 doit implementer l'heuristique deterministe de piles 2D et les tests associes.