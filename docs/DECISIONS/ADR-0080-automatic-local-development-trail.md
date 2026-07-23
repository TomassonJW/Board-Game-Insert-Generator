# ADR-0080 - Journal local automatique du parcours de développement

## Statut

Acceptée le 2026-07-23 sur décision explicite de Thomas.

Cette décision remplace la partie interface et collecte manuelle d'ADR-0077. Le format `SolverCaseBundle` et son producteur interne restent disponibles pour les outils de développement, mais le bouton DEV disparaît de la palette.

## Contexte

La capture manuelle imposait de cliquer au bon instant, pouvait manquer un état transitoire et transformait Thomas en opérateur de diagnostic. Elle bloquait aussi une campagne dont le but principal est de générer, rejouer et comparer de nombreux cas de manière autonome.

Un bundle complet à chaque clic serait fidèle mais trop lourd. Un simple journal de texte serait léger mais ne permettrait pas de retrouver l'état exact du projet.

## Options

### A - Conserver le bouton DEV et la gate humaine

Simple techniquement, mais fragile, lent et contraire à l'objectif d'autonomie du benchmark.

### B - Écrire un SolverCaseBundle complet après chaque action

Très riche, mais coûteux en calcul, en espace disque et en écritures répétées.

### C - Journal chronologique compact et états de projet dédupliqués

Chaque action écrit une ligne courte. Chaque état complet du projet est stocké localement une seule fois par empreinte, puis référencé par les lignes suivantes.

## Décision

Retenir l'option C.

La palette enregistre automatiquement :

- le début de session ;
- chaque bouton pressé ;
- chaque champ modifié et l état complet qui en résulte ;
- chaque demande envoyée au moteur et son résultat ;
- les ouvertures et enregistrements de documents ;
- les actions Fusion ;
- les erreurs de communication.

Les événements sont écrits sous `Documents/BGIG/projects/dev-action-logs/session-.../events.jsonl`. Les états complets du projet sont conservés dans le sous-dossier `snapshots/` et dédupliqués par SHA-256.

Les nombres, booléens et choix fermés peuvent être journalisés. Le texte libre est seulement marqué comme modifié dans la ligne d'événement ; l'état complet reste dans la copie locale du projet. Les chemins de documents, secrets, jetons, mots de passe et identifiants assimilés sont refusés. Aucun journal ni projet personnel n'est ajouté automatiquement au dépôt.

Une panne du journal ne doit jamais bloquer une action produit. Le journal n'appelle ni solveur, ni finalisation, ni CAD, ni scène Fusion et ne modifie pas l'algorithme.

Le bouton `DEV · Capturer le cas` est supprimé. L'action interne `capture_solver_case` reste compatible pour les tests et outils hors interface.

La paire humaine R1 n'est plus une condition de lancement de P64-L06. Les cas réels disponibles et les futurs journaux restent des preuves complémentaires. La campagne autonome commence par le corpus versionné, les générateurs T0/T1 et les oracles internes ; elle peut ensuite intégrer un cas réel seulement après anonymisation et validation.

## Conséquences

### Positives

- aucun clic spécial ni synchronisation humaine fragile ;
- parcours complet analysable après coup ;
- états exacts disponibles sans duplication massive ;
- benchmark autonome débloqué ;
- séparation conservée entre observation, benchmark et modification du solveur.

### Limites

- le journal n'est pas à lui seul une preuve géométrique ;
- un état personnel reste local tant qu'il n'est pas anonymisé et relu ;
- l'absence de bouton retire l'export manuel immédiat d'un bundle depuis la palette ;
- aucune validation Fusion ou impression n'est déduite du journal.

## Validation

Contrat : `docs/P64_L05V_R2_AUTOMATIC_ACTION_LOG_CONTRACT.md`.

Preuve : `docs/P64_L05V_R2_AUTOMATIC_ACTION_LOG_EVIDENCE.md`.

fusion-validated: false. print-validated: false.
