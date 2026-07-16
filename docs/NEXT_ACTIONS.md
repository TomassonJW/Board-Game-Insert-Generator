# Next Actions

Dernière mise à jour : 2026-07-16

## Version active

V0.1 reste mvp-accepted par P66 (package 0.1.20), fusion-validated: true et
print-validated: false. La fondation UX V0.2 continue dans P44 sans promouvoir
de capacité géométrique ou physique.

## Dernier état réel

P44-M007 est implemented et automated-validated dans le package Fusion 0.1.39
avec la correction P44-M007H02 :

- validation dérivée après 350 ms et proposition complète après 1 500 ms de stabilité ;
- réponses obsolètes ignorées et aucun rendu de fond ne remplace le DOM éditable ;
- focus, sélection et position de saisie préservés pendant autosave, validation et solve ;
- Aperçu priorisé, fallback manuel et matérialisation toujours explicite ;
- preset `Cartes` non sleevé par défaut ;
- `Méthode de mesure` placée à droite, immédiatement avant le menu `...` ;
- `Épaisseur paquet` affiche Z ; `Épaisseur carte × nb` affiche Qté et Épaisseur carte ;
- activer les sleeves propose 3 mm sur X/Y et 0,19 mm par carte sur Z dans les deux méthodes ;
- en épaisseur paquet, un nombre de cartes estimé, grisé et non éditable, est calculé par Z / 0,31 puis arrondi à l’entier le plus proche ;
- le Z résolu ajoute cette estimation multipliée par le delta sleeve Z, sans cumul lors des sauvegardes ;
- conteneurs repliables et `Hauteur de conception` dérivée, grisée et non éditable ;
- solveur de placement, budgets, tolérances, géométrie, CAD IR et scène inchangés.

Le package 0.1.37 a échoué la saisie rapide. Le package 0.1.38 a corrigé le
focus mais sa gate a été remplacée avant observation afin d’intégrer la
clarification cartes/sleeves 0.1.39. P44-M009H05 reste fusion-validated dans
Fusion 360 (package 0.1.36, preuve
`P44-M009H05 Fusion OK 0.1.36 - commit 7c76ba0`). P44-M007H02 n’est pas encore
fusion-validated et aucune valeur physique ni impression réelle n’est validée.

## Prochaine action recommandée

### P44-M007H02V - Gate Fusion corrective focus et cartes/sleeves

Statut : human-fusion-check-required après installation du package 0.1.39.

Thomas vérifie dans Fusion uniquement :

1. remplacer rapidement la sélection complète de plusieurs champs successifs ;
   autosave, minima et proposition ne volent ni focus ni sélection ;
2. seul le calcul correspondant aux dernières valeurs devient visible après
   environ 1,5 seconde de stabilité ;
3. le preset s’appelle `Cartes` et `Sleeves` est décoché par défaut ;
4. `Méthode de mesure` est le dernier champ avant `...`, après Z en
   `Épaisseur paquet` et après Épaisseur carte en mode compté ;
5. les champs Z ou Qté/Épaisseur carte apparaissent uniquement dans leur méthode ;
6. activer les sleeves expose X/Y = 3 mm et Z/carte = 0,19 mm dans les deux méthodes ;
7. avec Épaisseur paquet Z = 24 mm, l’estimation affiche 77 cartes et le Z résolu
   affiche 38,63 mm ; décocher les sleeves ramène le Z résolu à 24 mm ;
8. replier un conteneur masque ses assets sans masquer son en-tête ;
9. Aperçu, fallback manuel, hauteur grisée et absence de scène automatique restent conformes.

Preuve attendue :

```text
P44-M007H02 Fusion OK 0.1.39 - commit <sha>
```

Cette gate qualifie le comportement UI observé. Elle ne calibre pas les valeurs
3 mm, 0,19 mm ou 0,31 mm, ne valide pas la géométrie imprimée et ne vaut pas
validation d’impression.

Ne pas ouvrir P45/P46, P47-P50, P67, P68 ou P69 avant ce retour. P44-V reste la
gate globale de fondation UX et print-validated: false reste obligatoire.

## Lots découverts, non ouverts

- `P45-M001` cadrera les dispositions des assets non-cartes (standard/auto,
  rangée et colonne verticale) avec effet réel sur les cavités et le solveur ;
  aucun contrôle décoratif n’est ajouté dans P44.
- `P0-M010` compactera le pilotage de reprise (index court, archives et vues
  actionnables) après la gate courante, sans supprimer l’historique ni mélanger
  cette maintenance documentaire au lot produit.

## Séquence verrouillée

P44-M005, P44-M006 et P44-M009H05 sont fusion-validated pour leurs parcours UX.
P44-M007H02 est implemented et automated-validated ; P44-M007H02V est la seule
action suivante autorisée. P45/P46 ne commencent pas avant P44-V ; P47-P50
restent bloqués jusqu’à P46 et P69 jusqu’à P50. P68 peut recueillir des faits
réels sans modifier les valeurs par défaut.

## Fin de chaque mission

Mettre à jour le pilotage, relire le diff, exécuter les preuves prévues, committer
puis intégrer directement dans main lorsqu’aucune gate humaine n’est ouverte.
Une gate Fusion ne devient jamais une validation d’impression.
