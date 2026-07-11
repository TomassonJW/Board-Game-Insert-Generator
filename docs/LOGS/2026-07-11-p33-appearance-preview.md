
# P33 - Forme et apparence V0

## Etat

- Statut : `implemented-studio-preview`, `browser-inspection-pending`.
- Scope : choix de forme et esthetique sauvegardes, visibles et transportes, mais non materialises.

## Decision appliquee

ADR-0042 demandait des parametres visuels versionnes apres P30. P33 ajoute donc `bgig.appearance.v0` sans nouvelle ADR : le choix est deja autorise par la direction `Atelier de rangement`, reste reversible et n a aucun effet sur le moteur ou les dimensions physiques.

## Preuves

- validation Python des enums et bornes ;
- export conservant l apparence et le digest P21 ;
- TypeScript et build Vite ;
- test frontend de la carte de finition et du message de protection.

## Limites

- aucun arrondi, biseau, label ou encoche n est encore cree dans Fusion ;
- le navigateur automatise est bloque par le sandbox Windows avant inspection visuelle ;
- aucun statut impression n est modifie.

## Suite

P34-GATE : autoriser un seul mecanisme cible, ses contraintes et un protocole d impression avant implementation.
