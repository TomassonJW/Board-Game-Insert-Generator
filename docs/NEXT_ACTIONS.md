# Next Actions

Dernière mise à jour : 2026-07-17

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

Le retour contextuel suivant confirme que P44-VH01 laisse désormais passer le
cas de hauteur initial, mais révèle deux limites du solveur : faux impossible
sur environ 30 conteneurs et 77 éléments malgré environ 40 % de volume minimal,
et attente de la saturation XY avant d'utiliser Z. P64-H01 corrige ces limites
dans le package 0.1.42 par partitions adaptatives bornées, arrangements XY
conscients de leur hauteur et score d'équilibre X/Y/Z avec charge des étages.

## Prochaine action recommandée

### P64-H01V - Recherche dense et équilibre spatial 3D

Statut : human-fusion-check-required. P64-H01 est implemented et
automated-validated dans le package 0.1.42. Le projet réel augmenté du petit
asset problématique trouve une solution complète en deux étages en environ
1,8 seconde ; les fixtures homogènes 2, 8 et 32 conteneurs choisissent
respectivement 1, 2 et 3 étages en mode Équilibré.

Thomas rouvre le projet dense, reproduit l'ajout du petit asset, vérifie que le
calcul reste constructible, que Z est utilisé progressivement et qu'aucune
scène ne change avant matérialisation. Retour attendu :

    P64-H01 Fusion OK 0.1.42 - commit <sha>

Après ce retour, P44-VH02 est la seule mission de code suivante : suppression
directe d’un élément, confirmation pour supprimer un conteneur non vide avec
tous ses éléments, et nom de conteneur incrémental en cas de doublon.

P44-V reste ouverte ; P45 ne commence pas. `print-validated: false`.

## Lots découverts, non ouverts

- `P45-M001` cadrera les dispositions des assets non-cartes (standard/auto,
  rangée et colonne verticale) avec effet réel sur les cavités et le solveur ;
  aucun contrôle décoratif n’est ajouté dans P44.

## Séquence verrouillée

P44-M005, P44-M006 et P44-M009H05 sont fusion-validated pour leurs parcours UX.
P44-M007H03 est désormais fusion-validated dans Fusion 360 ; P0-M010 et P44-VP
sont terminées. P44-VH01V est supersédée sans revendication fusion-validated par
P64-H01V, seule action humaine suivante. P44-V reste en KO contextuel et P45/P46
ne commencent pas avant sa reprise positive après P44-VH02. P47-P50 restent
bloqués jusqu’à P46 et P69 jusqu’à P50.
P68 peut recueillir des faits réels sans modifier les valeurs par défaut.

## Fin de chaque mission

Mettre à jour le pilotage, relire le diff, exécuter les preuves prévues, committer
puis intégrer directement dans main lorsqu’aucune gate humaine n’est ouverte.
Une gate Fusion ne devient jamais une validation d’impression.
