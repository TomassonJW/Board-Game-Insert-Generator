# P64-L09U-V — preuve du human-KO 0.1.71

## 1. Verdict

- package observé : `0.1.71` ;
- gate : `human-KO` ;
- statut de diffusion : `do-not-run` ;
- `fusion-validated=false` ;
- `print-validated=false`.

Le démarrage vierge, le calcul explicite et la finalisation restent des acquis
positifs. La matérialisation Fusion est bloquante et invalide la candidate.

## 2. Observations humaines

Thomas confirme le 2026-07-27 :

- BGIG démarre sur un projet neuf, vide et non enregistré ;
- le calcul de `CasLimite01+` et `CasLimite02+` produit un plan ;
- la finalisation produit un aperçu certifié ;
- la matérialisation du plan minimal comme du plan final échoue ;
- Fusion affiche une scène partielle incohérente composée de volumes outils ;
- l'erreur visible est :
  `Combine1 / Compute Failed / ALL_TOOL_BODY_REFERENCE_LOST`.

La capture ne représente donc pas un insert calculé différemment. Elle montre
des corps outils persistés avant l'échec du premier Combine. Cette scène
partielle ne doit ni être enregistrée comme résultat, ni être utilisée pour une
validation géométrique.

## 3. Preuve du journal local

Le journal automatique de la session confirme :

- deux matérialisations en échec après environ `513 ms` et `697 ms` ;
- arrêt dès le premier Combine ;
- statut passerelle `bridge_error` ;
- aucune synchronisation de scène ;
- calcul et finalisation antérieurs terminés normalement.

Il ne s'agit donc pas d'une nouvelle attente de quinze minutes. La candidate
0.1.71 échoue immédiatement sur une référence Fusion invalide.

## 4. Cause exacte

La BaseFeature était ouverte, puis chaque BRep transitoire était ajouté avec
`BRepBodies.add`. L'adaptateur conservait les objets renvoyés pendant
l'édition et les passait au Combine après `finishEdit`.

Dans Fusion, ces objets sont les corps sources de la BaseFeature. Après
`finishEdit`, les features suivantes doivent utiliser les corps résultats
exposés par `baseFeature.bodies`. Les références sources ne sont plus des corps
outils valides, d'où `ALL_TOOL_BODY_REFERENCE_LOST`.

## 5. Risque secondaire

L'échec intervenait après création de composants et de corps BGIG. Aucun
rollback global n'entourait la génération complète. Une erreur pouvait donc
laisser une scène partielle, exactement comme sur la capture.

Le correctif successeur doit :

1. relire les corps résultats après `finishEdit` ;
2. refuser tout écart de cardinalité ;
3. supprimer atomiquement tous les objets BGIG créés si la génération échoue ;
4. signaler explicitement si ce nettoyage n'est pas complet.

## 6. CasLimite01++

Le fichier personnel a été lu sans modification.

- deux éléments ont été ajoutés au `Conteneur anonymisé 001` ;
- `18` agencements locaux certifiés sont générés ;
- `7` variantes sont retenues pour la recherche globale ;
- les profils Normal et Approfondi atteignent leur plafond sans plan ;
- un essai contrôlé en mémoire, limité à l'agencement canonique du conteneur
  001, trouve un plan complet certifié en environ `15,8 s`.

Ce résultat prouve la logeabilité du cas et montre que la sélection explicite
d'une ou plusieurs variantes locales peut réduire causalement la recherche
globale. Il ne prouve pas que le produit courant sait déjà appliquer cette
sélection.

## 7. Frontière

- aucun benchmark, holdout ou corpus solveur n'a été exécuté ;
- aucun projet personnel n'a été modifié ou versionné ;
- aucune valeur physique n'a été inventée ;
- aucune cavité n'a été déplacée ;
- les évolutions de progression, annulation, sélection visuelle et épaisseur
  de séparateur sont cadrées séparément du correctif Fusion.
