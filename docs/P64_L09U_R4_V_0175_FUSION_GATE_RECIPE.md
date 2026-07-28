# P64-L09U-R4-V — recette Fusion 0.1.75

Statut : `ready-human-gate`.

Avant le verdict : `fusion-validated=false`, `print-validated=false`.

## Préparation déjà faite par Codex

- package 0.1.75 intégré dans `origin/main` ;
- add-in installé avec son marqueur de commit ;
- fixture et reçus R4 préparés ;
- trois projets personnels rejoués sans modification ;
- suite automatisée et preflight passés.

Ferme complètement Fusion avant de commencer afin de ne pas conserver l'ancien
code Python en mémoire.

## Étape 1 — démarrage

1. Rouvre Fusion et recharge BGIG.
2. Vérifie la version `0.1.75`.
3. Vérifie que BGIG démarre sur un projet vierge non enregistré.

KO immédiat si la version est différente ou si un ancien projet est rechargé.

## Étape 2 — CasLimite01+ avec plateau

1. Ouvre explicitement `CasLimite01+`.
2. Lance `Calculer`, puis `Finaliser` en mode Normal.
3. Dans l'aperçu, repère les cavités placées sous le plateau.
4. Matérialise le plan final.
5. Inspecte un conteneur qui reçoit le plateau :
   - l'encastrement du plateau garde sa bonne forme ;
   - après retrait visuel du plateau, la cavité située dessous est directement
     ouverte et accessible ;
   - aucune dalle ni épaisseur de paroi ne sépare l'encastrement de la cavité ;
   - la cavité conserve sa profondeur calibrée.
6. Vérifie que le surplus de hauteur du conteneur reste sous la cavité, pas
   entre la cavité et le plateau.

KO si une cavité paraît absente, enfermée ou recouverte par une couche imprimée.

## Étape 3 — variante sans plateau

1. Retire localement le plateau sans enregistrer le projet source.
2. Recalcule, finalise et matérialise.
3. Vérifie que les cavités restent ouvertes sur la face fonctionnelle finale,
   avec leur profondeur calibrée et le surplus sous leur fond.

Ne sauvegarde pas cette variante.

## Étape 4 — CasLimite02+

1. Ouvre explicitement `CasLimite02+`.
2. Calcule puis finalise en mode Normal.
3. Repère les deux plateaux et leurs paliers dans l'aperçu.
4. Matérialise le plan final.
5. Pour chaque cavité qui se trouve sous un plateau :
   - vérifie qu'elle existe ;
   - vérifie qu'elle est accessible depuis l'encastrement ;
   - vérifie l'absence de surcouche imprimée ;
   - vérifie que sa profondeur et sa position correspondent à l'aperçu.
6. Confirme toujours :
   - aucune somme de hauteur dans les empreintes disjointes ;
   - cumul uniquement dans l'intersection réelle ;
   - paliers locaux pour les éléments réellement empilés.

## Étape 5 — CasLimite01++

1. Ouvre explicitement `CasLimite01++`.
2. Calcule, finalise et matérialise sans enregistrer la source.
3. Vérifie toutes les cavités sous plateau : aucune ne doit être cachée par une
   paroi intermédiaire.
4. Confirme la répartition, la fidélité aperçu/Fusion, la réactivité et
   l'apparition progressive des modules.

## Étape 6 — temps et robustesse

Pour les trois projets, note séparément :

- calcul ;
- finalisation ;
- matérialisation ;
- éventuelle terminaison après plafond.

KO si `ALL_TOOL_BODY_REFERENCE_LOST` revient, si une feature Combine
rectangulaire apparaît, si une scène partielle subsiste ou si un dépassement de
plafond reste inexpliqué.

## Rapport

Donne :

- `P64-L09U-R4-V Fusion OK 0.1.75` si tout passe ;
- sinon `P64-L09U-R4-V Fusion KO 0.1.75`, le projet, le conteneur et la cavité
  concernés, le défaut exact, les temps et une capture utile.

Même en cas de succès Fusion, conserve `print-validated=false` tant qu'aucune
impression réelle n'est mesurée.
