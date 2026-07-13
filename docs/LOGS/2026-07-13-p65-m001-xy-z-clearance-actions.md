# P65-M001 - Jeux X-Y/Z et action Fusion persistante

Date : 2026-07-13
Statut : implemente, automated-validated, fusion-retest-required, print-validated: false

Le jeu historique devient le jeu X-Y affiche. Le nouveau `container_z_clearance_mm`
herite du X-Y dans les anciens projets, consomme la hauteur solvee et reste un
vide technique non imprimable. Aucun corps ni support automatique n est cree.

La palette 0.1.16 expose les deux jeux et place l unique action `Materialiser dans
Fusion` a cote de `Recalculer`. Elle reste desactivee sans solution complete et a
jour. Les valeurs experimentales ne sont pas recalibrees et la refonte visuelle
reste differee.

Les 430 tests passent et couvrent migration, cas anisotrope, piles hybrides,
validation, CAD IR et DOM. Validation Fusion et impression reelle non revendiquees. P65-M002 reste
la prochaine mission prete.

Installation locale : manifeste 0.1.16 et marqueurs Jeu Z entre conteneurs /
materialize-action verifies. Settings local absent ; aucune observation dans Fusion
n est revendiquee.
