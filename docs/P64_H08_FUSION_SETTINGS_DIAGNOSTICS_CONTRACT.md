# P64-H08 — Réglages Fusion, résultats honnêtes et diagnostic secondaire

Statut : `implemented`, `automated-validated` dans le package 0.1.51.

## Objectif borné

P64-H08 expose dans la palette Fusion le portefeuille déjà livré par P64-H07,
sans déplacer de décision métier dans Fusion :

- méthode : `Auto intelligent` par défaut, `Étages et piles`, `Placement 3D libre` ;
- effort : `Rapide`, `Normal` par défaut, `Approfondi` ;
- classement visible : `Équilibré` et `Compact` ;
- diagnostic secondaire du dernier calcul ;
- persistance locale additive des choix de recherche ;
- aperçu adaptatif maintenu, matérialisation toujours explicite.

Le lot ne modifie ni schéma `bgig.project.v1`, ni dimensions, ni defaults
physiques, ni tolérances, ni cavités, ni réservations, ni CAD IR, ni scène
Fusion automatique.

## Frontière et persistance

`solver_settings` est stocké dans `bgig_document_state_v1.json`, à côté de la
récupération locale du document. Cette préférence n'est jamais écrite dans le
JSON projet et reste donc compatible avec les projets existants et leurs
migrations.

Une réponse `save_solver_settings` ne contient pas de projet et ne reconstruit
pas le DOM éditable. Elle met seulement à jour l'état local, déclenche un aperçu
adaptatif borné, et conserve focus/sélection de l'éditeur actif.

## Sélection publique

`solve_partition_plan` accepte des paramètres optionnels, normalisés par
`solver_settings.py` :

| Choix | Familles admissibles | Règle de résultat |
| --- | --- | --- |
| Auto intelligent | baseline, greedy 3D, beam 3D | meilleur plan complet certifié parmi les familles exécutées |
| Étages et piles | baseline préservée | résultat historique inchangé, seulement décoré de métadonnées produit H08 |
| Placement 3D libre | greedy 3D, beam 3D | aucun plan baseline ne peut être sélectionné |

Les profils d'effort proviennent exclusivement du portefeuille H07. Ils restent
bornés, monotones et observables ; `Approfondi` ne garantit ni solution ni temps
maximum perçu. L'effort est affiché aussi pour la baseline, mais n'en modifie pas
l'algorithme préservé.

## Vérité et compatibilité

- seuls les plans complets certifiés sont matérialisables ;
- une absence dans un budget reste `no_solution_within_budget`, jamais une preuve
  d'impossibilité ;
- les propositions résiduelles historiques restent visibles et bloquées à la
  matérialisation ;
- les anciens critères de classement du projet restent lisibles comme
  compatibilité mais ne sont plus proposés comme choix actif P64-H08 ;
- méthode, effort, famille retenue, candidats certifiés, arrêt et durée sont
  secondaires et repliables dans l'aperçu.

## Validation automatisée

- normalisation des réglages et choix Auto / baseline / 3D libre ;
- résultat et matérialisabilité cohérents avec le statut du plan ;
- persistance locale sans auto-enregistrement du projet ;
- bridge Fusion sans `adsk` ;
- DOM : réglages visibles, classement borné et sauvegarde locale sans rendu
  global dans la réponse silencieuse ;
- régression baseline, portefeuille et palette existante.

## Gate suivante

Préparation : `scripts/fusion/prepare_p64_v2_solver_portfolio_test.ps1`.

P64-V2 doit vérifier dans Fusion les trois méthodes, les trois efforts, le
résultat et diagnostic honnêtes, la stabilité focus/sélection pendant saisie
rapide, et l'absence de matérialisation automatique. Elle ne valide ni valeurs
physiques ni impression. `print-validated: false`.
