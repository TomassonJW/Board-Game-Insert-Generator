# P64-L09U-R8-D — preuve de géométrie positive des conteneurs finalisés

Date : 2026-07-29.

Statut : `done-automated-validated`, `fusion-validated=false`,
`print-validated=false`.

## But

R8-D ferme l’ambiguïté mise en évidence par R8-A. La géométrie positive
exécutable n’est plus un agrandissement `cad_*` conditionné par un élément
plat. Elle est désormais la géométrie explicite du conteneur finalisé, figée
avant toute soustraction.

Cette mission ne corrige pas encore la traduction Z des coupes dans Fusion.
Elle prépare une frontière positive stable pour R8-E et R8-F.

## Contrat publié

La finalisation publie :

- `bgig.finalized_container_geometry.v1` ;
- `bgig.xy_composite_container_body.v3` ;
- `bgig.xy_composite_container_materialization_certificate.v3`.

Chaque prisme composite v3 distingue :

- `closure_origin_mm` et `closure_size_mm`, issus de la fermeture volumique ;
- `final_origin_mm` et `final_size_mm`, géométrie positive exécutable du
  conteneur finalisé ;
- `geometry_role=finalized_container` ;
- `positive_geometry_source=container_finalization`.

Les champs exécutables `cad_origin_mm` et `cad_size_mm` sont interdits dans le
schéma v3. Les adaptateurs peuvent encore lire les anciens schémas v1/v2 pour
les artefacts historiques, mais un nouveau plan finalisé n’en publie plus.

## Certificat positif figé

Le digest `positive_geometry_digest` couvre uniquement :

- le propriétaire ;
- le prisme cœur ;
- les prismes positifs finalisés ;
- leurs attaches X/Y ;
- leurs origines et dimensions de fermeture et de finalisation.

Il exclut les cavités, accès et encastrements soustractifs. Le certificat
agrégé impose :

- `flat_positive_body_count = 0` ;
- `flat_positive_union_count = 0` ;
- `flat_positive_operation_count = 0` ;
- `flat_positive_volume_mm3 = 0.0` ;
- `new_printable_body_count_attributed_to_flat_items = 0` ;
- `ambiguous_cad_geometry_field_count = 0`.

Les unions X/Y nécessaires à un conteneur composite restent autorisées, mais
elles sont comptées séparément comme unions du conteneur. Aucune n’est
attribuée à un plateau ou à un livret.

La CAD IR refuse un artefact finalisé si ce certificat manque, si son digest
positif diverge ou si un des compteurs positifs plats devient non nul.

## Comptabilité renommée

Le certificat v3 remplace la compensation ambiguë
« matière ajoutée au-dessus du corps final » par deux quantités explicites :

- volume positif de remplissage du conteneur pendant sa finalisation ;
- volume soustrait hors de l’enveloppe de fermeture.

Leur écart doit rester nul. Cette comptabilité ne transforme pas le
remplissage du conteneur en support d’élément plat : l’attribution positive
reste exclusivement `container_finalization`, et R8-E devra appliquer les
éléments plats dans une passe négative distincte.

## Préservations

- Les cavités calibrées gardent leurs dimensions et leurs ancres.
- Les accès verticaux restent ouverts.
- Les parois et fragments de matière restent certifiés.
- Le calcul minimal R8-C, les budgets et les solveurs ne changent pas.
- La grille produit `0,1 mm` reste distincte de l’epsilon numérique.
- L’adaptateur Fusion reconnaît seulement la nouvelle politique d’union
  positive du conteneur ; la traduction des coupes et l’exécuteur BRep ne sont
  pas modifiés dans R8-D.

## Vérifications

Compilation Python :

- modules produit, adaptateurs, squelette Fusion, script de préflight et tests
  touchés : `OK`.

Tests ciblés, sans benchmark ni holdout :

- composite finalisation/CAD/Fusion : `8/8` ;
- profondeurs et accès locaux : `17/17` ;
- calcul par étapes : `21/21` ;
- construction CAD IR : `14/14` ;
- aperçu : `8/8` ;
- pool de candidats : `2/2` ;
- gate de release ciblée : `6/6` en `144,566 s` ;
- durcissement de bout en bout : `5/5` ;
- diagnostics d’arrêt : `9/9`.

Total unique R8-D : `90/90`.

`git diff --check` : `OK`.

Les projets personnels n’ont pas été rejoués pendant R8-D. Leur SHA-256 reste :

- `CasLimite02+` :
  `5E84FE6F5C0B3E5F046201D442C414504DD95D4DB8E711169A2624485466D7DC` ;
- `CasLimite02++` :
  `83E9E90A6BFD86B18D3A157077A0E63DC2F543DDAB626ADB2151E269E01D9743`.

## Limite et suite

R8-D ne prétend pas que les encastrements sont déjà fidèles dans Fusion :
`fusion-validated=false`, `print-validated=false`.

R8-E doit maintenant extraire une passe
`bgig.flat_inset_subtraction_plan.v1`, appliquer les intervalles locaux exacts
et prouver que le digest positif R8-D reste identique avant et après cette
passe.
