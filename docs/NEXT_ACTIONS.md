# Next Actions

Dernière mise à jour : 2026-07-14

## Version active

V0.1 est mvp-accepted par P66 (package 0.1.20) ; fusion-validated: true,
print-validated: false. La fondation UX V0.2 est en cours dans P44, sans
qualification de géométrie ni d’impression.

## Dernière mission intégrée

P44-M003V est acceptée par P44-M003V Fusion OK 0.1.24 - commit 7b71d01.
P44-M004 est implemented et automated-validated sur le package 0.1.25 : les
contenus sont projetés dans leur conteneur parent à partir des collections
stables existantes. Le nom est le titre éditable, Déplacer vers… remplace le
rattachement permanent, et les modes Auto/Cible/Fixe respectent les cas
historiques Personnalisé.

Aucun schéma, bridge Python, solveur, tolérance, géométrie, CAD IR, scène
automatique ou complément n’a changé. Les textes nouveaux respectent le français UTF-8 accentué.

## Prochaine action recommandée

### Gate humaine P44-M004V

Statut : manual_validation_required, fusion-validated: false,
print-validated: false.

Dans Fusion, avec le package 0.1.25 installé, vérifier :

1. deux conteneurs avec des éléments affichés dans le bon parent ;
2. renommage, édition, déplacement via Déplacer vers…, sans perte de focus,
   caret, détails ouverts ni scroll ;
3. mode par conteneur Auto, Cible, Fixe, et un projet historique à axes mixtes
   conservé sous Personnalisé ;
4. contrôle global confirmé et refus de créer silencieusement des dimensions
   Cible ou Fixe manquantes ;
5. Solidité visible et Détails calculés secondaire ; aucune nouvelle scène ni
   action automatique.

Retour attendu : P44-M004V Fusion OK 0.1.25 - commit <sha>.

Un KO doit indiquer le conteneur, l’élément, l’action, la largeur approximative
et l’écart observé.

## Séquence verrouillée

P44-M005 reste bloquée jusqu’à P44-M004V. P44-M008/P44-M009 gardent leur
contrat et gate de tolérance ; P45/P46 ne commencent pas avant P44-V.
P47-P50 restent bloqués jusqu’à P46 et P69 jusqu’à P50. P68 peut recueillir
des faits réels sans modifier les valeurs par défaut. print-validated: false
reste obligatoire.

## Fin de chaque mission

Mettre à jour le pilotage, relire le diff, exécuter les preuves prévues,
committer puis intégrer directement dans main quand aucune gate humaine n’est
ouverte. Une gate Fusion ne devient jamais une validation d’impression.
