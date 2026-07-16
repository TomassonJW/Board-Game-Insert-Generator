# Next Actions

Dernière mise à jour : 2026-07-16

## Version active

V0.1 reste mvp-accepted par P66 (package 0.1.20), fusion-validated: true et print-validated: false. La fondation UX V0.2 continue dans P44 sans promouvoir de capacité géométrique ou physique.

## Dernier état réel

P44-M009H05 est implémentée dans le package 0.1.36 et automatisée. `fusion-validated: false`, `print-validated: false` :

- les jeux externes des conteneurs restent exclusivement globaux selon ADR-0064 ;
- les overrides asset, plateau et livret restent actifs ;
- Réglages est borné à une largeur lisible, avec son tableau X/Y–Z aligné à gauche ;
- les cartes conteneur regroupent nom, nombre d’éléments, minimum, mode, dimensions et épaisseurs sur une ligne technique compacte à largeur normale ;
- X, interversion, Y et Z apparaissent directement dans cette ligne en modes Cible et Fixe ; la flèche est absente en Auto ;
- l’identité et le minimum restent regroupés à gauche, tandis que Mode, dimensions, épaisseurs et actions sont justifiés à droite ;
- le mode global est intégré à droite du titre « Conteneurs », reflète Auto/Cible/Fixe ou Mixte et applique réellement le choix aux trois axes de tous les conteneurs ;
- aucune valeur, schéma, bridge, solveur, géométrie ou scène Fusion automatique ne change.

La revue du package 0.1.35 valide la compacité générale mais demande une dernière composition de l’en-tête conteneur et corrige l’état trompeur du mode global. P44-M009H04V est donc remplacée par P44-M009H05V.

## Prochaine action recommandée

### P44-M009H05V - Vérification Fusion de la densité finale 0.1.36

Statut : human-fusion-check-required après intégration et installation.

Vérifier dans Fusion :

1. le nom, le nombre d’éléments et le minimum calculé restent regroupés à gauche de chaque carte ;
2. Mode, X/Y/Z en Cible/Fixe, épaisseurs et actions sont alignés contre la droite ;
3. Auto masque toujours X/Y/Z et la flèche ;
4. le mode global est sur la même ligne que « Conteneurs », sans bande supplémentaire ;
5. il affiche « Mixte » lorsque les conteneurs diffèrent et reflète Auto, Cible ou Fixe lorsqu’ils sont uniformes ;
6. choisir Auto, Cible ou Fixe puis « Appliquer » met les trois axes de tous les conteneurs dans ce mode ;
7. aucune scène Fusion n’est créée ou modifiée automatiquement.

Retour OK attendu :

`P44-M009H05 Fusion OK 0.1.36 - commit <sha>`

P44-M007 redevient ready-for-explicit-go seulement après ce retour. P44-V reste la gate globale.

## Séquence verrouillée

P44-M005 et P44-M006 restent fusion-validated pour leurs parcours UX. P44-M009H05V est la seule prochaine action ; P44-M007 est bloquée. P45/P46 ne commencent pas avant P44-V ; P47-P50 restent bloqués jusqu’à P46 et P69 jusqu’à P50. P68 peut recueillir des faits réels sans modifier les valeurs par défaut. `print-validated: false` reste obligatoire.

## Fin de chaque mission

Mettre à jour le pilotage, relire le diff, exécuter les preuves prévues, committer puis intégrer directement dans main lorsqu’aucune gate humaine n’est ouverte. Une gate Fusion ne devient jamais une validation d’impression.