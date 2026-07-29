# P64-L09W-B — contrat du corpus produit et du holdout fermé

Date : 2026-07-30.

Statut : `implemented`, `automated-validated`, `holdout-sealed`.

## 1. Autorité et portée

Ce contrat implémente ADR-0107 et le contrat de mesure P64-L09W-A. Il fournit
les vérités nécessaires à la campagne P64-L09W-C sans modifier le solveur
évalué.

Le lot couvre :

- le split `regression` de P64-L09W-A, référencé par son schéma et son digest
  sans dupliquer ses fixtures ;
- 400 cas positifs ouverts, séparés en `discovery` et `tuning` ;
- 400 cas positifs privés dans un holdout neuf et fermé ;
- 40 contrôles impossibles avec borne formelle indépendante ;
- un plan soak déterministe de 2 000 recettes, hors gate courte ;
- une construction reprenable par checkpoints atomiques.

Il ne mesure encore aucun taux de récupération du solveur, n’ouvre pas le
holdout et ne change ni budget, ni grille, ni epsilon, ni valeur physique.

## 2. Artefacts et responsabilités

Artefacts versionnés :

- `src/board_game_insert_generator/product_solver_robustness_corpus.py` :
  recettes, reconstruction, témoins, oracles, preuves négatives, validations et
  engagements ;
- `scripts/solver/build_p64_l09w_b_product_corpus.py` : construction
  checkpointée et assemblage final ;
- `tests/fixtures/p64_l09w_b_product_corpus.v1.json` : manifest public ;
- `tests/test_p64_l09w_b_product_corpus.py` : invariants automatisés.

Artefacts privés et ignorés par Git :

- `.codex-work/p64-l09w-b/checkpoints/open/*.json` ;
- `.codex-work/p64-l09w-b/checkpoints/holdout/*.json` ;
- `.codex-work/p64-l09w-b/checkpoints/holdout_nonce.private.txt` ;
- `.codex-work/p64-l09w-b/sealed_holdout.private.json`.

Le manifest public référence la baseline `regression` immuable de A, puis
contient les cas ouverts, les contrôles négatifs, les agrégats préenregistrés du
holdout et son engagement. Il ne contient ni nonce, ni recette, ni projet, ni
témoin privé du holdout.

## 3. Vérité positive indépendante

Chaque cas positif suit obligatoirement cette séquence :

1. construire une recette et une graine déterministes ;
2. construire un placement complet sans appeler le solveur évalué ;
3. dériver le projet `bgig.project.v1` présenté au futur runner sans y inclure
   le placement ;
4. reconstruire l’éventuel état avant édition et une opération unique ;
5. recertifier le témoin par le certificateur BGIG courant ;
6. engager séparément recette, graine, projet, état avant édition, séquence,
   témoin, certificat et cas.

Le compteur `solver_invocation_count` doit rester nul dans la recette, le
témoin, l’oracle, le cas et les agrégats. Une vérité non reconstruite ou non
certifiée n’est pas publiée.

Les éléments plats des cas `common` utilisent la pose automatique produit. Les
cas `stress` utilisent des piles explicites, centrées et strictement
soustractives afin que la construction de vérité reste bornée sans fournir de
témoin au solveur évalué.

## 4. Distribution préenregistrée

Chaque ensemble positif de 400 cas contient exactement :

- 240 cas `common` ;
- 160 cas `stress`.

Les minima obligatoires sont appliqués indépendamment aux 400 cas ouverts et
aux 400 cas du holdout :

| Axe | Valeurs | Minimum par valeur |
| --- | --- | ---: |
| contenus par conteneur | 1, 2, 4, 8, 16, 32, 64 | 20 |
| conteneurs | 1, 2, 4, 8, 12, 18, 30, 50, 64 | 20 |
| occupation cible | 30 %, 65 %, 85 %, 95 % | 60 |
| éléments plats | 0, 1, 2, 3, 4, 5, 6, 10 | 20 |
| couches | 1, 2, 3, 4 ou plus | 40 |
| taille de boîte | petite, moyenne, grande | 60 |
| exécution | froide, ajout, retrait, paramètre local, paramètre global | 40 |

`discovery` contient les 240 cas ouverts `common`. `tuning` contient les 160 cas
ouverts `stress`. Le holdout conserve les mêmes strates sans publier ses cas.

## 5. Contrôles impossibles

Les 40 contrôles négatifs restent hors du dénominateur positif. Ils contiennent
exactement dix preuves de chacune des familles suivantes :

- volume total strictement supérieur au volume disponible ;
- borne stricte sur un axe ;
- empilement Z strictement supérieur à la hauteur disponible lorsque la
  section XY n’admet qu’un conteneur par couche ;
- réservation plate incompatible avec la borne X.

Chaque preuve est reconstruite depuis le projet et vérifie une inégalité
stricte sans exécuter le solveur.

## 6. Fermeture et ouverture unique du holdout

Le sidecar privé engage :

- le nonce de campagne ;
- les 400 cas positifs privés ;
- leur couverture ;
- `opened=false` ;
- `opening_count=0` ;
- `solver_invocation_count=0`.

P64-L09W-B et C ne peuvent jamais ouvrir ce sidecar. P64-L09W-D ne peut pas
l’utiliser pour choisir ou régler une hypothèse. P64-L09W-E pourra l’ouvrir une
seule fois, après engagement d’un candidat unique par commit, configuration,
limites et digest, puis écriture du reçu d’ouverture avant la première
exécution.

Après ouverture, le holdout est consommé. Toute nouvelle itération exige un
nouveau holdout.

## 7. Reprise et bornes de construction

Le builder écrit un fichier JSON atomique par cas. Un checkpoint existant est
accepté seulement si son schéma et son digest de recette correspondent à la
recette courante.

L’option `--max-new-records` borne le nombre total de nouveaux checkpoints
d’une invocation, partagé entre `open` et `holdout`.

Tant qu’un checkpoint manque :

- la sortie terminale vaut `status=paused` ;
- le nombre construit et le nombre restant sont publiés ;
- aucun manifest public final ni sidecar final n’est assemblé.

Lorsque les 800 checkpoints positifs existent, le builder valide les deux
distributions, scelle le sidecar, construit les contrôles négatifs, vérifie la
disjonction des splits et écrit les deux artefacts finaux atomiquement.

## 8. Disjonction et invariants fail-closed

Dans chaque distribution puis entre ouvert et holdout, aucune collision n’est
admise pour :

- `recipe_digest` ;
- `project_digest` ;
- `witness_digest` ;
- `edit_sequence_digest`.

Toute altération de recette, projet, témoin, oracle, preuve négative, couverture
ou engagement final est refusée.

Les invariants produit restent :

- grille produit `0,1 mm` ;
- epsilon géométrique `0,0001 mm` ;
- éléments plats strictement soustractifs ;
- aucun témoin fourni au solveur évalué ;
- aucun ancien holdout L06, L07 ou L08 réutilisé ;
- `fusion-validated=true` hérité de 0.1.80 ;
- `print-validated=false`.

## 9. Gate de clôture B

P64-L09W-B est terminée seulement si :

1. les 400 cas ouverts et les 400 cas privés reconstruisent leurs engagements ;
2. les minima pairwise sont satisfaits des deux côtés ;
3. les 40 preuves négatives sont valides ;
4. les quatre familles de digests sont disjointes entre ouvert et holdout ;
5. le manifest ne divulgue aucun contenu privé ;
6. le holdout reste à `opening_count=0` ;
7. la construction conserve `solver_invocation_count=0` ;
8. les tests ciblés et les gates documentaires passent.
