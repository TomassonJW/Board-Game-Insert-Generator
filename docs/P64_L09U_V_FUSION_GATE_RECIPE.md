# P64-L09U-V — recette Fusion humaine 0.1.71

## 1. Statut

- package candidat : `0.1.71` ;
- gate : `prepared-not-human-observed` ;
- `fusion-validated=false` ;
- `print-validated=false`.

## 2. Préconditions déjà préparées par Codex

- add-in 0.1.71 installé ;
- commit installé vérifié ;
- réglages Calcul et Finition sur Normal ;
- fixture publique et reçus installés ;
- projets personnels relus sans modification ;
- état de document configuré avec `current_path` vide ;
- aucun témoin intersession actif.

## 3. Redémarrage vierge

1. Ferme complètement Fusion.
2. Rouvre Fusion et recharge BGIG 0.1.71.
3. Ouvre l'Atelier de rangement.
4. Vérifie que BGIG présente un projet neuf, vide et non enregistré.
5. Vérifie qu'aucun ancien projet n'est rouvert automatiquement.

Verdict attendu : `OK`.

## 4. CasLimite01+

1. Ouvre explicitement `CasLimite01+.bgig.json`.
2. Clique sur Calculer en Normal.
3. Vérifie qu'un vrai calcul visible est exécuté et qu'il ne s'agit pas d'un
   retour instantané de témoin.
4. Note le temps du calcul.
5. Clique sur Finaliser en Normal.
6. Vérifie l'aperçu final et note le temps.
7. Lance Matérialiser en démarrant un chronomètre.
8. Observe si Fusion reste réactif.
9. Note le temps exact jusqu'à `scene_synchronized`.
10. Vérifie les 19 composants, les couches basses, le plateau virtuel, les
    cavités et l'absence de trou imprimable central.

Critère KO immédiat : matérialisation encore bloquée plusieurs minutes,
message durable « ne répond pas », scène partielle ou géométrie différente de
l'aperçu certifié.

## 5. CasLimite02+

1. Ouvre explicitement `CasLimite02+.bgig.json`.
2. Rejoue Calculer puis Finaliser en Normal.
3. Lance une matérialisation chronométrée.
4. Vérifie les 8 composants, la cavité orientée, le plateau/livret virtuel,
   les parois et le résiduel nul.
5. Note séparément calcul, finalisation et matérialisation.

## 6. Second redémarrage

1. Ferme complètement Fusion après les observations.
2. Rouvre Fusion et BGIG.
3. Vérifie à nouveau le projet vierge non enregistré.
4. Rouvre un cas explicitement.
5. Clique sur Calculer et vérifie qu'un vrai calcul repart de zéro.

## 7. Rapport attendu

Pour chaque cas, transmets :

- `calcul=OK|KO`, durée ;
- `finalisation=OK|KO`, durée ;
- `materialisation=OK|KO`, durée ;
- `fusion-responsive=true|false` ;
- `scene_synchronized=true|false` ;
- nombre de composants ;
- défauts visuels éventuels ;
- capture de l'aperçu et de la scène matérialisée.

Pour le redémarrage :

- `fresh_blank_startup=OK|KO` ;
- `previous_project_reopened=true|false` ;
- `fresh_calculation_observed=true|false`.

Ne promeus pas `print-validated` sans impression et mesures réelles.
