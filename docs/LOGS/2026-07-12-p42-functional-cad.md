# P42 - Geometrie fonctionnelle V0.1

## Resultat

Le plan complet P41 devient maintenant une scene CAD fonctionnelle testable :
bacs ouverts, logements par famille, remplissages demandes, bacs vides et
supports. Le Studio ne dit plus que la generation CAD arrivera plus tard :
il indique ce qui est pret pour Fusion et ce qui est impossible a fabriquer.

## Frontiere conservee

Le module `volume_cad.py` est pur Python. Il consomme le plan P41 mais
n importe pas Fusion. Fusion recoit uniquement `cad_ir.v0` et ne decide ni les
positions, ni les dimensions, ni les jeux.

## Regles importantes

- un logement reste ouvert jusqu au haut du bac et conserve son fond ;
- une region automatique trop petite apres jeu commun reste un jeu technique ;
- un remplissage exact trop fin est refuse avec une explication ;
- les arrondis, encoches et couvercles restent hors P42 ;
- aucun statut Fusion ou impression n est revendique.

## Preuves

- tests CAD IR et API locale ;
- add-in Fusion valide hors API sur les scenes P42 ;
- test de 50 bacs, 72 familles et 25 elements plats en mode compact ;
- build Studio TypeScript/Vite.

## Suite

P43 prepare puis demande uniquement le smoke humain Fusion du jeu temoin.
