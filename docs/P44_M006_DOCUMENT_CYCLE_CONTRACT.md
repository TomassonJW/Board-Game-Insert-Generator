# P44-M006 — Réglages, cycle document et diagnostic

## Statut

Mission P44-M006. Package cible : 0.1.29. La validation humaine Fusion est
requise avant toute intégration dans main. Cette mission ne valide aucune
impression réelle.

## Intention

Rendre la palette lisible pour une personne non technique sans déplacer la
logique métier hors du cœur Python :

- les réglages de conception essentiels sont visibles et décrits ;
- la hauteur de conception est dérivée de la hauteur intérieure de la boîte
  moins le jeu sous le couvercle ;
- un projet peut être nouveau, nommé, ouvert, enregistré et retrouvé ;
- la récupération locale protège la saisie sans remplacer silencieusement un
  fichier nommé ;
- les outils de scène Fusion restent discrets, dans Diagnostic et scène Fusion.

## Périmètre livré

Le bridge Python sans adsk conserve une récupération atomique locale et ajoute
un état de document local : fichier courant, liste récente bornée et dossier
par défaut Documents/BGIG/projects.

La palette expose Nouveau, Ouvrir, Enregistrer sous, Enregistrer et Exporter
une copie. Ouvrir et Enregistrer sous passent par le FileDialog natif Fusion,
initialisé dans le dossier de projets BGIG. Annuler un dialogue ne modifie ni
le projet ni le fichier courant.

La saisie non enregistrée est récupérée après 1,2 seconde sans effacer son état
sale ni déclencher un calcul, une matérialisation ou une inspection Fusion.
Enregistrer un document nommé écrit ce document puis la récupération locale.
Importer reste une action explicite distincte et ne réécrit pas le document
source importé.

## Invariants

- Le cœur dans src/board_game_insert_generator n’importe pas adsk.
- Le schéma bgig.project.v1, le solveur, les tolérances, la géométrie, CAD IR,
  les compléments historiques et les règles de matérialisation ne changent pas.
- Les compléments restent hors du parcours normal.
- La récupération locale est additive, atomique et distincte des paramètres
  techniques de l’add-in.
- Un nouveau projet ne peut pas écraser le dernier document nommé par
  Enregistrer.
- Les fichiers sont UTF-8 sans BOM ; tout texte humain de la palette est
  français accentué et sans séquence de mojibake.
- Effacer la scène demande confirmation et ne vise que les objets BGIG
  identifiés. Aucune scène n’est modifiée automatiquement.

## Validation automatisée

- tests de bridge : sauvegarde nommée, ouverture, récents, récupération,
  nouveau projet non destructif et nom accentué ;
- tests DOM : libellés visibles, hauteur dérivée, diagnostic replié et contrôles
  document ;
- tests transport : FileDialog strictement dans l’adaptateur Fusion ;
- syntaxe Python et JavaScript ;
- suite complète, compileall, frontière adsk et contrôle Git.

## Gate humaine P44-M006V

Dans Fusion 360, avec le package 0.1.29 :

1. ouvrir BGIG et vérifier les libellés français, la hauteur de conception
   calculée et le panneau diagnostic replié ;
2. Nouveau puis Enregistrer sous : vérifier le dialogue natif Fusion, le dossier
   par défaut, l’annulation sans perte et le nom affiché ;
3. modifier une valeur, attendre au moins deux secondes, fermer et rouvrir BGIG :
   vérifier la récupération locale ;
4. Ouvrir un fichier BGIG, vérifier que le document source est lu sans
   réécriture automatique, puis ouvrir un projet récent ;
5. vérifier Inspecter et Effacer la scène dans le diagnostic, avec confirmation
   pour Effacer ; aucun calcul ni changement de scène ne doit partir seul.

Réponse attendue : P44-M006 Fusion OK 0.1.29 - commit SHA, ou un KO
contextualisé.
