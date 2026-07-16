# Next Actions

Dernière mise à jour : 2026-07-15

## Version active

V0.1 est mvp-accepted par P66 (package 0.1.20), fusion-validated: true et
print-validated: false. La fondation UX V0.2 continue dans P44 sans promouvoir
de capacité géométrique ou physique.

## Dernier état réel

P44-M009 est implémentée dans le package 0.1.31 : trois rôles,
héritage X/Y/Z, zéro explicite, provenance et deux vecteurs externes de
conteneur. Les paires utilisent max, jamais une somme. Les projets historiques
restent compatibles. fusion-validated: false, print-validated: false.

P44-M004 est intégrée dans le package 0.1.25, mais sa revue humaine de densité
n’a pas été acceptée : la relation parent/enfants fonctionne, tandis que la
palette reste trop verticale pour comparer plusieurs cartes. Cette preuve ne
rend donc pas P44-M004 fusion-validated.

P44-M004V2 applique l’hybride C dans le package 0.1.26 : largeur utile de
1180 px, en-tête compact, une seule barre de création et densité, rangées
techniques pour boîte, plateaux/livrets, conteneurs et éléments, actions
secondaires en menus et calculs repliés. Aucun schéma, bridge, solveur,
tolérance, géométrie, CAD IR, scène automatique ou complément n’a changé.

P44-M004V2H01 complète cette direction dans le package 0.1.27 : barre Créer et
ligne Plateaux et livrets collantes sous les onglets, confirmations remontées et
masquées après 3 secondes, avertissements ou erreurs après 6 secondes.

## Dernières gates humaines acceptées

### P44-M004V2 — densité hybride C et hotfix H01

Thomas a confirmé : "P44-M004V2 Fusion OK 0.1.27 - commit 80c1a6c".

Statut : done-human-gate, fusion-validated pour la surface UX P44-M004V2
uniquement ; print-validated: false.

La preuve couvre la compacité hybride C, la comparaison des cartes conteneur /
éléments, les contrôles Créer et Plateaux et livrets collants sous les onglets,
ainsi que les notifications temporisées. Elle ne qualifie ni le schéma, ni le
bridge, ni le solveur, ni les tolérances, ni la géométrie, ni le CAD IR, ni la
scène Fusion, ni une impression réelle.

## P44-M005 acceptée — gate Fusion 0.1.28

Preuve humaine : "P44-M005 Fusion OK 0.1.28 - commit b8cf884".

Statut : done-human-gate, fusion-validated pour le parcours UX P44-M005 ;
print-validated: false.

La validation couvre la barre de création persistante, le preset et la
destination explicite (nouveau conteneur lié ou existant), les presets
personnels, le raccourci local "+", leur suppression locale et l'absence de
complément, calcul ou scène Fusion automatique. Elle ne qualifie ni schéma,
bridge, solveur, tolérance, géométrie, CAD IR ou impression.

P44-M006 devient ready-for-explicit-go et ne commence pas sans GO explicite.

## Prochaine action recommandée

### P44-M007 - Calcul adaptatif et Aperçu priorisé

Statut : ready-for-explicit-go après P44-M009H01V acceptée dans Fusion sur le
package 0.1.32 (commit 8fc5157).

Le prochain GO ouvre uniquement P44-M007. Inclure d’abord le micro-ajustement
UI déjà demandé : dans Réglages, « Hauteur de conception » reste dérivée et non
éditable, mais doit être visiblement grisée. Aucun calcul, schéma ou sémantique
ne change par ce détail. Puis appliquer le contrat P44-M007 : calcul hybride
adaptatif, requêtes obsolètes gérées, Aperçu priorisé et matérialisation
explicite. P44-V reste la gate globale.

## Séquence verrouillée

P44-M005, P44-M006 et P44-M009H01 sont intégrées et fusion-validated pour leurs
parcours UX. P44-M008 est acceptée ; P44-M007 est la seule prochaine mission
ready-for-explicit-go.
P44-M008/P44-M009 gardent leur contrat de tolérance. P45/P46 ne commencent pas avant P44-V ;
P47-P50 restent bloqués jusqu’à P46 et P69 jusqu’à P50. P68 peut recueillir des
faits réels sans modifier les valeurs par défaut. print-validated: false reste
obligatoire.

## Fin de chaque mission

Mettre à jour le pilotage, relire le diff, exécuter les preuves prévues,
committer puis intégrer directement dans main lorsqu’aucune gate humaine n’est
ouverte. Une gate Fusion ne devient jamais une validation d’impression.
