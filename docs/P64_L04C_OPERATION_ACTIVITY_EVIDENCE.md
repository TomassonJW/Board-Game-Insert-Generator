# P64-L04C — Preuve d'activité opérationnelle honnête

Date : 2026-07-22
Statut : implemented-core, implemented-fusion-bridge, implemented-fusion-ui, automated-validated

## Résultat livré

P64-L04C rend immédiatement visible toute analyse, calcul minimal, finalisation ou
matérialisation déclenchée explicitement depuis la palette Fusion. L'état expose :

- une identité exacte d'opération et sa révision source ;
- le type sémantique et l'étape courante ;
- le lifecycle active, completed, failed ou rejected ;
- le temps écoulé réel et la raison d'arrêt ;
- l'absence explicite de sémantique d'annulation utilisateur.

Aucun pourcentage ni ETA ne sont produits. Les détails techniques restent repliés
par défaut. Les actions, le focus et l'autosave existants sont préservés.

## Producteur pur et lifecycle

Le module src/board_game_insert_generator/operation_activity.py est déterministe :
les timestamps sont fournis par l'appelant, aucune horloge ni opération métier n'est
appelée par le producteur. L'état est dérivé et non persisté dans le projet.

Le producteur refuse seulement un second type sémantique déjà actif. Analyse, calcul,
finalisation et matérialisation restent des types distincts ; aucune concurrence
différente n'est bloquée sans contrat métier. materialize_project et
regenerate_project partagent volontairement le même type fusion_materialization.

Le bridge reprend ce verrou avec une identité de requête stable. Le terminal de
matérialisation est rafraîchi après la synchronisation réelle de la scène afin que
le temps affiché couvre aussi l'adaptateur Fusion, sans déplacer la logique métier
dans adsk.

## Invariants prouvés

- aucune opération métier n'est démarrée par l'état d'activité ;
- aucun solve global, finaliseur, CAD ou scène automatique n'est ajouté ;
- stale_or_cancelled reste une invalidation fail-closed et ne devient jamais une
  annulation utilisateur générique ;
- aucun bouton Annuler décoratif n'est présent ;
- aucun pourcentage, ETA, classement, budget ou deadline Deep ne change ;
- provenance, méthode, budgets, phases, lanes, incumbent et raisons d'arrêt restent
  transportés par leurs contrats existants ;
- le schéma projet, les valeurs physiques, la géométrie et la CAD IR sont inchangés.

## Vérifications exécutées

- producteur pur : 5/5 tests OK ;
- palette, bridge projet et synchronisation CAD : 85/85 tests OK ;
- suite complète : 648/648 tests OK en 163,810 s ;
- JavaScript extrait de palette.html : node --check OK ;
- Ruff ciblé sur les fichiers Python du diff : OK ;
- py_compile ciblé : OK.
- compileall sur src, add-in et tests : OK ;
- frontière adsk du cœur : OK ;
- git diff --check : OK.

Le contrôle Ruff incluant tout BoardGameInsertGenerator.py retrouve 7 F401
préexistants dans ses imports de compatibilité, hors lignes modifiées. Ils ne sont pas
corrigés dans L04C. Le Ruff global conserve les diagnostics historiques hors diff.

## Limites et vérité produit

- manifest Fusion inchangé à 0.1.58 ;
- aucune installation ni observation Fusion effectuée dans L04C ;
- fusion-validated: false ;
- print-validated: false ;
- aucune nouvelle revendication sur le cas dense 11 × 34 ;
- P64-L04V devient la prochaine gate humaine distincte.
