# P64-L09U-R7-E2 — grille des dispositions générales

Date : 2026-07-28.

Statut : `automated-validated`, `fusion-validated=false`,
`print-validated=false`.

## Écart découvert par la suite autorisée

La première exécution de la suite autorisée a correctement exclu les douze
modules benchmark/corpus/tournoi, puis a révélé un défaut réel dans le fixture
P66 :

- une cible historique de conteneur à `79,0667 mm` était encore utilisée comme
  dimension effective ;
- la répartition d'un surplus produisait des coordonnées comme `7,4333 mm` ;
- des découpes supérieures publiaient des largeurs comme `15,4667 mm` ;
- le contrôle Fusion rejetait donc la première géométrie dérivée hors grille.

Le contrôle Fusion n'a pas été assoupli. La correction est faite en amont.

## Règle exécutée

Le solveur volumétrique et les enveloppes finales appliquent maintenant :

- minimum imprimable : arrondi extérieur au tick supérieur ;
- limite disponible : arrondi intérieur au tick inférieur ;
- cible ou dimension effective : tick le plus proche ;
- allocation de surplus : ticks entiers uniquement ;
- partage centré d'un nombre impair de ticks : moitié basse à gauche/avant,
  tick restant à droite/arrière ;
- source historique conservée dans `bgig.product_grid_migration.v1` ;
- `source_project_written=false`.

Le fixture P66 prouve notamment :

```text
source target X = 79.0667 mm
effective target X = 79.1 mm
source project written = false
```

Ses deux réservations supérieures restent présentes. Deux coupes devenues
identiques sur la grille sont fusionnées : le nombre passe de `16` à `14`,
et le plan Fusion de `25` à `23` coupes totales.

## Identités déterministes actualisées

### CasLimite02++

- plan : `f9be542541f25ee440fe6f79960ae14e769e9afae0c6a0f20f43d7669ffefbec`
- CAD IR : `50111a5caa925a3afe8a0f78c7b554283719fb76caf7e307d6b1a88289039da9`
- artefact Fusion :
  `62631ac4134edcbd06244ebc551fb4c5300beed848d1122035c3c84b425dc9eb`
- géométrie plate inchangée :
  `11d5f5e3d630e55043833da19516bbc6e41e82c3215e0b4ea9532138c6175f3b`

### CasLimite02+

- plan : `77117555cb533e31ca97684a3360cb88617f282c4384f48995e27d949a1d5144`
- CAD IR : `f32c16fb858ab7bd58e20ca210eb15d61329104ece41e467ca8d0d85d2d263b3`
- artefact Fusion :
  `9902bb4ebe2385b8c540259e445da013002f7414e7523c968538eef5b5bddb72`
- géométrie plate inchangée :
  `c32de4997a29191a3fa22bf141b17d93057a87e8c7ced310866caaeff4b264ac`

## Validation

Gate ciblée élargie :

```text
Ran 120 tests in 126.767s
OK
```

Suite autorisée, avec exclusion avant import des douze modules interdits :

```text
Ran 926 tests in 620.666s
OK (skipped=1)
```

Audits des longueurs effectives :

| Cas | longueurs contrôlées | hors grille |
|---|---:|---:|
| CasLimite02++ | 5 453 | 0 |
| CasLimite02+ | 5 888 | 0 |

Les replays ne constituent ni un benchmark, ni un holdout, ni un corpus, ni un
tournoi solveur. Aucun gain de performance n'est revendiqué.

SHA-256 personnels avant/après :

- `CasLimite02+` :
  `5e84fe6f5c0b3e5f046201d442c414504dd95d4db8e711169a2624485466d7dc`
- `CasLimite02++` :
  `83e9e90a6bfd86b18d3a157077a0e63dc2f543ddab626adb2151e269e01d9743`

Ils sont strictement inchangés.
