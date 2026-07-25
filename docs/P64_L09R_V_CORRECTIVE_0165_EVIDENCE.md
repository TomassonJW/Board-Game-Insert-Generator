# P64-L09R-V — correctif 0.1.65 : compensation Z et budgets réactifs

Date : 2026-07-25

Statut : preuve corrective historique, `human-KO-after-install`, `superseded-by-ADR-0089`, `print-validated=false`.

## Incident observé pendant la gate 0.1.64

La gate P64-L09R-V a été ouverte avec l’add-in 0.1.64, sans être acceptée. Deux défauts ont été observés :

- dans une boîte de 60 mm, hauteur utile 59,6 mm, un plan certifié sans plateau culminait à 52,8 mm ; l’ajout d’un plateau 100 × 100 × 1 mm conduisait pourtant à `no_solution_within_budget` pour tous les budgets essayés ;
- changer le budget de calcul ne redessinait pas toujours son champ de durée, tandis qu’un changement du budget de finition provoquait indirectement ce rafraîchissement.

Les journaux locaux montrent que le worker SCIP recevait bien la réservation, mais gardait chaque hauteur de conteneur à son minimum. Le modèle exigeait simultanément qu’un corps atteigne le sommet de conception sous le plateau : il déclarait alors le modèle natif infaisable. Dans la palette, `saveSolverSetting` persistait l’état sans appeler immédiatement `renderSolverSettings`, contrairement au chemin de finition.

Aucune donnée personnelle ni snapshot local n’est ajouté au dépôt.

## Correction solveur

Le calcul minimal conserve une seule deadline globale et suit désormais ce chemin borné pour une réservation supérieure :

1. SCIP résout le placement minimal des conteneurs à leurs enveloppes minimales ;
2. une passe exacte choisit seulement un conteneur Z non figé qui chevauche réellement la réservation ;
3. elle ajoute uniquement la compensation nécessaire pour atteindre le sommet de conception ;
4. elle refuse la compensation si elle dépasse la boîte, rencontre un autre corps, réduit une variante, touche une cavité trop peu profonde ou concerne un axe Z figé ;
5. le certificat BGIG commun reste obligatoire avant toute publication ou matérialisation ;
6. si cette passe ne peut pas produire une proposition sûre, le modèle couplé SCIP reste le repli dans le temps restant ; un timeout reste `no_solution_within_budget`.

Le worker couplé porte aussi une hauteur Z variable limitée aux conteneurs non figés et justifiée par un support de réservation. Les sorties natives déclarent leur hauteur réelle ; la projection BGIG rejette toute expansion X/Y, toute réduction Z ou toute expansion Z non autorisée.

## Correction interface

`saveSolverSetting` appelle maintenant `renderSolverSettings()` avant l’envoi au bridge. Le sélecteur et le champ adjacent `3 s / 10 s / 20 s / 60 s / 3 min max` se mettent donc à jour immédiatement dans la palette, indépendamment de Fusion et du budget de finition.

## Preuves

- Régressions unitaires : conteneur Z automatique extensible sous plateau, projection de la hauteur native réelle, refus d’expansion sur Z figé, rafraîchissement immédiat du budget de calcul.
- Test natif CPython 3.14 + SCIP 10.0.2 : solution trouvée, hauteur portée de 52,8 mm à 55 mm, une invocation, certificat de projection valide.
- Rejeu local du cas exact observé : `solution_found`, 18 placements, `placement_certified=true`, `materializable=true`, sommet maximal 59,6 mm pour 59,6 mm utiles, environ 4 s en Normal.
- Préparateur P64-L09R-V 0.1.65 en dry-run : deux fixtures, deux réservations plateau, digest de préflight valide, aucune écriture AppData.
- Suite complète : 875/875 en 261,340 s ; un test natif SCIP ignoré sous Python 3.10, puis exécuté séparément avec le CPython 3.14 de Fusion et passé.

## Limites

- Ce rejeu natif n’est pas encore une observation dans l’interface Fusion 360 ; la gate humaine doit reprendre avec 0.1.65.
- Aucune finition, impression, tolérance physique ou fermeture de couvercle n’est validée par ce correctif.
- Le snapshot local ayant révélé l’incident reste hors dépôt.

## Suite

Le package 0.1.65 du commit `2dbc272` a été publié, installé et observé. Le rafraîchissement du budget est acquis, mais la gate est KO : le calcul allonge arbitrairement un conteneur sous plateau et la finition reste incomplète.

La suite canonique est `docs/P64_L09R_V_0165_HUMAN_KO_EVIDENCE.md`, ADR-0089 puis le Goal P64-L09S. L’ancienne recette ne reprend pas. `print-validated=false` reste obligatoire.