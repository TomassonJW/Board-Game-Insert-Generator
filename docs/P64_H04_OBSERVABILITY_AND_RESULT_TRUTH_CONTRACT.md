# P64-H04 — Résultats honnêtes, observabilité et corpus de régression

Statut : `terminé et intégré` le 2026-07-17 ; P64-H05 devient la mission suivante unique.

Agent conseillé : Terra. Une revue senior est requise sur les contrats publics
de résultat ; aucun travail algorithmique Luna n'est nécessaire dans ce lot.

## 1. Objectif

Rendre le comportement actuel mesurable et honnête avant d'introduire une
nouvelle stratégie. P64-H04 ne cherche pas davantage de placements : il décrit
exactement ce qui a été essayé, pourquoi le run s'est arrêté et si le moteur a
prouvé ou seulement échoué à trouver une solution.

## 2. Dépendances et sources

- `docs/P64_MULTI_SOLVER_PORTFOLIO_PROGRAM.md`, sections 6 à 8 et 13 ;
- ADR-0068 ;
- contrats P64-H01/H02 ;
- essai local P64-H03 consultable en lecture seule pour récupérer les faits et
  fixtures utiles, sans reprendre son algorithme ni son ADR-0067 ;
- état réel sauvegardé par Fusion, à anonymiser avant ajout au dépôt.

## 3. Livrables obligatoires

1. Un statut interne distinct pour :
   `solution_found`, `no_solution_within_budget`, `proven_impossible`,
   `invalid_input`, `stale_or_cancelled`.
2. Une compatibilité additive du transport : aucun ancien projet n'est migré et
   aucune clé source n'est supprimée.
3. Un bloc de télémétrie versionné contenant au minimum : famille/version,
   request id/révision, temps, budgets, candidats, états/placements essayés,
   coupes agrégées, solutions certifiées et motif d'arrêt.
4. Des diagnostics français :
   - `Aucune solution trouvée dans le budget` pour l'épuisement heuristique ;
   - `Impossible prouvé` seulement quand le code possède une preuve explicite ;
   - `Projet à corriger` pour l'invalidité d'entrée.
5. Un corpus de fixtures anonymisées : cas simple réussi, cas dense P64-H01,
   cas P64-H02 à réservations, dernier cas réel non résolu et au moins un vrai
   conflit formel indépendant de l'heuristique.
6. Le vocabulaire `Niveaux de départ Z` pour le nombre de plans Z distincts ;
   ne pas appeler automatiquement ces plans des couches visibles.
7. Une vue développeur repliée ou des données de diagnostic transportées sans
   mutation du DOM éditable. Une nouvelle fenêtre n'est pas requise dans H04.

## 4. Règles de classification

- Une validation d'entrée contradictoire peut produire `invalid_input`.
- Une borne nécessaire violée de façon mathématique et indépendante de l'ordre
  peut produire `proven_impossible` seulement si le diagnostic cite la preuve.
- Un timeout, budget atteint, beam/ordre/partition épuisé, candidat non trouvé ou
  candidats rejetés après validation produit `no_solution_within_budget`.
- Une requête dont l'identifiant ou la révision n'est plus courant produit
  `stale_or_cancelled` et ne remplace aucun résultat visible.
- Une proposition partielle n'est jamais `solution_found` et reste non
  matérialisable.
- Le booléen historique éventuellement conservé pour compatibilité est une
  projection du nouveau statut, jamais sa source de vérité.

## 5. Télémétrie et confidentialité

Le schéma doit être additif, déterministe et sérialisable. Les identifiants
utilisateur peuvent être remplacés par des identifiants stables anonymisés dans
les fixtures. Ne stocker ni chemin AppData, ni nom de document personnel, ni
contenu extérieur au projet nécessaire à la reproduction.

Les compteurs absents d'une famille valent `not_applicable` ou sont omis selon
un contrat explicite ; ils ne doivent pas être inventés à zéro. Le temps réel ne
participe pas au digest déterministe.

## 6. Fichiers à inspecter avant édition

L'agent confirme les noms réels au préflight, puis cible au minimum :

- `partition_solver.py` et `volumetric_stage_solver.py` pour les motifs d'arrêt ;
- les dataclasses/serializers du plan P64 ;
- le bridge de palette et la projection de résultat ;
- le JavaScript de statut/diagnostic sans reconstruction du formulaire ;
- les tests solveur, transport, stale responses et documents.

Fusion/adsk ne reçoit aucune logique métier.

## 7. Non-objectifs absolus

- nouvel ordre, seed, partition, EP/EMS, beam ou augmentation de budget ;
- modification du score ou sélection d'un autre candidat ;
- modification de schéma projet, dimensions, defaults, jeux, tolérances,
  cavités, supports, réservations, géométrie ou CAD IR ;
- fenêtre modale, timer de recalcul supplémentaire ou autosave profond ;
- matérialisation automatique ;
- revendication d'impossibilité formelle pour un échec heuristique.

## 8. Acceptation automatisée

- chaque motif d'arrêt actuel est mappé vers un statut testé ;
- une troncature de budget donne `no_solution_within_budget` ;
- un projet invalide donne `invalid_input` avant recherche ;
- aucun test n'obtient `proven_impossible` sans code de preuve autorisé ;
- une réponse obsolète ne modifie ni statut, ni diagnostic, ni focus ;
- chaque fixture expose famille, budget, motif d'arrêt et compteurs cohérents ;
- les placements réussis restent identiques aux références H01/H02 ;
- le corpus dense ne contient aucune donnée locale non nécessaire ;
- suite complète, `compileall`, exemple CLI, frontière `adsk` et
  `git diff --check` passent.

## 9. Gate et clôture

P64-H04 n'ouvre pas de gate Fusion autonome si aucun nouveau panneau visible
n'est ajouté. Un changement de libellé utilisateur est couvert par tests DOM et
sera observé avec P64-V2. Après intégration, P64-H05 devient la seule mission
`ready`.

Le rapport final doit fournir : fichiers, mapping complet des anciens motifs
d'arrêt, tests, fixtures ajoutées, limites, commit intégré et rappel de P64-H05.
`fusion-validated` et `print-validated` ne changent pas.
