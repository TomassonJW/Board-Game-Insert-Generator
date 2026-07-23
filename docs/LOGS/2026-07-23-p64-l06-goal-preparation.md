# 2026-07-23 — Préparation du Goal P64-L06

## Contexte

Le programme L06 décrivait les familles de cas, comparateurs et tiers, mais pas
encore un lancement autonome suffisamment borné pour une pause nocturne, une
reprise sûre et une intégration algorithmique sans surapprentissage.

Les cinq bundles locaux ont été listés en lecture seule. Les trois plus récents
sont la séquence déjà analysée avant le correctif R1 ; aucune nouvelle paire
postérieure à l'installation `e817432` n'est présente. L06A reste donc bloqué.

## Changements

- ajout d'un runbook Goal canonique plafonné à 36 h et 2 Gio ;
- séparation des axes P45 et P64 et des familles A à E ;
- splits regression, discovery, tuning et holdout fermé ;
- tournoi progressif avant un soak facultatif ;
- petit oracle exact interne prioritaire pour ne dépendre d'aucune installation ;
- une seule amélioration algorithmique intégrable dans le premier Goal ;
- checkpoints atomiques, protocole de pause/reprise et arrêts explicites ;
- prompt `/goal` prêt pour la nouvelle tâche ;
- `.codex-work/` ignoré pour les artefacts temporaires bornés.

## Recherche vérifiée

Les sources officielles confirment :

- PackingSolver possède un solveur `box` pour parallélépipèdes 3D, rotations et
  limite de temps, sous licence MIT, mais demande une compilation CMake ;
- `3d-bin-container-packing` fournit LAFF et brute force sous Apache-2.0 ; son
  propre guide réserve le brute force aux petites cardinalités et recommande une
  deadline ;
- OR-Tools CP-SAT convient aux modèles de contraintes, mais la modélisation 3D
  BGIG et la dépendance restent à décider séparément.

Ces moteurs restent des comparateurs offline, jamais des sorties crues ni des
dépendances produit implicites.

## Impact

La future campagne peut progresser sans outil externe, éviter le produit
cartésien de cas redondants et refuser une optimisation surajustée au projet
personnel. Aucun comportement produit ou solveur n'est modifié.

## Validation

- garde documentaire : 2/2 ;
- Ruff ciblé : OK ;
- py_compile ciblé : OK ;
- suite complète : 682/682 en 163,352 s ;
- recherche de chemins personnels et secrets : OK ;
- `git diff --check` et staged diff-check : OK.

## Suite

Créer une nouvelle tâche BGIG sur un worktree propre. Elle doit attendre le
lancement explicite `/goal` de Thomas, vérifier d'abord la paire R1 et ne pas
redemander de GO après ce lancement.
