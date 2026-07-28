# P64-L09U-R7-E — preuve grille produit, migrations et digests

Date : 2026-07-28.

Statut : `automated-validated`, `fusion-validated=false`,
`print-validated=false`.

## Frontières quantifiées

La grille `0,1 mm` couvre désormais :

- candidats et ancres X/Y ;
- empreintes, prises et épaisseurs effectives ;
- cellules XY locales et intervalles Z ;
- distances et marges publiées par les certificats ;
- enveloppes et dimensions dérivées du plan ;
- prismes, coupes et CAD IR ;
- coordonnées et dimensions du plan Fusion.

L'epsilon `0,0001 mm` reste explicitement exclu de l'audit de géométrie
produit. Il sert uniquement aux comparaisons numériques et topologiques.

## Migration sans écriture

Chaque réservation publie `bgig.product_grid_migration.v1` :

- dimensions physiques sources inchangées ;
- axes sources hors grille, le cas échéant ;
- valeur requise avant grille ;
- valeur effective ;
- direction d'arrondi ;
- ticks de la pose retenue ;
- `source_project_written=false`.

Une régression avec source `70,04 × 120,06 × 2,03 mm` prouve que la source
reste exacte tandis que l'empreinte et l'épaisseur effectives sont quantifiées
de manière conservative.

Les deux projets personnels observés n'exigent aucune migration de valeur
physique : `migration_required_count=0`.

## Identités

La disposition plate publie un digest fonctionnel basé uniquement sur :

- le schéma de grille ;
- des ticks entiers ;
- la politique d'arrondi ;
- la version de l'ordre automatique.

Le finaliseur passe de
`bgig.bounded_coupled_finalization.v12` à
`bgig.bounded_coupled_finalization.v13`.
Le plan minimal, la CAD IR et leur identité changent donc avec le contrat.

### CasLimite02++

- digest géométrie plate :
  `11d5f5e3d630e55043833da19516bbc6e41e82c3215e0b4ea9532138c6175f3b`
- digest plan :
  `4ac7f86018463bc39f5cf85cea3567589a85500c5cde3080e932093b82f4f2a3`
- digest CAD IR :
  `7925ad790a84f1ac64adcab667f62f7340d280a66eef4977219f4666c1c90be2`

### CasLimite02+

- digest géométrie plate :
  `c32de4997a29191a3fa22bf141b17d93057a87e8c7ced310866caaeff4b264ac`
- digest plan :
  `0a1ebf2594dc792f2277991f38e2364020681431e62767d17a74fecb8f6b5aed`
- digest CAD IR :
  `584e02ddf3345f43eecde63fb78b58f5da485761f65f1f9e7ad7fbfb086ce23e`

## Audit reproductible

Outil :
`scripts/fusion/p64_l09u_r7_grid_audit.py`.

Résultats :

| Cas | longueurs effectives contrôlées | hors grille |
|---|---:|---:|
| CasLimite02++ | 5 453 | 0 |
| CasLimite02+ | 5 888 | 0 |

Les valeurs physiques sources et les valeurs « avant grille » sont exclues de
l'audit effectif, mais restent visibles dans le rapport de migration.

## Mesures honnêtes

Pour `CasLimite02++` :

- ancres admissibles avant déduplication : `840` ;
- ancres après quantification/déduplication : `709` ;
- doublons fusionnés : `131` ;
- poses évaluées : `1780` ;
- états retenus : `64` ;
- calcul local observé : `13 757,638 ms` ;
- finalisation locale observée : `3 152,956 ms`.

Pour `CasLimite02+` :

- ancres admissibles avant déduplication : `1199` ;
- ancres après quantification/déduplication : `1043` ;
- doublons fusionnés : `156` ;
- poses évaluées : `2500` ;
- états retenus : `64` ;
- calcul local observé : `14 462,103 ms` ;
- finalisation locale observée : `1 613,126 ms`.

La réduction `2450 -> 1780` du nombre de poses sur `CasLimite02++` appartient
au correctif R7 complet, qui change aussi les ancres et les contraintes ; elle
ne prouve pas à elle seule un gain dû à la grille. `CasLimite02+` reste à
`2500` poses. Les temps locaux ne montrent aucun gain stable. Aucun gain de
performance n'est revendiqué.

Ces replays ne sont ni un benchmark, ni un holdout, ni un corpus, ni un
tournoi solveur.

## Validation

```text
Ran 77 tests in 18.496s
OK
```

SHA-256 personnels avant/après :

- `CasLimite02+` :
  `5e84fe6f5c0b3e5f046201d442c414504dd95d4db8e711169a2624485466d7dc`
- `CasLimite02++` :
  `83e9e90a6bfd86b18d3a157077a0e63dc2f543ddab626adb2151e269e01d9743`

Ils sont strictement inchangés.

## Extension E2 après suite autorisée

La suite autorisée a détecté un ancien chemin volumétrique qui répartissait
encore des surplus à quatre décimales. La correction et les identités
actualisées sont consignées dans
`docs/P64_L09U_R7_E2_FULL_LAYOUT_GRID_EVIDENCE.md`.
