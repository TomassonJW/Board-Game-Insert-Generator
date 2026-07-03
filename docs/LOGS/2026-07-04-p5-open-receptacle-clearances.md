# 2026-07-04 - P5-M003 open receptacle clearances

## Mission

Specialiser les receptacles ouverts `tokens`, `dice` et `meeples` dans le coeur
Python pur, sans generation Fusion reelle.

## Resultat

- Les cavites `tokens` peuvent omettre `clearance_mm` et utilisent
  `token_clearance_mm`.
- Les cavites `dice` utilisent aussi `token_clearance_mm` de maniere provisoire,
  sans ajouter de valeur par defaut non calibree.
- Les cavites `meeples` utilisent `meeple_clearance_mm`.
- Une clearance explicite inferieure au profil actif est refusee.
- `clearance_source` reste expose dans les rapports Markdown/JSON et la CAD IR.
- `examples/simple_open_tray.json` couvre les trois types.

## Limites

- Les cavites restent abstraites et non coupees dans Fusion.
- Les clearances restent non validees physiquement.
- P5-M004 touche a l'ergonomie avancee et requiert une decision humaine avant de
  continuer.

## Gate atteinte

Gate P5-M004 : encoches de doigts/fonds arrondis. Recommandation : autoriser
uniquement des features abstraites CAD-agnostic ou recadrer en documentation avant
toute implementation.
