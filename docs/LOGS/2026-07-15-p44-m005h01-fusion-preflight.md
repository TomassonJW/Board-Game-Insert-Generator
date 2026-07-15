# 2026-07-15 — P44-M005H01 contrôle Fusion robuste

Le premier préflight P44-M005 a installé le package 0.1.28 mais a échoué sur
son propre marqueur accentué, lu différemment par PowerShell Windows.

Le contrôle emploie désormais le préfixe ASCII `Nouveau conteneur li`, présent
dans le libellé UTF-8 de la palette. Aucun runtime, package, schéma, bridge ou
comportement produit ne change.

La gate P44-M005V reste inchangée.
