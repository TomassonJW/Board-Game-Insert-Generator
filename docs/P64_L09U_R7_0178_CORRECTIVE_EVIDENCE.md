# P64-L09U-R7 — preuve corrective 0.1.78

Date : 2026-07-28.

Statut avant installation : `automated-validated`,
`candidate-prepared`, `fusion-validated=false`,
`print-validated=false`.

## Verdict remplacé

La candidate 0.1.77 reste `human-KO`, `do-not-run`. Son acquis humain sur la
profondeur des cavités, y compris les micro-chevauchements, reste protégé par
les régressions R6.

La candidate corrective R7 est 0.1.78.

## Contrats livrés

- placement automatique sur grille `0,1 mm` ;
- marge dure égale au jeu de boîte plus la paroi minimale ;
- séparation minimale entre zones plates disjointes ;
- score déterministe favorisant couverture utile et centrage ;
- rejet des fragments de matière sous le minimum ;
- recertification finale sans déplacement silencieux ;
- ordre automatique par empreinte réellement orientée, petite sous grande ;
- ordre historique conservé comme trace, pas comme autorité automatique ;
- intervalles Z et identité propagés jusqu'au plan Fusion ;
- zéro volume additif résiduel au-dessus des corps finaux ;
- source physique conservée, migration effective explicite ;
- contrôle Fusion strict de la grille produit.

## Replays personnels

`CasLimite02+` et `CasLimite02++` ont été lus sans sauvegarde ni
normalisation en place.

SHA-256 avant/après :

- `CasLimite02+` :
  `5e84fe6f5c0b3e5f046201d442c414504dd95d4db8e711169a2624485466d7dc`
- `CasLimite02++` :
  `83e9e90a6bfd86b18d3a157077a0e63dc2f543ddab626adb2151e269e01d9743`

Les deux valeurs sont strictement inchangées.

## Mesures de grille

| Cas | longueurs effectives contrôlées | hors grille |
|---|---:|---:|
| CasLimite02++ | 5 453 | 0 |
| CasLimite02+ | 5 888 | 0 |

Les compteurs de candidats prouvent une déduplication, mais pas un gain de
temps stable. Aucun gain de performance n'est revendiqué.

## Validation automatisée

- gate ciblée élargie : `120/120` ;
- suite autorisée : `926/926`, un test ignoré ;
- matrice release 0.1.78 : `59/59`, un test ignoré ;
- préparateur à blanc : `84/84`, deux replays personnels ;
- douze modules benchmark/corpus/tournoi exclus avant import de la suite
  autorisée ;
- aucun benchmark, holdout, corpus ou tournoi exécuté.

Préflight :

```text
version=0.1.78
digest=bbb4a2e6dccf1b5e84a0d5268cd9b7792e52d8bb3134e07004a5935532e4e537
fusion-validated=false
print-validated=false
```

## Limite restante

Le package n'est pas encore observé dans une scène Fusion réelle. La promotion
reste bloquée par la gate humaine
`docs/P64_L09U_R7_V_0178_FUSION_GATE_RECIPE.md`.
