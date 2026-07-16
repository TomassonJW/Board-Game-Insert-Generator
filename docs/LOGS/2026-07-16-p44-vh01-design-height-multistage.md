# P44-VH01 - Diagnostic hauteur et multi-étages

Date : 2026-07-16

## Fait observé

Dans la gate P44-V, un projet dense restait impossible après passage du Z visible à 5 000 mm. Les diagnostics continuaient à signaler des cavités incapables de gagner 10 mm sous une réservation supérieure.

## Cause

La palette mettait à jour box.inner_dimensions_mm.z, mais pas box.usable_height_mm. Le solveur recevait donc encore l’ancienne hauteur. Une fixture transmise avec 5 000 mm réellement utilisables construit correctement cinq niveaux pour 24 conteneurs et un plateau.

## Décision d’implémentation

Synchroniser la donnée redondante à la frontière de la palette, conformément à ADR-0064. Ne modifier ni le solveur, ni ses budgets, ni les valeurs physiques. Isoler les demandes de suppression et de nommage dans P44-VH02.

## Validation

Tests DOM et solveur ciblés verts. La suite complète et la préparation Fusion sont requises avant intégration. fusion-validated: false, print-validated: false.
