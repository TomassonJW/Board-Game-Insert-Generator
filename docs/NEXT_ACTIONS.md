# Next Actions

Dernière mise à jour : 2026-07-16

## Version active

V0.1 reste mvp-accepted par P66 (package 0.1.20), fusion-validated: true et print-validated: false. La fondation UX V0.2 continue dans P44 sans promouvoir de capacité géométrique ou physique.

## Dernier état réel

P44-M009H05 est fusion-validated dans Fusion 360 (package 0.1.36, commit 7c76ba0). print-validated: false :

- les jeux externes des conteneurs restent exclusivement globaux selon ADR-0064 ;
- les overrides asset, plateau et livret restent actifs ;
- Réglages est borné à une largeur lisible, avec son tableau X/Y–Z aligné à gauche ;
- les cartes conteneur regroupent nom, nombre d’éléments, minimum, mode, dimensions et épaisseurs sur une ligne technique compacte à largeur normale ;
- X, interversion, Y et Z apparaissent directement dans cette ligne en modes Cible et Fixe ; la flèche est absente en Auto ;
- l’identité et le minimum restent regroupés à gauche, tandis que Mode, dimensions, épaisseurs et actions sont justifiés à droite ;
- le mode global est intégré à droite du titre « Conteneurs », reflète Auto/Cible/Fixe ou Mixte et applique réellement le choix aux trois axes de tous les conteneurs ;
- aucune valeur, schéma, bridge, solveur, géométrie ou scène Fusion automatique ne change.

La revue Fusion confirme la composition finale et l’application du mode global. P44-M009H05V ferme la gate corrective ; aucune propriété physique ni impression réelle n’est validée.

## Prochaine action recommandée

### P44-M007 - Calcul adaptatif et Aperçu priorisé

Statut : ready-for-explicit-go. Le GO est déjà accordé pour la reprise dans le nouveau clavardage après son préflight Git et documentaire.

Objectif borné : calcul hybride adaptatif, annulation des requêtes obsolètes, Aperçu en premier et Matérialiser toujours explicite. Inclure le micro-ajustement UI qui maintient « Hauteur de conception » visiblement grisée car dérivée et non éditable.

Ne pas ouvrir P45/P46, P47-P50, P67, P68 ou P69. La prochaine gate humaine sera préparée seulement à la fin de P44-M007 selon son contrat.

P44-V reste la gate globale de fondation UX et print-validated: false reste obligatoire.

## Séquence verrouillée

P44-M005, P44-M006 et P44-M009H05 sont fusion-validated pour leurs parcours UX. P44-M007 est la seule mission suivante autorisée. P45/P46 ne commencent pas avant P44-V ; P47-P50 restent bloqués jusqu’à P46 et P69 jusqu’à P50. P68 peut recueillir des faits réels sans modifier les valeurs par défaut.

## Fin de chaque mission

Mettre à jour le pilotage, relire le diff, exécuter les preuves prévues, committer puis intégrer directement dans main lorsqu’aucune gate humaine n’est ouverte. Une gate Fusion ne devient jamais une validation d’impression.