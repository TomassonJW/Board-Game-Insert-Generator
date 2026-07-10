# 2026-07-10 - P23 Local Composer

## Decision appliquee

La validation humaine de l option D est appliquee : l app locale est la premiere surface de composition et Fusion reste un adaptateur CAD/export futur.

## Livrables

- ADR-0040 : contrat d architecture local React/Vite + adaptateur Python loopback.
- `bgig.local_composer.v0` : draft JSON versionne, strictement valide avant conversion vers les contrats moteur.
- API loopback : health, starter, portefeuille P21 et export de selection, uniquement sur localhost avec CORS borne.
- BGIG Studio : parcours boite, assets, reservations, candidats, variantes, selection et telechargement local de la selection/CAD IR.
- Scripts de lancement et d arret locaux ; commande CLI `serve-local-composer` pour l API seule.

## Preuves

- Tests Python dedies : draft deterministe, export metadata-ready, rejet de schema et endpoints HTTP/CORS.
- Build TypeScript/Vite passe.
- Recette loopback passee : starter, portefeuille de 2 variantes, selection recommandee, export `cad_ir.v0`, statut `materialization_status = not_authorized`, preflight CORS 204 et UI servie 200.

## Limites et prochaine mission

- Aucune materialisation Fusion, export imprimable, validation ergonomique ou impression physique.
- L inspection visuelle automatisee est a rejouer : le runtime navigateur a ete bloque par le sandbox Windows avant ouverture.
- P24-M001 est ready pour rendre les allocations multi-assets, erreurs de saisie et import/export plus explicites.