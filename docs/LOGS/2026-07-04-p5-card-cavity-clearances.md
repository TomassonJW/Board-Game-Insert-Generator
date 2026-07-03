# 2026-07-04 - P5-M002 card cavity clearances

## Mission

Ajouter des logements de cartes et cartes sleevees dans le perimetre P5 moteur
Python pur, sans generation Fusion reelle.

## Resultat

- `clearance_mm` reste obligatoire pour les cavites generiques.
- Les cavites `cards` et `sleeved_cards` peuvent omettre `clearance_mm`.
- Le loader resout alors le jeu depuis `card_clearance_mm` ou
  `sleeved_card_clearance_mm` du profil actif.
- La validation refuse une valeur explicite inferieure au minimum du profil actif.
- Les rapports Markdown/JSON et la CAD IR exposent `clearance_source`.
- `examples/simple_card_tray.json` couvre les deux cas.

## Limites

- Les cavites restent abstraites : aucun cut Fusion, boolean ou extrusion
  soustractive n'est genere.
- Les valeurs de clearance restent experimentales et non validees par impression.
- La specialisation tokens/des/meeples reste pour `P5-M003`.

## Gate suivante

Toute generation reelle de cavites dans Fusion 360 reste bloquee par gate humaine
explicite.
