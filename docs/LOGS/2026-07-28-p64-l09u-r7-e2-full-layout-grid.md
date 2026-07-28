# 2026-07-28 — P64-L09U-R7-E2

La suite autorisée a révélé que la grille `0,1 mm` était complète pour les
réservations plates, mais pas encore pour une ancienne allocation volumétrique
P66.

Le correctif conserve la source `79,0667 mm`, publie `79,1 mm` comme valeur
effective, distribue les surplus en ticks entiers et maintient le rejet Fusion
de toute géométrie dérivée hors grille.

Validation : `120/120` tests ciblés, puis `926/926` tests autorisés, un test
ignoré et douze modules benchmark/corpus/tournoi exclus avant import.
