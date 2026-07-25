# Preuve P64-L09S-D - fermeture composite XY bornee

- mission: P64-L09S-D
- status: implemented-and-tested
- date: 2026-07-25
- source: calcul minimal certifie et inchange
- resultat: proposition composite certifiee, non encore publiable comme plan final avant P64-L09S-E
- print-validated=false

## Contrat implemente

Le repli D n'est tente qu'apres l'echec honnete de la fermeture rectangulaire globale C. Il construit d'abord une partition rectangulaire brute complete sans reservation haute, puis soustrait exactement les prismes de plateau ou livret ouverts sur le dessus.

Chaque proprietaire conserve un seul corps logique compose d'un coeur et, si necessaire, d'annexes rectangulaires. Les certificats imposent :

- un proprietaire unique par prisme ;
- un Z bas commun au coeur et a toutes ses annexes ;
- la conservation integrale de l'enveloppe minimale ;
- une connexion de chaque annexe par une vraie face verticale X ou Y d'aire strictement positive ;
- `z_only_attachment_count=0` ;
- `edge_or_point_attachment_count=0` ;
- une couverture exacte du volume imprimable hors reservations et vides techniques certifies ;
- `printable_residual_volume_mm3=0` ;
- `partition_complete_by_construction=true`.

Une reservation interne qui ne debouche pas sur le dessus est refusee avec `xy_composite_reservation_not_top_open`.

## Verite du cycle

Le cas recent avec plateau non decoupable par C produit maintenant `xy_composite_candidate_ready_for_cad_ir`. La proposition composite et son certificat sont exposes dans le rapport de finition, mais :

- `materializable=false` ;
- `partial_plan_published=false` ;
- le plan minimal courant est preserve ;
- aucun `finalized_plan` n'est publie avant les unions et encoches exactes de P64-L09S-E.

Le paquet Fusion futur reference le nouveau module pur Python, sans installation Fusion pendant D.

## Preuves automatisees

- contrat composite cible : 3/3 ;
- cycle etage avec le cas plateau recent : 19/19 ;
- fermeture rectangulaire C sans regression : 4/4 ;
- DOM et liste statique du paquet Fusion : 41/41 ;
- authorized_suite: 817/817 ;
- tests benchmark/holdout/tournament/corpus exclus : 72 ;
- test SCIP natif ignore sous Python 3.10 : 1.

Aucun benchmark ni holdout n'a ete lance. Aucun package Fusion n'a ete installe. Aucune validation Fusion ou impression n'est revendiquee.
