# Next Actions

Dernière mise à jour : 2026-07-16

## Version active

V0.1 reste mvp-accepted par P66 (package 0.1.20), fusion-validated: true et print-validated: false. La fondation UX V0.2 continue dans P44 sans promouvoir de capacité géométrique ou physique.

## Dernier état réel

P44-M009H03 est implémentée dans le package 0.1.34 et automatisée. `fusion-validated: false`, `print-validated: false` :

- les jeux externes des conteneurs sont exclusivement globaux ;
- les anciennes valeurs par bac restent chargeables et roundtrippables, mais sont inactives ;
- les jeux par asset, plateau et livret restent actifs ;
- Réglages utilise une interface dense avec épaisseurs séparées et un tableau X/Y–Z ;
- « Hauteur de conception » reste calculée, grisée et non éditable ;
- aucune valeur, géométrie, scène Fusion automatique ou sémantique d’impression n’est ajoutée.

La validation fonctionnelle de P44-M009H01 puis la gate proposée P44-M009H02V sont révoquées par la décision produit ADR-0064. Le package 0.1.33 n’est pas fusion-validated.

## Prochaine action recommandée

### P44-M009H03V - Vérification Fusion des jeux globaux 0.1.34

Statut : human-fusion-check-required après intégration et installation.

Vérifier dans Fusion :

1. aucune carte de conteneur n’affiche « Jeu externe », « Voisinage total » ou un réglage de tolérance propre au bac ;
2. les volets de tolérance des assets restent présents et un override local ne modifie aucun autre asset ;
3. les volets de jeu des plateaux et livrets restent présents et locaux ;
4. Réglages affiche séparément « Épaisseurs minimales » et « Jeux (tolérances) » ;
5. le tableau contient exactement les lignes « Jeu entre conteneurs », « Jeu conteneur-boîte » et « Jeu élément-cavité (par défaut) », avec les colonnes X/Y et Z ;
6. modifier le jeu entre conteneurs X/Y ou Z s’applique globalement à tous les conteneurs ;
7. modifier le jeu conteneur-boîte X/Y agit sur le périmètre et Z agit sur la marge sous couvercle ;
8. modifier le jeu élément-cavité par défaut met à jour les assets hérités sans écraser leurs overrides ;
9. « Hauteur de conception » est visiblement grisée et non éditable ;
10. aucune scène Fusion n’est créée ou modifiée automatiquement.

Retour OK attendu :

`P44-M009H03 Fusion OK 0.1.34 - commit <sha>`

P44-M007 redevient ready-for-explicit-go seulement après ce retour. P44-V reste la gate globale.

## Séquence verrouillée

P44-M005 et P44-M006 restent fusion-validated pour leurs parcours UX. P44-M009H03V est la seule prochaine action ; P44-M007 est bloquée. P45/P46 ne commencent pas avant P44-V ; P47-P50 restent bloqués jusqu’à P46 et P69 jusqu’à P50. P68 peut recueillir des faits réels sans modifier les valeurs par défaut. `print-validated: false` reste obligatoire.

## Fin de chaque mission

Mettre à jour le pilotage, relire le diff, exécuter les preuves prévues, committer puis intégrer directement dans main lorsqu’aucune gate humaine n’est ouverte. Une gate Fusion ne devient jamais une validation d’impression.