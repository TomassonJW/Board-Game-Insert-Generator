# P64-L09U-R3-V — preuve humaine KO 0.1.74

## Verdict

Verdict de Thomas le 2026-07-28 :

```text
P64-L09U-R3-V Fusion KO 0.1.74
```

La candidate est `human-KO`, `do-not-run`. Elle ne vaut ni validation Fusion,
ni validation d'impression.

`fusion-validated=false`, `print-validated=false`.

## Acquis humains à préserver

- Sans plateau, les cavités de `CasLimite01+` ont la bonne profondeur et la
  bonne position.
- Avec plateau, l'encastrement du plateau lui-même est correct.
- Les cavités existent encore et conservent apparemment leur calibre.
- La composition locale des plateaux est plus proche du besoin.
- Les acquis 0.1.73 de calcul, finalisation, aperçu fidèle, matérialisation
  progressive, BRep transitoire et absence de Combine perdu restent à
  préserver.

## Défaut bloquant exact

Les cavités recouvertes par un plateau sont enfermées sous une dalle imprimée.
Elles paraissent absentes depuis l'extérieur, mais l'inspection intérieure
montre qu'elles existent au mauvais niveau, séparées de l'encastrement par une
épaisseur égale à la paroi canonique.

Le défaut est observé dans :

- `CasLimite01+` avec plateau ;
- `CasLimite02+`, où certaines cavités paraissent absentes ou inaccessibles ;
- `CasLimite01++`, avec le même recouvrement.

## Comportement attendu clarifié

1. Finaliser d'abord le conteneur et sa cavité comme s'il n'y avait aucun
   plateau : profondeur calibrée inchangée, cavité ouverte sur la face
   fonctionnelle haute, surplus Z sous la cavité.
2. Appliquer ensuite l'encastrement local du plateau.
3. Lorsqu'une cavité se trouve sous cet encastrement, abaisser son sommet
   exactement jusqu'au dessous de la découpe locale, en réutilisant l'épaisseur
   et les jeux déjà résolus du plateau.
4. Ne laisser aucune matière imprimée entre ces deux vides.
5. Le plateau amovible ferme la cavité lorsqu'il est en place ; une fois le
   plateau retiré, la cavité doit être directement accessible.

La profondeur, X/Y, l'orientation et les dimensions de la cavité restent
inchangés. Seule son origine Z finale est recalée.

## Cause confirmée dans le contrat 0.1.74

Le contrat R3 calculait :

```text
sommet de cavité = dessous de découpe locale - épaisseur de paroi
```

Cette soustraction fabrique précisément la dalle observée. Le correctif doit
utiliser :

```text
sommet de cavité = dessous de découpe locale
```

La séparation imprimée intermédiaire vaut donc exactement `0 mm`.

## Périmètre

- Aucun benchmark, holdout, corpus ou tournoi solveur.
- Aucun projet personnel modifié ou versionné.
- Aucun changement de valeur physique.
- Les plateaux et livrets restent des réservations virtuelles.
- Les jobs annulables, miniatures et séparateurs distincts restent hors scope.
