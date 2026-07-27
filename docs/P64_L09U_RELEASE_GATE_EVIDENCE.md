# P64-L09U — preuve corrective et candidate 0.1.71

## 1. Statut

- mission corrective : `automated-validated` ;
- candidate source : `0.1.71` ;
- verdict Fusion : `prepared-not-human-observed` ;
- `fusion-validated=false` ;
- `print-validated=false`.

## 2. Démarrage et persistance

Le chemin produit démarre désormais sur un projet vierge non enregistré :

- le dernier projet n'est pas rouvert ;
- `current_path` est remis à vide au chargement ;
- l'ancien brouillon de récupération n'est pas lu ;
- l'ouverture des fichiers nommés et récents reste explicite ;
- aucune sauvegarde de récupération n'est écrite ;
- aucun témoin certifié n'est chargé ou enregistré entre deux sessions.

Les anciens fichiers sont préservés mais inertes.

## 3. Recalcul frais

Le calcul passe toujours `initial_incumbent=None`.

La condition circulaire de la voie dense est supprimée. La réservation
supérieure automatique est résolue dans le problème spécialisé « piles au
sol », puis certifiée avec les corps et cavités figés.

Le replay local en lecture seule passe sur six variantes :

- `CasLimite01` ;
- `CasLimite01+` ;
- `CasLimite02` ;
- variante contenu seul ;
- variante jeux seuls ;
- `CasLimite02+`.

Sur un passage observé pendant le correctif :

- `CasLimite01+` : calcul frais environ `3.4 s`, finalisation certifiée ;
- `CasLimite02+` : calcul frais environ `11.4 s`, finalisation certifiée.

Ces durées sont informatives et ne remplacent pas la mesure Fusion.

## 4. Matérialisation groupée

Le CAD IR conserve chaque prisme et chaque coupe. L'adaptateur les groupe
seulement lors de l'exécution Fusion, par corps propriétaire.

Le replay correctif observe :

- `CasLimite01+` : `19` composants, `349` unions logiques en `19` lots et
  `113` coupes logiques en `19` lots ;
- `CasLimite02+` : `8` composants, `331` unions logiques en `8` lots et
  `129` coupes logiques en `8` lots.

Les variations de compte logique entre solutions certifiées restent permises.
Le rapport essentiel est stable : deux lots booléens principaux au maximum
par propriétaire pour ces opérations rectangulaires.

## 5. Certificats conservés

Les replays certifient :

- cavités figées ;
- unions avant coupes ;
- réservation supérieure virtuelle ;
- paroi minimale existante ;
- jeux externes ;
- corps composites ;
- `printable_residual_volume_mm3=0` ;
- CAD IR `ready_for_fusion`.

## 6. Préparation de gate

Le preflight public est
`scripts/fusion/p64_l09uv_preflight.py`.

Le préparateur est
`scripts/fusion/prepare_p64_l09uv_gate.ps1`.

Il :

- lance les tests ciblés ;
- rejoue les cas locaux en lecture seule s'ils existent ;
- génère la fixture et les reçus ;
- installe l'add-in 0.1.71 ;
- vérifie les marqueurs installés ;
- conserve les fichiers historiques ;
- configure un démarrage vierge ;
- laisse à Thomas uniquement les observations Fusion.

## 7. Validations

- tests ciblés solveur, palette, CAD, adaptateur et release : verts ;
- suite globale autorisée : `880/880` en `384.051 s` ;
- test ignoré : `1`, intégration SCIP native indisponible sous Python 3.10 ;
- modules exécutés : `113` ;
- modules benchmark/corpus/tournoi exclus : `12` ;
- replay local exact : `6/6`, lecture seule ;
- preflight :
  `53fc3f5adce84e51a2477113c171b11fbe723b12315ff01af185a19a502cb565`.

## 8. Limites

- aucune mesure réelle 0.1.71 n'est encore disponible dans Fusion ;
- le gain de performance reste à confirmer humainement ;
- aucune impression n'a été réalisée ;
- aucun benchmark ou holdout solveur n'a été exécuté.
