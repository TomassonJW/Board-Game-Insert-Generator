# P64-L09U-R7-C2 — preuve parois canoniques et score utile

Date : 2026-07-28.

Statut : `automated-validated`, `fusion-validated=false`,
`print-validated=false`.

## Portée

Ce lot rend les contraintes suivantes dures dès le placement automatique :

- empreinte et prise à au moins la paroi canonique du bord de boîte ;
- deux zones plates disjointes séparées d'au moins cette même paroi ;
- empreintes, prises et ancres publiées sur la grille produit `0,1 mm`.

Le score ne compare que les poses faisables. Il maximise ensuite la couverture
des conteneurs finalisables, le recouvrement sain entre éléments plats, le
centrage sur cette couverture, la marge résiduelle et enfin le centrage de
boîte. La signature canonique départage les égalités.

La recertification des fragments de matière de la géométrie composite reste le
lot C3 : C2 ne prétend pas encore supprimer toutes les micro-coupes finales.

## Régressions automatisées

Les tests couvrent notamment :

- rejet d'une empreinte au bord de boîte ;
- rejet d'un espace résiduel de `0,4 mm` quand le minimum vaut `1,2 mm` ;
- placement automatique respectant la marge de boîte ;
- préférence pour une couverture de corps figés ;
- préférence pour le centre utile plutôt que le centre arbitraire de boîte ;
- conservation des tests R6 de profondeur, accès et réservations locales.

Résultat ciblé :

```text
Ran 62 tests in 14.662s
OK
```

## Replays personnels en lecture seule

### CasLimite02+

- SHA-256 avant :
  `5e84fe6f5c0b3e5f046201d442c414504dd95d4db8e711169a2624485466d7dc`
- SHA-256 après : identique.
- pose retenue :
  `board@0° x=64,4 y=11,1`,
  `booklet@90° x=94,4 y=24,6`.
- couverture utile : `18 446,88 mm²`.
- marge minimale au-delà du minimum : `9,9 mm`.
- poses évaluées : `2500`; rejets de paroi : `347`.

### CasLimite02++

- SHA-256 avant :
  `83e9e90a6bfd86b18d3a157077a0e63dc2f543ddab626adb2151e269e01d9743`
- SHA-256 après : identique.
- pose retenue :
  `board@0° x=43,9 y=1,2`,
  `booklet@90° x=28,9 y=11,5`.
- couverture utile : `40 130,88 mm²`.
- marge minimale au-delà du minimum : `0,0 mm`, donc paroi exacte `1,2 mm`.
- poses évaluées : `2450`; rejets de paroi : `705`.

Ces mesures ne constituent pas un benchmark. Aucun gain de temps n'est
revendiqué.

## Limite connue

L'ordre vertical reste encore historique dans ce lot. Les fragments produits
par l'intersection exacte entre coupes et corps composites doivent encore être
recertifiés sans déplacement silencieux en C3.
