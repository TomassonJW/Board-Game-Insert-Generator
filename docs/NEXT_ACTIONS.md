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

### P0-M010 - Compacter le pilotage de reprise

Statut : ready.

Dépendance satisfaite : P44-M007H03V est fusion-validated dans Fusion 360.

Objectif : réduire le coût de reprise, les lectures redondantes et les risques
de divergence du backlog/roadmap sans perdre l’historique auditable.

Scope autorisé : documentation et pilotage uniquement : index courant court,
vues `actif / prochain / bloqué`, archives et liens de reprise. Aucun changement
runtime, produit, solveur, schéma ou valeur physique ; aucune suppression
destructive d’historique.

Vérifications attendues :

1. relire le diff documentaire et vérifier les liens vers les contrats actifs ;
2. conserver les anciennes décisions et preuves en archive auditable ;
3. garder une seule mission `ready` et une séquence explicite vers P45 ;
4. mettre à jour STATUS, NEXT_ACTIONS, BACKLOG et le journal de mission.

Ne pas ouvrir P45/P46, P47-P50, P67, P68 ou P69 pendant P0-M010. La validation
Fusion ne vaut pas validation d’impression et `print-validated: false` reste
obligatoire.

## Lots découverts, non ouverts

- `P45-M001` cadrera les dispositions des assets non-cartes (standard/auto,
  rangée et colonne verticale) avec effet réel sur les cavités et le solveur ;
  aucun contrôle décoratif n’est ajouté dans P44.

## Séquence verrouillée

P44-M005, P44-M006 et P44-M009H05 sont fusion-validated pour leurs parcours UX.
P44-M007H03 est désormais fusion-validated dans Fusion 360 ; P0-M010 est la
seule action suivante autorisée. P45/P46 ne commencent pas avant la fin de P0 et
la gate P44 appropriée ; P47-P50 restent bloqués jusqu’à P46 et P69 jusqu’à P50.
P68 peut recueillir des faits réels sans modifier les valeurs par défaut.

## Fin de chaque mission

Mettre à jour le pilotage, relire le diff, exécuter les preuves prévues, committer
puis intégrer directement dans main lorsqu’aucune gate humaine n’est ouverte.
Une gate Fusion ne devient jamais une validation d’impression.
