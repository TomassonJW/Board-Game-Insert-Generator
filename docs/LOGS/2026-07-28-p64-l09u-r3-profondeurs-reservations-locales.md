# 2026-07-28 — P64-L09U-R3 profondeur et réservations locales

- Candidate : 0.1.74.
- L'ancienne compensation qui ajoutait l'encastrement à la profondeur de
  cavité est supprimée.
- La finalisation fige le calibre et résout seulement l'origine Z.
- Les réservations sont composées sur des cellules XY exactes avec intervalles
  Z locaux.
- La fermeture interne utilise un garde conservateur borné ; il ne définit
  jamais la géométrie de sortie, reconstruite depuis les régions locales.
- L'interface sépare recherche, plafond, terminaison et temps mural total.
- Replays personnels : trois cas passés en lecture seule, SHA-256 inchangés.
- Validation : 126 tests du préparateur, puis 895 tests autorisés, 1 ignoré,
  12 modules interdits exclus.
- Statut : `automated-validated`, `ready-human-gate`,
  `fusion-validated=false`, `print-validated=false`.
