# P31 - Bacs ouverts depuis une selection P21

## Resultat

Le Studio exporte des bacs ouverts : une enveloppe P21, quatre parois, un fond de 1.2 mm et une cavite `free` top-open par module. Les positions et tailles externes P21 ne changent pas.

## Preuves

- 249 tests Python, dont projection, cavites et refus P31.
- Build TypeScript/Vite passe.
- Export reel `mixed-box` : 3 composants, 3 cavites, 3 coupes dans le plan Fusion hors API.

## Limites

Aucune scene Fusion ni impression n a encore ete observee. Les assets sont traces, pas ajustes par compartiment ; aucun notch, arrondi, couvercle ou mecanisme n est ajoute.

## Gate suivante

Smoke Fusion P31 : verifier les trois bacs dans Fusion avec `P31_FUSION_OPEN_TRAY_SMOKE.md`.