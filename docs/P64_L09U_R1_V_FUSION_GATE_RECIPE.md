# P64-L09U-R1-V — recette Fusion humaine 0.1.72

## 1. Statut

- package candidat : `0.1.72` ;
- 0.1.71 : `human-KO`, `do-not-run` ;
- gate : `prepared-not-human-observed` ;
- `fusion-validated=false` ;
- `print-validated=false`.

## 2. Avant de commencer

1. Ne poursuis pas dans le document qui contient la scène partielle 0.1.71.
2. Sauvegarde séparément tout travail Fusion non BGIG que tu veux conserver.
3. Ferme complètement Fusion.
4. Rouvre Fusion, puis BGIG.
5. Vérifie que la version affichée est `0.1.72`.
6. Ouvre un nouveau design Fusion vierge.

Le démarrage BGIG attendu est un projet neuf, vide et non enregistré.

## 3. Smoke d'échec propre

Ce contrôle vérifie d'abord que l'ancien défaut ne laisse plus de volumes
outils.

1. Ouvre explicitement `CasLimite01+.bgig.json`.
2. Clique sur Calculer en Normal.
3. Lance Matérialiser sur le plan minimal.
4. Chronomètre jusqu'au message de synchronisation.
5. Vérifie qu'aucun message `ALL_TOOL_BODY_REFERENCE_LOST` n'apparaît.
6. En cas d'autre erreur, vérifie qu'aucun corps BGIG partiel ne reste.

Verdict KO immédiat :

- retour de `ALL_TOOL_BODY_REFERENCE_LOST` ;
- outils rectangulaires visibles comme scène partielle ;
- scène annoncée synchronisée après une erreur ;
- composants BGIG partiels restant après l'échec.

## 4. CasLimite01+ final

1. Si le plan minimal a été matérialisé, utilise la commande BGIG de nettoyage
   de scène avant de continuer.
2. Clique sur Finaliser en Normal.
3. Vérifie que l'aperçu final reste cohérent.
4. Lance Matérialiser et chronomètre.
5. Vérifie la réactivité de Fusion.
6. Vérifie les `19` composants attendus pour cette solution, les couches
   basses, le plateau virtuel, les cavités et l'absence de trou imprimable.

Le compte exact peut varier seulement si le plan certifié sélectionné diffère ;
la scène doit toujours correspondre à l'aperçu courant.

## 5. CasLimite02+

1. Nettoie la scène BGIG.
2. Ouvre explicitement `CasLimite02+.bgig.json`.
3. Clique sur Calculer en Normal.
4. Clique sur Finaliser en Normal.
5. Matérialise le plan final en chronométrant.
6. Vérifie les `8` composants attendus pour cette solution, la cavité orientée,
   la réservation supérieure, les parois et l'absence de volumes outils.

## 6. Redémarrage

1. Ferme complètement Fusion.
2. Rouvre Fusion et BGIG.
3. Vérifie un projet BGIG neuf, vide et non enregistré.
4. Vérifie qu'aucun ancien projet n'est rouvert automatiquement.
5. Rouvre un cas explicitement et confirme qu'un vrai calcul repart.

## 7. Rapport attendu

Pour chaque matérialisation :

- `materialisation=OK|KO`, durée ;
- `fusion-responsive=true|false` ;
- `scene_synchronized=true|false` ;
- `all_tool_body_reference_lost=true|false` ;
- `partial_bgig_scene_after_error=true|false` ;
- nombre de composants ;
- défaut visuel éventuel et capture.

Pour le cycle :

- `calcul=OK|KO`, durée ;
- `finalisation=OK|KO`, durée ;
- `fresh_blank_startup=OK|KO` ;
- `previous_project_reopened=true|false` ;
- `fresh_calculation_observed=true|false`.

Ne promeus ni `fusion-validated` ni `print-validated` sans les preuves humaines
correspondantes.
