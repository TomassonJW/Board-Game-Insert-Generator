# P64-L09W-B — preuve du corpus produit et du holdout fermé

Date : 2026-07-30.

Statut : `done`, `automated-validated`, `integrated-pending`.

## 1. Résultat

P64-L09W-B livre un corpus produit neuf, reconstructible et indépendant du
solveur évalué :

- split `regression` : baseline A immuable référencée, sans duplication ;
- 400 positifs ouverts : 240 `discovery/common`, 160 `tuning/stress` ;
- 400 positifs privés : 240 `common`, 160 `stress` ;
- 40 contrôles impossibles : dix par famille de preuve ;
- un plan soak déterministe de 2 000 recettes ;
- zéro appel solveur pendant la construction des vérités.

Le holdout reste fermé. Aucun taux de succès solveur n’est revendiqué dans B.

## 2. Reprise réelle et construction bornée

La reprise a commencé depuis l’état privé vérifié suivant :

- 400/400 checkpoints ouverts ;
- 273/400 checkpoints holdout ;
- 127 cas holdout restants ;
- aucun manifest public final ;
- aucun sidecar final ;
- nonce privé non affiché.

L’option `--max-new-records` et son test de reprise ont été relus puis le test
unitaire ciblé a repassé avant toute nouvelle construction.

Un premier essai terminal limité par la couche d’attente à 30 s n’a écrit aucun
checkpoint. L’absence de processus et le compte 273/400 ont été revérifiés
avant l’unique reprise.

La construction réelle a ensuite suivi des lots distincts et terminaux :

| Nouveaux cas maximum | État après lot |
| ---: | ---: |
| 1 | 274/400 |
| 5 | 279/400 |
| 10 | 289/400 |
| 20 | 309/400 |
| 20 | 329/400 |
| 20 | 349/400 |
| 20 | 369/400 |
| 20 | 389/400 |
| 11 | 400/400 et assemblage final |

Chaque lot a utilisé le wrapper gardé, un heartbeat de 10 s et un timeout métier
explicite. Aucune commande monolithique n’a été relancée et aucun checkpoint
valide n’a été supprimé.

## 3. Engagements finaux

Manifest public :

- chemin :
  `tests/fixtures/p64_l09w_b_product_corpus.v1.json` ;
- schéma : `bgig.product_solver_robustness_corpus.v1` ;
- générateur : `p64-l09w-product-pairwise-v2` ;
- digest :
  `04dd2bf5feed37b7d5e72e523d5d7f0cd6bc0672f9ecfb55b227d5fcb6635840`.

Sidecar privé :

- chemin :
  `.codex-work/p64-l09w-b/sealed_holdout.private.json` ;
- schéma : `bgig.product_solver_robustness_holdout.v1` ;
- digest :
  `18bd401058f882b4deb2951e775b344e1a4d00b49994e5ffaa962572b876ec5a` ;
- `opened=false` ;
- `opening_count=0` ;
- `solver_invocation_count=0`.

Le nonce reste uniquement dans l’artefact privé et n’a pas été affiché.

## 4. Couverture et séparation

Le vérificateur final recharge les deux artefacts avec les validateurs
versionnés puis confirme :

- minima pairwise ouverts : satisfaits ;
- minima pairwise holdout : satisfaits ;
- comptes holdout : 240 `common`, 160 `stress` ;
- comptes ouverts : 240 `discovery`, 160 `tuning` ;
- source `regression` : baseline A
  `26aed0b3...7105`, cas non réembarqués ;
- 40 contrôles négatifs ;
- zéro collision ouvert/holdout pour les digests de recette, projet, témoin et
  séquence d’édition ;
- `holdout_recipes_embedded=false` ;
- `opening_count=0` ;
- `solver_invocation_count=0`.

Les tests vérifient aussi :

- reconstruction et recertification courantes d’un cas positif ;
- absence de témoin ou de placements dans le projet futur remis au solveur ;
- reconstruction distincte des cinq types d’exécution ;
- engagements ouverts et privés distincts ;
- quatre familles de bornes négatives ;
- refus fail-closed après altération ;
- déterminisme du soak ;
- borne et reprise du builder ;
- compacité logique du manifest public et absence de fuite privée.

## 5. Changements produit

Le solveur, ses lanes, SCIP, ses budgets, ses limites, la grille, l’epsilon, la
géométrie, la finalisation, le CAD IR et Fusion ne changent pas.

Le seul nouveau code de cœur produit ici construit et vérifie les données de
campagne. Il n’est pas appelé par le parcours utilisateur 0.1.80.

## 6. Validation

Résultats observés avant le commit de clôture :

- compilation Python du module, du builder et du test : OK ;
- test ciblé de borne/reprise : `1/1`, OK ;
- suite P64-L09W-B : `10/10`, OK ;
- suite P64-L09W complète : `21/21`, OK ;
- contrats documentaires : `11/11`, OK ;
- suite complète canonique finale : `1054/1054`, `1` skip prévu, OK en
  `561,949 s` ;
- vérificateur final : `status=final_corpus_verified`.

Le lint Ruff ciblé n’a pas pu démarrer car Ruff n’est pas installé dans le
Python courant. Aucune dépendance n’a été ajoutée pour contourner cette limite ;
la compilation Python et la suite complète couvrent la clôture B.

## 7. Limites et prochaine frontière

- Le holdout n’a pas été exécuté : c’est un invariant, pas une lacune.
- Aucun taux 95 % ou 99 % n’est encore démontré.
- La matérialisation reste `not-measured-offline`.
- `fusion-validated=true` reste l’acquis 0.1.80 ; B ne demande aucun replay
  humain.
- `print-validated=false`.

P64-L09W-C doit maintenant construire le runner produit borné et instrumenté,
exécuter uniquement les splits ouverts, mesurer la baseline 0.1.80 et classer
causalement les pertes avant toute optimisation.
