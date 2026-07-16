# Next Actions

Dernière mise à jour : 2026-07-16

## Version active

V0.1 reste mvp-accepted par P66 (package 0.1.20), fusion-validated: true et print-validated: false. La fondation UX V0.2 continue dans P44 sans promouvoir de capacité géométrique ou physique.

## Dernier état réel

P44-M009H04 est implémentée dans le package 0.1.35 et automatisée. `fusion-validated: false`, `print-validated: false` :

- les jeux externes des conteneurs restent exclusivement globaux selon ADR-0064 ;
- les overrides asset, plateau et livret restent actifs ;
- Réglages est borné à une largeur lisible, avec son tableau X/Y–Z aligné à gauche ;
- les cartes conteneur regroupent nom, nombre d’éléments, minimum, mode, dimensions et épaisseurs sur une ligne technique compacte à largeur normale ;
- X, interversion, Y et Z apparaissent directement dans cette ligne en modes Cible et Fixe ; la flèche est absente en Auto ;
- aucune valeur, schéma, bridge, solveur, géométrie ou scène Fusion automatique ne change.

La revue du package 0.1.34 a confirmé la direction fonctionnelle de H03, mais n’a pas accepté sa composition UI. P44-M009H03V est donc remplacée par P44-M009H04V.

## Prochaine action recommandée

### P44-M009H04V - Vérification Fusion de la densité finale 0.1.35

Statut : human-fusion-check-required après intégration et installation.

Vérifier dans Fusion :

1. Réglages ne s’étale plus sur toute la largeur et les champs X/Y–Z restent alignés verticalement dans un bloc proche des libellés ;
2. Épaisseurs minimales et Comportement sont lisibles, compacts et alignés à gauche ;
3. en mode Auto, la carte conteneur reste sur une rangée compacte et n’affiche ni dimensions explicites ni flèche X/Y ;
4. en mode Cible ou Fixe, X, la flèche, Y et Z apparaissent dans l’en-tête, sans rangée dédiée supplémentaire ;
5. le nombre d’éléments est placé sous le nom, le minimum est compact et proche du titre ;
6. les libellés indiquent « Épaisseur paroi » et « Épaisseur fond » ;
7. les jeux globaux H03 et les overrides locaux asset, plateau et livret restent fonctionnels ;
8. aucune scène Fusion n’est créée ou modifiée automatiquement.

Retour OK attendu :

`P44-M009H04 Fusion OK 0.1.35 - commit <sha>`

P44-M007 redevient ready-for-explicit-go seulement après ce retour. P44-V reste la gate globale.

## Séquence verrouillée

P44-M005 et P44-M006 restent fusion-validated pour leurs parcours UX. P44-M009H04V est la seule prochaine action ; P44-M007 est bloquée. P45/P46 ne commencent pas avant P44-V ; P47-P50 restent bloqués jusqu’à P46 et P69 jusqu’à P50. P68 peut recueillir des faits réels sans modifier les valeurs par défaut. `print-validated: false` reste obligatoire.

## Fin de chaque mission

Mettre à jour le pilotage, relire le diff, exécuter les preuves prévues, committer puis intégrer directement dans main lorsqu’aucune gate humaine n’est ouverte. Une gate Fusion ne devient jamais une validation d’impression.