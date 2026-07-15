# Next Actions

Dernière mise à jour : 2026-07-15

## Version active

V0.1 est mvp-accepted par P66 (package 0.1.20), fusion-validated: true et
print-validated: false. La fondation UX V0.2 continue dans P44 sans promouvoir
de capacité géométrique ou physique.

## Dernier état réel

P44-M004 est intégrée dans le package 0.1.25, mais sa revue humaine de densité
n’a pas été acceptée : la relation parent/enfants fonctionne, tandis que la
palette reste trop verticale pour comparer plusieurs cartes. Cette preuve ne
rend donc pas P44-M004 fusion-validated.

P44-M004V2 applique l’hybride C dans le package 0.1.26 : largeur utile de
1180 px, en-tête compact, une seule barre de création et densité, rangées
techniques pour boîte, plateaux/livrets, conteneurs et éléments, actions
secondaires en menus et calculs repliés. Aucun schéma, bridge, solveur,
tolérance, géométrie, CAD IR, scène automatique ou complément n’a changé.

## Prochaine action recommandée

### Gate humaine P44-M004V2

Statut : manual_validation_required, fusion-validated: false,
print-validated: false.

Dans Fusion avec le package 0.1.26, vérifier la densité réelle à la largeur
habituelle puis plus étroite, la comparaison de plusieurs parents/enfants, la
lisibilité des champs principaux, les menus secondaires, la stabilité de saisie
et l’absence de calcul ou scène automatique.

Retour attendu : P44-M004V2 Fusion OK 0.1.26 - commit <sha>.

Un KO doit indiquer largeur approximative, carte, champ et écart observé.

## Séquence verrouillée

P44-M005 reste bloquée jusqu’à P44-M004V2. P44-M008/P44-M009 gardent leur
contrat de tolérance. P45/P46 ne commencent pas avant P44-V ; P47-P50 restent
bloqués jusqu’à P46 et P69 jusqu’à P50. P68 peut recueillir des faits réels sans
modifier les valeurs par défaut. print-validated: false reste obligatoire.

## Fin de chaque mission

Mettre à jour le pilotage, relire le diff, exécuter les preuves prévues,
committer puis intégrer directement dans main lorsqu’aucune gate humaine
n’est ouverte. Une gate Fusion ne devient jamais une validation d’impression.
