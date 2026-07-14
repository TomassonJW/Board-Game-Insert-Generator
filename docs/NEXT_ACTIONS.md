# Next Actions

Dernière mise à jour : 2026-07-14

## Version active

V0.1 est `mvp-accepted` par P66 (package 0.1.20) ; `fusion-validated: true`,
`print-validated: false`. La fondation UX V0.2 est en cours dans P44, sans
qualification de géométrie ni d’impression.

## Dernière mission intégrée

P44-M003 est `implemented` et `automated-validated` sur le package 0.1.24.
La palette comporte maintenant quatre onglets : `Boîte et plateaux`,
`Conteneurs et éléments`, `Réglages`, `Aperçu`. Les boutons
`Précédent`/`Suivant` ont disparu. L’interversion X/Y est locale et
atomique pour boîte, élément, plateau/livret et contrat de conteneur.

Aucun schéma, bridge Python, solveur, tolérance, géométrie, CAD IR, scène
automatique ou complément n’a changé. Les textes modifiés sont UTF-8
accentués conformément au contrat P44.

## Prochaine action recommandée

### Gate humaine P44-M003V

Statut : `manual_validation_required`, `fusion-validated: false`, `print-validated: false`.

Dans Fusion, avec le package 0.1.24 installé, vérifier :

1. les quatre onglets et la disparition de `Précédent`/`Suivant` ;
2. Boîte avec plateaux/livrets, puis Conteneurs avec éléments, sans perte de
   saisie ou de scroll ;
3. `Ordre de retrait`, la phrase de placement et `Orientation historique` d’un
   plateau/livret ;
4. chaque bouton X/Y : valeurs boîte, élément, plateau/livret et mode/valeurs
   X/Y d’un conteneur ; aucune origine X/Y ne doit bouger ;
5. le rendu réel des accents français, y compris `Boîte`, `Éléments`, `Réglages`,
   `Aperçu`, `Épaisseur` et `Quantité`.

Retour attendu :

```text
P44-M003V Fusion OK 0.1.24 - commit <sha>
```

Un KO doit indiquer l’onglet, l’objet, la largeur approximative et l’écart observé.

## Séquence verrouillée

P44-M004 reste bloquée jusqu’à P44-M003V. P44-M008/P44-M009 gardent leur
contrat et gate de tolérance ; P45/P46 ne commencent pas avant P44-V.
P47-P50 restent bloqués jusqu’à P46 et P69 jusqu’à P50. P68 peut
recueillir des faits réels sans modifier les valeurs par défaut.
`print-validated: false` reste obligatoire.


## Fin de chaque mission

Mettre à jour le pilotage, relire le diff, exécuter les preuves prévues,
committer puis intégrer directement dans `main` quand aucune gate humaine
n’est ouverte. Une gate Fusion ne devient jamais une validation d’impression.
