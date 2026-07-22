# P64-L04V — preuve de préparation de la gate Fusion

Date : 2026-07-22
Statut : préparation automatisée validée ; observation Fusion humaine en attente.

## Périmètre

Cette preuve prépare seulement la gate combinée P64-L04V. Elle ne revendique ni
`fusion-validated` ni `print-validated`, ne modifie aucun solveur, budget,
géométrie, finalisation, CAD IR ou scène automatique.

Le préparateur `scripts/fusion/prepare_p64_l04v_gate.ps1` vérifie hors Fusion
un chemin d'insertion locale qui conserve les poses monde et un fallback explicite
qui reste `stale` sans solve global implicite. Il installe ensuite l'add-in courant,
écrit les réglages de palette bornés et produit le fixture portable
`p64-l04v-pocket-baseline.bgig.json` dans `Documents/BGIG/projects`.

## Preuves automatisées

- `python scripts/fusion/p64_l04v_preflight.py` : OK ; `placement_reused` puis
  `global_solve_required`, avec 0 invocation du solveur global dans les deux cas.
- `prepare_p64_l04v_gate.ps1 -DryRun` : OK ; préflight, installation et réglages
  simulés, plus 92 tests ciblés (9 + 5 + 24 + 11 + 35 + 8).
- Test de non-régression du fixture : 2/2 OK.
- Ruff ciblé et `py_compile` : OK.
- Suite complète : 650/650 tests OK en 150,672 s.

## Suite et limite

L'installation réelle et les observations visuelles restent la gate humaine L04V.
Suivre `P64_L04V_FUSION_GATE_CHECKLIST.md`, relever l'étape, le temps écoulé,
l'absence de pourcentage artificiel, les détails de provenance et les transitions
stale/scène. Une réponse humaine contextualisée est nécessaire avant toute
promotion de capability.
