# Next Actions

Dernière mise à jour : 2026-07-17

## Version active

V0.1 reste `mvp-accepted` par P66, `fusion-validated: true` et
`print-validated: false`. P44 poursuit la fondation UX V0.2, mais P44-V reste en
KO contextuel tant que le solveur n'a pas passé P64-V2.

## Dernier état réel

- P44-M007H03 est `fusion-validated` dans Fusion 0.1.40 par la preuve
  `P44-M007H03 Fusion OK 0.1.40 - commit 92f07c8`.
- P44-M009H05 reste `fusion-validated` dans Fusion 0.1.36 par la preuve
  `P44-M009H05 Fusion OK 0.1.36 - commit 7c76ba0`.
- Le package initial P44-M007 0.1.37 a été supersédé ; P44-M007H03 0.1.40
  reste la référence validée pour focus, sleeves et Aperçu.
- P44-VH02 a corrigé suppression et nommage ; ses faits UX sont acceptés
  contextuellement, sans valider le solveur ni le package 0.1.43.
- P64-H01 est `fusion-validated` dans Fusion 0.1.42 par la preuve
  `P64-H01 Fusion OK 0.1.42 - commit 5865645`.
- P64-H02 est implémenté et automatisé dans 0.1.44, mais P64-H02V est un KO
  contextuel : un nouveau petit ajout peut encore épuiser la recherche alors
  que du volume reste disponible.
- Un essai local P64-H03 non commité a exploré d'autres ordres/structures. Un
  nouveau cas réel l'a également mis en échec ; il reste préservé hors `main`.
- P64-A01 documente la rupture : le solveur actuel devient baseline rapide ;
  placement 3D libre, beam et portefeuille Auto sont introduits derrière un
  contrat et un validateur communs.

## Prochaine action recommandée

### P64-H04 — Résultats honnêtes, observabilité et corpus de régression

Statut : `ready`. Contrat :
`docs/P64_H04_OBSERVABILITY_AND_RESULT_TRUTH_CONTRACT.md`.

Résultat attendu :

- distinguer `Solution trouvée`, `Aucune solution trouvée dans le budget`,
  `Impossible prouvé`, `Projet à corriger` et réponse obsolète/annulée ;
- exposer famille, budget, temps, candidats, états, motifs de coupe et motif
  d'arrêt sans voler le focus ;
- anonymiser et geler les cas réels P64-H01/H02/H03 dans la suite ;
- conserver exactement les placements actuels : aucun nouvel algorithme, seed,
  budget, score, schéma, default, tolérance, cavité ou comportement de scène.

Agent conseillé : Terra avec revue senior du contrat de résultat. Aucune gate
Fusion autonome n'est ouverte par défaut ; les libellés seront observés dans
P64-V2.

## Lots suivants, non ouverts

1. P64-H05 : contrat commun et baseline `Étages et piles`.
2. P64-H06 : placement 3D libre greedy EP/EMS.
3. P64-H07 : beam robuste, efforts et portefeuille `Auto intelligent`.
4. P64-H08 : réglages Fusion et diagnostic secondaire.
5. P64-V2 : gate humaine, puis reprise de P44-V.
6. P45/P46 selon leurs contrats actuels.
7. P64-F01/F02 après P46 : fermeture continue puis harmonisation modulaire.
8. P64-F03 après retours physiques ; P64-X01 exact seulement sous nouvelle gate.

## Séquence verrouillée

P64-H04 est la seule mission `ready`. P64-H05 à H08 s'ouvrent une par une. Aucune
preuve P64-H02/H03 ne doit être revendiquée. P44-V, P45 et P46 attendent P64-V2
puis la reprise positive de P44-V. P47-P50 restent bloqués jusqu'à P46 et P69
jusqu'à P50. P68 peut recueillir des faits réels sans recalibrer les defaults.

## Fin de chaque mission

Mettre à jour le pilotage, relire le diff, exécuter les preuves prévues, committer
puis intégrer directement dans `main` lorsqu'aucune gate humaine n'est ouverte.
Une gate Fusion ne devient jamais une validation d'impression.
