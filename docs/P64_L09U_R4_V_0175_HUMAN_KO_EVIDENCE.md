# P64-L09U-R4-V — preuve humaine KO 0.1.75

Date : 2026-07-28.

Verdict : `human-KO`, `do-not-run`.

`fusion-validated=false`, `print-validated=false`.

## Observation de Thomas

- Les cavités des conteneurs connexes aux plateaux sont au bon endroit.
- La paroi intermédiaire entre le dessous du plateau et les cavités a bien
  disparu.
- Le défaut concerne uniquement les cavités partiellement recouvertes par un
  plateau.
- Dans la partie de ces cavités située hors de l'emprise du plateau, le volume
  supérieur du conteneur reste plein au niveau des assets.
- Ces cavités deviennent presque fermées et difficilement accessibles depuis
  leur partie hors plateau.
- Les autres conteneurs ne présentent pas ce défaut.

## Cause confirmée

Dès qu'une cavité chevauchait une découpe locale, R4 abaissait tout son volume
calibré sous cette découpe. Les coupes verticales qui devaient prolonger la
partie hors plateau jusqu'à sa face fonctionnelle locale étaient désactivées.

Le défaut ne vient ni du solveur, ni d'un déplacement des cavités, ni de leur
profondeur. Il vient de la matière supérieure conservée dans l'empreinte XY de
la cavité hors plateau.

## Acquis conservés

- position, orientation, dimensions et profondeur des cavités ;
- continuité directe entre cavité et découpe sous le plateau ;
- fonds et parois latérales canoniques ;
- réservations et paliers locaux ;
- finalisation, aperçu, CAD IR, chemin BRep transitoire et rollback.

## Suite

P64-L09U-R5 rétablit une ouverture verticale strictement bornée à l'empreinte de
la cavité :

- jusqu'au dessous de la découpe dans chaque région recouverte ;
- jusqu'à la face fonctionnelle locale dans chaque région hors plateau.

La candidate suivante est 0.1.76. Une nouvelle observation Fusion reste
obligatoire.
