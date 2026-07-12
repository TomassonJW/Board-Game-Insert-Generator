# P38 - Studio de saisie V0.1

Date : 2026-07-12

## Resultat

Le Studio est reconstruit autour de `bgig.project.v1` et du langage courant :
boite, pieces a ranger, plateaux/livrets, bacs demandes, remplissage et reglages
de fabrication. Les anciennes notions de candidats, layers, apparence et
couvercles ne font plus partie du parcours MVP.

## Preuves

- 275 tests Python passent ;
- le build TypeScript/Vite passe ;
- le Studio local, son API de sante et `/api/project-v1/starter` repondent en
  HTTP 200 ;
- le projet starter expose `bgig.project.v1`.

L inspection navigateur automatisee reste techniquement indisponible dans le
sandbox Windows. Ce n est pas une gate humaine, et aucun statut Fusion ou
impression n est declare.

## Suite

P39 derive les bacs et logements depuis les pieces et leur bac cible. V0.2 et
V0.3 restent explicitement differees jusqu a l acceptation du MVP V0.1.