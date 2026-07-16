# Next Actions

Dernière mise à jour : 2026-07-16

## Version active

V0.1 reste mvp-accepted par P66 (package 0.1.20), fusion-validated: true et
print-validated: false. La fondation UX V0.2 continue dans P44 sans promouvoir
de capacité géométrique ou physique.

## Dernier état réel

P44-M007 est implemented et automated-validated dans le package Fusion 0.1.40
avec le correctif P44-M007H03 :

- validation dérivée après 350 ms et proposition complète après 1 500 ms de stabilité ;
- réponses obsolètes ignorées, DOM éditable non remplacé en arrière-plan et focus/sélection préservés ;
- tout fait carte invalidé affiche immédiatement `À recalculer` jusqu’à la réponse courante ;
- Aperçu priorisé, fallback manuel et matérialisation toujours explicite ;
- preset `Cartes` non sleevé par défaut ;
- `Méthode de mesure` reste à droite, immédiatement avant le menu `...` ;
- `Épaisseur paquet` affiche Z ; `Épaisseur carte × nb` affiche Qté et Épaisseur carte ;
- activer les sleeves propose 3 mm sur X/Y et 0,19 mm par carte sur Z ;
- `Nb cartes`, grisé, utilise le Z déclaré divisé par 0,31 et arrondi à l’entier le plus proche ;
- les X/Y et Z manuels déclarés restent séparés des dimensions résolues, sans cumul au roundtrip ;
- le cas X = 66, Y = 88, Z = 27, sleeves 3/0,19 donne 87 cartes et 69 × 91 × 43,53 mm ;
- les contrôles cartes sont compactés afin de conserver `Résolu` sur la même ligne large ;
- les modes `Compact` et `Détaillé` et leur persistance ont été supprimés ;
- chaque conteneur reste repliable et un bouton global replie/déplie tous les conteneurs ;
- les épaisseurs de paroi/fond héritées affichent `Défaut` ;
- `Hauteur de conception` reste dérivée, grisée et non éditable ;
- solveur de placement, budgets, tolérances, géométrie, CAD IR et scène inchangés.

Le package 0.1.37 a échoué la saisie rapide. Le package 0.1.38 a été supersédé
avant observation. Le retour Fusion sur 0.1.39 est un KO contextuel : delta X/Y
manuel absent de `Résolu` et faits dérivés parfois anciens. P44-M009H05 reste
fusion-validated dans Fusion 360 (package 0.1.36, preuve
`P44-M009H05 Fusion OK 0.1.36 - commit 7c76ba0`). P44-M007H03 est désormais
fusion-validated dans Fusion 360 (package 0.1.40, preuve
`P44-M007H03 Fusion OK 0.1.40 - commit 92f07c8`). Aucune valeur physique ni
impression réelle n’est validée ; `print-validated: false` reste obligatoire.

## Prochaine action recommandée

### P44-VP - Préparer la gate globale de fondation UX

Statut : ready.

P0-M010 est terminé : le parcours de reprise commence désormais par
[PILOTAGE_CURRENT.md](PILOTAGE_CURRENT.md). P44-VP prépare la gate P44-V, sans
ouvrir P45.

Objectif : consolider les preuves P44-M001 à P44-M009 et rendre la revue humaine
P44-V courte, reproductible et sans ambiguïté.

Scope : documentation et préparation de gate seulement. Aucun changement runtime,
solveur, schéma, valeur physique, géométrie ou scène automatique.

Ne pas ouvrir P45/P46, P47-P50, P67, P68 ou P69 pendant P44-VP.
`print-validated: false` reste obligatoire.

## Lots découverts, non ouverts

- `P45-M001` cadrera les dispositions des assets non-cartes (standard/auto,
  rangée et colonne verticale) avec effet réel sur les cavités et le solveur ;
  aucun contrôle décoratif n’est ajouté dans P44.

## Séquence verrouillée

P44-M005, P44-M006 et P44-M009H05 sont fusion-validated pour leurs parcours UX.
P44-M007H03 est désormais fusion-validated dans Fusion 360 ; P0-M010 est
terminée et P44-VP est la seule action suivante autorisée. P45/P46 ne commencent
pas avant P44-V ; P47-P50 restent bloqués jusqu’à P46 et P69 jusqu’à P50.
P68 peut recueillir des faits réels sans modifier les valeurs par défaut.

## Fin de chaque mission

Mettre à jour le pilotage, relire le diff, exécuter les preuves prévues, committer
puis intégrer directement dans main lorsqu’aucune gate humaine n’est ouverte.
Une gate Fusion ne devient jamais une validation d’impression.
