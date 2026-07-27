# P64-L09T-F — preuve du certificat et de la CAD composite

Date : 2026-07-27.

Statut : `automated-validated`.

`fusion-validated=false`, `print-validated=false`.

## Objectif vérifié

La fermeture hybride v2 produite par E est maintenant le plan final réellement
publié. Le finaliseur ne revient plus à la fermeture v1 pour fabriquer la CAD.
Il recertifie les placements minimaux exacts, puis attache aux propriétaires la
géométrie composite, ses coupes et leurs preuves.

Le parcours publié est :

1. figer les poses monde des corps minimaux et des cavités ;
2. reprendre les prismes composites certifiés par E ;
3. découper ces prismes selon les frontières utiles à la CAD ;
4. construire un arbre d'unions par vraies faces X/Y ;
5. unir tous les prismes d'un propriétaire ;
6. couper ses cavités figées et leurs accès verticaux ;
7. couper les réservations et prises supérieures exactes ;
8. refuser toute divergence de géométrie, de volume ou d'identité.

## Cavités immuables

Chaque cavité reçoit un contrat `frozen_cavity_world_pose_v1` dérivé du plan
minimal certifié :

- propriétaire et index stables ;
- origine et dimensions monde ;
- origine, dimensions et rotation du corps minimal source ;
- empreinte déterministe de pose ;
- accès vertical depuis le sommet de la cavité jusqu'au sommet de conception.

La rotation Z à `90°` est transformée explicitement et testée. Aucune étape de
finition, de CAD IR ou d'adaptation Fusion ne recalcule ou ne translate cette
pose.

Le puits d'accès n'est pas retiré pendant la fermeture géométrique : cela
casserait artificiellement le corps minimal avant l'union. Il devient une coupe
CAD ciblée uniquement sur le composant propriétaire, après toutes ses unions.
Un corps voisin peut donc rester indépendant et amovible sans être amputé.

## CAD IR composite v2

Chaque propriétaire porte un
`bgig.xy_composite_cad_body.v2` avec la politique
`hybrid_xy_composite_v2`.

Le volume englobant du composant est déclaré comme
`bounding_box_not_solid`. Les vrais prismes sont créés séparément, ordonnés par
un arbre d'attaches X/Y, puis joints au cœur. Les opérations CAD IR suivent
strictement :

1. création du cœur ;
2. unions des annexes ;
3. cavités de contenu figées ;
4. accès verticaux de ces cavités ;
5. coupes supérieures exactes.

Un propriétaire produit exactement un composant utilisateur. Les annexes ne
créent ni nouveau conteneur, ni support artificiel.

## Certificats et refus

Le certificat
`bgig.xy_composite_cad_materialization_certificate.v2` vérifie :

- certificat composite source positif et résiduel imprimable nul ;
- même volume composite entre fermeture et CAD ;
- même volume final après les coupes exactes ;
- arbre d'unions complet avant les coupes ;
- poses de cavités identiques à leurs contrats figés ;
- accès verticaux présents sur les seuls propriétaires concernés ;
- enveloppes de paroi des réservations toujours certifiées ;
- une empreinte de géométrie CAD concordante.

La CAD IR recalcule l'empreinte du corps composite et les empreintes des poses
de cavité. Une divergence est refusée avant tout plan Fusion. Les rejets du
finaliseur transportent des sous-codes dédiés au certificat source, aux
volumes, aux unions, aux poses, aux accès et aux parois.

## Preuves automatisées

| Preuve | Résultat |
| --- | --- |
| Fixture publique plateau récente | plan final v2, résiduel nul, CAD IR prête |
| Cavité figée | pose monde exacte et accès vertical propriétaire |
| Rotation Z 90° | origine et dimensions monde transformées exactement |
| Ordre CAD | unions avant cavités, accès et réservations |
| Adaptateur Fusion pur | un composant par propriétaire, attaches X/Y |
| Empreinte CAD altérée | refus fail-closed |
| Pose de cavité altérée | refus fail-closed |
| Scénario multi-propriétaires P66 | finalisation, CAD IR et plan Fusion purs réussis |

## Validation exécutée

- Gate ciblée finalisation composite, CAD IR, adaptateur Fusion, calcul staged,
  diagnostics et pool plateau : `157/157`, OK.
- Gate globale autorisée : `866/866`, OK en `285.542 s`, avec un test SCIP
  natif ignoré.
- Douze modules benchmark, corpus et tournoi ont été exclus exactement comme
  en E. Aucun benchmark, holdout, tournoi, corpus solveur ou artefact canonique
  associé n'a été exécuté ou régénéré.

## Fichiers de comportement concernés

- `src/board_game_insert_generator/coupled_finalization.py`
- `src/board_game_insert_generator/partition_cad.py`
- `fusion_addin/BoardGameInsertGenerator/fusion_skeleton.py`
- `scripts/fusion/p64_l09sv_preflight.py`
- `tests/test_p64_l09t_f_composite_cad.py`
- `tests/test_p64_l09s_f_end_to_end_hardening.py`
- `tests/test_plateau_candidate_pool.py`
- `tests/test_staged_calculation.py`

## Limites et suite

- Le plan d'exécution Fusion est validé hors Fusion ; aucune création B-Rep
  réelle n'est observée dans cette mission.
- Aucun package ou add-in n'est installé en F.
- `0.1.69` reste `human-KO`, `do-not-run`.
- P64-L09T-G doit maintenant durcir la matrice complète, empaqueter la première
  candidate suivante, l'installer et préparer la gate humaine V.
