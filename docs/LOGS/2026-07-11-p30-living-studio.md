# P30 - Studio vivant

## Resultat

La direction `Atelier de rangement` est implementee dans `frontend/` : cinq etapes progressives, vue 2D de boite vivante, information de fabrication lisible et controles techniques reserves au mode expert.

## Preuves

- Build TypeScript/Vite passe.
- Suite Python : 248 tests passent, dont le contrat frontend P30.
- API loopback et UI locale repondent en HTTP 200.

## Limites

Le navigateur de recette ne peut pas etre initialise dans ce sandbox Windows (`apply deny-read ACLs`). L inspection visuelle automatisee reste donc a rejouer. Le preview P30 est un plan de rangement, pas un bac physique.

## Suite

Preparer P31-GATE pour choisir la projection vers des bacs fonctionnels avant tout changement de geometrie ou de Fusion.
