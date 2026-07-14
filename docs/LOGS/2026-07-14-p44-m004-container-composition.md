# 2026-07-14 — P44-M004 conteneurs parents et contenus enfants

- Décision : la relation parent/enfant est une projection de contents[].container_group_id vers container_groups[], sans arbre récursif ni migration.
- Portée : titre éditable unique, déplacement secondaire, modes de taille unifiés, compatibilité historique par axe et contrôle global confirmé.
- Exclusions : solver, jeux, géométrie, CAD IR, scène, bridge Python, compléments, couleurs personnalisables et toolbar.
- Preuve restante : gate humaine P44-M004V dans Fusion pour le package 0.1.25.