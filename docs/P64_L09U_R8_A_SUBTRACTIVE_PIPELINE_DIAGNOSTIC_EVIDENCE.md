# P64-L09U-R8-A — diagnostic du pipeline soustractif des éléments plats

Date : 2026-07-28.

Statut : `done-diagnostic`, `no-product-code-change`,
`P64-L09U-R8-B-ready`, `fusion-validated=false`,
`print-validated=false`.

## Verdict

Le modèle produit donné par Thomas est cohérent. Le défaut vient du contrat
interne et de son exécution, pas de la manière dont le besoin a été expliqué.

Deux divergences distinctes se cumulent :

1. la finalisation fabrique une extension positive conditionnée par une
   réservation plate, puis tente de l'annuler par une coupe ;
2. le plan Fusion déplace certaines coupes locales vers le haut du corps avant
   leur exécution BRep.

La première matière positive attribuable à un plateau ou à un livret apparaît
donc pendant la finalisation composite, avant la CAD IR. Le déplacement Fusion
laisse ensuite une partie mesurable de cette matière dans le corps réel.

Un correctif de rendu ou le seul déplacement de la coupe Fusion ne suffirait
pas : il masquerait le défaut visible sans rétablir le modèle strictement
soustractif.

## Entrées immuables

Les deux projets personnels ont été lus sans sauvegarde ni normalisation en
place :

| Projet | SHA-256 avant | SHA-256 après |
|---|---|---|
| `CasLimite02+.bgig.json` | `5E84FE6F5C0B3E5F046201D442C414504DD95D4DB8E711169A2624485466D7DC` | identique |
| `CasLimite02++.bgig.json` | `83E9E90A6BFD86B18D3A157077A0E63DC2F543DDAB626ADB2151E269E01D9743` | identique |

La CAD IR installée après le dernier replay humain de `CasLimite02++` a été
copiée en lecture seule dans `.codex-work` pour l'analyse. Sa copie porte le
SHA-256
`394DFD5D80BC2327C7ABA5E960129E38DA6E33AC4AE9E7473C4C311D68160B66`
avant et après l'audit.

Tous les fichiers temporaires restent hors Git et seront supprimés à la fin du
Goal.

## Profil autoritaire dans Fusion

Le journal humain versionné confirme les temps suivants :

| Cas | Action | Effort | Recherche | Solveur exposé | Résultat |
|---|---|---|---:|---|---|
| `CasLimite02+` | calcul | Normal | `22,823 s` | SCIP, 1 invocation, limite `20 s` | aucune solution |
| `CasLimite02+` | calcul | Long | `61,799 s` | SCIP, 1 invocation, limite `60 s` | aucune solution |
| `CasLimite02+` | calcul | Approfondi maximal | `90,991 s` | télémétrie de lane absente au succès | solution certifiée |
| `CasLimite02++` | calcul | Approfondi maximal | `87,192 s` | télémétrie de lane absente au succès | solution certifiée |

`CasLimite02+` demande donc `175,613 s` cumulées avant le premier résultat.
Le journal ne permet pas d'attribuer honnêtement les deux succès approfondis à
une lane précise : le résumé `external_solver` est vide dans ces réponses.
Cette lacune de télémétrie est constatée ; elle ne doit pas être remplacée par
une supposition.

La finition et la matérialisation ne sont pas les phases lentes :

| Cas | Finition | Candidats | Itérations | Résolution globale | Rejets | Matérialisation |
|---|---:|---:|---:|---:|---:|---:|
| `CasLimite02+` | `2,186 s` | `5/5` | `29` | `1` | `0` | `0,783 s` |
| `CasLimite02++` | `2,095 s` | `4/4` | `23` | `1` | `0` | `0,815 s` |

Les statuts publiés sont bien `finalized_plan_ready` puis
`scene_synchronized`. Le succès rapide de ces deux phases ne prouve donc pas la
géométrie produite.

## Replays locaux instrumentés

Le poste Codex utilise Python 3.10 sans le runtime SCIP natif embarqué par
Fusion. Les replays locaux mesurent ainsi le repli interne ; ils ne remplacent
pas les temps Fusion ci-dessus.

| Cas | Effort | Temps calcul | Lanes | États | Essais de pose | Complétions | Candidats certifiés |
|---|---|---:|---:|---:|---:|---:|---:|
| `CasLimite02+` | Normal | `20 495,812 ms` | `3` | `818` | `1 399` | `0` | `0` |
| `CasLimite02+` | Approfondi | `166 956,097 ms` | `9` | `9 019` | `19 342` | `0` | `0` |
| `CasLimite02++` | Normal | `20 432,406 ms` | `3` | `649` | `1 053` | `0` | `0` |

Les trois runs terminent par `no_solution_within_budget`. Aucun rejet de
certificat n'est compté parce qu'aucune complétion géométrique n'atteint le
certificat.

Mesures mémoire utiles :

| Run | Pic RSS | Hausse RSS de la phase calcul | Hausse du tas Python |
|---|---:|---:|---:|
| `CasLimite02+` approfondi | `61 689 856` octets | `26 828 800` octets | `7 642 533` octets |
| `CasLimite02++` Normal | `43 425 792` octets | `8 466 432` octets | `2 268 636` octets |

La première instrumentation du run Normal de `CasLimite02+` ne remontait pas
le RSS Windows ; seule sa hausse de tas Python, `2 531 327` octets, est
exploitable. L'instrumentation RSS a été corrigée avant les deux runs suivants.

Le profil ne montre ni fuite ni rejet tardif dominant. Il montre une recherche
de placement sans complétion sur le repli local et, dans Fusion, deux
invocations SCIP bornées sans candidat avant le succès approfondi. R8 ne lance
aucun benchmark, holdout, corpus ou tournoi solveur.

## Trace de la première divergence

### 1. Calcul minimal — conforme au principe soustractif

`certify_top_inset_reservation_prisms()` :

- conserve les enveloppes minimales ;
- publie les volumes réservés avec `printable=false` ;
- publie `support_count=0` ;
- ne crée aucune coupe ni aucun corps automatique ;
- diffère les coupes à la finalisation.

À cette frontière, plateau et livret restent des décisions de pose, d'ordre,
d'intervalle et de couverture. Aucun volume imprimable positif ne leur est
attribué.

### 2. Finalisation composite — première matière positive

Dans `_attach_xy_composite_geometry()`, chaque cellule possède d'abord une
`final_size_mm`. Si son sommet correspond au plan de support local d'une
réservation, le code exécute ensuite :

```text
cad_top = max(final_top, design_top)
cad_size.z = cad_top - final_origin.z
```

Cette hausse n'existe que parce qu'une réservation plate couvre la cellule.
Elle fabrique donc un volume positif après la géométrie dite finale, puis
`_composite_cell_cuts()` décrit les volumes qui devraient l'enlever.

Sur la CAD IR exacte de `CasLimite02++`, le certificat reconnaît :

```text
additive_above_final_volume_mm3 = 125019,76
cut_above_final_volume_mm3 = 125019,76
additive_above_final_residual_volume_mm3 = 0
```

Le certificat accepte l'égalité de deux volumes agrégés. Il ne prouve ni
l'identité spatiale des volumes, ni l'absence d'opération positive liée aux
éléments plats. Son champ `no_additive_volume_above_final_bodies=true` signifie
en réalité « volume ajouté égal au volume qu'une coupe amont prévoit de
retirer », pas « aucune matière positive créée ».

Il s'agit de la première contradiction avec le contrat de Thomas.

### 3. Aperçu et CAD IR — contrat ambigu propagé

L'aperçu lit les `cad_size_mm`, donc les prismes déjà rehaussés. La CAD IR crée
et unit également ces prismes avant de transporter les coupes et leurs
`local_interval_z_mm`.

La CAD IR observée contient :

- `8` composants imprimables, tous de rôle `container` ;
- `0` corps imprimable de plateau ou livret ;
- `61` unions d'annexes de conteneurs ;
- `20` coupes supérieures, dont `18` empreintes et `2` prises ;
- `9` coupes liées au plateau et `11` liées au livret.

Les `61` unions ne portent pas d'attribution aux éléments plats. Le contrat
actuel ne peut donc pas prouver l'invariant « zéro union liée aux éléments
plats », même si aucun corps plat séparé n'est créé.

### 4. Plan Fusion — intervalle local conservé mais non exécuté

La CAD IR transporte correctement les intervalles locaux. Dans
`_cavity_cut_plans()`, le plan Fusion :

1. lit et valide `local_interval_z_mm` ;
2. conserve ces valeurs comme métadonnées ;
3. calcule pourtant `cut_plane_world_z` au sommet du prisme ;
4. place `cut_origin_mm.z` sur ce sommet.

La position réellement consommée par la BRep n'est donc pas l'intervalle local
pour une couche enterrée.

Sur `CasLimite02++`, `17` coupes sur `20` coïncident par hasard avec le sommet.
Les trois coupes du livret situées sous le plateau divergent :

| Corps | Intervalle demandé | Intervalle BRep produit | Décalage |
|---|---|---|---:|
| `container:c2` | `[63,8 ; 65,8]` | `[67,8 ; 69,8]` | `+4 mm` |
| `container:c4` | `[63,8 ; 65,8]` | `[67,8 ; 69,8]` | `+4 mm` |
| `container:c6` | `[63,8 ; 65,8]` | `[67,8 ; 69,8]` | `+4 mm` |

Le déplacement vaut exactement l'épaisseur du plateau supérieur.

### 5. BRep transitoire — matière laissée dans l'encastrement

`_create_boolean_rectangular_blank()` construit chaque outil de coupe entre :

```text
[cut_origin_mm.z - cut_size_mm.z ; cut_origin_mm.z]
```

Il exécute donc l'intervalle déplacé du plan Fusion, pas
`local_interval_z_mm`.

Audit volumique de l'artefact exact :

| Corps | Vide demandé | Vide réellement couvert | Vide demandé non retiré |
|---|---:|---:|---:|
| `container:c2` | `12 996,48 mm³` | `10 794,72 mm³` | `2 201,76 mm³` |
| `container:c4` | `71 314,32 mm³` | `48 642,44 mm³` | `22 671,88 mm³` |
| `container:c6` | `37 710,40 mm³` | `31 374,84 mm³` | `6 335,56 mm³` |
| `container:tokens` | `4 073,76 mm³` | `4 073,76 mm³` | `0 mm³` |
| **Total** | **`126 094,96 mm³`** | **`94 885,76 mm³`** | **`31 209,20 mm³`** |

Les coupes réelles restent entièrement dans le vide attendu, mais elles
recoupent une partie déjà retirée par la couche supérieure. Elles n'ouvrent
donc jamais les `31 209,20 mm³` de la couche inférieure.

Ce défaut explique directement les plaques ou fermetures visibles dans les
zones empilées. Il n'est pas nécessaire d'invoquer un défaut esthétique.

## Pourquoi les tests étaient verts

Les régressions R6/R7 prouvent la présence des bons
`local_interval_z_mm` dans l'aperçu, la CAD IR et l'objet plan Fusion. Elles ne
prouvent pas que `cut_origin_mm` désigne le sommet de ce même intervalle.

Le cas Fusion simple ne couvre qu'une coupe ouverte sur le sommet du corps :
dans ce cas particulier, l'ancien calcul est juste.

Enfin, le certificat de finalisation compare des volumes planifiés avant la
transformation Fusion. Il ne recalcule pas le volume exécuté depuis les
origines BRep.

La régression manquante est donc un cas empilé qui compare, pour chaque coupe :

```text
intervalle CAD IR
= intervalle du plan Fusion
= intervalle de l'outil BRep
```

## Règles formalisées pour R8-B

Soit :

- `F` la matière des conteneurs finalisés avant tout élément plat ;
- `E_i` l'encastrement local exact de l'élément plat `i` ;
- `M` la matière imprimable finale.

Le seul résultat admissible est :

```text
M = F \ union(E_i)
```

Les certificats doivent prouver simultanément :

1. volume positif attribuable aux éléments plats : `0 mm³` ;
2. union attribuable aux éléments plats : `0` ;
3. nouveau corps imprimable attribuable aux éléments plats : `0` ;
4. profondeur locale : somme exacte des épaisseurs couvrantes ;
5. chaque intervalle Fusion/BRep identique à l'intervalle métier ;
6. cavités calibrées, accès, fonds et parois minimales inchangés ;
7. ordre automatique petit-dessous/grand-dessus inchangé ;
8. grille produit `0,1 mm` distincte de l'epsilon numérique ;
9. BRep transitoire, rollback et projets personnels préservés.

Un certificat ne peut plus conclure à zéro résidu par compensation entre un
volume ajouté et un volume qu'une étape ultérieure prévoit de retirer.

## Options comparées

| Option | Simplicité | Robustesse | Maintenance | Testabilité | Coût de recherche | Verdict |
|---|---|---|---|---|---|---|
| Corriger seulement `cut_origin_mm.z` dans Fusion | forte | faible | faible à court terme, dette conservée | bonne localement | nul | rejetée comme solution R8 |
| Durcir seulement le certificat volumique actuel | moyenne | moyenne | contrat positif/soustractif toujours ambigu | moyenne | nul | garde utile, solution rejetée |
| Séparer explicitement conteneur finalisé puis passe de coupes | moyenne | forte | forte, une source de vérité | forte de bout en bout | borné, sans nouveau solveur | recommandée |
| Reconstruire le solveur ou la fermeture globale | faible | incertaine | coûteuse | difficile | élevé | prématurée et hors preuve |

L'option recommandée ne change ni solveur, ni budget, ni valeur physique. Elle
déplace la responsabilité :

1. le calcul minimal ne publie que poses, enveloppes et réservations
   non imprimables ;
2. la finalisation produit explicitement les seuls conteneurs finalisés ;
3. une passe pure construit uniquement l'union des encastrements à soustraire ;
4. aperçu, certificat, CAD IR, plan Fusion et BRep consomment ce même contrat.

## Suite autorisée

R8-A est close. R8-B peut maintenant créer l'ADR structurelle et découper la
reconstruction en incréments R8-C à R8-F. Aucune nouvelle gate humaine n'est
ouverte avant la candidate R8-G.
