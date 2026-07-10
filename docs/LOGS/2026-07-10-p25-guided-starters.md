# 2026-07-10 - P25 Demarrage guide par modele de jeu

## Mission

Offrir des points de depart locaux pour qu un debutant puisse commencer sans construire un JSON brut.

## Livrables

- Catalogue loopback de trois drafts `bgig.local_composer.v0` : boite mixte, jeu de cartes et boite avec plateau.
- Endpoint `GET /api/starters` borne a localhost.
- Cartes de selection dans le Studio ; le choix clone le draft en memoire et ne persiste rien sur le serveur.

## Preuves

- Chaque template produit une recommandation P21 resolue.
- Tests Python du catalogue et de la route API.
- Recette locale : catalogue 200, CORS local, UI 200, trois recommandations non nulles.

## Limites

- Les templates ne remplacent pas les mesures reelles de la boite et des assets.
- Aucun catalogue distant, compte, cloud, collaboration, Fusion, export imprimable ou validation physique.
- L inspection visuelle navigateur reste a rejouer hors sandbox Windows.
