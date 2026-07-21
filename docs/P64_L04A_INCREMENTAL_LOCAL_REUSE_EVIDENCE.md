# P64-L04A — Preuve de réutilisation locale incrémentale

Date : 2026-07-22
Statut : `implemented-core`, `implemented-fusion-bridge`,
`implemented-fusion-ui`, `automated-validated`.
Package Fusion : 0.1.58.
`fusion-validated: false` ; `print-validated: false`.

Autorité :

- [ADR-0075](DECISIONS/ADR-0075-pre-final-local-layout-reuse.md) ;
- [contrat P64-L04](P64_L04_INCREMENTAL_LOCAL_REUSE_CONTRACT.md) ;
- ADR-0070 pour la propriété P45/P64 ;
- ADR-0074 pour `minimal_layout`, matérialisation et identité de scène.

## 1. Résultat livré

Le cœur pur tente une recertification locale avant de rendre obligatoire un
nouveau solve global :

```text
édition locale
  -> frontière locale courante
  -> conservation des cavités existantes
  -> insertion rectangulaire bornée dans l’enveloppe déjà placée
  -> fallback éventuel vers une variante certifiée de même enveloppe
  -> certificat local
  -> certificat minimal global sans recherche
```

Une réussite crée un nouvel artefact et conserve les poses monde. Un refus ne
lance pas le solveur : l’ancien plan devient stale et l’interface demande une
action `Calculer l’agencement minimal`.

## 2. Implémentation

### Cœur

`src/board_game_insert_generator/incremental_layout_reuse.py` ajoute :

- `incremental_fixed_envelope_v1`, version 1 ;
- caps : 4 conteneurs touchés, 8 nouvelles cavités par conteneur,
  128 positions par cavité et 1 024 états locaux par conteneur ;
- conservation stricte des origines encore admissibles ;
- positions candidates issues des parois et contacts de cavités ;
- fallback vers la frontière locale courante à enveloppe exacte ;
- certificat local commun puis `certify_minimal_free_3d_plan` ;
- intégrité recalculée du `plan_digest` source avant toute réutilisation ;
- comparaison des corps, origines, tailles locale/monde et rotations ;
- provenance, compteurs, stop reason et compteur solve global à zéro.

### Orchestration

`staged_calculation.py` tente L04A seulement lorsqu’un plan minimal certifié
était courant, que la source a changé et que les réglages solveur sont
inchangés. Un succès :

- marque un nouvel artefact global courant ;
- ne remplit pas le cache de solve global ;
- rend le plan finalisé stale ;
- rend la CAD/scène désynchronisée ;
- expose le plan courant sans calcul par `current_minimal_partition()`.

### Fusion bridge et palette

Pendant `validate_project`, le bridge renvoie le plan recertifié sans appeler
`calculate_layout`. La palette :

- remplace l’aperçu obsolète par le nouvel artefact courant ;
- affiche `Élément intégré localement — Placement global conservé` ;
- affiche `Recalcul global requis` en cas de refus ;
- garde producteur, conteneurs, caps et compteurs dans un détail replié ;
- ne matérialise ni ne met à jour la scène automatiquement.

## 3. Matrice des fixtures contractuelles

| # | Preuve |
| --- | --- |
| 1 | Ajout de `compartment:c` dans une poche 8 × 16 × 8 mm ; origines A/B conservées. |
| 2 | Enveloppe locale, origine monde, taille monde et rotation identiques avant/après. |
| 3 | Ajout 20 × 20 × 10 mm refusé ; plan absent et solve global à zéro. |
| 4 | Changement de boîte classé `not_attempted / global_dependency_changed`. |
| 5 | Nouveau conteneur classé `global_solve_required` sans exception ni solve. |
| 6 | Certificats locaux et altérations de digest restent fail-closed dans la suite commune P45. |
| 7 | Plan source au certificat global ou au `plan_digest` altéré refusé avant réutilisation. |
| 8 | Session staged : nouvelle révision, nouveau plan et nouvel artifact digest. |
| 9 | Plan finalisé stale et scène `desynchronized`, sans mutation Fusion. |
| 10 | Bridge `validate_project` renvoie le plan courant sous patch interdisant le solveur global. |
| 11 | Échange de dimensions A/B : producteur strict refusé, variante certifiée de même enveloppe retenue. |
| 12 | Deux exécutions donnent plan, rapport, compteurs et caps identiques. |
| 13 | Cas dense 11 × 34 inchangé : aucune nouvelle revendication de solution. |
| 14 | L’analyse contextuelle existante conserve `unknown` sans promotion. |
| 15 | Frontière `adsk` : aucun import Fusion dans `src/board_game_insert_generator`. |

## 4. Vérifications

- 9/9 tests L04A purs et staged ;
- 22/22 tests `test_fusion_palette_project.py` ;
- 34/34 tests DOM ;
- 10/10 tests staged historiques ;
- 8/8 tests transport Qt ;
- 5/5 tests P66 ;
- 6/6 tests Fusion-only ;
- 636/636 suite complète, 154,576 s, wrapper Windows gardé ;
- Ruff ciblé : OK ;
- `py_compile` ciblé : OK ;
- syntaxe JavaScript extraite de la palette, `node --check` : OK.
- `compileall` ciblé : OK ;
- frontière `adsk` du cœur pur : OK ;
- `git diff --check` : OK, avertissements de normalisation CRLF uniquement.

## 5. Limites et vérité

- le producteur reste rectangulaire et conservateur ; il peut refuser une
  solution locale qui existerait avec une sémantique P45 future ;
- aucune pose monde voisine n’est explorée ;
- le succès local ne prétend pas améliorer l’optimalité du plan global ;
- Rapide, Normal, Approfondi et leurs budgets restent inchangés ;
- L04B possède la correction Approfondi anytime ;
- L04C possède le retour d’attente des opérations longues ;
- aucune finalisation, capacité C01/C02, cale, valeur physique ou scène
  automatique n’est incluse ;
- le cas dense reste `no_solution_within_budget` ;
- aucune observation Fusion 0.1.58 ni impression réelle n’est revendiquée.
