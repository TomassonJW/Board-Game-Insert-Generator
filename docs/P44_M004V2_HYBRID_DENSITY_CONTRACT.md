# P44-M004V2 — Contrat de densité structurelle hybride C

Date : 2026-07-14
Statut : implémenté, validation Fusion humaine requise
Package cible : palette Fusion 0.1.26

## Contexte

La revue humaine du package 0.1.25 confirme plusieurs comportements de P44-M004,
mais refuse la densité réelle de l’interface. À largeur Fusion proche de 1280 px,
la palette plafonnait à 920 px, répétait titres, aides et contrôles de densité,
et repoussait le premier conteneur sous la ligne de flottaison. Plusieurs
conteneurs et leurs éléments enfants restaient difficiles à comparer.

Thomas a choisi l’option hybride C : utiliser la largeur disponible, conserver
des cibles accessibles, afficher les réglages primaires en rangées techniques et
déporter seulement les actions ou calculs secondaires.

## Dépendances

- P44-M003V acceptée ;
- P44-M004 intégrée sur main ;
- retour humain de densité sur 0.1.25 reçu ;
- aucun changement de modèle nécessaire.

## Périmètre livré

1. largeur utile maximale portée de 920 à 1180 px ;
2. marque, titre, état et cycle de vie condensés dans une ligne d’en-tête ;
3. messages globaux sortis du flux vertical ;
4. une seule barre de création, presets et densité ;
5. suppression de la grande carte « Démarrage rapide » et des aides redondantes ;
6. boîte, plateaux/livrets, conteneurs et éléments présentés en grilles
   techniques horizontales ;
7. nom éditable unique, champs principaux et solidité visibles en permanence ;
8. actions secondaires sous menu local et calculs automatiques sous
   « Détails calculés » replié ;
9. conteneur parent et éléments enfants conservés dans une composition compacte ;
10. cibles interactives principales de 40 px et repli responsive à 1020, 760 et
    559 px ;
11. libellés nouveaux et touchés en français UTF-8 accentué.

## Invariants et exclusions

- aucun schéma ou format de projet modifié ;
- aucune migration ;
- aucun bridge ou action Fusion ajouté ;
- aucun solveur, tolérance, géométrie, CAD IR ou scène Fusion modifié ;
- aucune matérialisation ou vérification automatique ;
- aucun complément historique réactivé ;
- aucun travail dans frontend/, Vite ou local_composer.

La relation métier reste contents[].container_group_id. Le compactage ne crée
ni arbre récursif ni conteneur de conteneur.

## Critères automatisés

- un seul contrôle Densité des listes ;
- présence des grilles box-inline-grid, flat-primary-grid,
  container-primary-grid et asset-primary-grid ;
- absence des titres verticaux redondants de prise, placement, solidité et
  éléments contenus ;
- actions bridge inchangées ;
- état de focus, caret, détails ouverts et scroll toujours restauré ;
- syntaxe JavaScript, tests DOM, bridge, roundtrip et installation valides.

## Gate humaine P44-M004V2

Dans Fusion avec le package 0.1.26, vérifier à la largeur habituelle puis dans une
palette plus étroite :

1. que boîte et premier plateau apparaissent sans grand espace mort ;
2. que le premier conteneur arrive rapidement sous la barre de création ;
3. que plusieurs conteneurs et leurs éléments enfants se comparent réellement ;
4. que nom, forme/type, X/Y/Z, quantité ou mode, paroi et fond restent lisibles ;
5. que les menus secondaires ne ferment pas la saisie ni ne déplacent le scroll ;
6. que le repli responsive reste utilisable et que les actions mesurent au moins
   40 px ;
7. qu’aucun calcul ni aucune scène Fusion ne se déclenche automatiquement.

Retour attendu : P44-M004V2 Fusion OK 0.1.26 - commit <sha>.

Un KO doit préciser la largeur approximative, la carte, le champ et l’écart
observé. P44-M005 reste bloquée jusqu’à cette preuve.

## Hotfix P44-M004V2H01 — contrôles collants et notifications

Package cible : palette Fusion 0.1.27.

La revue 0.1.26 accepte la densité hybride C et demande deux ajustements bornés :

- la barre Créer de Conteneurs et éléments reste collée immédiatement sous les
  onglets pendant le défilement ;
- la ligne Plateaux et livrets, ses résumés et son action d’ajout suivent la même
  règle dans le premier onglet ;
- l’offset collant est calculé depuis la hauteur réelle de l’en-tête, y compris
  après repli responsive ;
- les confirmations disparaissent après 3 secondes ;
- avertissements et erreurs disparaissent après 6 secondes ;
- chaque nouveau message annule le minuteur précédent ;
- le toast est remonté en haut de la palette pour ne plus masquer les premiers
  champs de la liste.

Aucun comportement métier, schéma, bridge, solveur, tolérance, géométrie, CAD IR
ou scène Fusion n’est modifié.

Retour attendu : P44-M004V2 Fusion OK 0.1.27 - commit <sha>.
