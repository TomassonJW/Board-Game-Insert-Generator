# P64-L05V-R2 - Contrat du journal automatique

Date : 2026-07-23

Statut cible : implemented-fusion-bridge, implemented-fusion-ui, automated-validated ; fusion-validated: false ; print-validated: false.

## Objectif

Conserver automatiquement le parcours utile dans BGIG sans bouton spécial, sans ralentir le moteur et sans exiger une capture humaine au bon instant.

## Sorties locales

Une session produit :

- `dev-action-logs/session-.../events.jsonl` : une ligne JSON compacte par événement ;
- `dev-action-logs/session-.../snapshots/project-<sha256>.bgig.json` : un état complet par empreinte unique.

Le schéma d'événement est `bgig.dev_action_log_event.v1`.

## Événements obligatoires

- `session_started` ;
- `button_pressed` ;
- `field_changed` ;
- `project_changed` avec état complet dédupliqué ;
- `bridge_request` ;
- `bridge_response` ;
- `bridge_failure` ;
- `document_request` ;
- `fusion_action_requested`.

Chaque ligne porte au minimum la session, la séquence, l'heure, la révision, la vue active, le type et un résumé d'état. Les résultats conservent les statuts et raisons d'arrêt du calcul minimal, de la réutilisation locale et de l'insertion dans le volume global.

## Efficacité

- un clic écrit une seule ligne compacte ;
- un état complet identique n'est écrit qu'une fois ;
- le journal n'appelle aucune opération du moteur ;
- l'écriture est locale et sérielle ;
- une erreur du journal ne bloque jamais l'action demandée par l'utilisateur.

## Protection des données

- aucun chemin de document dans les événements ;
- aucun secret, jeton, mot de passe ou identifiant assimilé ;
- aucune valeur de texte libre dans les lignes de changement ;
- les états complets restent exclusivement dans le stockage local BGIG ;
- aucune promotion automatique dans Git ou dans le corpus versionné.

## Frontières

Le lot ne modifie ni solveur, ni budget, ni délai, ni certificat, ni géométrie, ni finalisation, ni CAD, ni scène Fusion. Il ne crée aucune auto-modification et n'installe aucune dépendance.

Le bouton DEV est absent de la palette. Le producteur historique de SolverCaseBundle reste interne et compatible.

## Acceptation

- stockage et déduplication testés hors Fusion ;
- clés sensibles et sessions dangereuses refusées ;
- route du journal séparée du traitement projet et du solveur ;
- chaque bouton et chaque changement de champ instrumentés ;
- demandes, résultats et erreurs instrumentés ;
- bouton et styles DEV absents ;
- manifest porté à 0.1.59 ;
- suite complète, Ruff ciblé, `py_compile`, frontière `adsk` et contrôles Git réussis.
