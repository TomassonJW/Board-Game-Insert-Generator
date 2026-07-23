# P64-L07C — contrat des adapters externes isolés

## 1. Statut et portée

Statut : `implemented-core`, `automated-validated`.

P64-L07C fournit le protocole commun, les verrous d'artefacts et quatre workers
réels pour le tournoi externe. Il ne change aucun routage produit et ne livre
aucun binaire tiers dans Git.

`fusion-validated: false`. `print-validated: false`.

## 2. Quatre moteurs et quatre familles

| Candidat | Version réellement observée | Famille | Gate produit après L07C |
|---|---:|---|---|
| OR-Tools CP-SAT | 9.15.6755 | programmation par contraintes / SAT | candidat |
| HiGHS | 1.15.1 | programmation linéaire mixte | candidat |
| SCIP via PySCIPOpt | SCIP 10.0.2 / PySCIPOpt 6.2.1 | programmation entière à contraintes | benchmark seulement, inventaire natif à terminer |
| LAFF | 4.2.1 | heuristique spécialisée de packing par niveaux | benchmark seulement, revue EPL/EDL à terminer |

Ces quatre moteurs sont externes. BGIG et l'oracle interne L06 ne comptent pas
dans ce total.

L'inspection réelle corrige deux hypothèses de L07A :

- le wheel PySCIPOpt 6.2.1 embarque SCIP 10.0.2, pas 10.0.3 ;
- LAFF `points` dépend d'Eclipse Collections 13.0.0, dont le POM publie les
  licences EPL-1.0 et EDL-1.0 ;
- le wheel PySCIPOpt contient notamment `libscip`, IPOPT, CoinMumps et des
  runtimes Intel, alors que son répertoire de licences expose seulement l'avis
  du wrapper PySCIPOpt.

Les deux ambiguïtés de redistribution sont fermées pour le produit en classant
SCIP et LAFF `benchmark-only`. Elles n'autorisent aucune intégration ultérieure
sans nouvelle preuve de licence.

## 3. Verrou avant exécution

Le verrou `bgig.external_solver_artifact_lock.v1` contient 32 artefacts :

- wheels Python complets et dépendances ;
- JAR, POM et sources LAFF utiles à l'audit ;
- Eclipse Collections ;
- JDK Temurin 17 portable et sa somme officielle.

Chaque fichier est vérifié par taille et SHA-256 avant le premier worker du
candidat. Le reçu ne contient aucun chemin local et est lié au verrou.

Digest du verrou :
`58736ecde2a6bfbc4d57c3e5bc4e947c9875fe9f7a3c654cb87594e91c552bc6`.

Les caches, environnements installés, classes Java et données téléchargées
restent sous `.codex-work` et hors Git. Aucune installation globale n'est
effectuée.

## 4. Entrée commune

Le modèle partagé `bgig.external_floor_problem.v1` représente :

- tous les corps demandés ;
- des rectangles alignés sur les axes ;
- un seul niveau au fond de la boîte ;
- les marges boîte-corps et corps-corps BGIG ;
- une rotation Z de 0 ou 90 degrés selon le cas ;
- une grille exacte de 0,001 mm.

Les quatre workers reçoivent exactement le même fichier
`P64L07FLOOR/1`, la même limite totale, la même graine et le même nombre de
threads.

Le modèle est complet pour une preuve d'impossibilité seulement si le cas
déclare un niveau, aucune réservation et des marges uniformes fidèlement
converties. Une régression sans déclaration de niveau peut fournir une solution
positive certifiée, mais pas une preuve d'impossibilité produit.

## 5. Refus sans perte de contrainte

L'adapter répond `unsupported` avant le worker pour :

- plusieurs niveaux exigés ;
- une réservation supérieure ;
- une exécution incrémentale ;
- une politique de rotation inconnue ;
- une enveloppe fixe supérieure au minimum, car ce worker publie uniquement un
  `minimal_layout` et ne la transforme pas en partition finalisée ;
- une dimension non représentable à 0,001 mm ;
- plus de 64 participants.

Il ne transforme jamais silencieusement un cas T1 en cas T0. Les formes
volumétriques, empilements, supports partiels et réservations restent donc
documentés comme hors de ce premier adapter. Ils pourront devenir une famille
de modèle distincte, pas une extension implicite.

## 6. Sortie et statuts

Le rapport `bgig.external_solver_adapter_result.v2` publie :

- candidat, version, famille, source, licence et digests ;
- contraintes appliquées et complétude exacte ;
- temps moteur, temps total et coût de démarrage ;
- mémoire maximale observée, threads, graine et limites ;
- statut brut et statut BGIG ;
- placement proposé, métriques et certificat frais ;
- erreurs et limites non couvertes.

Les statuts propres au tournoi sont :

- `solution_found` : placement reconstruit et recertifié ;
- `infeasible_proven` : moteur exact et modèle déclaré complet ;
- `bounded_unknown` : absence de solution sans preuve suffisante ;
- `unsupported` : contrainte non représentée ;
- `certificate_rejected` : placement externe refusé par BGIG ;
- `external_error` : worker, checkpoint ou sortie invalide.

LAFF ne peut jamais publier `infeasible_proven`.

## 7. Recertification et isolation

Le worker ne reçoit ni oracle ni réponse attendue. Sa sortie est d'abord
revérifiée indépendamment : participants, bornes, rotation et non-recouvrement.

BGIG reconstruit ensuite des `Free3DPlacement` au fond de la boîte et relance
`bgig.minimal_layout_certificate.v1`. Seul un certificat frais positif rend la
solution visible. Un certificat refusé efface la solution du rapport.

Chaque worker :

- tourne dans un processus séparé ;
- charge seulement son environnement local ;
- fonctionne hors ligne, sans service, compte, secret ou télémétrie ;
- est arrêté sur limite totale ou mémoire ;
- écrit un checkpoint lié au problème et au digest du worker afin d'éviter une
  double exécution après interruption.

## 8. Contrôles exacts L07C

L07C crée trois petits projets BGIG publics :

1. deux carrés 40 × 40 dans 100 × 80, faisable ;
2. deux rectangles 70 × 40 dans 110 × 70, rotation requise ;
3. deux carrés 60 × 60 dans 100 × 80, impossible sur un niveau.

Les quatre entrées nommées `small_exact_controls` dans le manifest L07B ne sont
pas utilisées comme preuve L07C : leur matérialisation réelle comporte une
réservation, plusieurs niveaux ou plusieurs variantes. Le manifest et son
holdout scellé ne sont pas réécrits ; cette limite est tracée explicitement.

Gate réelle : 12 résultats sur 12 conformes, huit placements positifs
recertifiés, trois preuves exactes d'impossibilité et un `bounded_unknown`
honnête pour LAFF.

Preuve versionnée :
`tests/fixtures/p64_l07c_external_adapter_controls.v1.json`.

## 9. Frontières

P64-L07C ne modifie ni solveur produit, lane, ordre, budget public, deadline,
schéma projet, tolérance, géométrie, propriété P45/P64, finalisation, CAD,
scène, manifest Fusion ou valeur physique. Le holdout L07 reste fermé.

Aucune revendication nouvelle n'est faite sur le cas dense 11 × 34.
