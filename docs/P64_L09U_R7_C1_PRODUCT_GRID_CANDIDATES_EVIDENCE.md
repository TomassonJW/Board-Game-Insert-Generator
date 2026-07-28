# P64-L09U-R7-C1 — preuve grille produit et candidats

Date : 2026-07-28.

Statut : `implemented-core`, `automated-validated`.

`fusion-validated=false`, `print-validated=false`.

## Périmètre

Ce lot introduit uniquement :

- les conversions canoniques entre millimètres et ticks de `0,1 mm` ;
- les arrondis directionnels et enveloppes conservatrices ;
- la quantification/déduplication des ancres XY ;
- la quantification des empreintes et prises automatiques ;
- les compteurs de recherche avant/après quantification.

Le certificat final des fragments de paroi, le nouveau score et l'ordre de pile
restent hors de C1.

## Implémentation

`product_grid.py` fournit :

- dixième le plus proche, moitié à l'extérieur du zéro ;
- arrondi inférieur/supérieur ;
- enveloppe de taille vers l'extérieur ;
- intervalle vers l'extérieur ;
- représentation et publication par ticks.

Le plan de réservations publie :

- `bgig.product_grid.v1` ;
- `step_mm=0.1` ;
- ticks d'origine et de taille ;
- confirmation que l'epsilon `0,0001 mm` n'est pas un pas de recherche ;
- compteurs d'ancres brutes, admissibles et dédupliquées.

## Replay `CasLimite02++`

Source strictement en lecture seule.

SHA-256 avant/après :

```text
83E9E90A6BFD86B18D3A157077A0E63DC2F543DDAB626ADB2151E269E01D9743
```

Mesures du replay autorisé :

| Mesure | Avant C1 | Après C1 |
|---|---:|---:|
| poses évaluées | `2450` | `2450` |
| états retenus | `64` | `64` |
| rejets paroi actuels | `678` | `678` |
| ancres admissibles avant quantification | non exposé | `652` |
| ancres après quantification | non exposé | `578` |
| doublons fusionnés par la grille | non exposé | `74` |
| calcul observé | `9287,504 ms` | `9525,192 ms` |
| finalisation observée | `2927,692 ms` | `2681,079 ms` |

La prise du livret passe notamment de valeurs dérivées `78,88 / 22,24 mm` à
`78,8 / 22,4 mm`.

## Verdict de mesure

- La grille réduit le nombre d'ancres uniques dans ce replay : `74` doublons
  admissibles sont fusionnés.
- Elle ne réduit pas le nombre de poses réellement évaluées dans ce lot :
  `2450` avant et après.
- Les temps varient dans les deux sens ; aucun gain de temps n'est démontré.
- Aucun benchmark, holdout, corpus ou tournoi n'a été exécuté.

## Validation

- tests grille/réservations : inclus dans la matrice ciblée ;
- matrice ciblée grille, réservations, solve minimal, pile au sol et
  profondeur R6 : `58/58` ;
- compilation Python ciblée : OK ;
- Ruff : non disponible dans l'environnement (`No module named ruff`).

## Limites

Les régions Z, prismes finaux, coupes CAD et plan Fusion ne sont pas encore tous
quantifiés par ce seul lot. Les micro-encoches de 0.1.77 ne sont donc pas
annoncées corrigées.

## Suite

R7-C2 applique les marges de boîte/parois dures et remplace le score qui
pénalise actuellement les recouvrements utiles.
